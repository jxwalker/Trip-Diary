"""
Google Places Enhancer Service
Enriches restaurant and attraction data with photos, ratings, and booking links
"""
import os
import re
from typing import Dict, List, Optional
import googlemaps
from dotenv import load_dotenv
from pathlib import Path
import asyncio
import aiohttp

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class GooglePlacesEnhancer:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if self.api_key:
            self.client = googlemaps.Client(key=self.api_key)
        else:
            self.client = None
            print("[WARNING] GOOGLE_MAPS_API_KEY not found in environment "
                  "variables")
            print("[INFO] To enable enhanced maps and attraction details, "
                  "get a free API key from:")
            print("https://developers.google.com/maps/documentation/places/"
                  "web-service/get-api-key")
            print("[INFO] Then set GOOGLE_MAPS_API_KEY in your environment "
                  "or .env file")
    
    async def initialize(self):
        """Initialize the Google Places enhancer service"""
        pass
    
    async def search_attractions(self, location: str, limit: int = 10) -> List[Dict]:
        """Search for attractions in a location"""
        if not self.client:
            print("[WARNING] Google Maps API key not configured")
            return []
        
        try:
            # Search for tourist attractions using Places API (New)
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = "https://places.googleapis.com/v1/places:searchText"
                headers = {
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.types,places.id,places.photos,places.regularOpeningHours,places.priceLevel"
                }
                payload = {
                    "textQuery": f"tourist attractions in {location}",
                    "maxResultCount": limit
                }
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"Places API (New) search failed: {error_text}")
                        return []
                    
                    data = await response.json()
                    places_result = {"results": data.get("places", [])}
            
            attractions = []
            for place in places_result.get('results', [])[:limit]:
                attraction = {
                    "name": place.get('displayName', {}).get('text', ''),
                    "address": place.get('formattedAddress', ''),
                    "rating": place.get('rating', 0),
                    "types": place.get('types', []),
                    "place_id": place.get('id', ''),
                    "price_level": place.get('priceLevel'),
                    "opening_hours": place.get('regularOpeningHours', {}),
                    "photos": []
                }
                
                if place.get('photos'):
                    for photo in place['photos'][:3]:  # Max 3 photos
                        photo_url = (
                            f"https://maps.googleapis.com/maps/api/place/photo"
                            f"?maxwidth=400&photoreference={photo['photo_reference']}"
                            f"&key={self.api_key}"
                        )
                        attraction['photos'].append(photo_url)
                
                attractions.append(attraction)
            
            return attractions
            
        except Exception as e:
            print(f"Error searching attractions: {e}")
            return []
            
    async def enhance_restaurant(self, restaurant: Dict, 
                                 destination: str) -> Dict:
        """
        Enhance a restaurant with Google Places data including photos and 
        booking URLs
        """
        if not self.client:
            print("[WARNING] Google Maps API key not configured")
            return restaurant
            
        try:
            # Search for the restaurant
            query = (f"{restaurant.get('name', '')} restaurant "
                    f"{restaurant.get('address', '')} {destination}")
            places_result = self.client.places(query=query)
            
            if not places_result.get('results'):
                print(f"[DEBUG] No Google Places results for: {query}")
                return restaurant
                
            place = places_result['results'][0]
            place_id = place['place_id']
            
            # Get detailed information
            details = self.client.place(place_id)['result']
            
            # Enhance restaurant data
            enhanced = restaurant.copy()
            
            # Add Google data
            enhanced['google_place_id'] = place_id
            enhanced['rating'] = details.get('rating', 
                                            restaurant.get('rating'))
            enhanced['user_ratings_total'] = details.get('user_ratings_total', 
                                                        0)
            enhanced['price_level'] = details.get('price_level', '')
            
            # Full address
            if details.get('formatted_address'):
                enhanced['address'] = details['formatted_address']
                
            # Phone number
            if details.get('formatted_phone_number'):
                enhanced['phone'] = details['formatted_phone_number']
                
            # Website
            if details.get('website'):
                enhanced['website'] = details['website']
                
            # Opening hours
            if details.get('opening_hours'):
                hours = details['opening_hours']
                enhanced['hours'] = hours.get('weekday_text', [])
                enhanced['open_now'] = hours.get('open_now', None)
                
            # Photos
            if details.get('photos'):
                photo_refs = []
                for photo in details['photos'][:3]:  # Get up to 3 photos
                    photo_ref = photo.get('photo_reference')
                    if photo_ref:
                        # Store photo reference instead of full URL to avoid 
                        # exposing API key
                        photo_url = f"/api/places/photo/{photo_ref}"
                        photo_refs.append(photo_url)
                enhanced['photos'] = photo_refs
                enhanced['photo'] = photo_refs[0] if photo_refs else None
                
            # Google Maps URL
            if details.get('url'):
                enhanced['google_maps_url'] = details['url']
                
            # Static map image for the restaurant
            if details.get('geometry', {}).get('location'):
                location = details['geometry']['location']
                lat, lng = location['lat'], location['lng']
                # Store coordinates instead of full URL to avoid exposing 
                static_map_url = (f"/api/places/staticmap?lat={lat}&lng={lng}"
                                f"&type=restaurant")
                enhanced['static_map_url'] = static_map_url
                enhanced['coordinates'] = {"lat": lat, "lng": lng}
                
            # Try to extract or create booking URLs
            enhanced['booking_url'] = await self._find_booking_url(
                restaurant.get('name', ''),
                destination,
                details.get('website', '')
            )
            
            # Add review snippets
            if details.get('reviews'):
                reviews = details['reviews'][:2]  # Get top 2 reviews
                enhanced['reviews'] = [
                    {
                        'rating': r.get('rating'),
                        'text': r.get('text', '')[:200],  # Truncate reviews
                        'time': r.get('relative_time_description', '')
                    }
                    for r in reviews
                ]
                
            print(f"[DEBUG] Enhanced {restaurant.get('name')} with "
                  f"Google Places data")
            return enhanced
            
        except Exception as e:
            print(f"[ERROR] Failed to enhance restaurant "
                  f"{restaurant.get('name')}: {e}")
            return restaurant
            
    async def _find_booking_url(self, restaurant_name: str, city: str, 
                                website: str = "") -> str:
        """
        Try to find or construct a booking URL for the restaurant
        """
        # Clean restaurant name for URL
        clean_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip()
        url_name = clean_name.lower().replace(' ', '-')
        
        # Check if website is already a booking platform
        if website:
            if ('opentable.com' in website or 'resy.com' in website or 
                'yelp.com/biz' in website):
                return website
                
        # Try common booking platforms
        booking_urls = {
            'opentable': (f"https://www.opentable.com/s/?term={clean_name}"
                         f"&location={city}"),
            'resy': (f"https://resy.com/cities/{city.lower()}"
                    f"?query={clean_name}"),
            'yelp': (f"https://www.yelp.com/search?find_desc={clean_name}"
                    f"&find_loc={city}")
        }
        
        # Return OpenTable as default
        return booking_urls['opentable']
        
    async def enhance_restaurants_batch(self, restaurants: List[Dict], 
                                        destination: str) -> List[Dict]:
        """
        Enhance multiple restaurants in parallel
        """
        if not restaurants:
            return []
            
        print(f"[DEBUG] Enhancing {len(restaurants)} restaurants with "
              f"Google Places data...")
        
        # Process in parallel with rate limiting
        enhanced_restaurants = []
        for i in range(0, len(restaurants), 3):  # Process 3 at a time
            batch = restaurants[i:i+3]
            tasks = [self.enhance_restaurant(r, destination) for r in batch]
            results = await asyncio.gather(*tasks)
            enhanced_restaurants.extend(results)
            
            # Small delay between batches
            if i + 3 < len(restaurants):
                await asyncio.sleep(0.5)
                
        return enhanced_restaurants
        
    async def enhance_attraction(self, attraction: Dict, 
                                 destination: str) -> Dict:
        """
        Enhance an attraction with Google Places data
        """
        if not self.client:
            return attraction
            
        try:
            # Search for the attraction
            query = (f"{attraction.get('name', '')} "
                    f"{attraction.get('address', '')} {destination}")
            places_result = self.client.places(query=query)
            
            if not places_result.get('results'):
                return attraction
                
            place = places_result['results'][0]
            place_id = place['place_id']
            
            # Get detailed information
            details = self.client.place(place_id)['result']
            
            # Enhance attraction data
            enhanced = attraction.copy()
            
            # Add Google data
            enhanced['google_place_id'] = place_id
            enhanced['rating'] = details.get('rating', 
                                            attraction.get('rating'))
            enhanced['user_ratings_total'] = details.get('user_ratings_total', 
                                                        0)
            
            # Full address
            if details.get('formatted_address'):
                enhanced['address'] = details['formatted_address']
                
            # Website
            if details.get('website'):
                enhanced['website'] = details['website']
                
            # Opening hours
            if details.get('opening_hours'):
                hours = details['opening_hours']
                enhanced['hours'] = hours.get('weekday_text', [])
                enhanced['open_now'] = hours.get('open_now', None)
                
            # Photos
            if details.get('photos'):
                photo_refs = []
                for photo in details['photos'][:3]:
                    photo_ref = photo.get('photo_reference')
                    if photo_ref:
                        # Store photo reference instead of full URL to avoid 
                        # exposing API key
                        photo_url = f"/api/places/photo/{photo_ref}"
                        photo_refs.append(photo_url)
                enhanced['photos'] = photo_refs
                enhanced['photo'] = photo_refs[0] if photo_refs else None
                
            # Google Maps URL
            if details.get('url'):
                enhanced['google_maps_url'] = details['url']
                
            # Static map image for the attraction
            if details.get('geometry', {}).get('location'):
                location = details['geometry']['location']
                lat, lng = location['lat'], location['lng']
                # Store coordinates instead of full URL to avoid exposing 
                static_map_url = (f"/api/places/staticmap?lat={lat}&lng={lng}"
                                f"&type=attraction")
                enhanced['static_map_url'] = static_map_url
                enhanced['coordinates'] = {"lat": lat, "lng": lng}
                
            # Enhanced booking URLs for different attraction types
            attraction_type = attraction.get('type', '').lower()
            if 'museum' in attraction_type or 'gallery' in attraction_type:
                enhanced['booking_url'] = (details.get('website', '') or 
                    f"https://www.viator.com/searchResults/all?text="
                    f"{attraction.get('name', '')}&destId={destination}")
                enhanced['ticket_info'] = ("Advance booking recommended for "
                    "popular museums")
            elif 'park' in attraction_type or 'garden' in attraction_type:
                enhanced['booking_url'] = (details.get('website', '') or 
                    f"https://maps.google.com/?cid={place_id}")
                enhanced['ticket_info'] = "Free entry - no booking required"
            elif 'monument' in attraction_type or 'landmark' in attraction_type:
                enhanced['booking_url'] = (details.get('website', '') or 
                    f"https://maps.google.com/?cid={place_id}")
                enhanced['ticket_info'] = ("Check website for entry "
                    "requirements")
            else:
                enhanced['booking_url'] = (details.get('website', '') or 
                    f"https://maps.google.com/?cid={place_id}")
                enhanced['ticket_info'] = ("Check website for entry "
                    "requirements")
                
            print(f"[DEBUG] Enhanced {attraction.get('name')} with "
                  f"Google Places data")
            return enhanced
            
        except Exception as e:
            print(f"[ERROR] Failed to enhance attraction "
                  f"{attraction.get('name')}: {e}")
            return attraction
            
    async def enhance_attractions_batch(self, attractions: List[Dict], 
                                        destination: str) -> List[Dict]:
        """
        Enhance multiple attractions in parallel
        """
        if not attractions:
            return []
            
        print(f"[DEBUG] Enhancing {len(attractions)} attractions with "
              f"Google Places data...")
        
        # Process in parallel with rate limiting
        enhanced_attractions = []
        for i in range(0, len(attractions), 3):
            batch = attractions[i:i+3]
            tasks = [self.enhance_attraction(a, destination) for a in batch]
            results = await asyncio.gather(*tasks)
            enhanced_attractions.extend(results)
            
            if i + 3 < len(attractions):
                await asyncio.sleep(0.5)
                
        return enhanced_attractions
    
    async def get_destination_map_data(self, destination: str) -> Dict:
        """
        Get comprehensive map data for a destination including coordinates 
        and map URLs
        """
        if not self.client:
            return {
                "destination": destination,
                "error": "Google Maps API key not configured",
                "setup_instructions": ("Get a free API key from "
                    "https://developers.google.com/maps/documentation/"
                    "places/web-service/get-api-key")
            }
        
        try:
            # Get coordinates for the destination
            geocode_result = self.client.geocode(destination)
            if not geocode_result:
                return {
                    "destination": destination,
                    "error": f"Could not find coordinates for {destination}"
                }
            
            location = geocode_result[0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            
            # Create various map URLs
            map_urls = {
                "google_maps": f"https://maps.google.com/?q={lat},{lng}",
                "google_maps_embed": (f"https://www.google.com/maps/embed/"
                    f"v1/place?key={self.api_key}&q={lat},{lng}"),
                "directions": (f"https://maps.google.com/maps/dir/?api=1"
                    f"&destination={lat},{lng}"),
                "street_view": f"https://maps.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lng}"
            }
            
            return {
                "destination": destination,
                "coordinates": {"lat": lat, "lng": lng},
                "map_urls": map_urls,
                "formatted_address": geocode_result[0].get('formatted_address', destination)
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get map data for {destination}: {e}")
            return {
                "destination": destination,
                "error": str(e)
            }
    
    async def create_attraction_route(self, attractions: List[Dict], start_location: str = None) -> Dict:
        """
        Create an optimized route between attractions
        """
        if not self.client or not attractions:
            return {
                "error": "Google Maps API key not configured or no attractions provided"
            }
        
        try:
            # Get coordinates for all attractions
            waypoints = []
            for attraction in attractions:
                if attraction.get('coordinates'):
                    waypoints.append(f"{attraction['coordinates']['lat']},{attraction['coordinates']['lng']}")
                elif attraction.get('address'):
                    # Geocode the address
                    geocode_result = self.client.geocode(attraction['address'])
                    if geocode_result:
                        location = geocode_result[0]['geometry']['location']
                        waypoints.append(f"{location['lat']},{location['lng']}")
            
            if not waypoints:
                return {"error": "Could not get coordinates for attractions"}
            
            # Create route URL
            if start_location:
                route_url = f"https://maps.google.com/maps/dir/{start_location}/"
            else:
                route_url = f"https://maps.google.com/maps/dir/"
            
            route_url += "/".join(waypoints)
            
            return {
                "route_url": route_url,
                "waypoints": waypoints,
                "attraction_count": len(attractions),
                "optimization_note": "Route is optimized for efficient travel between attractions"
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to create attraction route: {e}")
            return {"error": str(e)}
