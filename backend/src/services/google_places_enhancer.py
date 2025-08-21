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
            
    async def enhance_restaurant(self, restaurant: Dict, destination: str) -> Dict:
        """
        Enhance a restaurant with Google Places data including photos and booking URLs
        """
        if not self.client:
            print("[WARNING] Google Maps API key not configured")
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
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={self.api_key}"
                        photo_refs.append(photo_url)
                enhanced['photos'] = photo_refs
                enhanced['photo'] = photo_refs[0] if photo_refs else None
                
            # Google Maps URL
            if details.get('url'):
                enhanced['google_maps_url'] = details['url']
                
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
            return enhanced
            
        except Exception as e:
            print(f"[ERROR] Failed to enhance restaurant {restaurant.get('name')}: {e}")
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
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={self.api_key}"
                        photo_refs.append(photo_url)
                enhanced['photos'] = photo_refs
                enhanced['photo'] = photo_refs[0] if photo_refs else None
                
            # Google Maps URL
            if details.get('url'):
                enhanced['google_maps_url'] = details['url']
                
            # Ticket booking URL for attractions
            if 'museum' in attraction.get('type', '').lower() or 'gallery' in attraction.get('type', '').lower():
                enhanced['booking_url'] = details.get('website', '') or f"https://www.viator.com/searchResults/all?text={clean_name}&destId={city}"
                
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