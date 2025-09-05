"""
Optimized Guide Service
High-performance guide generation using concurrent processing and optimized APIs
"""
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable
from pathlib import Path
from dotenv import load_dotenv
import logging

from .optimized_perplexity_service import OptimizedPerplexityService
from .google_weather_service import GoogleWeatherService
from .guide_validator import GuideValidator
from .enhanced_google_places_service import EnhancedGooglePlacesService

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


class OptimizedGuideService:
    """
    High-performance guide service that:
    - Uses concurrent API calls for 3-5x faster generation
    - Integrates weather data automatically
    - Validates guide completeness
    - Provides real-time progress updates
    - Handles errors gracefully with fallbacks
    """
    
    def __init__(self):
        self.perplexity_service = OptimizedPerplexityService()
        self.weather_service = GoogleWeatherService()
        self.google_places_service = EnhancedGooglePlacesService()

        # Performance tracking
        self.generation_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_time": 0.0,
            "cache_hits": 0
        }
    
    async def generate_optimized_guide(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        extracted_data: Dict = None,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None
    ) -> Dict:
        """
        Generate complete travel guide using optimized concurrent processing
        
        Args:
            destination: Travel destination
            start_date: Trip start date (YYYY-MM-DD)
            end_date: Trip end date (YYYY-MM-DD)
            hotel_info: Hotel information dict
            preferences: User preferences dict
            extracted_data: Additional extracted data
            progress_callback: Optional progress callback function
            
        Returns:
            Complete travel guide dict or error response
        """
        start_time = datetime.now()
        self.generation_stats["total_requests"] += 1
        
        try:
            if progress_callback:
                await progress_callback(5, "Initializing optimized guide generation")
            
            # Validate inputs
            if not destination or not start_date or not end_date:
                return self._create_error_response("Missing required parameters")
            
            # Build context for generation
            context = self._build_context(
                destination, start_date, end_date, 
                hotel_info, preferences, extracted_data or {}
            )
            
            if progress_callback:
                await progress_callback(15, "Starting concurrent data fetching")
            
            # Execute concurrent tasks
            guide_data = await self._fetch_all_data_concurrently(
                destination, start_date, end_date, preferences, progress_callback
            )
            
            if guide_data.get("error"):
                return guide_data  # Return error if concurrent fetching failed
            
            if progress_callback:
                await progress_callback(85, "Assembling complete guide")
            
            # Assemble final guide
            complete_guide = await self._assemble_complete_guide(
                guide_data, context, progress_callback
            )
            
            # Validate guide completeness
            is_valid, errors, validation_details = GuideValidator.validate_guide(complete_guide)
            
            if not is_valid:
                logger.warning(f"Guide validation failed: {errors}")
                return {
                    "error": "Guide validation failed",
                    "message": f"Generated guide for {destination} is incomplete: {', '.join(errors)}",
                    "validation_errors": errors,
                    "validation_details": validation_details,
                    "destination": destination,
                    "generated_at": datetime.now().isoformat()
                }
            
            # Add metadata
            generation_time = (datetime.now() - start_time).total_seconds()
            complete_guide.update({
                "validation_passed": True,
                "generation_time_seconds": generation_time,
                "generated_with": "optimized_guide_service",
                "generated_at": datetime.now().isoformat(),
                "performance_stats": {
                    "concurrent_requests": 5,  # Weather + 4 Perplexity tasks
                    "total_time": generation_time,
                    "cache_used": guide_data.get("cache_key") is not None
                }
            })
            
            # Update stats
            self.generation_stats["successful_requests"] += 1
            self.generation_stats["average_time"] = (
                (self.generation_stats["average_time"] * (self.generation_stats["successful_requests"] - 1) + generation_time) 
                / self.generation_stats["successful_requests"]
            )
            
            if progress_callback:
                await progress_callback(100, f"Guide ready! Generated in {generation_time:.1f}s")
            
            logger.info(f"Guide generated successfully for {destination} in {generation_time:.1f}s")
            return complete_guide
            
        except Exception as e:
            logger.error(f"Guide generation failed for {destination}: {e}")
            return self._create_error_response(f"Guide generation failed: {str(e)}")
    
    async def _fetch_all_data_concurrently(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        preferences: Dict,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """Fetch all guide data using concurrent API calls"""
        
        # Create concurrent tasks
        tasks = []
        
        # Task 1: Google Places restaurants (high-quality real data)
        google_places_restaurants_task = self._fetch_google_places_restaurants(destination, preferences)
        tasks.append(google_places_restaurants_task)

        # Task 1b: Google Places attractions (high-quality real data with photos)
        google_places_attractions_task = self._fetch_google_places_attractions(destination, preferences)
        tasks.append(google_places_attractions_task)

        # Task 2: Perplexity guide data (attractions, events, practical info, daily suggestions)
        # Create async callback wrapper if progress_callback exists
        perplexity_callback = None
        if progress_callback:
            async def perplexity_progress(p, m):
                if progress_callback:  # Double check it's still not None
                    try:
                        await progress_callback(15 + p * 0.4, m)
                    except Exception as e:
                        logger.error(f"Error in perplexity_progress callback: {e}")
                        raise
            perplexity_callback = perplexity_progress

        logger.debug(f"Created perplexity_callback: {perplexity_callback}")

        perplexity_task = self.perplexity_service.generate_complete_guide_data(
            destination, start_date, end_date, preferences,
            progress_callback=perplexity_callback
        )
        tasks.append(perplexity_task)

        # Task 3: Weather data
        weather_task = self.weather_service.get_weather_forecast(
            destination, start_date, end_date
        )
        tasks.append(weather_task)
        
        try:
            # Execute all tasks concurrently with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=45  # 45 second total timeout
            )

            google_places_restaurants, google_places_attractions, perplexity_data, weather_data = results

            # Handle Google Places restaurants data
            if isinstance(google_places_restaurants, Exception):
                logger.warning(f"Google Places restaurants fetch failed: {google_places_restaurants}")
                google_places_restaurants = []  # Fallback to empty list

            # Handle Google Places attractions data
            if isinstance(google_places_attractions, Exception):
                logger.warning(f"Google Places attractions fetch failed: {google_places_attractions}")
                google_places_attractions = []  # Fallback to empty list

            # Handle Perplexity data
            if isinstance(perplexity_data, Exception):
                logger.error(f"Perplexity data fetch failed: {perplexity_data}")
                return self._create_error_response(f"Failed to fetch guide data: {str(perplexity_data)}")

            if perplexity_data.get("error"):
                return perplexity_data  # Return Perplexity error

            # Handle weather data (non-critical)
            if isinstance(weather_data, Exception):
                logger.warning(f"Weather data fetch failed: {weather_data}")
                weather_data = {"error": str(weather_data)}

            # Combine data - Replace Perplexity restaurants with Google Places restaurants
            combined_data = perplexity_data.copy()
            combined_data["restaurants"] = google_places_restaurants  # Use Google Places restaurants

            # Combine Google Places attractions with Perplexity attractions
            perplexity_attractions = perplexity_data.get('attractions', [])
            all_attractions = google_places_attractions + perplexity_attractions

            # Remove duplicates by name and limit to top attractions
            seen_names = set()
            unique_attractions = []
            for attraction in all_attractions:
                name = attraction.get('name', '')
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_attractions.append(attraction)

            combined_data["attractions"] = unique_attractions[:8]  # Top 8 attractions
            combined_data["weather_data"] = weather_data

            logger.info(f"Combined data: {len(google_places_restaurants)} Google Places restaurants, "
                       f"{len(google_places_attractions)} Google Places attractions, "
                       f"{len(perplexity_attractions)} Perplexity attractions, "
                       f"{len(unique_attractions)} total unique attractions")

            return combined_data
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching data for {destination}")
            return self._create_error_response(f"Timeout fetching data for {destination}")
        except Exception as e:
            logger.error(f"Error in concurrent data fetching: {e}")
            return self._create_error_response(f"Error fetching data: {str(e)}")

    async def _fetch_google_places_restaurants(self, destination: str, preferences: Dict) -> List[Dict]:
        """Fetch restaurants using Google Places API"""
        try:
            # Initialize Google Places service if not already done
            await self.google_places_service.initialize()

            # Get cuisine preferences
            cuisine_preferences = preferences.get("dining", {}).get("cuisineTypes", [])

            # Search for restaurants
            restaurants = []

            # If specific cuisines requested, search for each
            if cuisine_preferences:
                for cuisine in cuisine_preferences[:3]:  # Limit to top 3 cuisines
                    try:
                        cuisine_restaurants = await self.google_places_service.search_restaurants(
                            location=destination,
                            cuisine_type=cuisine,
                            limit=5
                        )
                        restaurants.extend(cuisine_restaurants)
                    except Exception as e:
                        logger.warning(f"Failed to fetch {cuisine} restaurants: {e}")

            # Always do a general search for top restaurants
            try:
                general_restaurants = await self.google_places_service.search_restaurants(
                    location=destination,
                    limit=10
                )
                restaurants.extend(general_restaurants)
            except Exception as e:
                logger.warning(f"Failed to fetch general restaurants: {e}")

            # Remove duplicates based on place ID
            seen_ids = set()
            unique_restaurants = []
            for restaurant in restaurants:
                place_id = restaurant.get("id")
                if place_id and place_id not in seen_ids:
                    seen_ids.add(place_id)
                    unique_restaurants.append(restaurant)

            logger.info(f"Fetched {len(unique_restaurants)} unique restaurants from Google Places")
            return unique_restaurants[:15]  # Return top 15

        except Exception as e:
            logger.error(f"Google Places restaurant fetch failed: {e}")
            return []  # Return empty list on error

    async def _fetch_google_places_attractions(self, destination: str, preferences: Dict) -> List[Dict]:
        """Fetch attractions using Google Places API"""
        try:
            # Initialize Google Places service if not already done
            await self.google_places_service.initialize()

            # Search for attractions
            attractions = await self.google_places_service.search_attractions(
                location=destination,
                limit=8  # Get top 8 attractions with photos
            )

            logger.info(f"Fetched {len(attractions)} unique attractions from Google Places")
            return attractions

        except Exception as e:
            logger.error(f"Error fetching Google Places attractions: {e}")
            return []  # Return empty list on error

    def _format_restaurants_for_frontend(self, restaurants: List[Dict]) -> List[Dict]:
        """Format restaurant data for frontend display"""
        formatted_restaurants = []

        for restaurant in restaurants:
            # Create generalized description from restaurant data and reviews
            description = self._generate_restaurant_description(restaurant)

            # Format for frontend
            formatted_restaurant = {
                "name": restaurant.get("name", ""),
                "cuisine": restaurant.get("cuisine", ""),
                "description": description,
                "address": restaurant.get("address", ""),
                "rating": restaurant.get("rating"),
                "review_count": restaurant.get("review_count"),
                "price_range": restaurant.get("price_level", ""),
                "price_level_numeric": restaurant.get("price_level_numeric"),
                "phone": restaurant.get("phone", ""),
                "website": restaurant.get("website", ""),
                "map_url": restaurant.get("google_maps_url", ""),
                "photos": restaurant.get("photos", []),
                "main_photo": restaurant.get("main_photo", ""),
                "booking_urls": {
                    "google_maps": restaurant.get("google_maps_url", ""),
                    "opentable": restaurant.get("booking_urls", {}).get("opentable", ""),
                    "website": restaurant.get("website", "")
                },
                "primary_booking_url": restaurant.get("google_maps_url", ""),
                "reviews": restaurant.get("reviews", []),
                "source": restaurant.get("source", "google_places"),
                # Additional fields for enhanced display
                "why_recommended": self._generate_recommendation_reason(restaurant),
                "best_dishes": self._extract_best_dishes(restaurant),
                "visit_tips": self._generate_visit_tips(restaurant)
            }

            formatted_restaurants.append(formatted_restaurant)

        return formatted_restaurants

    def _format_attractions_for_frontend(self, attractions: List[Dict]) -> List[Dict]:
        """Format attraction data for frontend display with all required details"""
        formatted_attractions = []

        for attraction in attractions:
            # Ensure all required fields are present
            formatted_attraction = {
                "name": attraction.get("name", ""),
                "description": attraction.get("description", ""),
                "address": attraction.get("address", ""),
                "rating": attraction.get("rating"),
                "review_count": attraction.get("review_count"),
                "phone": attraction.get("phone", ""),
                "website": attraction.get("website", ""),
                "google_maps_url": attraction.get("google_maps_url", ""),
                "photos": attraction.get("photos", []),
                "main_photo": attraction.get("main_photo", ""),
                "hours": attraction.get("hours", []),
                "open_now": attraction.get("open_now"),
                "price_level": attraction.get("price_level", ""),
                "types": attraction.get("types", []),
                "source": attraction.get("source", "google_places"),

                # Enhanced fields
                "category": self._determine_attraction_category(attraction),
                "visit_duration": self._suggest_visit_duration(attraction),
                "best_time_to_visit": self._suggest_best_time(attraction),
                "ticket_info": self._get_ticket_info(attraction),
                "accessibility": attraction.get("accessibility", ""),

                # Booking and info URLs
                "booking_urls": {
                    "google_maps": attraction.get("google_maps_url", ""),
                    "website": attraction.get("website", ""),
                    "tripadvisor": self._generate_tripadvisor_url(attraction),
                    "viator": self._generate_viator_url(attraction)
                },
                "primary_booking_url": attraction.get("website", "") or attraction.get("google_maps_url", "")
            }

            formatted_attractions.append(formatted_attraction)

        return formatted_attractions

    def _determine_attraction_category(self, attraction: Dict) -> str:
        """Determine the category of an attraction"""
        types = attraction.get("types", [])
        name = attraction.get("name", "").lower()

        if any(t in types for t in ["museum", "art_gallery"]):
            return "Museum & Culture"
        elif any(t in types for t in ["park", "natural_feature"]):
            return "Parks & Nature"
        elif any(t in types for t in ["church", "place_of_worship"]):
            return "Religious Sites"
        elif any(t in types for t in ["tourist_attraction", "point_of_interest"]):
            return "Tourist Attraction"
        elif "market" in name or "shopping" in name:
            return "Shopping & Markets"
        else:
            return "Attraction"

    def _suggest_visit_duration(self, attraction: Dict) -> str:
        """Suggest how long to spend at an attraction"""
        types = attraction.get("types", [])
        name = attraction.get("name", "").lower()

        if any(t in types for t in ["museum", "art_gallery"]):
            return "2-3 hours"
        elif any(t in types for t in ["park", "natural_feature"]):
            return "1-2 hours"
        elif any(t in types for t in ["church", "place_of_worship"]):
            return "30-60 minutes"
        elif "market" in name:
            return "1-2 hours"
        else:
            return "1-2 hours"

    def _suggest_best_time(self, attraction: Dict) -> str:
        """Suggest the best time to visit"""
        types = attraction.get("types", [])
        name = attraction.get("name", "").lower()

        if any(t in types for t in ["museum", "art_gallery"]):
            return "Morning (less crowded)"
        elif any(t in types for t in ["park", "natural_feature"]):
            return "Early morning or late afternoon"
        elif any(t in types for t in ["church", "place_of_worship"]):
            return "Morning or early afternoon"
        elif "market" in name:
            return "Morning (best selection)"
        else:
            return "Morning or afternoon"

    def _get_ticket_info(self, attraction: Dict) -> str:
        """Get ticket information for attraction"""
        types = attraction.get("types", [])

        if any(t in types for t in ["museum", "art_gallery"]):
            return "Tickets usually required - check website for prices"
        elif any(t in types for t in ["park", "natural_feature"]):
            return "Usually free entry"
        elif any(t in types for t in ["church", "place_of_worship"]):
            return "Usually free entry, donations welcome"
        else:
            return "Check website for entry requirements"

    def _generate_tripadvisor_url(self, attraction: Dict) -> str:
        """Generate TripAdvisor search URL"""
        name = attraction.get("name", "")
        if name:
            # Simple search URL - in production you'd want proper URL encoding
            search_name = name.replace(" ", "%20")
            return f"https://www.tripadvisor.com/Search?q={search_name}"
        return ""

    def _generate_viator_url(self, attraction: Dict) -> str:
        """Generate Viator booking URL"""
        name = attraction.get("name", "")
        if name:
            # Simple search URL - in production you'd want proper URL encoding
            search_name = name.replace(" ", "%20")
            return f"https://www.viator.com/searchResults/all?text={search_name}"
        return ""

    def _generate_restaurant_description(self, restaurant: Dict) -> str:
        """Generate a generalized restaurant description from data and reviews"""
        name = restaurant.get("name", "")
        cuisine = restaurant.get("cuisine", "")
        rating = restaurant.get("rating")
        review_count = restaurant.get("review_count")
        price_level = restaurant.get("price_level_numeric")
        reviews = restaurant.get("reviews", [])

        # Start with basic info
        description_parts = []

        # Cuisine and style description
        if cuisine and cuisine.lower() != "restaurant":
            if price_level and price_level >= 4:
                description_parts.append(f"An upscale {cuisine.lower()} restaurant")
            elif price_level and price_level >= 3:
                description_parts.append(f"A refined {cuisine.lower()} establishment")
            else:
                description_parts.append(f"A popular {cuisine.lower()} restaurant")
        else:
            if price_level and price_level >= 4:
                description_parts.append("An upscale dining establishment")
            elif price_level and price_level >= 3:
                description_parts.append("A refined restaurant")
            else:
                description_parts.append("A popular local restaurant")

        # Add location context based on actual destination - NO HARDCODED LOCATIONS
        address = restaurant.get("address", "")
        if address:
            # Extract the city/area from the address
            address_parts = address.split(',')
            if len(address_parts) >= 2:
                area = address_parts[-2].strip()  # Usually the city/area before country
                description_parts.append(f"located in {area}")
            else:
                # Just use the destination city name
                destination_city = destination.split(',')[0].strip() if destination else ""
                if destination_city:
                    description_parts.append(f"in {destination_city}")

        # Add reputation and quality indicators
        if rating and review_count and rating >= 4.7 and review_count >= 1000:
            description_parts.append(f"Known for exceptional quality with an outstanding {rating}/5 rating from over {review_count:,} diners")
        elif rating and review_count and rating >= 4.5 and review_count >= 500:
            description_parts.append(f"Highly acclaimed with a {rating}/5 rating from {review_count:,} satisfied customers")
        elif rating and review_count and rating >= 4.0 and review_count >= 100:
            description_parts.append(f"Well-regarded with a solid {rating}/5 rating")
        elif review_count and review_count >= 500:
            description_parts.append(f"A popular choice among locals and visitors with {review_count:,} reviews")

        # Extract common themes from reviews for specialties
        specialties = self._extract_restaurant_specialties(reviews, cuisine)
        if specialties:
            description_parts.append(f"Particularly noted for {', '.join(specialties)}")

        # Add atmosphere description based on price level and reviews
        atmosphere = self._determine_restaurant_atmosphere(restaurant, reviews)
        if atmosphere:
            description_parts.append(atmosphere)

        # Join all parts into a coherent description
        description = ". ".join(description_parts) + "."

        # Clean up any double periods or awkward phrasing
        description = description.replace("..", ".").replace(". .", ".")

        return description

    def _extract_restaurant_specialties(self, reviews: List[Dict], cuisine: str) -> List[str]:
        """Extract what the restaurant is known for from reviews"""
        specialties = []

        # Common food keywords to look for in reviews
        food_keywords = {
            "pasta": "pasta dishes",
            "pizza": "pizza",
            "steak": "steaks",
            "seafood": "seafood",
            "fish": "fresh fish",
            "wine": "wine selection",
            "dessert": "desserts",
            "cheese": "cheese selection",
            "bread": "fresh bread",
            "soup": "soups",
            "salad": "salads",
            "truffle": "truffle dishes",
            "foie gras": "foie gras",
            "oyster": "oysters",
            "chocolate": "chocolate desserts",
            "tasting menu": "tasting menus",
            "seasonal": "seasonal ingredients"
        }

        # Count mentions in reviews
        keyword_counts = {}
        for review in reviews[:5]:  # Check first 5 reviews
            text = review.get("text", "").lower()
            for keyword, description in food_keywords.items():
                if keyword in text:
                    keyword_counts[description] = keyword_counts.get(description, 0) + 1

        # Get top 2-3 most mentioned specialties
        sorted_specialties = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        specialties = [specialty for specialty, count in sorted_specialties[:3] if count >= 2]

        # No fallback specialties - only use what's found in reviews

        return specialties[:2]  # Limit to 2 specialties

    def _determine_restaurant_atmosphere(self, restaurant: Dict, reviews: List[Dict]) -> str:
        """Determine restaurant atmosphere from data and reviews"""
        price_level = restaurant.get("price_level_numeric")
        rating = restaurant.get("rating")

        # Analyze review text for atmosphere keywords
        atmosphere_keywords = {
            "romantic": ["romantic", "intimate", "cozy", "candlelit"],
            "casual": ["casual", "relaxed", "friendly", "laid-back"],
            "elegant": ["elegant", "sophisticated", "upscale", "refined"],
            "lively": ["lively", "bustling", "energetic", "vibrant"],
            "quiet": ["quiet", "peaceful", "calm", "serene"]
        }

        atmosphere_scores = {}
        for review in reviews[:3]:  # Check first 3 reviews
            text = review.get("text", "").lower()
            for atmosphere, keywords in atmosphere_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                atmosphere_scores[atmosphere] = atmosphere_scores.get(atmosphere, 0) + score

        # Determine atmosphere based on price level and review analysis
        if price_level and price_level >= 4:
            if atmosphere_scores.get("elegant", 0) > 0 or atmosphere_scores.get("romantic", 0) > 0:
                return "The atmosphere is elegant and sophisticated, perfect for special occasions"
            else:
                return "Offers an upscale dining experience with refined service"
        elif price_level and price_level >= 3:
            if atmosphere_scores.get("romantic", 0) > 0:
                return "Features a romantic and intimate setting"
            elif atmosphere_scores.get("lively", 0) > 0:
                return "Boasts a lively and welcoming atmosphere"
            else:
                return "Provides a comfortable and refined dining environment"
        else:
            if atmosphere_scores.get("casual", 0) > 0:
                return "Offers a casual and friendly atmosphere"
            elif atmosphere_scores.get("lively", 0) > 0:
                return "Known for its vibrant and energetic ambiance"
            else:
                return "Provides a welcoming local dining experience"

    def _generate_recommendation_reason(self, restaurant: Dict) -> str:
        """Generate why this restaurant is recommended"""
        rating = restaurant.get("rating")
        review_count = restaurant.get("review_count")
        cuisine = restaurant.get("cuisine", "restaurant")

        if rating and review_count and rating >= 4.7 and review_count >= 1000:
            return f"Exceptional {cuisine.lower()} with outstanding {rating}/5 rating from {review_count:,} diners"
        elif rating and rating >= 4.5:
            return f"Highly rated {cuisine.lower()} with {rating}/5 stars"
        elif review_count and review_count >= 500:
            return f"Popular local {cuisine.lower()} with {review_count:,} reviews"
        else:
            return f"Quality {cuisine.lower()} worth visiting"

    def _extract_best_dishes(self, restaurant: Dict) -> List[str]:
        """Extract best dishes from reviews"""
        dishes = []
        reviews = restaurant.get("reviews", [])

        # Simple keyword extraction from reviews
        dish_keywords = ["pasta", "pizza", "steak", "fish", "chicken", "dessert", "wine", "salad", "soup"]

        for review in reviews[:3]:  # Check first 3 reviews
            text = review.get("text", "").lower()
            for keyword in dish_keywords:
                if keyword in text and keyword not in dishes:
                    dishes.append(keyword.title())
                    if len(dishes) >= 3:
                        break
            if len(dishes) >= 3:
                break

        return dishes

    def _generate_visit_tips(self, restaurant: Dict) -> str:
        """Generate visit tips for the restaurant"""
        rating = restaurant.get("rating")
        price_level = restaurant.get("price_level_numeric")

        tips = []

        if price_level and price_level >= 4:
            tips.append("Reservations highly recommended")
        elif rating and rating >= 4.5:
            tips.append("Popular spot - consider booking ahead")

        if "lunch" in restaurant.get("name", "").lower():
            tips.append("Great for lunch")

        return "; ".join(tips) if tips else ""

    async def _assemble_complete_guide(
        self,
        guide_data: Dict,
        context: Dict,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """Assemble complete guide from fetched data"""
        
        if progress_callback:
            await progress_callback(90, "Assembling final guide")
        
        # Extract data
        restaurants = guide_data.get("restaurants", [])
        attractions = guide_data.get("attractions", [])
        events = guide_data.get("events", [])
        practical_info = guide_data.get("practical_info", {})
        daily_suggestions = guide_data.get("daily_suggestions", [])
        weather_data = guide_data.get("weather_data", {})
        
        # Create comprehensive guide structure
        complete_guide = {
            # Required fields for validation
            "summary": self._generate_summary(context, restaurants, attractions),
            "destination_insights": self._generate_destination_insights(context, practical_info),
            "daily_itinerary": self._format_daily_itinerary(daily_suggestions, context),
            "restaurants": self._format_restaurants_for_frontend(restaurants[:8]),  # Top 8 restaurants
            "attractions": self._format_attractions_for_frontend(attractions[:8]),  # Top 8 attractions
            "practical_info": practical_info,
            
            # Additional content
            "events": events,
            "weather": self._format_weather_data(weather_data),
            "weather_summary": weather_data.get("summary", {}),
            "hidden_gems": self._extract_hidden_gems(attractions, restaurants),
            "neighborhoods": self._extract_neighborhoods(attractions, restaurants),
            
            # Metadata
            "destination": context["destination"],
            "start_date": context["start_date"],
            "end_date": context["end_date"],
            "trip_duration_days": context["trip_duration_days"],
            "hotel_info": context.get("hotel_info", {}),
            "preferences": context.get("preferences", {}),
        }
        
        return complete_guide
    
    def _build_context(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        extracted_data: Dict
    ) -> Dict:
        """Build context for guide generation"""
        from datetime import datetime
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days + 1
        
        return {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "trip_duration_days": duration,
            "hotel_info": hotel_info,
            "preferences": preferences,
            "extracted_data": extracted_data,
            "generation_timestamp": datetime.now().isoformat()
        }
    
    def _generate_summary(self, context: Dict, restaurants: List, attractions: List) -> str:
        """Generate guide summary"""
        destination = context["destination"]
        duration = context["trip_duration_days"]
        
        summary = f"Your {duration}-day guide to {destination} features "
        
        if restaurants:
            summary += f"{len(restaurants)} carefully selected restaurants, "
        if attractions:
            summary += f"{len(attractions)} must-visit attractions, "
        
        summary += f"and personalized recommendations based on your interests. "
        summary += f"This guide covers everything from local favorites to hidden gems, "
        summary += f"ensuring you experience the best of {destination} during your visit."
        
        return summary
    
    def _generate_destination_insights(self, context: Dict, practical_info: Dict) -> str:
        """Generate destination insights"""
        destination = context["destination"]
        
        insights = f"{destination} offers a unique blend of experiences for travelers. "
        
        if isinstance(practical_info, dict):
            transportation = practical_info.get("transportation", "")
            if transportation and isinstance(transportation, str):
                insights += f"Getting around is convenient with {transportation[:100]}... "
            
            currency = practical_info.get("currency", "")
            if currency and isinstance(currency, str):
                insights += f"The local currency and payment methods include {currency[:100]}... "
        
        insights += f"This destination is perfect for travelers seeking authentic experiences and memorable moments."
        
        return insights

    def _format_daily_itinerary(self, daily_suggestions: List, context: Dict) -> List[Dict]:
        """Format daily itinerary from suggestions"""
        if not daily_suggestions:
            # Create basic itinerary structure if no suggestions
            duration = context["trip_duration_days"]
            itinerary = []
            for day in range(1, duration + 1):
                from datetime import datetime, timedelta
                start_date = datetime.strptime(context["start_date"], "%Y-%m-%d")
                current_date = start_date + timedelta(days=day-1)

                itinerary.append({
                    "day": day,
                    "date": current_date.strftime("%Y-%m-%d"),
                    "activities": [
                        f"Morning: Explore {context['destination']}",
                        f"Afternoon: Visit local attractions",
                        f"Evening: Enjoy local cuisine"
                    ]
                })
            return itinerary

        # Format existing suggestions
        formatted_itinerary = []
        for suggestion in daily_suggestions:
            activities = []
            if suggestion.get("morning"):
                activities.append(f"Morning: {suggestion['morning']}")
            if suggestion.get("afternoon"):
                activities.append(f"Afternoon: {suggestion['afternoon']}")
            if suggestion.get("evening"):
                activities.append(f"Evening: {suggestion['evening']}")

            formatted_itinerary.append({
                "day": suggestion.get("day", len(formatted_itinerary) + 1),
                "date": suggestion.get("date", ""),
                "activities": activities,
                "transport_notes": suggestion.get("transport_notes", ""),
                "estimated_cost": suggestion.get("estimated_cost", "")
            })

        return formatted_itinerary

    def _format_weather_data(self, weather_data: Dict) -> List[Dict]:
        """Format weather data for guide"""
        if weather_data.get("error") or not weather_data.get("daily_forecasts"):
            return []

        return weather_data.get("daily_forecasts", [])

    def _extract_hidden_gems(self, attractions: List, restaurants: List) -> List[Dict]:
        """Extract hidden gems from attractions and restaurants"""
        hidden_gems = []

        # Look for less touristy attractions
        for attraction in attractions:
            if any(keyword in attraction.get("description", "").lower()
                   for keyword in ["hidden", "local", "secret", "off the beaten", "gem"]):
                hidden_gems.append({
                    "name": attraction.get("name", ""),
                    "type": "attraction",
                    "description": attraction.get("description", ""),
                    "address": attraction.get("address", "")
                })

        # Look for local favorite restaurants
        for restaurant in restaurants:
            if any(keyword in restaurant.get("recommendation", "").lower()
                   for keyword in ["local", "hidden", "authentic", "family-owned"]):
                hidden_gems.append({
                    "name": restaurant.get("name", ""),
                    "type": "restaurant",
                    "description": restaurant.get("recommendation", ""),
                    "address": restaurant.get("address", "")
                })

        return hidden_gems[:5]  # Top 5 hidden gems

    def _extract_neighborhoods(self, attractions: List, restaurants: List) -> List[str]:
        """Extract neighborhood names from attractions and restaurants"""
        neighborhoods = set()

        # Extract from addresses
        for item in attractions + restaurants:
            address = item.get("address", "")
            if address:
                # Simple neighborhood extraction (this could be improved with geocoding)
                parts = address.split(",")
                if len(parts) >= 2:
                    potential_neighborhood = parts[-2].strip()
                    if len(potential_neighborhood) < 50:  # Reasonable neighborhood name length
                        neighborhoods.add(potential_neighborhood)

        return list(neighborhoods)[:8]  # Top 8 neighborhoods

    def _create_error_response(self, error_message: str) -> Dict:
        """Create standardized error response"""
        return {
            "error": error_message,
            "summary": "",
            "destination_insights": "",
            "daily_itinerary": [],
            "restaurants": [],
            "attractions": [],
            "events": [],
            "practical_info": {},
            "weather": [],
            "hidden_gems": [],
            "neighborhoods": [],
            "generated_at": datetime.now().isoformat(),
            "generated_with": "optimized_guide_service"
        }
    

    def get_performance_stats(self) -> Dict:
        """Get service performance statistics"""
        return self.generation_stats.copy()
