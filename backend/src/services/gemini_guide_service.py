"""
Gemini Magazine-Quality Guide Service

Generates world-class travel guides using Google Gemini 2.0 with magazine-quality writing.
This service creates guides that read like features in Condé Nast Traveler or Travel + Leisure.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from src.gpt_providers.gemini_gpt import GeminiGPT
from src.services.weather_service import WeatherService
from src.services.google_places_service import GooglePlacesService


class GeminiGuideService:
    """Generate magazine-quality travel guides using Gemini 2.0."""

    def __init__(self):
        """Initialize the Gemini guide service."""
        # Initialize Gemini
        self.gemini = GeminiGPT(model="gemini-2.0-flash-exp")

        # Initialize supporting services
        self.weather_service = WeatherService()
        self.places_service = GooglePlacesService()

        # Load magazine-quality prompts
        self.prompts = self._load_magazine_prompts()

        print("[GeminiGuide] Service initialized with Gemini 2.0")

    def _load_magazine_prompts(self) -> Dict[str, Any]:
        """Load magazine-quality prompt templates."""
        try:
            prompts_path = Path(__file__).parent.parent / "prompts_magazine.json"
            with open(prompts_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Could not load magazine prompts: {e}")
            return self._default_magazine_prompts()

    def _default_magazine_prompts(self) -> Dict[str, Any]:
        """Fallback prompts if file can't be loaded."""
        return {
            "editorial_system": {
                "base": "You are a world-class travel editor and writer for a prestigious magazine like Condé Nast Traveler."
            },
            "travel_guide_magazine": {
                "master_prompt_template": "Create an exceptional travel guide for {destination}.",
                "sections": {}
            }
        }

    def _detect_persona(self, preferences: Dict) -> Dict[str, str]:
        """Detect traveler persona from preferences."""
        food_score = preferences.get('food', 0)
        culture_score = preferences.get('culture', 0)
        adventure_score = preferences.get('adventure', 0)
        luxury_score = preferences.get('luxury', 0)

        # Determine primary persona
        if luxury_score > 7 and food_score > 7:
            persona = "luxury_epicurean"
            description = "Discerning traveler who appreciates culinary excellence, refined service, and exclusive experiences"
            style = "Sophisticated, with emphasis on Michelin-starred dining and luxury hospitality"
        elif culture_score > 7:
            persona = "culture_connoisseur"
            description = "Intellectually curious traveler drawn to art, history, and cultural immersion"
            style = "Educated and appreciative, with art historical and architectural context"
        elif adventure_score > 7:
            persona = "adventure_seeker"
            description = "Intrepid explorer seeking authentic experiences and off-the-beaten-path discoveries"
            style = "Energetic and experiential, focusing on active engagement and local immersion"
        elif preferences.get('romance', 0) > 7:
            persona = "romantic_escape"
            description = "Couple seeking intimate moments, atmospheric settings, and memorable experiences"
            style = "Sensory and atmospheric, emphasizing ambiance and special moments"
        else:
            persona = "sophisticated_traveler"
            description = "Well-traveled individual seeking quality experiences across dining, culture, and exploration"
            style = "Balanced and refined, appreciating both iconic attractions and hidden gems"

        return {
            "persona": persona,
            "description": description,
            "style": style
        }

    def _build_context(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        extracted_data: Dict
    ) -> Dict[str, Any]:
        """Build comprehensive context for guide generation."""
        # Parse dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        duration = (end - start).days

        # Detect persona
        persona_info = self._detect_persona(preferences)

        # Build preferences summary
        pref_items = []
        for key, value in preferences.items():
            if value > 5:
                pref_items.append(f"{key} (interest level: {value}/10)")
        preferences_summary = ", ".join(pref_items) if pref_items else "General travel interests"

        # Determine budget level
        luxury_score = preferences.get('luxury', 5)
        if luxury_score >= 8:
            budget_level = "Luxury/Premium (no budget constraints)"
        elif luxury_score >= 6:
            budget_level = "Upscale (quality-focused with flexibility)"
        elif luxury_score >= 4:
            budget_level = "Mid-range (value-conscious but willing to splurge)"
        else:
            budget_level = "Budget-savvy (cost-conscious)"

        # Determine pace and walking level
        pace = extracted_data.get('pace', 'moderate')
        walking_level = preferences.get('walking', 5)

        # Group type
        group_type = extracted_data.get('group_type', 'solo/couple')

        return {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "duration": duration,
            "month_year": start.strftime("%B %Y"),
            "dates": f"{start.strftime('%B %d')} - {end.strftime('%d, %Y')}",
            "hotel_info": hotel_info,
            "preferences": preferences,
            "preferences_summary": preferences_summary,
            "persona": persona_info["persona"],
            "persona_description": persona_info["description"],
            "persona_style": persona_info["style"],
            "budget_level": budget_level,
            "pace": pace,
            "walking_level": walking_level,
            "group_type": group_type,
            "extracted_data": extracted_data
        }

    async def generate_magazine_guide(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        extracted_data: Dict,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a magazine-quality travel guide using Gemini 2.0.

        This creates guides with:
        - Evocative, literary writing style
        - Rich cultural and historical context
        - Specific, actionable recommendations
        - Insider tips and hidden gems
        - Magazine-quality narrative flow

        Args:
            destination: City/region name
            start_date: ISO format start date
            end_date: ISO format end date
            hotel_info: Hotel/accommodation details
            preferences: User preferences dict
            extracted_data: Additional extracted information
            progress_callback: Optional callback for progress updates

        Returns:
            Dict containing the complete magazine-quality guide
        """
        start_time = datetime.now()

        try:
            # Build context
            if progress_callback:
                await progress_callback(5, "Analyzing traveler profile and preferences")

            context = self._build_context(
                destination, start_date, end_date,
                hotel_info, preferences, extracted_data
            )

            # Get weather forecast
            if progress_callback:
                await progress_callback(10, "Fetching real-time weather forecast")

            weather_data = await self.weather_service.get_weather_forecast(
                destination, start_date, end_date
            )

            # Build the master prompt using magazine templates
            if progress_callback:
                await progress_callback(15, "Crafting personalized editorial prompt")

            master_prompt = self._construct_magazine_prompt(context)

            # Generate the guide using Gemini
            if progress_callback:
                await progress_callback(25, "Generating magazine-quality guide with Gemini 3 Pro")

            system_prompt = self._build_system_prompt(context)

            # Call Gemini 3 with optimized parameters for creative writing
            # Note: Gemini 3 is less verbose by default, so we use higher temperature
            # and explicit prompting for creative, literary style
            result = await self.gemini.generate_text_async(
                prompt=master_prompt,
                system=system_prompt,
                temperature=0.95,  # Higher for Gemini 3 to encourage creative, verbose output
                max_tokens=16384  # Gemini 3 supports up to 64K, using 16K for guides
            )

            if "error" in result:
                return {
                    "error": "Failed to generate guide with Gemini",
                    "message": result.get("error", "Unknown error"),
                    "generated_with": "gemini-2.0-flash-exp (failed)"
                }

            guide_content = result["content"]

            if progress_callback:
                await progress_callback(70, "Parsing and structuring guide content")

            # Parse the guide into structured format
            parsed_guide = await self._parse_magazine_guide(guide_content, context)

            # Enrich with Google Places photos
            if progress_callback:
                await progress_callback(80, "Enriching with photos and location data")

            await self._enrich_with_places_data(parsed_guide, destination)

            # Add weather data
            if weather_data and not weather_data.get("error"):
                parsed_guide["weather"] = weather_data.get("daily_forecasts", [])
                parsed_guide["weather_summary"] = weather_data.get("summary", {})

            # Add metadata
            end_time = datetime.now()
            parsed_guide["raw_content"] = guide_content
            parsed_guide["generated_with"] = "gemini-2.0-flash-exp"
            parsed_guide["generated_at"] = datetime.now().isoformat()
            parsed_guide["generation_time_seconds"] = (end_time - start_time).total_seconds()
            parsed_guide["validation_passed"] = True
            parsed_guide["quality_level"] = "magazine"

            if progress_callback:
                await progress_callback(100, "Magazine-quality guide complete")

            print(f"[GeminiGuide] Generated {len(guide_content)} chars in {parsed_guide['generation_time_seconds']:.1f}s")

            return parsed_guide

        except Exception as e:
            print(f"[ERROR] Gemini guide generation failed: {str(e)}")
            import traceback
            traceback.print_exc()

            return {
                "error": "Guide generation failed",
                "message": str(e),
                "generated_with": "gemini-2.0-flash-exp (error)"
            }

    def _build_system_prompt(self, context: Dict) -> str:
        """Build the system prompt with editorial guidelines optimized for Gemini 3."""
        base = self.prompts["editorial_system"]["base"]

        # CRITICAL for Gemini 3: Explicitly request verbose, creative output
        # Gemini 3 is less verbose by default and prefers direct answers
        gemini3_instructions = """

**CRITICAL INSTRUCTIONS FOR GEMINI 3:**
You MUST write in a verbose, creative, literary style for this travel guide.
DO NOT be concise or direct - this is a magazine feature, not a factual report.
EXPAND on every detail with rich, evocative language and sensory descriptions.
WRITE LONG, engaging paragraphs that transport the reader to the destination.
INCLUDE specific cultural context, historical anecdotes, and insider knowledge.
AIM FOR MAXIMUM DETAIL - restaurant write-ups should be 150-200 words each.
This is premium content for a luxury travel magazine - be expansive and literary."""

        guidelines = "\n\n**STYLE GUIDELINES:**\n" + "\n".join(
            f"- {g}" for g in self.prompts["editorial_system"]["style_guidelines"]
        )

        standards = "\n\n**QUALITY STANDARDS:**\n" + "\n".join(
            f"- {s}" for s in self.prompts["editorial_system"]["quality_standards"]
        )

        persona_voice = ""
        persona = context.get("persona", "sophisticated_traveler")
        if persona in self.prompts.get("persona_voices", {}):
            voice = self.prompts["persona_voices"][persona]
            persona_voice = f"\n\n**VOICE FOR THIS TRAVELER:**\nTone: {voice['tone']}\nPriorities: {voice['priorities']}\nLanguage: {voice['language']}"

        return base + gemini3_instructions + guidelines + standards + persona_voice

    def _construct_magazine_prompt(self, context: Dict) -> str:
        """Construct the comprehensive magazine-style prompt."""
        # Get master template
        template = self.prompts["travel_guide_magazine"]["master_prompt_template"]
        master = template.format(**context)

        # Add section-specific prompts
        sections = self.prompts["travel_guide_magazine"]["sections"]

        section_prompts = []

        # Opening
        if "opening" in sections:
            section_prompts.append(f"\n\n## OPENING\n{sections['opening']['prompt'].format(**context)}")

        # Destination insights
        if "destination_insights" in sections:
            section_prompts.append(f"\n\n## DESTINATION INSIGHTS\n{sections['destination_insights']['prompt'].format(**context)}")

        # Weather & packing
        if "weather_packing" in sections:
            section_prompts.append(f"\n\n## WEATHER & PACKING\n{sections['weather_packing']['prompt'].format(**context)}")

        # Daily itinerary
        if "daily_itinerary" in sections:
            section_prompts.append(f"\n\n## DAILY ITINERARY\n{sections['daily_itinerary']['prompt'].format(**context)}")

        # Restaurants
        if "restaurant_guide" in sections:
            section_prompts.append(f"\n\n## RESTAURANT GUIDE\n{sections['restaurant_guide']['prompt'].format(**context)}")

        # Attractions
        if "attractions_experiences" in sections:
            section_prompts.append(f"\n\n## ATTRACTIONS & EXPERIENCES\n{sections['attractions_experiences']['prompt'].format(**context)}")

        # Events
        if "events_whats_on" in sections:
            section_prompts.append(f"\n\n## WHAT'S ON (EVENTS)\n{sections['events_whats_on']['prompt'].format(**context)}")

        # Hidden gems
        if "hidden_gems" in sections:
            section_prompts.append(f"\n\n## HIDDEN GEMS\n{sections['hidden_gems']['prompt'].format(**context)}")

        # Practical info
        if "practical_wisdom" in sections:
            section_prompts.append(f"\n\n## PRACTICAL WISDOM\n{sections['practical_wisdom']['prompt'].format(**context)}")

        # Closing
        if "closing" in sections:
            section_prompts.append(f"\n\n## CLOSING\n{sections['closing']['prompt'].format(**context)}")

        return master + "".join(section_prompts)

    async def _parse_magazine_guide(self, content: str, context: Dict) -> Dict[str, Any]:
        """Parse the magazine guide into structured format using Gemini."""

        parsing_prompt = f"""Parse this magazine-style travel guide into structured JSON format.

GUIDE CONTENT:
{content}

Extract and structure the following:

1. **summary**: Opening 2-3 paragraphs (the compelling introduction)
2. **destination_insights**: The destination context and neighborhood descriptions
3. **daily_itinerary**: Array of daily plans with this structure:
   - day: number
   - title: day name/theme
   - date: date string
   - morning: description of morning activities with times
   - afternoon: description of afternoon activities
   - evening: description of evening activities
   - highlights: array of key experiences for the day

4. **restaurants**: Array of restaurants with:
   - name, cuisine, address, price_range ($-$$$$)
   - description (the magazine write-up)
   - chef_info, signature_dishes
   - phone, website, reservations
   - insider_tip

5. **attractions**: Array with:
   - name, type, address
   - description (the narrative)
   - best_time_to_visit, time_needed
   - hours, price
   - insider_tip, photo_spots
   - website

6. **events**: Array of current events with:
   - name, type, date, time
   - venue, address
   - description, price
   - booking_link

7. **hidden_gems**: Array with:
   - name, description, location, why_special

8. **practical_info**: Object with:
   - transportation: array of tips
   - money: array of tips
   - cultural: array of etiquette and norms
   - safety: array of safety info
   - tips: array of general tips

9. **packing_list**: Array of packing recommendations
10. **closing**: Final paragraphs

Return ONLY valid JSON, no markdown formatting."""

        try:
            result = await self.gemini.generate_json(
                prompt=parsing_prompt,
                system="You are a precise data parser. Extract information accurately and return valid JSON only."
            )

            if "error" in result:
                print(f"[WARN] JSON parsing failed, returning raw content")
                return {
                    "summary": content[:500],
                    "raw_content": content,
                    "parsing_note": "Could not parse into structured format"
                }

            return result

        except Exception as e:
            print(f"[ERROR] Parsing failed: {e}")
            return {
                "summary": content[:500],
                "raw_content": content,
                "parsing_error": str(e)
            }

    async def _enrich_with_places_data(self, guide: Dict, destination: str):
        """Enrich guide with Google Places photos and data."""
        try:
            # Enrich restaurants with photos
            if "restaurants" in guide and isinstance(guide["restaurants"], list):
                for restaurant in guide["restaurants"][:10]:  # Limit to avoid quota issues
                    name = restaurant.get("name", "")
                    if name:
                        place_data = await self.places_service.search_place(
                            f"{name} restaurant {destination}"
                        )
                        if place_data and not place_data.get("error"):
                            restaurant["main_photo"] = place_data.get("photo_url", "")
                            restaurant["rating"] = place_data.get("rating", 0)
                            restaurant["google_maps_url"] = place_data.get("maps_url", "")
                            if not restaurant.get("address"):
                                restaurant["address"] = place_data.get("address", "")

            # Enrich attractions with photos
            if "attractions" in guide and isinstance(guide["attractions"], list):
                for attraction in guide["attractions"][:10]:
                    name = attraction.get("name", "")
                    if name:
                        place_data = await self.places_service.search_place(
                            f"{name} {destination}"
                        )
                        if place_data and not place_data.get("error"):
                            attraction["main_photo"] = place_data.get("photo_url", "")
                            attraction["rating"] = place_data.get("rating", 0)
                            attraction["google_maps_url"] = place_data.get("maps_url", "")
                            if not attraction.get("address"):
                                attraction["address"] = place_data.get("address", "")

            print(f"[GeminiGuide] Enriched guide with Google Places data")

        except Exception as e:
            print(f"[WARN] Could not enrich with Places data: {e}")
            # Non-fatal, continue without photos
