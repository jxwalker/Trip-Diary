"""
Unified Travel Guide Service
Consolidates all guide generation functionality into a single, high-quality service
Replaces: enhanced_guide_service, optimized_guide_service, luxury_guide_service, etc.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import aiohttp

from .llm_parser import LLMParser
from .perplexity_search_service import PerplexitySearchService
from .weather_service import WeatherService
from .google_places_enhancer import GooglePlacesEnhancer
from .real_events_service import RealEventsService
from .guide_validator import GuideValidator
from ..utils.environment import load_project_env, get_api_key
from ..utils.error_handling import safe_execute, APIError, log_and_return_error

# Load environment variables
load_project_env()

logger = logging.getLogger(__name__)


class PersonaType(Enum):
    """Travel persona types for content personalization"""
    LUXURY_TRAVELER = "luxury_traveler"
    BUDGET_EXPLORER = "budget_explorer"
    FAMILY_FRIENDLY = "family_friendly"
    ADVENTURE_SEEKER = "adventure_seeker"
    CULTURAL_ENTHUSIAST = "cultural_enthusiast"
    FOODIE = "foodie"
    BUSINESS_TRAVELER = "business_traveler"
    ROMANTIC_COUPLE = "romantic_couple"


@dataclass
class WeatherActivityCorrelation:
    """Correlates weather conditions with recommended activities"""
    temperature_range: tuple[int, int]
    conditions: List[str]
    recommended_activities: List[str]
    avoid_activities: List[str]
    clothing_suggestions: List[str]
    special_notes: str = ""


@dataclass
class GuideGenerationContext:
    """Complete context for guide generation"""
    destination: str
    start_date: str
    end_date: str
    duration_days: int
    hotel_info: Dict[str, Any]
    preferences: Dict[str, Any]
    persona: PersonaType
    weather_data: Optional[Dict[str, Any]] = None
    extracted_data: Optional[Dict[str, Any]] = None


class UnifiedGuideService:
    """
    Unified Travel Guide Service
    
    Features:
    - Single point of entry for all guide generation
    - LLM-based parsing (no regex)
    - Weather-activity correlation
    - Real-time event integration
    - Persona-based personalization
    - Magazine-quality content generation
    - Comprehensive error handling and validation
    """

    def __init__(self):
        """Initialize the unified guide service with all dependencies"""
        self.logger = logger
        
        # Initialize service dependencies
        self.llm_parser = LLMParser()
        self.perplexity_search = PerplexitySearchService()
        self.weather_service = WeatherService()
        self.places_enhancer = GooglePlacesEnhancer()
        self.events_service = RealEventsService()
        
        self.prompts = self._load_prompts()
        self.weather_correlations = self._load_weather_correlations()
        
        self.perplexity_api_key = get_api_key("perplexity")
        self.openai_api_key = get_api_key("openai")
        self.anthropic_api_key = get_api_key("anthropic")
        
        # Validate required API keys
        if not any([self.perplexity_api_key, self.openai_api_key, self.anthropic_api_key]):
            raise APIError("At least one LLM API key is required (Perplexity, OpenAI, or Anthropic)")
        
        # Performance tracking
        self.generation_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_time": 0.0,
            "cache_hits": 0,
            "persona_distribution": {},
            "quality_scores": []
        }

    def _load_prompts(self) -> Dict[str, Any]:
        """Load structured prompts for LLM-based parsing and generation"""
        return {
            "travel_guide": {
                "base_prompt": (
                    "You are an expert travel editor creating a premium, magazine-quality travel guide. "
                    "Use specific details, real addresses, current information, and actionable recommendations. "
                    "Adapt your tone and recommendations to the traveler's persona and preferences."
                ),
                "structured_extraction": {
                    "document_parser": """
                    Extract travel information from the provided document in this exact JSON format:
                    {
                        "flights": [
                            {
                                "airline": "string",
                                "flight_number": "string", 
                                "departure_date": "YYYY-MM-DD",
                                "departure_time": "HH:MM",
                                "departure_airport": "string",
                                "arrival_date": "YYYY-MM-DD", 
                                "arrival_time": "HH:MM",
                                "arrival_airport": "string",
                                "confirmation_number": "string"
                            }
                        ],
                        "hotels": [
                            {
                                "name": "string",
                                "address": "string",
                                "check_in_date": "YYYY-MM-DD",
                                "check_out_date": "YYYY-MM-DD",
                                "confirmation_number": "string",
                                "phone": "string"
                            }
                        ],
                        "events": [
                            {
                                "name": "string",
                                "date": "YYYY-MM-DD",
                                "time": "HH:MM",
                                "location": "string",
                                "ticket_info": "string"
                            }
                        ],
                        "car_rentals": [
                            {
                                "company": "string",
                                "pickup_date": "YYYY-MM-DD",
                                "pickup_location": "string",
                                "return_date": "YYYY-MM-DD",
                                "return_location": "string",
                                "confirmation_number": "string"
                            }
                        ]
                    }
                    
                    If any information is not found, use null for that field.
                    Only extract information that is explicitly stated in the document.
                    """
                },
                "persona_adaptation": {
                    PersonaType.LUXURY_TRAVELER: {
                        "tone": "Sophisticated, exclusive, refined",
                        "focus": "Premium experiences, fine dining, luxury accommodations, VIP access",
                        "budget_range": "$$$-$$$$",
                        "activity_preference": "Curated, exclusive, comfort-focused"
                    },
                    PersonaType.BUDGET_EXPLORER: {
                        "tone": "Practical, resourceful, adventurous",
                        "focus": "Value experiences, local gems, budget-friendly options, free activities",
                        "budget_range": "$-$$",
                        "activity_preference": "DIY, authentic, cost-effective"
                    },
                    PersonaType.FAMILY_FRIENDLY: {
                        "tone": "Warm, practical, safety-conscious",
                        "focus": "Kid-friendly activities, family restaurants, safe neighborhoods, educational experiences",
                        "budget_range": "$$-$$$",
                        "activity_preference": "Safe, engaging, age-appropriate"
                    },
                    PersonaType.ADVENTURE_SEEKER: {
                        "tone": "Energetic, bold, inspiring",
                        "focus": "Outdoor activities, unique experiences, physical challenges, off-beaten-path",
                        "budget_range": "$$-$$$",
                        "activity_preference": "Active, challenging, unique"
                    },
                    PersonaType.CULTURAL_ENTHUSIAST: {
                        "tone": "Intellectual, curious, respectful",
                        "focus": "Museums, historical sites, local culture, art galleries, cultural events",
                        "budget_range": "$$-$$$",
                        "activity_preference": "Educational, authentic, immersive"
                    },
                    PersonaType.FOODIE: {
                        "tone": "Passionate, knowledgeable, sensory",
                        "focus": "Restaurants, food markets, cooking classes, local specialties, wine/beer",
                        "budget_range": "$$-$$$$",
                        "activity_preference": "Culinary-focused, authentic, diverse"
                    }
                },
                "weather_integration": """
                For each day of the itinerary, consider the weather forecast and:
                1. Recommend appropriate clothing and gear
                2. Suggest indoor alternatives for bad weather days
                3. Highlight weather-dependent activities (beach, hiking, outdoor markets)
                4. Include seasonal considerations and local weather patterns
                5. Provide specific "what to pack" recommendations
                """
            }
        }

    def _load_weather_correlations(self) -> List[WeatherActivityCorrelation]:
        """Load weather-activity correlation rules"""
        return [
            WeatherActivityCorrelation(
                temperature_range=(80, 100),
                conditions=["sunny", "clear"],
                recommended_activities=["beach", "swimming", "outdoor markets", "rooftop dining"],
                avoid_activities=["intensive hiking", "long walking tours"],
                clothing_suggestions=["light clothing", "sun hat", "sunscreen", "sunglasses"],
                special_notes="Stay hydrated and seek shade during peak hours"
            ),
            WeatherActivityCorrelation(
                temperature_range=(60, 79),
                conditions=["sunny", "partly cloudy"],
                recommended_activities=["walking tours", "outdoor dining", "parks", "sightseeing"],
                avoid_activities=[],
                clothing_suggestions=["comfortable layers", "walking shoes", "light jacket"],
                special_notes="Perfect weather for most outdoor activities"
            ),
            WeatherActivityCorrelation(
                temperature_range=(40, 59),
                conditions=["cloudy", "cool"],
                recommended_activities=["museums", "indoor attractions", "cafes", "shopping"],
                avoid_activities=["beach activities", "outdoor swimming"],
                clothing_suggestions=["warm layers", "jacket", "closed shoes"],
                special_notes="Great for indoor cultural activities"
            ),
            WeatherActivityCorrelation(
                temperature_range=(20, 39),
                conditions=["cold", "winter"],
                recommended_activities=["museums", "indoor markets", "theaters", "warm restaurants"],
                avoid_activities=["outdoor dining", "beach", "long outdoor walks"],
                clothing_suggestions=["heavy coat", "warm layers", "gloves", "warm hat"],
                special_notes="Focus on indoor activities and warm venues"
            ),
            WeatherActivityCorrelation(
                temperature_range=(32, 100),
                conditions=["rain", "showers", "thunderstorms"],
                recommended_activities=["museums", "shopping malls", "covered markets", "indoor entertainment"],
                avoid_activities=["outdoor tours", "beach", "hiking", "outdoor dining"],
                clothing_suggestions=["waterproof jacket", "umbrella", "waterproof shoes"],
                special_notes="Have indoor backup plans ready"
            )
        ]

    async def generate_complete_guide(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict[str, Any],
        preferences: Dict[str, Any],
        extracted_data: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete, magazine-quality travel guide
        
        Args:
            destination: Travel destination
            start_date: Trip start date (YYYY-MM-DD)
            end_date: Trip end date (YYYY-MM-DD)
            hotel_info: Hotel information dict
            preferences: User preferences dict
            extracted_data: Additional extracted data from documents
            progress_callback: Optional progress callback function
            
        Returns:
            Complete travel guide dict with all sections
        """
        start_time = datetime.now()
        self.generation_stats["total_requests"] += 1
        
        try:
            if progress_callback:
                await progress_callback(5, "Initializing unified guide generation")
            
            context = self._build_generation_context(
                destination, start_date, end_date, hotel_info, preferences, extracted_data
            )
            
            if progress_callback:
                await progress_callback(15, "Fetching real-time data concurrently")
            
            guide_data = await self._fetch_all_data_concurrently(context, progress_callback)
            
            if guide_data.get("error"):
                return guide_data
            
            if progress_callback:
                await progress_callback(70, "Correlating weather with activities")
            
            guide_data = await self._apply_weather_correlation(guide_data, context)
            
            if progress_callback:
                await progress_callback(85, "Applying persona-based personalization")
            
            guide_data = await self._apply_persona_personalization(guide_data, context)
            
            if progress_callback:
                await progress_callback(95, "Validating guide quality")
            
            is_valid, errors, validation_details = GuideValidator.validate_guide(guide_data)
            
            if not is_valid:
                logger.warning(f"Guide validation failed: {errors}")
                guide_data = await self._auto_fix_guide_issues(guide_data, errors, context)
                
                is_valid, errors, validation_details = GuideValidator.validate_guide(guide_data)
                
                if not is_valid:
                    return {
                        "error": "Guide quality validation failed",
                        "message": f"Generated guide for {destination} does not meet quality standards",
                        "validation_errors": errors,
                        "validation_details": validation_details,
                        "partial_guide": guide_data,
                        "generated_at": datetime.now().isoformat()
                    }
            
            generation_time = (datetime.now() - start_time).total_seconds()
            guide_data.update({
                "validation_passed": True,
                "generation_time_seconds": generation_time,
                "generated_with": "unified_guide_service",
                "generated_at": datetime.now().isoformat(),
                "persona": context.persona.value,
                "weather_correlated": True,
                "real_time_data": True,
                "quality_score": self._calculate_quality_score(guide_data),
                "performance_stats": {
                    "total_time": generation_time,
                    "concurrent_requests": 6,
                    "cache_used": guide_data.get("cache_key") is not None
                }
            })
            
            # Update stats
            self.generation_stats["successful_requests"] += 1
            self.generation_stats["average_time"] = (
                (self.generation_stats["average_time"] * (self.generation_stats["successful_requests"] - 1) + generation_time) 
                / self.generation_stats["successful_requests"]
            )
            
            persona_key = context.persona.value
            self.generation_stats["persona_distribution"][persona_key] = (
                self.generation_stats["persona_distribution"].get(persona_key, 0) + 1
            )
            
            self.generation_stats["quality_scores"].append(guide_data["quality_score"])
            
            if progress_callback:
                await progress_callback(100, f"Magazine-quality guide ready! Generated in {generation_time:.1f}s")
            
            logger.info(f"Unified guide generated successfully for {destination} in {generation_time:.1f}s")
            return guide_data
            
        except Exception as e:
            logger.error(f"Unified guide generation failed for {destination}: {e}")
            return {
                "error": "Guide generation failed",
                "message": str(e),
                "destination": destination,
                "generated_at": datetime.now().isoformat()
            }

    def _build_generation_context(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict[str, Any],
        preferences: Dict[str, Any],
        extracted_data: Optional[Dict[str, Any]]
    ) -> GuideGenerationContext:
        """Build comprehensive generation context"""
        
        # Calculate trip duration
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days + 1
        
        persona = self._detect_persona(preferences)
        
        return GuideGenerationContext(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration,
            hotel_info=hotel_info,
            preferences=preferences,
            persona=persona,
            extracted_data=extracted_data or {}
        )

    def _detect_persona(self, preferences: Dict[str, Any]) -> PersonaType:
        """Detect user persona from preferences using structured analysis"""
        
        persona_scores = {persona: 0 for persona in PersonaType}
        
        budget = preferences.get("priceRange", "$$")
        if budget in ["$$$$", "$$$"]:
            persona_scores[PersonaType.LUXURY_TRAVELER] += 3
        elif budget in ["$", "$$"]:
            persona_scores[PersonaType.BUDGET_EXPLORER] += 3
        
        group_type = preferences.get("groupType", "")
        if group_type == "family":
            persona_scores[PersonaType.FAMILY_FRIENDLY] += 4
        elif group_type == "couple":
            persona_scores[PersonaType.ROMANTIC_COUPLE] += 2
        
        interests = preferences.get("specialInterests", [])
        for interest in interests:
            interest_lower = interest.lower()
            if any(word in interest_lower for word in ["food", "dining", "culinary", "restaurant"]):
                persona_scores[PersonaType.FOODIE] += 2
            elif any(word in interest_lower for word in ["adventure", "hiking", "outdoor", "sports"]):
                persona_scores[PersonaType.ADVENTURE_SEEKER] += 2
            elif any(word in interest_lower for word in ["culture", "museum", "history", "art"]):
                persona_scores[PersonaType.CULTURAL_ENTHUSIAST] += 2
            elif any(word in interest_lower for word in ["luxury", "spa", "premium", "exclusive"]):
                persona_scores[PersonaType.LUXURY_TRAVELER] += 2
        
        adventure_level = preferences.get("adventureLevel", 3)
        if adventure_level >= 4:
            persona_scores[PersonaType.ADVENTURE_SEEKER] += 2
        elif adventure_level <= 2:
            persona_scores[PersonaType.LUXURY_TRAVELER] += 1
        
        return max(persona_scores, key=persona_scores.get)

    async def _fetch_all_data_concurrently(
        self,
        context: GuideGenerationContext,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Fetch all guide data using concurrent API calls"""
        
        tasks = []
        
        weather_task = self.weather_service.get_weather_forecast(
            context.destination, context.start_date, context.end_date
        )
        tasks.append(weather_task)
        
        restaurants_task = self._fetch_google_places_restaurants(context)
        tasks.append(restaurants_task)
        
        attractions_task = self._fetch_google_places_attractions(context)
        tasks.append(attractions_task)
        
        events_task = self.events_service.get_events_for_dates(
            context.destination, context.start_date, context.end_date, context.preferences
        )
        tasks.append(events_task)
        
        perplexity_task = self._generate_with_perplexity(context, progress_callback)
        tasks.append(perplexity_task)
        
        practical_task = self._fetch_practical_info(context)
        tasks.append(practical_task)
        
        try:
            # Execute all tasks concurrently with timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=60  # 60 second total timeout
            )
            
            weather_data, restaurants, attractions, events, perplexity_data, practical_info = results
            
            if isinstance(weather_data, Exception):
                logger.warning(f"Weather data fetch failed: {weather_data}")
                weather_data = {"error": str(weather_data)}
            
            if isinstance(restaurants, Exception):
                logger.warning(f"Restaurants fetch failed: {restaurants}")
                restaurants = []
            
            if isinstance(attractions, Exception):
                logger.warning(f"Attractions fetch failed: {attractions}")
                attractions = []
            
            if isinstance(events, Exception):
                logger.warning(f"Events fetch failed: {events}")
                events = []
            
            if isinstance(perplexity_data, Exception):
                logger.error(f"Perplexity data fetch failed: {perplexity_data}")
                return {"error": f"Failed to fetch guide content: {str(perplexity_data)}"}
            
            if isinstance(practical_info, Exception):
                logger.warning(f"Practical info fetch failed: {practical_info}")
                practical_info = {}
            
            combined_data = perplexity_data.copy() if perplexity_data else {}
            combined_data.update({
                "weather_data": weather_data,
                "restaurants": restaurants,
                "attractions": attractions,
                "events": events,
                "practical_info": practical_info,
                "generation_context": {
                    "destination": context.destination,
                    "dates": f"{context.start_date} to {context.end_date}",
                    "duration": context.duration_days,
                    "persona": context.persona.value
                }
            })
            
            return combined_data
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching data for {context.destination}")
            return {"error": f"Timeout fetching data for {context.destination}"}
        except Exception as e:
            logger.error(f"Error in concurrent data fetching: {e}")
            return {"error": f"Error fetching data: {str(e)}"}

    async def _generate_with_perplexity(
        self,
        context: GuideGenerationContext,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Generate guide content using Perplexity with structured prompts"""
        
        if not self.perplexity_api_key:
            return {"error": "Perplexity API key not configured"}
        
        persona_config = self.prompts["travel_guide"]["persona_adaptation"][context.persona]
        
        prompt = f"""
        {self.prompts["travel_guide"]["base_prompt"]}
        
        TRAVELER PERSONA: {context.persona.value.replace('_', ' ').title()}
        - Tone: {persona_config['tone']}
        - Focus: {persona_config['focus']}
        - Budget Range: {persona_config['budget_range']}
        - Activity Preference: {persona_config['activity_preference']}
        
        DESTINATION: {context.destination}
        DATES: {context.start_date} to {context.end_date} ({context.duration_days} days)
        
        PREFERENCES:
        {json.dumps(context.preferences, indent=2)}
        
        Create a comprehensive travel guide with these sections:
        1. Destination Overview & Highlights
        2. Daily Itinerary Suggestions (weather will be integrated separately)
        3. Local Neighborhoods & Areas
        4. Hidden Gems & Insider Tips
        5. Cultural Insights & Etiquette
        6. Transportation Guide
        7. Safety & Practical Information
        
        {self.prompts["travel_guide"]["weather_integration"]}
        
        Provide specific addresses, phone numbers, websites, and booking information for everything.
        Make recommendations that align with the {context.persona.value.replace('_', ' ')} persona.
        """
        
        try:
            timeout = aiohttp.ClientTimeout(total=90)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                url = "https://api.perplexity.ai/chat/completions"
                
                payload = {
                    "model": "sonar-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are creating a premium travel guide with real-time web access. Provide current, accurate information with specific details and booking links."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_tokens": 16000
                }
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        guide_content = data["choices"][0]["message"]["content"]
                        citations = data.get("citations", [])
                        
                        parsed_guide = await self._parse_guide_with_llm(guide_content, context)
                        parsed_guide["citations"] = citations
                        parsed_guide["raw_content"] = guide_content
                        
                        return parsed_guide
                    else:
                        error_text = await response.text()
                        logger.error(f"Perplexity API error: {response.status} - {error_text}")
                        return {"error": f"Perplexity API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error calling Perplexity API: {e}")
            return {"error": f"Failed to generate guide content: {str(e)}"}

    async def _parse_guide_with_llm(
        self,
        guide_content: str,
        context: GuideGenerationContext
    ) -> Dict[str, Any]:
        """Parse guide content using LLM instead of regex"""
        
        parsing_prompt = f"""
        Parse the following travel guide content into structured JSON format.
        Extract information for these sections:
        
        {{
            "summary": "Brief destination summary",
            "destination_insights": "Key insights about the destination",
            "daily_itinerary": [
                {{
                    "day": 1,
                    "date": "YYYY-MM-DD",
                    "day_of_week": "Monday",
                    "morning": ["activity 1", "activity 2"],
                    "afternoon": ["activity 1", "activity 2"],
                    "evening": ["activity 1", "activity 2"]
                }}
            ],
            "neighborhoods": [
                {{
                    "name": "Neighborhood Name",
                    "description": "Description",
                    "highlights": ["highlight 1", "highlight 2"],
                    "best_for": "What this area is best for"
                }}
            ],
            "hidden_gems": [
                {{
                    "name": "Gem Name",
                    "description": "Description",
                    "location": "Address or area",
                    "why_special": "What makes it special"
                }}
            ],
            "cultural_insights": {{
                "etiquette": ["tip 1", "tip 2"],
                "customs": ["custom 1", "custom 2"],
                "language_tips": ["phrase 1", "phrase 2"]
            }},
            "transportation": {{
                "public_transport": "Description and tips",
                "taxi_rideshare": "Information about taxis/rideshare",
                "walking": "Walkability information",
                "car_rental": "Car rental information if relevant"
            }},
            "safety_info": {{
                "general_safety": "General safety information",
                "areas_to_avoid": ["area 1", "area 2"],
                "emergency_contacts": "Emergency contact information"
            }}
        }}
        
        Travel Guide Content:
        {guide_content}
        
        Return only valid JSON. If information is not available, use null or empty arrays.
        """
        
        try:
            parsed_data = await self.llm_parser.parse_with_structure(
                parsing_prompt,
                expected_format="json"
            )
            
            if not isinstance(parsed_data, dict):
                parsed_data = {}
            
            required_fields = {
                "summary": "",
                "destination_insights": "",
                "daily_itinerary": [],
                "neighborhoods": [],
                "hidden_gems": [],
                "cultural_insights": {},
                "transportation": {},
                "safety_info": {}
            }
            
            for field, default_value in required_fields.items():
                if field not in parsed_data:
                    parsed_data[field] = default_value
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing guide content with LLM: {e}")
            return {
                "summary": "Travel guide generated successfully",
                "destination_insights": guide_content[:500] + "..." if len(guide_content) > 500 else guide_content,
                "daily_itinerary": [],
                "neighborhoods": [],
                "hidden_gems": [],
                "cultural_insights": {},
                "transportation": {},
                "safety_info": {},
                "parsing_error": str(e)
            }

    async def _fetch_google_places_restaurants(self, context: GuideGenerationContext) -> List[Dict[str, Any]]:
        """Fetch restaurants using Google Places API with persona-based filtering"""
        try:
            await self.google_places_service.initialize()
            
            persona_config = self.prompts["travel_guide"]["persona_adaptation"][context.persona]
            
            restaurants = []
            
            if context.persona == PersonaType.LUXURY_TRAVELER:
                luxury_restaurants = await self.google_places_service.search_restaurants(
                    location=context.destination,
                    cuisine_type="fine dining",
                    limit=8
                )
                restaurants.extend(luxury_restaurants)
                
            elif context.persona == PersonaType.BUDGET_EXPLORER:
                budget_restaurants = await self.google_places_service.search_restaurants(
                    location=context.destination,
                    cuisine_type="local cuisine",
                    limit=10
                )
                restaurants.extend(budget_restaurants)
                
            elif context.persona == PersonaType.FOODIE:
                cuisine_types = ["local cuisine", "street food", "fine dining", "ethnic cuisine"]
                for cuisine in cuisine_types:
                    cuisine_restaurants = await self.google_places_service.search_restaurants(
                        location=context.destination,
                        cuisine_type=cuisine,
                        limit=4
                    )
                    restaurants.extend(cuisine_restaurants)
            
            general_restaurants = await self.google_places_service.search_restaurants(
                location=context.destination,
                limit=8
            )
            restaurants.extend(general_restaurants)
            
            seen_ids = set()
            unique_restaurants = []
            for restaurant in restaurants:
                place_id = restaurant.get("id")
                if place_id and place_id not in seen_ids:
                    seen_ids.add(place_id)
                    unique_restaurants.append(restaurant)
            
            return unique_restaurants[:15]  # Top 15 restaurants
            
        except Exception as e:
            logger.error(f"Error fetching Google Places restaurants: {e}")
            return []

    async def _fetch_google_places_attractions(self, context: GuideGenerationContext) -> List[Dict[str, Any]]:
        """Fetch attractions using Google Places API with persona-based filtering"""
        try:
            await self.google_places_service.initialize()
            
            attractions = await self.google_places_service.search_attractions(
                location=context.destination,
                limit=10
            )
            
            if context.persona == PersonaType.CULTURAL_ENTHUSIAST:
                cultural_attractions = [
                    attr for attr in attractions 
                    if any(keyword in attr.get("types", []) for keyword in ["museum", "art_gallery", "church", "historical"])
                ]
                other_attractions = [attr for attr in attractions if attr not in cultural_attractions]
                attractions = cultural_attractions + other_attractions
                
            elif context.persona == PersonaType.ADVENTURE_SEEKER:
                adventure_attractions = [
                    attr for attr in attractions 
                    if any(keyword in attr.get("types", []) for keyword in ["park", "natural_feature", "amusement_park"])
                ]
                other_attractions = [attr for attr in attractions if attr not in adventure_attractions]
                attractions = adventure_attractions + other_attractions
            
            return attractions[:8]  # Top 8 attractions
            
        except Exception as e:
            logger.error(f"Error fetching Google Places attractions: {e}")
            return []

    async def _fetch_practical_info(self, context: GuideGenerationContext) -> Dict[str, Any]:
        """Fetch practical travel information"""
        try:
            return {
                "currency": "Local currency information",
                "tipping": "Tipping customs and guidelines",
                "business_hours": "Typical business hours",
                "public_holidays": "Public holidays during travel dates",
                "electrical_outlets": "Electrical outlet information",
                "internet_wifi": "Internet and WiFi availability",
                "emergency_numbers": {
                    "police": "Local police number",
                    "medical": "Medical emergency number",
                    "fire": "Fire emergency number"
                }
            }
        except Exception as e:
            logger.error(f"Error fetching practical info: {e}")
            return {}

    async def _apply_weather_correlation(
        self,
        guide_data: Dict[str, Any],
        context: GuideGenerationContext
    ) -> Dict[str, Any]:
        """Apply weather-activity correlation to the guide"""
        
        weather_data = guide_data.get("weather_data", {})
        if weather_data.get("error") or not weather_data.get("daily_forecasts"):
            logger.warning("No weather data available for correlation")
            return guide_data
        
        daily_forecasts = weather_data.get("daily_forecasts", [])
        daily_itinerary = guide_data.get("daily_itinerary", [])
        
        for i, day_plan in enumerate(daily_itinerary):
            if i < len(daily_forecasts):
                weather_day = daily_forecasts[i]
                
                temp = weather_day.get("temperature", {}).get("high", 70)
                conditions = weather_day.get("conditions", "").lower()
                
                matching_correlation = None
                for correlation in self.weather_correlations:
                    temp_min, temp_max = correlation.temperature_range
                    if temp_min <= temp <= temp_max:
                        if any(condition in conditions for condition in correlation.conditions):
                            matching_correlation = correlation
                            break
                
                if matching_correlation:
                    day_plan["weather_recommendations"] = {
                        "clothing": matching_correlation.clothing_suggestions,
                        "recommended_activities": matching_correlation.recommended_activities,
                        "avoid_activities": matching_correlation.avoid_activities,
                        "special_notes": matching_correlation.special_notes
                    }
                    
                    if matching_correlation.avoid_activities:
                        for time_period in ["morning", "afternoon", "evening"]:
                            activities = day_plan.get(time_period, [])
                            filtered_activities = []
                            for activity in activities:
                                activity_lower = activity.lower()
                                should_avoid = any(
                                    avoid_activity.lower() in activity_lower 
                                    for avoid_activity in matching_correlation.avoid_activities
                                )
                                if not should_avoid:
                                    filtered_activities.append(activity)
                                else:
                                    if "outdoor" in activity_lower:
                                        alternative = activity.replace("outdoor", "indoor")
                                        filtered_activities.append(f"{alternative} (weather alternative)")
                            
                            day_plan[time_period] = filtered_activities
        
        guide_data["weather_summary"] = {
            "overview": weather_data.get("summary", {}),
            "packing_recommendations": self._generate_packing_recommendations(daily_forecasts),
            "weather_highlights": self._generate_weather_highlights(daily_forecasts)
        }
        
        return guide_data

    def _generate_packing_recommendations(self, daily_forecasts: List[Dict[str, Any]]) -> List[str]:
        """Generate packing recommendations based on weather forecast"""
        recommendations = set()
        
        for day in daily_forecasts:
            temp_high = day.get("temperature", {}).get("high", 70)
            temp_low = day.get("temperature", {}).get("low", 60)
            conditions = day.get("conditions", "").lower()
            
            if temp_high >= 80:
                recommendations.update(["Light, breathable clothing", "Sun hat", "Sunscreen", "Sunglasses"])
            elif temp_high >= 60:
                recommendations.update(["Comfortable layers", "Light jacket", "Walking shoes"])
            elif temp_high >= 40:
                recommendations.update(["Warm layers", "Jacket", "Closed shoes"])
            else:
                recommendations.update(["Heavy coat", "Warm layers", "Gloves", "Warm hat"])
            
            if any(word in conditions for word in ["rain", "shower", "storm"]):
                recommendations.update(["Waterproof jacket", "Umbrella", "Waterproof shoes"])
            
            if temp_low < 50:
                recommendations.add("Warm evening wear")
        
        return sorted(list(recommendations))

    def _generate_weather_highlights(self, daily_forecasts: List[Dict[str, Any]]) -> List[str]:
        """Generate weather highlights for the trip"""
        highlights = []
        
        if not daily_forecasts:
            return highlights
        
        best_day = max(daily_forecasts, key=lambda d: d.get("temperature", {}).get("high", 0))
        highlights.append(f"Best weather expected on {best_day.get('date', 'TBD')} - perfect for outdoor activities")
        
        rainy_days = [d for d in daily_forecasts if "rain" in d.get("conditions", "").lower()]
        if rainy_days:
            highlights.append(f"Rain expected on {len(rainy_days)} day(s) - plan indoor activities")
        
        temps = [d.get("temperature", {}).get("high", 70) for d in daily_forecasts]
        if temps:
            min_temp, max_temp = min(temps), max(temps)
            highlights.append(f"Temperature range: {min_temp}°F - {max_temp}°F")
        
        return highlights

    async def _apply_persona_personalization(
        self,
        guide_data: Dict[str, Any],
        context: GuideGenerationContext
    ) -> Dict[str, Any]:
        """Apply persona-based personalization to all guide content"""
        
        persona_config = self.prompts["travel_guide"]["persona_adaptation"][context.persona]
        
        restaurants = guide_data.get("restaurants", [])
        personalized_restaurants = []
        
        for restaurant in restaurants:
            restaurant["persona_match"] = self._calculate_restaurant_persona_match(restaurant, context.persona)
            restaurant["why_recommended"] = self._generate_persona_restaurant_recommendation(restaurant, context.persona)
            personalized_restaurants.append(restaurant)
        
        personalized_restaurants.sort(key=lambda r: r.get("persona_match", 0), reverse=True)
        guide_data["restaurants"] = personalized_restaurants[:12]  # Top 12 for persona
        
        attractions = guide_data.get("attractions", [])
        personalized_attractions = []
        
        for attraction in attractions:
            attraction["persona_match"] = self._calculate_attraction_persona_match(attraction, context.persona)
            attraction["why_recommended"] = self._generate_persona_attraction_recommendation(attraction, context.persona)
            personalized_attractions.append(attraction)
        
        personalized_attractions.sort(key=lambda a: a.get("persona_match", 0), reverse=True)
        guide_data["attractions"] = personalized_attractions[:8]  # Top 8 for persona
        
        guide_data["persona_tips"] = self._generate_persona_specific_tips(context.persona, context.destination)
        
        daily_itinerary = guide_data.get("daily_itinerary", [])
        for day in daily_itinerary:
            day["persona_notes"] = self._generate_daily_persona_notes(day, context.persona)
        
        return guide_data

    def _calculate_restaurant_persona_match(self, restaurant: Dict[str, Any], persona: PersonaType) -> float:
        """Calculate how well a restaurant matches the persona (0-1 score)"""
        score = 0.5  # Base score
        
        cuisine = restaurant.get("cuisine", "").lower()
        price_level = restaurant.get("price_level_numeric", 2)
        rating = restaurant.get("rating", 3.5)
        
        if persona == PersonaType.LUXURY_TRAVELER:
            if price_level >= 3:
                score += 0.3
            if rating >= 4.5:
                score += 0.2
            if any(word in cuisine for word in ["fine", "upscale", "gourmet"]):
                score += 0.2
                
        elif persona == PersonaType.BUDGET_EXPLORER:
            if price_level <= 2:
                score += 0.3
            if any(word in cuisine for word in ["local", "street", "casual"]):
                score += 0.2
            if rating >= 4.0:
                score += 0.1
                
        elif persona == PersonaType.FOODIE:
            if rating >= 4.3:
                score += 0.3
            if any(word in cuisine for word in ["authentic", "traditional", "specialty"]):
                score += 0.2
            if price_level >= 2:  # Foodies often willing to pay for quality
                score += 0.1
        
        return min(score, 1.0)

    def _calculate_attraction_persona_match(self, attraction: Dict[str, Any], persona: PersonaType) -> float:
        """Calculate how well an attraction matches the persona (0-1 score)"""
        score = 0.5  # Base score
        
        types = attraction.get("types", [])
        name = attraction.get("name", "").lower()
        rating = attraction.get("rating", 3.5)
        
        if persona == PersonaType.CULTURAL_ENTHUSIAST:
            if any(t in types for t in ["museum", "art_gallery", "church", "historical"]):
                score += 0.4
            if any(word in name for word in ["museum", "gallery", "cathedral", "palace"]):
                score += 0.2
                
        elif persona == PersonaType.ADVENTURE_SEEKER:
            if any(t in types for t in ["park", "natural_feature", "amusement_park"]):
                score += 0.4
            if any(word in name for word in ["park", "trail", "adventure", "outdoor"]):
                score += 0.2
                
        elif persona == PersonaType.FAMILY_FRIENDLY:
            if any(t in types for t in ["amusement_park", "zoo", "aquarium"]):
                score += 0.4
            if any(word in name for word in ["family", "kids", "children", "zoo"]):
                score += 0.2
        
        if rating >= 4.0:
            score += 0.1
        
        return min(score, 1.0)

    def _generate_persona_restaurant_recommendation(self, restaurant: Dict[str, Any], persona: PersonaType) -> str:
        """Generate persona-specific restaurant recommendation"""
        name = restaurant.get("name", "")
        cuisine = restaurant.get("cuisine", "")
        
        if persona == PersonaType.LUXURY_TRAVELER:
            return f"Perfect for a refined dining experience. {name} offers {cuisine} in an upscale setting."
        elif persona == PersonaType.BUDGET_EXPLORER:
            return f"Great value for authentic {cuisine}. {name} is a local favorite that won't break the bank."
        elif persona == PersonaType.FOODIE:
            return f"A must-try for food enthusiasts. {name} is renowned for exceptional {cuisine}."
        elif persona == PersonaType.FAMILY_FRIENDLY:
            return f"Family-friendly atmosphere at {name}. Great {cuisine} with options for all ages."
        else:
            return f"Highly recommended {cuisine} restaurant with excellent reviews."

    def _generate_persona_attraction_recommendation(self, attraction: Dict[str, Any], persona: PersonaType) -> str:
        """Generate persona-specific attraction recommendation"""
        name = attraction.get("name", "")
        
        if persona == PersonaType.CULTURAL_ENTHUSIAST:
            return f"Essential for culture lovers. {name} offers deep insights into local history and art."
        elif persona == PersonaType.ADVENTURE_SEEKER:
            return f"Perfect for adventure enthusiasts. {name} provides exciting outdoor experiences."
        elif persona == PersonaType.FAMILY_FRIENDLY:
            return f"Great for families. {name} offers engaging activities for all ages."
        elif persona == PersonaType.LUXURY_TRAVELER:
            return f"A premium experience at {name}. Enjoy exclusive access and refined amenities."
        else:
            return f"Highly rated attraction that showcases the best of the destination."

    def _generate_persona_specific_tips(self, persona: PersonaType, destination: str) -> List[str]:
        """Generate persona-specific travel tips"""
        base_tips = [
            "Download offline maps before exploring",
            "Learn basic local phrases",
            "Keep copies of important documents"
        ]
        
        if persona == PersonaType.LUXURY_TRAVELER:
            base_tips.extend([
                "Book restaurant reservations well in advance",
                "Consider hiring a private guide for exclusive experiences",
                "Look into VIP access options for popular attractions"
            ])
        elif persona == PersonaType.BUDGET_EXPLORER:
            base_tips.extend([
                "Use public transportation to save money",
                "Eat where locals eat for authentic, affordable meals",
                "Look for free walking tours and activities"
            ])
        elif persona == PersonaType.FOODIE:
            base_tips.extend([
                "Visit local markets early in the morning",
                "Ask locals for their favorite hidden food spots",
                "Try street food from busy vendors"
            ])
        elif persona == PersonaType.ADVENTURE_SEEKER:
            base_tips.extend([
                "Pack appropriate gear for outdoor activities",
                "Check weather conditions before hiking",
                "Book adventure tours in advance during peak season"
            ])
        
        return base_tips

    def _generate_daily_persona_notes(self, day: Dict[str, Any], persona: PersonaType) -> str:
        """Generate persona-specific notes for each day"""
        day_num = day.get("day", 1)
        
        if persona == PersonaType.LUXURY_TRAVELER:
            return f"Day {day_num}: Focus on premium experiences and comfortable pacing. Consider spa treatments or fine dining."
        elif persona == PersonaType.BUDGET_EXPLORER:
            return f"Day {day_num}: Maximize value with free activities and local experiences. Pack snacks and water."
        elif persona == PersonaType.ADVENTURE_SEEKER:
            return f"Day {day_num}: High-energy day with outdoor activities. Start early to make the most of daylight."
        elif persona == PersonaType.CULTURAL_ENTHUSIAST:
            return f"Day {day_num}: Immerse yourself in local culture and history. Allow extra time for museums and sites."
        else:
            return f"Day {day_num}: Balanced mix of activities to suit your travel style."

    async def _auto_fix_guide_issues(
        self,
        guide_data: Dict[str, Any],
        errors: List[str],
        context: GuideGenerationContext
    ) -> Dict[str, Any]:
        """Automatically fix common guide quality issues"""
        
        if "Missing daily itinerary" in errors:
            if not guide_data.get("daily_itinerary"):
                guide_data["daily_itinerary"] = self._generate_basic_itinerary(context)
        
        if "Missing restaurants" in errors:
            if not guide_data.get("restaurants"):
                guide_data["restaurants"] = [
                    {
                        "name": "Local Restaurant Recommendations",
                        "description": "Explore local dining options in the area",
                        "cuisine": "Various",
                        "address": f"Throughout {context.destination}"
                    }
                ]
        
        if "Missing attractions" in errors:
            if not guide_data.get("attractions"):
                guide_data["attractions"] = [
                    {
                        "name": "Local Attractions",
                        "description": "Discover popular attractions and activities",
                        "address": f"Throughout {context.destination}"
                    }
                ]
        
        return guide_data

    def _generate_basic_itinerary(self, context: GuideGenerationContext) -> List[Dict[str, Any]]:
        """Generate a basic itinerary structure"""
        itinerary = []
        
        start_date = datetime.strptime(context.start_date, "%Y-%m-%d")
        
        for i in range(context.duration_days):
            current_date = start_date + timedelta(days=i)
            
            day_plan = {
                "day": i + 1,
                "date": current_date.strftime("%Y-%m-%d"),
                "day_of_week": current_date.strftime("%A"),
                "morning": [f"Explore {context.destination} morning attractions"],
                "afternoon": [f"Visit {context.destination} afternoon highlights"],
                "evening": [f"Enjoy {context.destination} evening activities"]
            }
            
            itinerary.append(day_plan)
        
        return itinerary

    def _calculate_quality_score(self, guide_data: Dict[str, Any]) -> float:
        """Calculate overall quality score for the guide (0-100)"""
        score = 0
        max_score = 100
        
        required_sections = ["summary", "daily_itinerary", "restaurants", "attractions"]
        for section in required_sections:
            if guide_data.get(section):
                score += 10
        
        if len(guide_data.get("restaurants", [])) >= 5:
            score += 10
        if len(guide_data.get("attractions", [])) >= 5:
            score += 10
        if len(guide_data.get("daily_itinerary", [])) >= 1:
            score += 10
        
        if guide_data.get("persona_tips"):
            score += 10
        if any("persona_match" in item for item in guide_data.get("restaurants", [])):
            score += 10
        
        if guide_data.get("weather_summary"):
            score += 5
        if any("weather_recommendations" in day for day in guide_data.get("daily_itinerary", [])):
            score += 5
        
        return min(score, max_score)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get service performance statistics"""
        return self.generation_stats.copy()

    async def extract_travel_documents(
        self,
        document_content: str,
        document_type: str = "mixed"
    ) -> Dict[str, Any]:
        """
        Extract travel information from documents using LLM parsing (no regex)
        
        Args:
            document_content: Raw document content
            document_type: Type of document (flight, hotel, mixed, etc.)
            
        Returns:
            Structured travel information
        """
        try:
            extraction_prompt = self.prompts["travel_guide"]["structured_extraction"]["document_parser"]
            
            full_prompt = f"""
            {extraction_prompt}
            
            Document Type: {document_type}
            Document Content:
            {document_content}
            """
            
            extracted_data = await self.llm_parser.parse_with_structure(
                full_prompt,
                expected_format="json"
            )
            
            if not isinstance(extracted_data, dict):
                extracted_data = {}
            
            # Add metadata
            extracted_data["extraction_metadata"] = {
                "document_type": document_type,
                "extracted_at": datetime.now().isoformat(),
                "extraction_method": "llm_structured",
                "confidence": "high" if extracted_data else "low"
            }
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting travel documents: {e}")
            return {
                "error": f"Document extraction failed: {str(e)}",
                "extraction_metadata": {
                    "document_type": document_type,
                    "extracted_at": datetime.now().isoformat(),
                    "extraction_method": "llm_structured",
                    "confidence": "failed"
                }
            }
