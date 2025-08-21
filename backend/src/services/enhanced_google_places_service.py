"""
Enhanced Google Places Service
Comprehensive restaurant and attraction data using Google Places API
Cost-effective alternative to Yelp with rich data including photos, reviews, and booking info
"""
import asyncio
import aiohttp
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import os
import googlemaps
from pathlib import Path
from dotenv import load_dotenv

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """Service error exception"""
    pass


class ConfigurationError(Exception):
    """Configuration error exception"""
    pass


class EnhancedGooglePlacesService:
    """Enhanced Google Places API service for comprehensive restaurant and attraction data"""
    
    def __init__(self):
        """Initialize Google Places service"""
        self.logger = logger
        
        # API configuration
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if self.api_key:
            self.client = googlemaps.Client(key=self.api_key)
        else:
            self.client = None
        
        # Cache configuration
        self.cache_ttl = 3600  # 1 hour cache
        self._initialized = False
        
        # Simple in-memory cache for testing
        self._cache = {}
        
    @property
    def service_name(self) -> str:
        return "google_places"
    
    @property
    def api_key_required(self) -> bool:
        return True
    
    async def initialize(self) -> None:
        """Initialize the service"""
        if not self.api_key:
            raise ConfigurationError("GOOGLE_MAPS_API_KEY not configured")
        
        # Test API connectivity
        await self.validate_api_key()
        self._initialized = True
        logger.info("Google Places service initialized successfully")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            # Simple API test
            await self.validate_api_key()
            return {
                "status": "healthy",
                "service": "google_places",
                "timestamp": datetime.now().isoformat(),
                "api_key_configured": bool(self.api_key)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "google_places",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "api_key_configured": bool(self.api_key)
            }
    
    async def cleanup(self) -> None:
        """Cleanup service resources"""
        # No persistent connections to clean up
        pass
    
    async def validate_api_key(self) -> bool:
        """Validate the Google Places API key"""
        if not self.api_key or not self.client:
            raise ConfigurationError("GOOGLE_MAPS_API_KEY not configured")
        
        try:
            # Test with a simple place search
            result = self.client.places(query="restaurant", location="New York, NY")
            return bool(result.get('results'))
            
        except Exception as e:
            logger.error(f"Google Places API key validation failed: {e}")
            raise ConfigurationError(f"Invalid Google Places API key: {e}")
    
    async def search_restaurants(
        self,
        location: str,
        cuisine_type: Optional[str] = None,
        price_range: Optional[str] = None,
        limit: int = 20,
        radius: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for restaurants using Google Places API
        
        Args:
            location: Location to search (e.g., "New York, NY")
            cuisine_type: Type of cuisine (e.g., "italian", "mexican")
            price_range: Price range (1-4, where 1 = $, 4 = $$$$)
            limit: Number of results to return
            radius: Search radius in meters
            
        Returns:
            List of restaurant data dictionaries
        """
        if not self.client:
            raise ConfigurationError("Google Places API not configured")
        
        # Build search query
        query = f"restaurant in {location}"
        if cuisine_type:
            query = f"{cuisine_type} restaurant in {location}"
        
        # Check cache first
        cache_key = f"google_restaurants_{hashlib.md5(f'{query}_{price_range}_{limit}'.encode()).hexdigest()}"
        if cache_key in self._cache:
            logger.info(f"Returning cached Google Places restaurant search for {location}")
            return self._cache[cache_key]
        
        try:
            restaurants = []
            
            # Search for restaurants
            if radius:
                # Use nearby search with radius
                places_result = self.client.places_nearby(
                    location=location,
                    radius=radius,
                    type='restaurant',
                    keyword=cuisine_type
                )
            else:
                # Use text search
                places_result = self.client.places(
                    query=query,
                    type='restaurant'
                )
            
            # Process results
            for place in places_result.get('results', [])[:limit]:
                try:
                    # Get detailed information
                    place_id = place['place_id']
                    details = self.client.place(
                        place_id,
                        fields=[
                            'name', 'formatted_address', 'formatted_phone_number',
                            'rating', 'user_ratings_total', 'price_level', 'website',
                            'opening_hours', 'photos', 'reviews', 'url', 'geometry',
                            'types', 'business_status'
                        ]
                    )['result']
                    
                    # Format restaurant data
                    restaurant = await self._format_restaurant_data(details, place_id)
                    
                    # Filter by price range if specified
                    if price_range and restaurant.get('price_level_numeric'):
                        target_price = self._convert_price_range_to_numeric(price_range)
                        if target_price and restaurant['price_level_numeric'] != target_price:
                            continue
                    
                    restaurants.append(restaurant)
                    
                except Exception as e:
                    logger.warning(f"Failed to process restaurant {place.get('name', 'unknown')}: {e}")
                    continue
            
            # Sort by rating and review count
            restaurants.sort(key=lambda x: (x.get('rating', 0), x.get('review_count', 0)), reverse=True)
            
            # Cache the results
            self._cache[cache_key] = restaurants
            
            logger.info(f"Found {len(restaurants)} restaurants in {location}")
            return restaurants
            
        except Exception as e:
            logger.error(f"Google Places restaurant search failed: {e}")
            raise ServiceError(f"Restaurant search failed: {e}")
    
    async def _format_restaurant_data(self, details: Dict[str, Any], place_id: str) -> Dict[str, Any]:
        """Format Google Places data into standardized restaurant format"""
        
        # Extract cuisine types from Google Places types
        cuisine_types = []
        place_types = details.get('types', [])
        cuisine_mapping = {
            'bakery': 'Bakery',
            'bar': 'Bar',
            'cafe': 'Cafe',
            'meal_delivery': 'Delivery',
            'meal_takeaway': 'Takeaway',
            'restaurant': 'Restaurant'
        }
        
        for place_type in place_types:
            if place_type in cuisine_mapping:
                cuisine_types.append(cuisine_mapping[place_type])
        
        # Format photos
        photos = []
        if details.get('photos'):
            for photo in details['photos'][:5]:  # Get up to 5 photos
                photo_ref = photo.get('photo_reference')
                if photo_ref:
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={self.api_key}"
                    photos.append(photo_url)
        
        # Format reviews
        reviews = []
        if details.get('reviews'):
            for review in details['reviews'][:3]:  # Get top 3 reviews
                reviews.append({
                    'author_name': review.get('author_name', ''),
                    'rating': review.get('rating', 0),
                    'text': review.get('text', '')[:300],  # Truncate long reviews
                    'time': review.get('relative_time_description', ''),
                    'source': 'google'
                })
        
        # Format opening hours
        opening_hours = []
        open_now = None
        if details.get('opening_hours'):
            opening_hours = details['opening_hours'].get('weekday_text', [])
            open_now = details['opening_hours'].get('open_now')
        
        # Generate booking URLs
        booking_urls = await self._generate_booking_urls(details)
        
        return {
            "id": place_id,
            "name": details.get('name', ''),
            "cuisine": ', '.join(cuisine_types) if cuisine_types else 'Restaurant',
            "address": details.get('formatted_address', ''),
            "phone": details.get('formatted_phone_number', ''),
            "rating": details.get('rating', 0),
            "review_count": details.get('user_ratings_total', 0),
            "price_level": self._format_price_level(details.get('price_level')),
            "price_level_numeric": details.get('price_level'),
            "website": details.get('website', ''),
            "google_maps_url": details.get('url', ''),
            "photos": photos,
            "main_photo": photos[0] if photos else None,
            "reviews": reviews,
            "opening_hours": opening_hours,
            "open_now": open_now,
            "coordinates": {
                "latitude": details.get('geometry', {}).get('location', {}).get('lat'),
                "longitude": details.get('geometry', {}).get('location', {}).get('lng')
            },
            "business_status": details.get('business_status', 'OPERATIONAL'),
            "booking_urls": booking_urls,
            "primary_booking_url": booking_urls.get('opentable') or booking_urls.get('google_maps'),
            "source": "google_places"
        }
    
    def _format_price_level(self, price_level: Optional[int]) -> str:
        """Convert Google price level to $ symbols"""
        if price_level is None:
            return "$$"
        return "$" * (price_level + 1) if price_level >= 0 else "$$"
    
    def _convert_price_range_to_numeric(self, price_range: str) -> Optional[int]:
        """Convert price range string to Google's numeric format"""
        mapping = {"$": 0, "$$": 1, "$$$": 2, "$$$$": 3}
        return mapping.get(price_range)
    
    async def _generate_booking_urls(self, details: Dict[str, Any]) -> Dict[str, str]:
        """Generate booking URLs for the restaurant"""
        name = details.get('name', '')
        website = details.get('website', '')
        google_maps_url = details.get('url', '')
        
        booking_urls = {}
        
        # Google Maps URL (always available)
        if google_maps_url:
            booking_urls['google_maps'] = google_maps_url
        
        # Check if website is a known booking platform
        if website:
            if 'opentable.com' in website:
                booking_urls['opentable'] = website
            elif 'resy.com' in website:
                booking_urls['resy'] = website
            elif 'yelp.com' in website:
                booking_urls['yelp'] = website
            else:
                booking_urls['website'] = website
        
        # Generate OpenTable search URL
        if name:
            clean_name = name.replace(' ', '+').replace('&', 'and')
            booking_urls['opentable_search'] = f"https://www.opentable.com/s/?term={clean_name}"
        
        return booking_urls

    async def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Get detailed information about a Google Places location"""
        if not self.client:
            raise ConfigurationError("Google Places API not configured")

        try:
            details = self.client.place(
                place_id,
                fields=[
                    'name', 'formatted_address', 'formatted_phone_number',
                    'rating', 'user_ratings_total', 'price_level', 'website',
                    'opening_hours', 'photos', 'reviews', 'url', 'geometry',
                    'types', 'business_status'
                ]
            )['result']

            return await self._format_restaurant_data(details, place_id)

        except Exception as e:
            logger.error(f"Google Places details failed: {e}")
            raise ServiceError(f"Place details failed: {e}")

    async def get_nearby_restaurants(
        self,
        lat: float,
        lng: float,
        radius: int = 1000,
        cuisine_type: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get restaurants near coordinates"""
        if not self.client:
            raise ConfigurationError("Google Places API not configured")

        try:
            # Use nearby search
            places_result = self.client.places_nearby(
                location=(lat, lng),
                radius=radius,
                type='restaurant',
                keyword=cuisine_type
            )

            restaurants = []
            for place in places_result.get('results', [])[:limit]:
                try:
                    place_id = place['place_id']
                    details = self.client.place(
                        place_id,
                        fields=[
                            'name', 'formatted_address', 'formatted_phone_number',
                            'rating', 'user_ratings_total', 'price_level', 'website',
                            'opening_hours', 'photos', 'reviews', 'url', 'geometry',
                            'types', 'business_status'
                        ]
                    )['result']

                    restaurant = await self._format_restaurant_data(details, place_id)
                    restaurants.append(restaurant)

                except Exception as e:
                    logger.warning(f"Failed to process nearby restaurant: {e}")
                    continue

            return {
                "results": restaurants,
                "total": len(restaurants),
                "center": {"lat": lat, "lng": lng},
                "radius": radius
            }

        except Exception as e:
            logger.error(f"Google Places nearby search failed: {e}")
            raise ServiceError(f"Nearby search failed: {e}")

    async def get_place_photos(self, place_id: str, max_photos: int = 5) -> List[str]:
        """Get photos for a Google Places location"""
        if not self.client:
            return []

        try:
            details = self.client.place(place_id, fields=['photos'])['result']

            photos = []
            if details.get('photos'):
                for photo in details['photos'][:max_photos]:
                    photo_ref = photo.get('photo_reference')
                    if photo_ref:
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={self.api_key}"
                        photos.append(photo_url)

            return photos

        except Exception as e:
            logger.error(f"Google Places photos fetch failed: {e}")
            return []

    async def get_place_reviews(self, place_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get reviews for a specific place"""
        if not self.client:
            return []

        try:
            details = self.client.place(place_id, fields=['reviews'])['result']

            reviews = []
            if details.get('reviews'):
                for review in details['reviews'][:limit]:
                    formatted_review = {
                        "author_name": review.get('author_name', ''),
                        "rating": review.get('rating', 0),
                        "text": review.get('text', ''),
                        "time": review.get('relative_time_description', ''),
                        "profile_photo_url": review.get('profile_photo_url', ''),
                        "source": "google"
                    }
                    reviews.append(formatted_review)

            return reviews

        except Exception as e:
            logger.error(f"Google Places reviews fetch failed: {e}")
            return []

    async def search_attractions(
        self,
        location: str,
        attraction_types: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search for attractions using Google Places API"""
        if not self.client:
            raise ConfigurationError("Google Places API not configured")

        # Default attraction types
        if not attraction_types:
            attraction_types = [
                'tourist_attraction', 'museum', 'art_gallery', 'park',
                'amusement_park', 'zoo', 'aquarium', 'church', 'monument'
            ]

        try:
            attractions = []

            for attraction_type in attraction_types:
                places_result = self.client.places_nearby(
                    location=location,
                    type=attraction_type,
                    rank_by='prominence'
                )

                for place in places_result.get('results', [])[:5]:  # Top 5 per type
                    try:
                        place_id = place['place_id']
                        details = self.client.place(
                            place_id,
                            fields=[
                                'name', 'formatted_address', 'rating', 'user_ratings_total',
                                'website', 'opening_hours', 'photos', 'url', 'geometry',
                                'types', 'business_status'
                            ]
                        )['result']

                        attraction = await self._format_attraction_data(details, place_id, attraction_type)
                        attractions.append(attraction)

                    except Exception as e:
                        logger.warning(f"Failed to process attraction: {e}")
                        continue

                if len(attractions) >= limit:
                    break

            # Remove duplicates and sort by rating
            seen_names = set()
            unique_attractions = []
            for attraction in attractions:
                name = attraction.get('name', '').lower()
                if name not in seen_names:
                    seen_names.add(name)
                    unique_attractions.append(attraction)

            unique_attractions.sort(key=lambda x: x.get('rating', 0), reverse=True)
            return unique_attractions[:limit]

        except Exception as e:
            logger.error(f"Google Places attraction search failed: {e}")
            raise ServiceError(f"Attraction search failed: {e}")

    async def _format_attraction_data(self, details: Dict[str, Any], place_id: str, attraction_type: str) -> Dict[str, Any]:
        """Format Google Places data into standardized attraction format"""

        # Format photos
        photos = []
        if details.get('photos'):
            for photo in details['photos'][:3]:  # Get up to 3 photos
                photo_ref = photo.get('photo_reference')
                if photo_ref:
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={self.api_key}"
                    photos.append(photo_url)

        # Format opening hours
        opening_hours = []
        open_now = None
        if details.get('opening_hours'):
            opening_hours = details['opening_hours'].get('weekday_text', [])
            open_now = details['opening_hours'].get('open_now')

        return {
            "id": place_id,
            "name": details.get('name', ''),
            "type": attraction_type.replace('_', ' ').title(),
            "address": details.get('formatted_address', ''),
            "rating": details.get('rating', 0),
            "review_count": details.get('user_ratings_total', 0),
            "website": details.get('website', ''),
            "google_maps_url": details.get('url', ''),
            "photos": photos,
            "main_photo": photos[0] if photos else None,
            "opening_hours": opening_hours,
            "open_now": open_now,
            "coordinates": {
                "latitude": details.get('geometry', {}).get('location', {}).get('lat'),
                "longitude": details.get('geometry', {}).get('location', {}).get('lng')
            },
            "business_status": details.get('business_status', 'OPERATIONAL'),
            "estimated_duration": self._estimate_visit_duration(attraction_type),
            "best_time_to_visit": self._suggest_visit_time(attraction_type),
            "source": "google_places"
        }

    def _estimate_visit_duration(self, attraction_type: str) -> str:
        """Estimate typical visit duration for attraction type"""
        duration_map = {
            'museum': '2-3 hours',
            'art_gallery': '1-2 hours',
            'park': '1-4 hours',
            'zoo': '3-5 hours',
            'aquarium': '2-3 hours',
            'amusement_park': '4-8 hours',
            'church': '30-60 minutes',
            'monument': '15-30 minutes',
            'tourist_attraction': '1-2 hours'
        }
        return duration_map.get(attraction_type, '1-2 hours')

    def _suggest_visit_time(self, attraction_type: str) -> str:
        """Suggest best time to visit for attraction type"""
        time_map = {
            'museum': 'Morning (10 AM - 12 PM)',
            'art_gallery': 'Morning or late afternoon',
            'park': 'Early morning or late afternoon',
            'zoo': 'Morning (animals more active)',
            'aquarium': 'Any time (indoor)',
            'amusement_park': 'Early morning (fewer crowds)',
            'church': 'Morning or early afternoon',
            'monument': 'Golden hour for photos',
            'tourist_attraction': 'Morning (fewer crowds)'
        }
        return time_map.get(attraction_type, 'Morning recommended')
