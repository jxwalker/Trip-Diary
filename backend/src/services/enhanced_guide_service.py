"""
Enhanced Travel Guide Service
Uses advanced LLM prompting to create magazine-quality travel guides
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable
from pathlib import Path
import aiohttp

from .guide_parser import GuideParser
from .llm_parser import LLMParser
from .perplexity_search_service import PerplexitySearchService
from .weather_service import WeatherService
from .google_places_enhancer import GooglePlacesEnhancer
from ..utils.environment import load_project_env, get_api_key
from ..utils.error_handling import safe_execute, APIError, log_and_return_error

# Load environment variables
load_project_env()

logger = logging.getLogger(__name__)

class EnhancedGuideService:
    """
    Enhanced Travel Guide Service
    Uses advanced LLM prompting to create magazine-quality travel guides
    """

    def __init__(self):
        """Initialize the enhanced guide service with all dependencies"""
        self.logger = logger

        # Initialize service dependencies
        self.parser = GuideParser()
        self.llm_parser = LLMParser()
        self.perplexity_search = PerplexitySearchService()
        self.weather_service = WeatherService()
        self.places_enhancer = GooglePlacesEnhancer()

        # Load prompts configuration
        self.prompts = self._load_prompts()

        # API configurations using centralized environment utilities
        self.perplexity_api_key = get_api_key("perplexity")
        self.openai_api_key = get_api_key("openai")
        self.anthropic_api_key = get_api_key("anthropic")

        # Validate required API keys
        if not any([self.perplexity_api_key, self.openai_api_key, self.anthropic_api_key]):
            raise APIError("At least one LLM API key is required (Perplexity, OpenAI, or Anthropic)")

    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts configuration from JSON file, with a safe default fallback.
        Returns a dict that contains the keys expected by _construct_master_prompt
        so single-pass generation never crashes if the file is missing.
        """
        def default_prompts() -> Dict[str, Any]:
            return {
                "travel_guide": {
                    "base_prompt": (
                        "You are a seasoned travel editor crafting a glossy magazine-style, personalized guide. "
                        "Use rich, specific details, real addresses, times, booking links, and actionable tips."
                    ),
                    "components": {
                        "destination_overview": (
                            "Provide a vivid destination overview for {destination} during {month_year}, "
                            "considering the travel pace ({pace}), group ({group_type}), and interests."
                        ),
                        "weather_analysis": (
                            "Summarize the likely weather for {destination} from {start_date} to {end_date}, "
                            "including packing and what-to-wear guidance."
                        ),
                        "personalized_recommendations": {
                            "template": (
                                "Curate recommendations tailored to this traveler. Reflect preferences: {preferences_summary}."
                            )
                        },
                        "daily_itinerary": {
                            "template": (
                                "Build a detailed day-by-day itinerary ({duration} total) with specific times and places; "
                                "balance walking level ({walking_level}) and interests."
                            )
                        },
                        "events_search": (
                            "Include real events that align with dates ({dates}) and interests, with ticket links."
                        ),
                        "restaurant_guide": {
                            "template": (
                                "List restaurants with address, phone, cuisine, price, booking link, hours, and why it fits."
                            )
                        },
                        "local_insights": (
                            "Add insider tips, transport guidance, money matters, safety notes, and cultural etiquette."
                        ),
                        "hidden_gems": (
                            "Highlight lesser-known gems and photo spots, avoiding over-touristed cliches."
                        ),
                        "shopping_guide": (
                            "If relevant to preferences, suggest neighborhoods or streets and what to buy."
                        ),
                        "evening_entertainment": (
                            "Offer nightlife/theater/music options based on the traveler's nightlife level."
                        )
                    },
                    "output_format": (
                        "Structure with sections: Summary, Destination Insights, Weather, Daily Itinerary, "
                        "Restaurants, Attractions, Events, Neighborhoods (if relevant), Practical Info, Hidden Gems."
                    )
                }
            }
        try:
            prompts_path = Path(__file__).parent.parent / "prompts.json"
            with open(prompts_path, 'r') as f:
                loaded = json.load(f)
                # Ensure essential structure exists; otherwise, fallback
                if not isinstance(loaded, dict) or "travel_guide" not in loaded:
                    self.logger.warning("prompts.json missing expected keys; using defaults")
                    return default_prompts()
                return loaded
        except Exception as e:
            self.logger.warning(f"Could not load prompts.json: {e}")
            return default_prompts()
        
    async def generate_enhanced_guide(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        extracted_data: Dict,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None,
        single_pass: bool = True
    ) -> Dict:
        """
        Generate a comprehensive, personalized travel guide using REAL data
        NO MOCKS, NO PLACEHOLDERS - REAL PERPLEXITY SEARCHES ONLY
        """
        # Build the context from all available information
        context = self._build_context(
            destination, start_date, end_date, 
            hotel_info, preferences, extracted_data
        )
        
        # If no API key, return error instead of mocks
        if not self.perplexity_api_key:
            # If no API key, return error instead of mocks
            return {
                "error": "Perplexity API key not configured. Cannot generate real content.",
                "message": "Please configure PERPLEXITY_API_KEY in your .env file"
            }

        # Prefer single-pass generation for latency
        if single_pass:
            if progress_callback:
                await progress_callback(10, "Building personalized prompt")
            prompt = self._construct_master_prompt(context)
            
            if progress_callback:
                await progress_callback(20, "Fetching weather forecast")
            
            # Get real weather data
            weather_data = await self.weather_service.get_weather_forecast(
                destination, start_date, end_date
            )
            
            if progress_callback:
                await progress_callback(35, "Querying Perplexity")
            guide = await self._generate_with_perplexity(prompt, context)
            
            # Add real weather data to the guide
            if weather_data and not weather_data.get("error"):
                guide["weather"] = weather_data.get("daily_forecasts", [])
                guide["weather_summary"] = weather_data.get("summary", {})
            
            if progress_callback:
                await progress_callback(90, "Parsing and organizing guide")
            return guide
        else:
            # Multi-search mode (slower but more granular)
            return await self._generate_with_real_searches(context, progress_callback)
    
    def _build_context(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        extracted_data: Dict
    ) -> Dict:
        """Build comprehensive context for prompt generation"""
        
        # Calculate trip duration
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        duration = (end - start).days + 1
        
        # Format dates for readability
        formatted_dates = f"{start.strftime('%B %d')} to {end.strftime('%B %d, %Y')}"
        month_year = start.strftime("%B %Y")
        
        # Build preferences summary
        preferences_summary = self._build_preferences_summary(preferences)
        
        # Extract hotel address
        hotel_address = ""
        if hotel_info:
            hotel_address = hotel_info.get("address", "")
        
        persona = self._detect_persona(preferences)
        return {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "dates": formatted_dates,
            "month": start.strftime("%B"),
            "year": start.strftime("%Y"),
            "month_year": month_year,
            "duration": f"{duration} days",
            "duration_days": duration,
            "hotel_address": hotel_address,
            "hotel_info": hotel_info,
            "preferences": preferences,
            "preferences_summary": preferences_summary,
            "extracted_data": extracted_data,
            "pace": preferences.get("travelStyle", "balanced"),
            "group_type": preferences.get("groupType", "couple"),
            "walking_level": self._get_walking_description(preferences.get("walkingTolerance", 3)),
            "adventure_level": preferences.get("adventureLevel", 3),
            "nightlife_level": preferences.get("nightlife", 2),
            "price_range": preferences.get("priceRange", "$$"),
            "cuisines": ", ".join(preferences.get("cuisineTypes", ["Local Cuisine"])),
            "dietary": ", ".join(preferences.get("dietaryRestrictions", [])) or "None",
            "preferred_times": self._format_preferred_times(preferences.get("preferredTimes", {})),
            "persona": persona["label"],
            "persona_style": persona["style"],
            "persona_description": persona["description"]
        }
    
    def _build_preferences_summary(self, preferences: Dict) -> str:
        """Create a natural language summary of user preferences"""
        summary_parts = []
        
        # Interests
        interests = preferences.get("specialInterests", [])
        if interests:
            summary_parts.append(f"Interested in: {', '.join(interests)}")
        
        # Activity level
        walking = preferences.get("walkingTolerance", 3)
        if walking <= 2:
            summary_parts.append("Prefers minimal walking and easy-access locations")
        elif walking >= 4:
            summary_parts.append("Enjoys walking and exploring on foot")
        
        # Adventure level
        adventure = preferences.get("adventureLevel", 3)
        if adventure <= 2:
            summary_parts.append("Prefers well-known tourist attractions")
        elif adventure >= 4:
            summary_parts.append("Seeks unique, off-the-beaten-path experiences")
        
        # Food preferences
        cuisines = preferences.get("cuisineTypes", [])
        if cuisines:
            summary_parts.append(f"Food preferences: {', '.join(cuisines[:3])}")
        
        # Travel style
        pace = preferences.get("travelStyle", "balanced")
        summary_parts.append(f"Travel pace: {pace}")
        
        # Group type
        group = preferences.get("groupType", "couple")
        summary_parts.append(f"Traveling as: {group}")
        
        return "\n".join(summary_parts)
    
    def _get_walking_description(self, level: int) -> str:
        """Convert walking tolerance number to description"""
        descriptions = {
            1: "minimal walking preferred",
            2: "light walking only",
            3: "moderate walking",
            4: "comfortable with lots of walking",
            5: "loves walking everywhere"
        }
        return descriptions.get(level, "moderate walking")
    
    def _format_preferred_times(self, times: Dict) -> str:
        """Format preferred activity times"""
        active_times = []
        time_mapping = {
            "earlyMorning": "early morning (5am-8am)",
            "morning": "morning (8am-12pm)",
            "afternoon": "afternoon (12pm-5pm)",
            "evening": "evening (5pm-9pm)",
            "lateNight": "late night (9pm+)"
        }
        
        for key, label in time_mapping.items():
            if times.get(key, False):
                active_times.append(label)
        
        return ", ".join(active_times) if active_times else "flexible"
    
    def _construct_master_prompt(self, context: Dict) -> str:
        """Construct the master prompt using templates and context"""
        
        # Get base prompt and inject persona
        base = self.prompts["travel_guide"]["base_prompt"]
        persona_blurb = (
            f"Persona: {context.get('persona', 'Traveler')} — {context.get('persona_description','')}\n"
            f"Style: {context.get('persona_style','Refined, visual, concierge tone')}\n"
            f"Tailor voice, recommendations, pacing, and budget to this persona."
        )
        
        # Build component prompts
        components = []
        
        # Destination overview
        overview = self.prompts["travel_guide"]["components"]["destination_overview"]
        components.append(overview.format(**context))
        
        # Weather analysis
        weather = self.prompts["travel_guide"]["components"]["weather_analysis"]
        components.append(weather.format(**context))
        
        # Personalized recommendations
        recs = self.prompts["travel_guide"]["components"]["personalized_recommendations"]["template"]
        components.append(recs.format(**context))
        
        # Daily itinerary
        itinerary = self.prompts["travel_guide"]["components"]["daily_itinerary"]["template"]
        components.append(itinerary.format(**context))
        
        # Events search
        events = self.prompts["travel_guide"]["components"]["events_search"]
        components.append(events.format(**context))
        
        # Restaurant guide
        restaurants = self.prompts["travel_guide"]["components"]["restaurant_guide"]["template"]
        components.append(restaurants.format(**context))
        
        # Local insights
        insights = self.prompts["travel_guide"]["components"]["local_insights"]
        components.append(insights.format(**context))
        
        # Hidden gems
        gems = self.prompts["travel_guide"]["components"]["hidden_gems"]
        components.append(gems.format(**context))
        
        # Shopping guide (if interested)
        if context["preferences"].get("shopping", 0) > 2:
            shopping = self.prompts["travel_guide"]["components"]["shopping_guide"]
            components.append(shopping.format(**context))
        
        # Evening entertainment
        if context["nightlife_level"] > 2:
            evening = self.prompts["travel_guide"]["components"]["evening_entertainment"]
            components.append(evening.format(**context))
        
        # Output format
        output = self.prompts["travel_guide"]["output_format"]
        components.append(output.format(**context))
        
        # Combine all components
        master_prompt = f"{base}\n\n{persona_blurb}\n\n" + "\n\n".join(components)
        
        return master_prompt
    
    async def _generate_with_perplexity(self, prompt: str, context: Dict) -> Dict:
        """Generate guide using Perplexity API with web search.
        No mock fallbacks: on error, return structured empty results with error message.
        """
        
        if not self.perplexity_api_key:
            return {
                "error": "Perplexity API key not configured. Cannot generate real content.",
                "message": "Please configure PERPLEXITY_API_KEY in your .env file",
                "summary": "",
                "destination_insights": "",
                "weather": {},
                "daily_itinerary": [],
                "restaurants": [],
                "attractions": [],
                "events": [],
                "neighborhoods": [],
                "practical_info": {},
                "hidden_gems": [],
                "citations": []
            }
        
        try:
            print(f"[DEBUG] Starting Perplexity API call for {context.get('destination', 'unknown')}")
            timeout = aiohttp.ClientTimeout(total=90)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                # Perplexity API endpoint
                url = "https://api.perplexity.ai/chat/completions"
                
                payload = {
                    "model": "sonar-pro" if "sonar-pro" in os.getenv("PERPLEXITY_MODEL", "sonar") else "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are creating a GLOSSY MAGAZINE-STYLE travel guide with real-time web access.

CRITICAL REQUIREMENTS:
1. WEATHER: Provide specific daily weather forecasts with temperatures, conditions, and what to wear
2. ITINERARY: Create a detailed day-by-day schedule with specific times, locations, and activities
3. RESTAURANTS: Include full write-ups with ambiance descriptions, must-try dishes, chef backgrounds, reservation links
4. ATTRACTIONS: Detailed descriptions with insider tips, best photo spots, crowd avoidance strategies
5. EVENTS: Real events happening during the dates with ticket links and venue information
6. MAPS: Include specific addresses and cross-streets for everything
7. BOOKING: Provide direct booking URLs (OpenTable, Resy, Viator, museum websites)
8. LOCAL INSIGHTS: Hidden gems, local favorites, secret spots only insiders know
9. TRANSPORTATION: Specific routes, costs, apps to use, time estimates
10. NEIGHBORHOODS: Detailed area guides with character descriptions and what to find there

Format everything with rich descriptions, personal recommendations, and magazine-quality writing.
Include contact numbers, websites, and booking links for EVERYTHING.
Make it feel like a personalized concierge service, not a generic guide."""
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
                
                print(f"[DEBUG] Sending request to Perplexity API with {payload.get('max_tokens', 0)} max tokens")
                async with session.post(url, json=payload, headers=headers) as response:
                    print(f"[DEBUG] Perplexity API response status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        guide_content = data["choices"][0]["message"]["content"]
                        citations = data.get("citations", [])
                        print(f"[DEBUG] Received {len(guide_content)} characters from Perplexity")
                        
                        # Parse the guide content but preserve the richness
                        parsed_guide = await self._parse_rich_guide(guide_content)
                        parsed_guide["citations"] = citations
                        parsed_guide["raw_content"] = guide_content
                        
                        # Ensure weather is included
                        if "weather" not in parsed_guide or not parsed_guide["weather"]:
                            parsed_guide["weather"] = self._extract_weather_from_content(guide_content)
                        
                        # Ensure daily itinerary is included
                        if "daily_itinerary" not in parsed_guide or not parsed_guide["daily_itinerary"]:
                            parsed_guide["daily_itinerary"] = self._extract_itinerary_from_content(guide_content)
                        
                        return parsed_guide
                    else:
                        print(f"Perplexity API error: {response.status}")
                        return {
                            "error": f"Perplexity API error: {response.status}",
                            "summary": "",
                            "destination_insights": "",
                            "weather": {},
                            "daily_itinerary": [],
                            "restaurants": [],
                            "attractions": [],
                            "events": [],
                            "neighborhoods": [],
                            "practical_info": {},
                            "hidden_gems": [],
                            "citations": []
                        }
                        
        except Exception as e:
            print(f"[DEBUG] Error with Perplexity API: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "summary": "",
                "destination_insights": "",
                "weather": {},
                "daily_itinerary": [],
                "restaurants": [],
                "attractions": [],
                "events": [],
                "neighborhoods": [],
                "practical_info": {},
                "hidden_gems": [],
                "citations": []
            }
    
    async def _generate_with_openai(self, prompt: str, context: Dict) -> Dict:
        """Generate guide using OpenAI GPT-4"""
        
        if not self.openai_api_key:
            return {
                "error": "OpenAI API key not configured.",
                "summary": "",
                "destination_insights": "",
                "weather": {},
                "daily_itinerary": [],
                "restaurants": [],
                "attractions": [],
                "events": [],
                "neighborhoods": [],
                "practical_info": {},
                "hidden_gems": [],
                "citations": []
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                url = "https://api.openai.com/v1/chat/completions"
                
                payload = {
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert travel guide creator. Create detailed, personalized, and engaging travel guides that rival professional travel publications."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4000
                }
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        guide_content = data["choices"][0]["message"]["content"]
                        # Use LLM parser
                        parsed_guide = await self.llm_parser.parse_guide(guide_content)
                        parsed_guide["raw_content"] = guide_content
                        return parsed_guide
                    else:
                        print(f"OpenAI API error: {response.status}")
                        return {
                            "error": f"OpenAI API error: {response.status}",
                            "summary": "",
                            "destination_insights": "",
                            "weather": {},
                            "daily_itinerary": [],
                            "restaurants": [],
                            "attractions": [],
                            "events": [],
                            "neighborhoods": [],
                            "practical_info": {},
                            "hidden_gems": [],
                            "citations": []
                        }
                        
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            return {
                "error": str(e),
                "summary": "",
                "destination_insights": "",
                "weather": {},
                "daily_itinerary": [],
                "restaurants": [],
                "attractions": [],
                "events": [],
                "neighborhoods": [],
                "practical_info": {},
                "hidden_gems": [],
                "citations": []
            }
    
    def _parse_guide_content(self, content: str, citations: List) -> Dict:
        """Parse LLM response into structured guide format"""
        
        # Initialize guide structure
        guide = {
            "summary": "",
            "destination_insights": "",
            "weather": {},
            "daily_itinerary": [],
            "restaurants": [],
            "attractions": [],
            "events": [],
            "neighborhoods": [],
            "practical_info": {},
            "hidden_gems": [],
            "citations": citations,
            "raw_content": content
        }
        
        # Parse sections from the content
        sections = (content or "").split("\n## ")
        
        for section in sections:
            lines = section.split("\n")
            if not lines:
                continue
                
            first = lines[0] if lines else ""
            title = str(first or "").strip("#").strip().lower()
            content = "\n".join(lines[1:]).strip()
            
            if "summary" in title:
                guide["summary"] = content
            elif "insight" in title or "destination" in title:
                guide["destination_insights"] = content
            elif "itinerary" in title:
                guide["daily_itinerary"] = self._parse_itinerary(content)
            elif "dining" in title or "restaurant" in title:
                guide["restaurants"] = self._parse_restaurants(content)
            elif "cultural" in title or "entertainment" in title or "event" in title:
                guide["events"] = self._parse_events(content)
            elif "neighborhood" in title:
                guide["neighborhoods"] = self._parse_neighborhoods(content)
            elif "practical" in title:
                guide["practical_info"] = self._parse_practical_info(content)
            elif "hidden" in title or "secret" in title:
                guide["hidden_gems"] = self._parse_hidden_gems(content)
        
        return guide
    
    def _parse_itinerary(self, content: str) -> List[Dict]:
        """Parse daily itinerary from content"""
        days = []
        current_day = None
        
        for line in content.split("\n"):
            if line.startswith("### Day") or line.startswith("**Day"):
                if current_day:
                    days.append(current_day)
                current_day = {
                    "day": len(days) + 1,
                    "title": line.strip("#*").strip(),
                    "activities": []
                }
            elif current_day and line.strip():
                current_day["activities"].append(line.strip("- ").strip())
        
        if current_day:
            days.append(current_day)
        
        return days
    
    def _parse_restaurants(self, content: str) -> List[Dict]:
        """Parse restaurant recommendations from content"""
        restaurants = []
        current_restaurant = None
        
        for line in content.split("\n"):
            if line.startswith("### ") or line.startswith("**"):
                if current_restaurant:
                    restaurants.append(current_restaurant)
                current_restaurant = {
                    "name": line.strip("#*").strip(),
                    "description": "",
                    "details": []
                }
            elif current_restaurant:
                if line.strip():
                    if not current_restaurant["description"]:
                        current_restaurant["description"] = line.strip()
                    else:
                        current_restaurant["details"].append(line.strip("- ").strip())
        
        if current_restaurant:
            restaurants.append(current_restaurant)
        
        return restaurants
    
    def _parse_events(self, content: str) -> List[Dict]:
        """Parse events from content"""
        events = []
        for line in content.split("\n"):
            if line.strip() and not line.startswith("#"):
                events.append({"description": line.strip("- ").strip()})
        return events
    
    def _parse_neighborhoods(self, content: str) -> List[Dict]:
        """Parse neighborhood information"""
        neighborhoods = []
        current_area = None
        
        for line in content.split("\n"):
            if line.startswith("### ") or line.startswith("**"):
                if current_area:
                    neighborhoods.append(current_area)
                current_area = {
                    "name": line.strip("#*").strip(),
                    "description": "",
                    "highlights": []
                }
            elif current_area and line.strip():
                if not current_area["description"]:
                    current_area["description"] = line.strip()
                else:
                    current_area["highlights"].append(line.strip("- ").strip())
        
        if current_area:
            neighborhoods.append(current_area)
        
        return neighborhoods
    
    def _parse_practical_info(self, content: str) -> Dict:
        """Parse practical information"""
        info = {}
        current_category = "general"
        
        for line in content.split("\n"):
            if line.startswith("### ") or line.startswith("**"):
                current_category = (line or "").strip("#*").strip().lower()
                info[current_category] = []
            elif line.strip():
                if current_category not in info:
                    info[current_category] = []
                info[current_category].append(line.strip("- ").strip())
        
        return info
    
    def _parse_hidden_gems(self, content: str) -> List[Dict]:
        """Parse hidden gems and local secrets"""
        gems = []
        for line in content.split("\n"):
            if line.strip() and not line.startswith("#"):
                gems.append({"description": line.strip("- ").strip()})
        return gems
    
    async def _parse_rich_guide(self, content: str) -> Dict:
        """Parse guide content while preserving rich details"""
        # Use the LLM parser but with better preservation
        base_parse = await self.llm_parser.parse_guide(content)
        
        # Enhance with additional extraction
        sections = content.split("\n## ")
        
        for section in sections:
            section_lower = (section or "").lower()
            
            # Extract rich restaurant descriptions
            if "restaurant" in section_lower or "dining" in section_lower:
                base_parse["restaurant_writeups"] = section
            
            # Extract rich attraction descriptions  
            if "attraction" in section_lower or "must-see" in section_lower:
                base_parse["attraction_writeups"] = section
                
            # Extract neighborhoods
            if "neighborhood" in section_lower:
                base_parse["neighborhood_guide"] = section
                
            # Extract transportation
            if "transport" in section_lower or "getting around" in section_lower:
                base_parse["transportation_guide"] = section
        
        return base_parse
    
    def _detect_persona(self, preferences: Dict) -> Dict[str, str]:
        """Infer a persona label/style from preferences."""
        # Simple heuristic mapping
        cuisines = ", ".join(preferences.get("cuisineTypes", [])).lower()
        nightlife = preferences.get("nightlife", 2)
        walking = preferences.get("walkingTolerance", 3)
        pace = preferences.get("travelStyle", "balanced").lower()
        interests = ",".join(preferences.get("specialInterests", [])).lower()
        price = str(preferences.get("priceRange", "$$"))
        
        if "fine" in cuisines or price.count("$") >= 3 or "luxury" in interests:
            return {"label": "Luxury Epicurean", "style": "Conde Nast Traveler tone, refined and aspirational", "description": "High-end dining, design hotels, art and fashion, elevated experiences."}
        if "museums" in interests or "architecture" in interests:
            return {"label": "Culture Connoisseur", "style": "Sophisticated cultural editorial", "description": "Museums, galleries, historic districts, guided walks."}
        if nightlife >= 4:
            return {"label": "Nightlife Maven", "style": "Trendy, energetic, insider bar/club scene", "description": "Cocktail bars, live music, late-night eats, sleek venues."}
        if walking >= 4 and ("hiking" in interests or pace == "active"):
            return {"label": "Active Explorer", "style": "Adventurous, outdoorsy, energetic", "description": "Parks, waterfronts, scenic routes, active days."}
        if "family" in preferences.get("groupType", "").lower():
            return {"label": "Family Adventurer", "style": "Warm, practical, family-friendly", "description": "Kid-friendly museums, easy dining, logistics-first."}
        return {"label": "Balanced Traveler", "style": "Refined yet approachable editorial", "description": "Blend of iconic highlights and insider finds."}

    def _extract_weather_from_content(self, content: str) -> List[Dict]:
        """Extract weather information from content"""
        weather_data = []
        
        # Look for weather section
        weather_section = ""
        if "weather" in content.lower():
            parts = content.lower().split("weather")
            if len(parts) > 1:
                # Get the section after "weather"
                weather_section = parts[1].split("\n## ")[0] if "\n## " in parts[1] else parts[1][:1000]
                
                # Extract daily forecasts
                lines = weather_section.split("\n")
                for line in lines:
                    if any(day in line.lower() for day in ["day", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
                        weather_data.append({
                            "date": line.split(":")[0].strip() if ":" in line else "Day",
                            "conditions": line.split(":")[-1].strip() if ":" in line else line.strip(),
                            "temperature": "Check forecast"
                        })
        
        return weather_data[:7]  # Max 7 days
    
    def _extract_itinerary_from_content(self, content: str) -> List[Dict]:
        """Extract daily itinerary from content"""
        itinerary = []
        
        # Look for itinerary section
        if "itinerary" in content.lower() or "day 1" in content.lower():
            parts = content.split("\n")
            current_day = None
            current_activities = []
            
            for line in parts:
                # Check for day markers
                if any(f"day {i}" in (line or "").lower() for i in range(1, 10)):
                    # Save previous day if exists
                    if current_day:
                        itinerary.append({
                            "day": current_day,
                            "title": f"Day {current_day}",
                            "activities": current_activities
                        })
                    
                    # Start new day
                    current_day = len(itinerary) + 1
                    current_activities = []
                elif current_day and line.strip() and not line.startswith("#"):
                    # Add activity to current day
                    if line.strip().startswith("-") or line.strip().startswith("•"):
                        current_activities.append(line.strip("- •").strip())
                    elif ":" in line and any(time in (line or "").lower() for time in ["am", "pm", "morning", "afternoon", "evening"]):
                        current_activities.append(line.strip())
            
            # Add last day
            if current_day:
                itinerary.append({
                    "day": current_day,
                    "title": f"Day {current_day}",
                    "activities": current_activities
                })
        
        return itinerary
    
    async def _generate_with_real_searches(self, context: Dict, progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None) -> Dict:
        """Generate guide using real Perplexity searches - NO MOCKS"""
        
        try:
            if progress_callback:
                await progress_callback(5, "Preparing real-time searches")
            # Format dates for searches
            dates_dict = {
                "start": context["start_date"],
                "end": context["end_date"],
                "formatted": context["dates"]
            }
            
            # Run all searches in parallel for efficiency
            import asyncio
            
            # Get real weather
            if progress_callback:
                await progress_callback(5, "Fetching weather forecast")
            weather_task = self.weather_service.get_weather_forecast(
                context["destination"],
                context["start_date"],
                context["end_date"]
            )
            
            # Get real restaurants
            if progress_callback:
                await progress_callback(10, "Searching for top restaurants")
            restaurants_task = self.perplexity_search.search_restaurants(
                context["destination"],
                context["preferences"],
                dates_dict
            )
            
            # Get real attractions
            if progress_callback:
                await progress_callback(20, "Preparing attraction recommendations")
            attractions_task = self.perplexity_search.search_attractions(
                context["destination"],
                context["preferences"],
                dates_dict
            )
            
            # Get real events for the actual dates
            if progress_callback:
                await progress_callback(30, "Searching events")
            events_task = self.perplexity_search.search_events(
                context["destination"],
                context["start_date"],
                context["end_date"],
                context["preferences"]
            )
            
            # Get local insights
            if progress_callback:
                await progress_callback(35, "Fetching local insights")
            insights_task = self.perplexity_search.search_local_insights(
                context["destination"],
                dates_dict
            )
            
            # Execute all searches in parallel with error handling
            print(f"[GUIDE] 🚀 Starting parallel searches for {context.get('destination', 'unknown')}...")
            try:
                weather, restaurants, attractions, events, insights = await asyncio.gather(
                    weather_task,
                    restaurants_task,
                    attractions_task,
                    events_task,
                    insights_task,
                    return_exceptions=True
                )

                # Check for exceptions and log them
                if isinstance(attractions, Exception):
                    print(f"[GUIDE] ❌ Attractions search failed: {attractions}")
                    attractions = []
                else:
                    print(f"[GUIDE] ✅ Attractions search succeeded: {len(attractions)} items")

                if isinstance(restaurants, Exception):
                    print(f"[GUIDE] ❌ Restaurants search failed: {restaurants}")
                    restaurants = []
                else:
                    print(f"[GUIDE] ✅ Restaurants search succeeded: {len(restaurants)} items")

                if isinstance(events, Exception):
                    print(f"[GUIDE] ❌ Events search failed: {events}")
                    events = []
                else:
                    print(f"[GUIDE] ✅ Events search succeeded: {len(events)} items")

                if isinstance(weather, Exception):
                    print(f"[GUIDE] ❌ Weather search failed: {weather}")
                    weather = []
                else:
                    print(f"[GUIDE] ✅ Weather search succeeded: {len(weather) if isinstance(weather, list) else 'data available'}")

                if isinstance(insights, Exception):
                    print(f"[GUIDE] ❌ Insights search failed: {insights}")
                    insights = {}
                else:
                    print(f"[GUIDE] ✅ Insights search succeeded")

            except Exception as e:
                print(f"[GUIDE] ❌ Parallel execution failed: {e}")
                weather, restaurants, attractions, events, insights = [], [], [], [], {}
            
            # Enhance with Google Places data
            if progress_callback:
                await progress_callback(50, "Adding photos and booking links")
            
            # Enhance restaurants with photos and booking URLs
            if restaurants:
                restaurants = await self.places_enhancer.enhance_restaurants_batch(
                    restaurants, context["destination"]
                )
            
            # Enhance attractions with photos and details
            if attractions:
                attractions = await self.places_enhancer.enhance_attractions_batch(
                    attractions, context["destination"]
                )
            
            if progress_callback:
                await progress_callback(55, "Creating personalized daily itineraries")
            
            # Generate daily itineraries
            daily_itinerary = []
            previous_days = []
            
            start_date = datetime.strptime(context["start_date"], "%Y-%m-%d")
            for day_num in range(context["duration_days"]):
                current_date = start_date + timedelta(days=day_num)
                date_str = current_date.strftime("%Y-%m-%d")
                
                day_itinerary = await self.perplexity_search.search_daily_itinerary(
                    context["destination"],
                    day_num + 1,
                    date_str,
                    context["hotel_address"],
                    context["preferences"],
                    previous_days
                )
                
                daily_itinerary.append(day_itinerary)
                
                # Track what we've covered to avoid repetition
                if day_itinerary.get("morning"):
                    previous_days.extend([item for item in day_itinerary["morning"] if len(item) > 20][:2])
                if day_itinerary.get("afternoon"):
                    previous_days.extend([item for item in day_itinerary["afternoon"] if len(item) > 20][:2])
                if progress_callback:
                    pct = 55 + int(30 * (day_num + 1) / max(1, context["duration_days"]))
                    await progress_callback(min(pct, 85), f"Planning day {day_num + 1} itinerary")
            
            # Build the complete guide with real data
            # Ensure we have weather for all days
            weather_data = []
            weather_summary = {}
            if weather and not weather.get("error"):
                weather_data = weather.get("daily_forecasts", [])
                weather_summary = weather.get("summary", {})
                
                # Fill in missing days if needed
                days_needed = context["duration_days"]
                if len(weather_data) < days_needed:
                    print(f"[WARNING] Only {len(weather_data)} days of weather for {days_needed}-day trip")
                    # Add placeholder for missing days
                    for day in range(len(weather_data), days_needed):
                        weather_data.append({
                            "date": (datetime.strptime(context["start_date"], "%Y-%m-%d") + timedelta(days=day)).strftime("%Y-%m-%d"),
                            "conditions": "Check closer to date",
                            "temperature": {"high": "--", "low": "--"},
                            "description": "Weather forecast will be available closer to your travel date"
                        })
            elif insights.get("weather"):
                weather_data = insights.get("weather", [])
            
            guide = {
                "summary": f"Your personalized guide to {context['destination']} from {context['dates']}",
                "destination_insights": f"Real-time guide for {context['destination']} based on current information and your preferences: {context['preferences_summary']}",
                "weather": weather_data,
                "weather_summary": weather_summary,
                "daily_itinerary": daily_itinerary,
                "restaurants": restaurants,
                "attractions": attractions,
                "events": events,
                "neighborhoods": [],  # Can be enhanced with another search
                "practical_info": {
                    "transportation": insights.get("transportation", []),
                    "money": insights.get("money", []),
                    "cultural": insights.get("cultural", []),
                    "updates": insights.get("updates", []),
                    "tips": insights.get("tips", []),
                    "packing": weather_summary.get("packing_suggestions", []) if weather_summary else []
                },
                "hidden_gems": [],  # Can be enhanced with another search
                "citations": [],
                "generated_with": "real_perplexity_search",
                "timestamp": datetime.now().isoformat()
            }
            if progress_callback:
                await progress_callback(95, "Finalizing guide")

            # Log final guide summary
            print(f"[GUIDE] 🎉 GUIDE GENERATION COMPLETE!")
            print(f"[GUIDE] 📊 Final Guide Summary:")
            print(f"[GUIDE]   📍 Destination: {context['destination']}")
            print(f"[GUIDE]   📅 Dates: {context['dates']}")
            print(f"[GUIDE]   🍽️  Restaurants: {len(restaurants)}")
            print(f"[GUIDE]   🎭 Attractions: {len(attractions)}")
            print(f"[GUIDE]   🎪 Events: {len(events)}")
            print(f"[GUIDE]   📅 Itinerary days: {len(daily_itinerary)}")
            print(f"[GUIDE]   🌤️  Weather forecasts: {len(weather_data)}")
            print(f"[GUIDE]   ℹ️  Practical info sections: {len([k for k, v in guide['practical_info'].items() if v])}")

            # Log sample content
            if restaurants:
                print(f"[GUIDE]   🍽️  Sample restaurant: {restaurants[0].get('name', 'N/A')}")
            if attractions:
                print(f"[GUIDE]   🎭 Sample attraction: {attractions[0].get('name', 'N/A')}")
            if events:
                print(f"[GUIDE]   🎪 Sample event: {events[0].get('name', 'N/A')}")

            return guide
            
        except Exception as e:
            print(f"Error generating real guide: {e}")
            return {
                "error": str(e),
                "message": "Failed to generate guide with real data. Check API configuration."
            }
    
    # Removed mock generation methods - we only use real data now
    
    async def _enhance_with_realtime_data(self, guide: Dict, context: Dict) -> Dict:
        """Enhance guide with real-time data from various sources"""
        
        # This would integrate with real APIs for:
        # - Current weather from weather services
        # - Event listings from Ticketmaster, Eventbrite
        # - Restaurant availability from OpenTable
        # - Current exhibitions from museum APIs
        # - Local news from news APIs
        
        # For now, return the guide as-is
        return guide