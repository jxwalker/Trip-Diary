"""
Maps Service
Handles Google Maps integration for distances, travel times, and map generation
"""
import os
from typing import Dict, List, Tuple
import googlemaps
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class MapsService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if self.api_key:
            self.client = googlemaps.Client(key=self.api_key)
        else:
            self.client = None
    
    async def get_travel_time(self, origin: str, destination: str, 
                              mode: str = "driving") -> Dict:
        """
        Get travel time between two locations
        """
        if not self.client:
            return {
                "distance": None,
                "duration": None,
                "duration_value": None,
                "error": "GOOGLE_MAPS_API_KEY not configured"
            }
        
        try:
            result = self.client.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode=mode,
                units="imperial"
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                return {
                    "distance": element['distance']['text'],
                    "duration": element['duration']['text'],
                    "duration_value": element['duration']['value']
                }
            else:
                return {
                    "distance": None,
                    "duration": None,
                    "duration_value": None,
                    "error": "DistanceMatrix returned non-OK status"
                }
                
        except Exception as e:
            print(f"Maps API error: {e}")
            return {
                "distance": None,
                "duration": None,
                "duration_value": None,
                "error": str(e)
            }
    
    async def get_place_details(self, place_name: str) -> Dict:
        """
        Get details about a place
        """
        if not self.client:
            return {
                "name": place_name,
                "address": "",
                "phone": "",
                "rating": 0,
                "price_level": None,
                "website": "",
                "hours": [],
                "location": None,
                "error": "GOOGLE_MAPS_API_KEY not configured"
            }
        
        try:
            import aiohttp
            import json
            
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.api_key,
                'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.types,places.rating,places.priceLevel,places.internationalPhoneNumber,places.websiteUri,places.regularOpeningHours'
            }
            
            text_search_url = "https://places.googleapis.com/v1/places:searchText"
            request_body = {
                "textQuery": place_name,
                "maxResultCount": 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(text_search_url, headers=headers, json=request_body) as response:
                    if response.status == 200:
                        data = await response.json()
                        places = data.get('places', [])
                        if places:
                            place = places[0]
                            details = {
                                'name': place.get('displayName', {}).get('text', place_name),
                                'formatted_address': place.get('formattedAddress', ''),
                                'rating': place.get('rating', 0),
                                'price_level': place.get('priceLevel', 0),
                                'formatted_phone_number': place.get('internationalPhoneNumber', ''),
                                'website': place.get('websiteUri', ''),
                                'opening_hours': {
                                    'weekday_text': [period.get('openTime', '') + ' - ' + period.get('closeTime', '') 
                                                   for period in place.get('regularOpeningHours', {}).get('periods', [])]
                                },
                                'geometry': {
                                    'location': {
                                        'lat': place.get('location', {}).get('latitude', 0),
                                        'lng': place.get('location', {}).get('longitude', 0)
                                    }
                                }
                            }
                        else:
                            details = None
                    else:
                        if hasattr(self, 'client') and self.client:
                            try:
                                places_result = self.client.places(query=place_name)
                                if places_result['results']:
                                    place = places_result['results'][0]
                                    place_id = place['place_id']
                                    details = self.client.place(place_id, fields=[
                                        'name', 'formatted_address', 'formatted_phone_number',
                                        'website', 'rating', 'price_level', 'opening_hours', 'geometry'
                                    ])['result']
                                else:
                                    details = None
                            except Exception as e:
                                print(f"Legacy Places API fallback failed: {e}")
                                details = None
                        else:
                            details = None
                
            if details:
                return {
                    "name": details.get('name', place_name),
                    "address": details.get('formatted_address', ''),
                    "phone": details.get('formatted_phone_number', ''),
                    "rating": details.get('rating', 0),
                    "price_level": details.get('price_level', 0),
                    "website": details.get('website', ''),
                    "hours": details.get('opening_hours', {}).get(
                        'weekday_text', []),
                    "location": {
                        "lat": details['geometry']['location']['lat'],
                        "lng": details['geometry']['location']['lng']
                    }
                }
            else:
                return {
                    "name": place_name,
                    "address": "",
                    "phone": "",
                    "rating": 0,
                    "price_level": None,
                    "website": "",
                    "hours": [],
                    "location": None
                }
                
        except Exception as e:
            print(f"Place details error: {e}")
            return {
                "name": place_name,
                "address": "",
                "phone": "",
                "rating": 0,
                "price_level": None,
                "website": "",
                "hours": [],
                "location": None,
                "error": str(e)
            }
    
    def get_static_map_url(self, locations: List[Dict], 
                           size: str = "600x400") -> str:
        """
        Generate a static map URL with markers
        """
        if not self.api_key:
            return ""
        
        base_url = "https://maps.googleapis.com/maps/api/staticmap?"
        
        # Add parameters
        params = [
            f"size={size}",
            f"key={self.api_key}"
        ]
        
        # Add markers for each location
        for i, loc in enumerate(locations):
            if 'lat' in loc and 'lng' in loc:
                marker = (f"markers=color:red%7Clabel:{i+1}%7C"
                         f"{loc['lat']},{loc['lng']}")
                params.append(marker)
            elif 'address' in loc:
                marker = (f"markers=color:red%7Clabel:{i+1}%7C"
                         f"{loc['address'].replace(' ', '+')}")
                params.append(marker)
        
        # Set zoom to show all markers
        params.append("zoom=13")
        
        return base_url + "&".join(params)
    
    async def geocode_address(self, address: str) -> Tuple[float, float]:
        """
        Convert address to coordinates
        """
        if not self.client:
            return (40.7128, -74.0060)  # Default to NYC
        
        try:
            geocode_result = self.client.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return (location['lat'], location['lng'])
            else:
                return (40.7128, -74.0060)
        except Exception as e:
            print(f"Geocoding error: {e}")
            return (40.7128, -74.0060)
