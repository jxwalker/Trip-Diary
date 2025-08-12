"""
Enhanced Travel Guide Service
Uses advanced LLM prompting to create magazine-quality travel guides
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable
from pathlib import Path
import aiohttp
from dotenv import load_dotenv
from pathlib import Path
from .guide_parser import GuideParser
from .llm_parser import LLMParser
from .perplexity_search_service import PerplexitySearchService

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(env_path)

class EnhancedGuideService:
    def __init__(self):
        # Initialize parsers
        self.parser = GuideParser()
        self.llm_parser = LLMParser()
        self.perplexity_search = PerplexitySearchService()
        
        # Load prompts configuration
        prompts_path = Path(__file__).parent.parent / "prompts.json"
        with open(prompts_path, 'r') as f:
            self.prompts = json.load(f)
        
        # API configurations
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
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
                await progress_callback(35, "Querying Perplexity")
            guide = await self._generate_with_perplexity(prompt, context)
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
            "preferred_times": self._format_preferred_times(preferences.get("preferredTimes", {}))
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
        
        # Get base prompt
        base = self.prompts["travel_guide"]["base_prompt"]
        
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
        master_prompt = f"{base}\n\n" + "\n\n".join(components)
        
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
                            "content": """You are an expert travel guide creator with real-time web access. 
Create detailed, personalized guides with:
- Current restaurant recommendations with recent reviews
- Real-time events, exhibitions, and shows happening during the travel dates
- Current weather forecasts
- Up-to-date museum/gallery exhibitions
- Local transportation tips and costs
- Neighborhood recommendations based on preferences
IMPORTANT: Use actual current information from the web, not generic recommendations."""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        guide_content = data["choices"][0]["message"]["content"]
                        citations = data.get("citations", [])
                        
                        # Use LLM parser for better extraction
                        parsed_guide = await self.llm_parser.parse_guide(guide_content)
                        parsed_guide["citations"] = citations
                        parsed_guide["raw_content"] = guide_content
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
            print(f"Error with Perplexity API: {e}")
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
        sections = content.split("\n## ")
        
        for section in sections:
            lines = section.split("\n")
            if not lines:
                continue
                
            title = lines[0].strip("#").strip().lower()
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
                current_category = line.strip("#*").strip().lower()
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
            
            # Get real restaurants
            if progress_callback:
                await progress_callback(10, "Preparing restaurant recommendations")
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
            
            # Execute all searches in parallel
            restaurants, attractions, events, insights = await asyncio.gather(
                restaurants_task,
                attractions_task,
                events_task,
                insights_task
            )
            if progress_callback:
                await progress_callback(55, "Assembling daily itineraries")
            
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
            guide = {
                "summary": f"Your personalized guide to {context['destination']} from {context['dates']}",
                "destination_insights": f"Real-time guide for {context['destination']} based on current information and your preferences: {context['preferences_summary']}",
                "weather": insights.get("weather", []),
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
                    "tips": insights.get("tips", [])
                },
                "hidden_gems": [],  # Can be enhanced with another search
                "citations": [],
                "generated_with": "real_perplexity_search",
                "timestamp": datetime.now().isoformat()
            }
            if progress_callback:
                await progress_callback(95, "Finalizing guide")
            
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