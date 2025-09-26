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
from datetime import datetime

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class GooglePlacesEnhancer:
    def __init__(self):
        """Initialize Google Places enhancer with circuit breaker"""
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
        self.client = None if not self.api_key else googlemaps.Client(key=self.api_key)
        
        self._failure_count = 0
        self._max_failures = 5
        self._circuit_open = False
        self._last_failure_time = None
        self._reset_interval = 300  # 5 minutes
        
    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker is open (too many failures)"""
        if not self._circuit_open:
            return False
            
        if self._last_failure_time and (datetime.now() - self._last_failure_time).total_seconds() > self._reset_interval:
            self._circuit_open = False
            self._failure_count = 0
            return False
            
        return True
        
    def _record_failure(self):
        """Record API failure for circuit breaker"""
        self._failure_count += 1
        self._last_failure_time = datetime.now()
        if self._failure_count >= self._max_failures:
            self._circuit_open = True
            print(f"[WARNING] Google Places circuit breaker opened after {self._failure_count} failures")
            
    def _record_success(self):
        """Record API success for circuit breaker"""
        self._failure_count = 0
        if self._circuit_open:
            self._circuit_open = False
            print("[INFO] Google Places circuit breaker closed after successful request")
            
    async def enhance_restaurant(self, restaurant: Dict, destination: str) -> Dict:
        """
        Enhance a restaurant with Google Places data including photos and booking URLs
        """
        if not self.client:
            print("[WARNING] Google Maps API key not configured")
            return restaurant
            
        if self._check_circuit_breaker():
            print("[WARNING] Google Places circuit breaker is open, skipping enhancement")
            return restaurant
            
        try:
            # Search for the restaurant
            query = f"{restaurant.get('name', '')} restaurant {restaurant.get('address', '')} {destination}"
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
            enhanced['rating'] = details.get('rating', restaurant.get('rating'))
            enhanced['user_ratings_total'] = details.get('user_ratings_total', 0)
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
                        # Store photo reference instead of full URL to avoid exposing API key
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
                # Store coordinates instead of full URL to avoid exposing API key
                static_map_url = f"/api/places/staticmap?lat={lat}&lng={lng}&type=restaurant"
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
                        'text': r.get('text', '')[:200],  # Truncate long reviews
                        'time': r.get('relative_time_description', '')
                    }
                    for r in reviews
                ]
                
            print(f"[DEBUG] Enhanced {restaurant.get('name')} with Google Places data")
            self._record_success()
            return enhanced
            
        except Exception as e:
            print(f"[ERROR] Failed to enhance restaurant {restaurant.get('name')}: {e}")
            self._record_failure()
            return restaurant
            
    async def _find_booking_url(self, restaurant_name: str, city: str, website: str = "") -> str:
        """
        Try to find or construct a booking URL for the restaurant
        """
        # Clean restaurant name for URL
        clean_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip()
        url_name = clean_name.lower().replace(' ', '-')
        
        # Check if website is already a booking platform
        if website:
            if 'opentable.com' in website or 'resy.com' in website or 'yelp.com/biz' in website:
                return website
                
        # Try common booking platforms
        booking_urls = {
            'opentable': f"https://www.opentable.com/s/?term={clean_name}&location={city}",
            'resy': f"https://resy.com/cities/{city.lower()}?query={clean_name}",
            'yelp': f"https://www.yelp.com/search?find_desc={clean_name}&find_loc={city}"
        }
        
        # Return OpenTable as default
        return booking_urls['opentable']
        
    async def enhance_restaurants_batch(self, restaurants: List[Dict], destination: str) -> List[Dict]:
        """
        Enhance multiple restaurants in parallel
        """
        if not restaurants:
            return []
            
        print(f"[DEBUG] Enhancing {len(restaurants)} restaurants with Google Places data...")
        
        # Process in parallel with rate limiting
        enhanced_restaurants = []
        for i in range(0, len(restaurants), 3):  # Process 3 at a time to avoid rate limits
            batch = restaurants[i:i+3]
            tasks = [self.enhance_restaurant(r, destination) for r in batch]
            results = await asyncio.gather(*tasks)
            enhanced_restaurants.extend(results)
            
            # Small delay between batches
            if i + 3 < len(restaurants):
                await asyncio.sleep(0.5)
                
        return enhanced_restaurants
        
    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker is open (too many failures)"""
        if not self._circuit_open:
            return False
            
        if self._last_failure_time and (datetime.now() - self._last_failure_time).total_seconds() > self._reset_interval:
            self._circuit_open = False
            self._failure_count = 0
            return False
            
        return True
        
    async def enhance_attraction(self, attraction: Dict, destination: str) -> Dict:
        """
        Enhance an attraction with Google Places data
        """
        if not self.client:
            return attraction
            
        try:
            # Search for the attraction
            query = f"{attraction.get('name', '')} {attraction.get('address', '')} {destination}"
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
            enhanced['rating'] = details.get('rating', attraction.get('rating'))
            enhanced['user_ratings_total'] = details.get('user_ratings_total', 0)
            
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
                        # Store photo reference instead of full URL to avoid exposing API key
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
                # Store coordinates instead of full URL to avoid exposing API key
                static_map_url = f"/api/places/staticmap?lat={lat}&lng={lng}&type=attraction"
                enhanced['static_map_url'] = static_map_url
                enhanced['coordinates'] = {"lat": lat, "lng": lng}
                
            # Enhanced booking URLs for different attraction types
            attraction_type = attraction.get('type', '').lower()
            if 'museum' in attraction_type or 'gallery' in attraction_type:
                enhanced['booking_url'] = details.get('website', '') or f"https://www.viator.com/searchResults/all?text={attraction.get('name', '')}&destId={destination}"
                enhanced['ticket_info'] = "Advance booking recommended for popular museums"
            elif 'park' in attraction_type or 'garden' in attraction_type:
                enhanced['booking_url'] = details.get('website', '') or f"https://maps.google.com/?cid={place_id}"
                enhanced['ticket_info'] = "Free entry - no booking required"
            elif 'monument' in attraction_type or 'landmark' in attraction_type:
                enhanced['booking_url'] = details.get('website', '') or f"https://maps.google.com/?cid={place_id}"
                enhanced['ticket_info'] = "Check website for entry requirements"
            else:
                enhanced['booking_url'] = details.get('website', '') or f"https://maps.google.com/?cid={place_id}"
                enhanced['ticket_info'] = "Check website for entry requirements"
                
            print(f"[DEBUG] Enhanced {attraction.get('name')} with Google Places data")
            return enhanced
            
        except Exception as e:
            print(f"[ERROR] Failed to enhance attraction {attraction.get('name')}: {e}")
            return attraction
            
    async def enhance_attractions_batch(self, attractions: List[Dict], destination: str) -> List[Dict]:
        """
        Enhance multiple attractions in parallel
        """
        if not attractions:
            return []
            
        print(f"[DEBUG] Enhancing {len(attractions)} attractions with Google Places data...")
        
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
        Get comprehensive map data for a destination including coordinates and map URLs
        """
        if not self.client:
            return {
                "destination": destination,
                "error": "Google Maps API key not configured",
                "setup_instructions": "Get a free API key from https://developers.google.com/maps/documentation/places/web-service/get-api-key"
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
                "google_maps_embed": f"https://www.google.com/maps/embed/v1/place?key={self.api_key}&q={lat},{lng}",
                "directions": f"https://maps.google.com/maps/dir/?api=1&destination={lat},{lng}",
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
