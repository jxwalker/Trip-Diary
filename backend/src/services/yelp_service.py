"""
Yelp API Service Implementation
Real restaurant data integration using Yelp Fusion API
"""
import asyncio
import aiohttp
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import os
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


class YelpService:
    """Yelp Fusion API service for restaurant data"""

    def __init__(self):
        """Initialize Yelp service"""
        self.logger = logger

        # API configuration
        self.api_key = os.getenv("YELP_API_KEY")
        self.base_url = "https://api.yelp.com/v3"

        # Cache configuration
        self.cache_ttl = 3600  # 1 hour cache
        self._initialized = False

        # Simple in-memory cache for testing
        self._cache = {}

    @property
    def service_name(self) -> str:
        return "yelp"

    @property
    def api_key_required(self) -> bool:
        return True
    
    async def initialize(self) -> None:
        """Initialize the service"""
        if not self.api_key:
            raise ConfigurationError("YELP_API_KEY not configured")

        # Test API connectivity
        await self.validate_api_key()
        self._initialized = True
        logger.info("Yelp service initialized successfully")

    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            # Simple API test
            await self.validate_api_key()
            return {
                "status": "healthy",
                "service": "yelp",
                "timestamp": datetime.now().isoformat(),
                "api_key_configured": bool(self.api_key)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "yelp",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "api_key_configured": bool(self.api_key)
            }

    async def cleanup(self) -> None:
        """Cleanup service resources"""
        # No persistent connections to clean up
        pass
    
    async def validate_api_key(self) -> bool:
        """Validate the Yelp API key"""
        if not self.api_key:
            raise ConfigurationError("YELP_API_KEY not configured")

        try:
            # Test with a simple business search
            url = f"{self.base_url}/businesses/search"
            params = {
                "location": "New York, NY",
                "limit": 1
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, params=params, headers=headers, timeout=30
                ) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        raise ConfigurationError(
                            "Invalid Yelp API key: Unauthorized"
                        )
                    elif response.status == 403:
                        raise ConfigurationError(
                            "Invalid Yelp API key: Forbidden"
                        )
                    else:
                        error_text = await response.text()
                        raise ConfigurationError(
                            f"Yelp API validation failed: {response.status} - "
                            f"{error_text}"
                        )

        except ConfigurationError:
            # Re-raise configuration errors
            raise
        except Exception as e:
            logger.error(f"Yelp API key validation failed: {e}")
            raise ConfigurationError(f"Yelp API key validation error: {e}")

    async def _make_request(
        self, endpoint: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make a request to the Yelp API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=url,
                    params=params or {},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:

                    if response.status == 200:
                        return await response.json()
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("error", {}).get(
                            "description", "Unknown error"
                        )
                        raise ServiceError(f"Yelp API error: {error_msg}")

        except asyncio.TimeoutError:
            raise ServiceError("Yelp API request timeout")
        except Exception as e:
            logger.error(f"Yelp API request failed: {e}")
            raise ServiceError(f"Yelp API request failed: {e}")
    
    async def search_restaurants(
        self,
        location: str,
        cuisine_type: Optional[str] = None,
        price_range: Optional[str] = None,
        limit: int = 20,
        radius: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for restaurants using Yelp API
        
        Args:
            location: Location to search (e.g., "New York, NY")
            cuisine_type: Type of cuisine (e.g., "italian", "mexican")
            price_range: Price range (1-4, where 1 = $, 4 = $$$$)
            limit: Number of results to return (max 50)
            radius: Search radius in meters (max 40000)
            
        Returns:
            List of restaurant data dictionaries
        """
        # Build search parameters
        params = {
            "location": location,
            "categories": "restaurants",
            "limit": min(limit, 50),  # Yelp API limit
            "sort_by": "rating"
        }
        
        if cuisine_type:
            params["categories"] = f"restaurants,{cuisine_type.lower()}"
        
        if price_range:
            # Convert price range to Yelp format
            if isinstance(price_range, str):
                price_map = {"$": "1", "$$": "2", "$$$": "3", "$$$$": "4"}
                params["price"] = price_map.get(price_range, "2")
            else:
                params["price"] = str(price_range)
        
        if radius:
            params["radius"] = min(radius, 40000)  # Yelp API limit
        
        # Check cache first
        cache_key = (
            f"yelp_restaurants_"
            f"{hashlib.md5(str(params).encode()).hexdigest()}"
        )
        if cache_key in self._cache:
            logger.info(
                f"Returning cached Yelp restaurant search for {location}"
            )
            return self._cache[cache_key]

        try:
            response_data = await self._make_request(
                "businesses/search", params
            )

            # Parse and format restaurant data
            restaurants = []
            for business in response_data.get("businesses", []):
                restaurant = self._format_restaurant_data(business)
                restaurants.append(restaurant)

            # Cache the results
            self._cache[cache_key] = restaurants

            logger.info(f"Found {len(restaurants)} restaurants in {location}")
            return restaurants

        except Exception as e:
            logger.error(f"Yelp restaurant search failed: {e}")
            raise ServiceError(f"Restaurant search failed: {e}")
    
    def _format_restaurant_data(
        self, business: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format Yelp business data into standardized restaurant format"""
        return {
            "id": business.get("id"),
            "name": business.get("name"),
            "cuisine": ", ".join([
                cat.get("title", "") for cat in business.get("categories", [])
            ]),
            "address": business.get("location", {}).get("display_address", []),
            "formatted_address": ", ".join(
                business.get("location", {}).get("display_address", [])
            ),
            "phone": business.get("phone", ""),
            "rating": business.get("rating", 0),
            "review_count": business.get("review_count", 0),
            "price_level": business.get("price", "$$"),
            "price_range": business.get("price", "$$"),
            "website": business.get("url", ""),
            "yelp_url": business.get("url", ""),
            "image_url": business.get("image_url", ""),
            "photos": (
                [business.get("image_url")] if business.get("image_url") else []
            ),
            "coordinates": {
                "latitude": business.get("coordinates", {}).get("latitude"),
                "longitude": business.get("coordinates", {}).get("longitude")
            },
            "is_closed": business.get("is_closed", False),
            "transactions": business.get("transactions", []),
            "source": "yelp"
        }

    async def search_places(
        self,
        query: str,
        location: Optional[str] = None,
        radius: Optional[int] = None,
        place_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for places (restaurants) using Yelp API"""
        restaurants = await self.search_restaurants(
            location=location or query,
            cuisine_type=place_type,
            radius=radius
        )

        return {
            "results": restaurants,
            "total": len(restaurants),
            "query": query,
            "location": location
        }

    async def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """Get detailed information about a Yelp business"""
        try:
            response_data = await self._make_request(f"businesses/{place_id}")
            return self._format_restaurant_data(response_data)

        except Exception as e:
            logger.error(f"Yelp business details failed: {e}")
            raise ServiceError(f"Business details failed: {e}")

    async def get_nearby_places(
        self,
        lat: float,
        lng: float,
        radius: int = 1000,
        place_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get places near coordinates"""
        params = {
            "latitude": lat,
            "longitude": lng,
            "radius": min(radius, 40000),
            "categories": "restaurants",
            "limit": 20,
            "sort_by": "distance"
        }

        if place_type:
            params["categories"] = f"restaurants,{place_type.lower()}"

        try:
            response_data = await self._make_request(
                "businesses/search", params
            )

            restaurants = []
            for business in response_data.get("businesses", []):
                restaurant = self._format_restaurant_data(business)
                restaurants.append(restaurant)

            return {
                "results": restaurants,
                "total": len(restaurants),
                "center": {"lat": lat, "lng": lng},
                "radius": radius
            }

        except Exception as e:
            logger.error(f"Yelp nearby search failed: {e}")
            raise ServiceError(f"Nearby search failed: {e}")

    async def get_place_photos(self, place_id: str) -> List[str]:
        """Get photos for a Yelp business"""
        try:
            business_details = await self.get_place_details(place_id)
            photos = business_details.get("photos", [])

            # Yelp API doesn't provide multiple photos in basic search
            # We only get the main image_url
            return photos

        except Exception as e:
            logger.error(f"Yelp photos fetch failed: {e}")
            return []

    async def get_restaurant_reviews(
        self,
        business_id: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get reviews for a specific restaurant"""
        try:
            params = {"limit": min(limit, 3)}  # Yelp API limit is 3
            response_data = await self._make_request(
                f"businesses/{business_id}/reviews", params
            )

            reviews = []
            for review in response_data.get("reviews", []):
                formatted_review = {
                    "id": review.get("id"),
                    "rating": review.get("rating"),
                    "text": review.get("text", ""),
                    "time_created": review.get("time_created"),
                    "user": {
                        "name": review.get("user", {}).get("name", ""),
                        "image_url": review.get("user", {}).get(
                            "image_url", ""
                        )
                    },
                    "source": "yelp"
                }
                reviews.append(formatted_review)

            return reviews

        except Exception as e:
            logger.error(f"Yelp reviews fetch failed: {e}")
            return []
