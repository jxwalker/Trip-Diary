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
    
    async def get_travel_time(self, origin: str, destination: str, mode: str = "driving") -> Dict:
        """
        Get travel time between two locations
        """
        if not self.client:
            return self._mock_travel_time(origin, destination, mode)
        
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
                return self._mock_travel_time(origin, destination, mode)
                
        except Exception as e:
            print(f"Maps API error: {e}")
            return self._mock_travel_time(origin, destination, mode)
    
    def _mock_travel_time(self, origin: str, destination: str, mode: str) -> Dict:
        """
        Mock travel time for when API is not available
        """
        # Provide reasonable estimates
        if "airport" in origin.lower() or "airport" in destination.lower():
            return {
                "distance": "15 miles",
                "duration": "45 mins",
                "duration_value": 2700
            }
        else:
            return {
                "distance": "5 miles",
                "duration": "15 mins",
                "duration_value": 900
            }
    
    async def get_place_details(self, place_name: str) -> Dict:
        """
        Get details about a place
        """
        if not self.client:
            return self._mock_place_details(place_name)
        
        try:
            # Search for the place
            places_result = self.client.places(query=place_name)
            
            if places_result['results']:
                place = places_result['results'][0]
                place_id = place['place_id']
                
                # Get detailed information
                details = self.client.place(place_id)['result']
                
                return {
                    "name": details.get('name', place_name),
                    "address": details.get('formatted_address', ''),
                    "phone": details.get('formatted_phone_number', ''),
                    "rating": details.get('rating', 0),
                    "price_level": details.get('price_level', 0),
                    "website": details.get('website', ''),
                    "hours": details.get('opening_hours', {}).get('weekday_text', []),
                    "location": {
                        "lat": details['geometry']['location']['lat'],
                        "lng": details['geometry']['location']['lng']
                    }
                }
            else:
                return self._mock_place_details(place_name)
                
        except Exception as e:
            print(f"Place details error: {e}")
            return self._mock_place_details(place_name)
    
    def _mock_place_details(self, place_name: str) -> Dict:
        """
        Mock place details
        """
        return {
            "name": place_name,
            "address": "123 Main Street, City",
            "phone": "+1 555-0123",
            "rating": 4.5,
            "price_level": 2,
            "website": "https://example.com",
            "hours": [
                "Monday: 9:00 AM – 9:00 PM",
                "Tuesday: 9:00 AM – 9:00 PM",
                "Wednesday: 9:00 AM – 9:00 PM",
                "Thursday: 9:00 AM – 9:00 PM",
                "Friday: 9:00 AM – 10:00 PM",
                "Saturday: 10:00 AM – 10:00 PM",
                "Sunday: 10:00 AM – 8:00 PM"
            ],
            "location": {
                "lat": 40.7128,
                "lng": -74.0060
            }
        }
    
    def get_static_map_url(self, locations: List[Dict], size: str = "600x400") -> str:
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
                marker = f"markers=color:red%7Clabel:{i+1}%7C{loc['lat']},{loc['lng']}"
                params.append(marker)
            elif 'address' in loc:
                marker = f"markers=color:red%7Clabel:{i+1}%7C{loc['address'].replace(' ', '+')}"
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