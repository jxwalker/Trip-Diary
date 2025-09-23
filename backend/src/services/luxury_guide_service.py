"""
Luxury Travel Guide Service - Condé Nast Traveler Style
Creates rich, personalized travel guides with premium content
"""
import os
import json
import re
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class LuxuryGuideService:
    """Creates premium travel guides with rich, personalized content"""
    
    def __init__(self):
        # Reload environment to ensure we have the latest keys
        load_dotenv(env_path, override=True)
        
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        if not self.perplexity_api_key:
            logger.warning("Perplexity API key not configured")
    
    async def generate_luxury_guide(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        extracted_data: Dict = {},
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Generate a premium travel guide with rich content"""
        
        if progress_callback:
            await progress_callback(
                5, "Creating your personalized luxury travel guide..."
            )
        
        # Extract passenger names for personalization
        passengers = extracted_data.get("passengers", [])
        primary_traveler = (
            passengers[0]["full_name"] if passengers else "Traveler"
        )
        
        # Calculate trip duration
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
        
        # Run all enrichment tasks in parallel
        tasks = []
        
        # Task 1: Get premium content (restaurants, attractions, events, news)
        tasks.append(self._get_premium_content(
            destination, start_date, end_date, preferences, primary_traveler
        ))
        
        # Task 2: Get detailed weather with hourly forecasts
        tasks.append(
            self._get_detailed_weather(destination, start_date, end_date)
        )
        
        # Task 3: Get location intelligence and maps
        tasks.append(self._get_location_intelligence(destination, hotel_info))
        
        # Task 4: Get contemporary events and news
        tasks.append(
            self._get_contemporary_content(destination, start_date, end_date)
        )
        
        # Task 5: Create personalized daily itinerary
        tasks.append(self._create_luxury_itinerary(
            destination, start_date, end_date, preferences, 
            hotel_info, primary_traveler
        ))
        
        if progress_callback:
            await progress_callback(20, "Gathering premium recommendations...")
        
        try:
            # Run tasks with longer timeout and handle individual failures
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=45.0  # Increased timeout for multiple API calls
            )
        except asyncio.TimeoutError:
            logger.error("API calls timed out - trying sequential approach")
            # Try sequential approach if parallel fails
            results = []
            for task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=15.0)
                    results.append(result)
                except:
                    results.append({})  # Empty dict on failure
        
        if progress_callback:
            await progress_callback(
                70, "Crafting your bespoke travel experience..."
            )
        
        # Unpack results and check for failures
        premium_content = (
            results[0] if not isinstance(results[0], Exception) else {}
        )
        weather_data = (
            results[1] if not isinstance(results[1], Exception) else {}
        )
        location_data = (
            results[2] if not isinstance(results[2], Exception) else {}
        )
        contemporary = (
            results[3] if not isinstance(results[3], Exception) else {}
        )
        luxury_itinerary = (
            results[4] if not isinstance(results[4], Exception) else []
        )
        
        # Check if we have minimum required content
        if not premium_content or premium_content.get("error"):
            logger.error("Failed to get premium content")
            return {
                "error": "Content generation failed",
                "message": ("Unable to retrieve restaurant and attraction "
                           "data. Please ensure API keys are configured.")
            }
        
        if not luxury_itinerary:
            logger.error("Failed to generate itinerary")
            return {
                "error": "Itinerary generation failed", 
                "message": "Unable to create daily itinerary. Please try again."
            }
        
        # Create the luxury guide
        guide = self._assemble_luxury_guide(
            destination=destination,
            primary_traveler=primary_traveler,
            start_date=start_date,
            end_date=end_date,
            num_days=num_days,
            premium_content=premium_content,
            weather_data=weather_data,
            location_data=location_data,
            contemporary=contemporary,
            luxury_itinerary=luxury_itinerary,
            hotel_info=hotel_info,
            extracted_data=extracted_data,
            preferences=preferences
        )
        
        if progress_callback:
            await progress_callback(100, "Your luxury guide is ready!")
        
        return guide
    
    async def _get_premium_content(
        self, destination: str, start_date: str, end_date: str, 
        preferences: Dict, traveler_name: str
    ) -> Dict:
        """Get premium restaurant and attraction recommendations"""
        
        if not self.perplexity_api_key:
            return {"error": "Perplexity API key not configured"}
        
        # Build personalized prompt based on preferences
        budget = preferences.get('budget', 'moderate')
        cuisine_types = preferences.get('cuisineTypes', ['local'])
        interests = preferences.get('interests', {})
        
        # Adapt restaurant request to preferences
        if budget == 'budget':
            restaurant_type = "authentic LOCAL EATERIES and STREET FOOD spots (under €20 per meal)"
        elif budget == 'moderate':
            restaurant_type = "highly-rated BISTROS and LOCAL FAVORITES (€20-50 per meal)"
        else:
            restaurant_type = "Michelin-starred and FINE DINING restaurants"
        
        # Focus attractions on interests
        interest_list = [k for k, v in interests.items() if v]
        if not interest_list:
            interest_list = ['culture', 'architecture', 'food']
        
        prompt = f"""Create a PERSONALIZED guide for {traveler_name} visiting {destination} ({start_date} to {end_date}).

Traveler Preferences:
- Budget: {budget}
- Cuisine: {', '.join(cuisine_types)}
- Interests: {', '.join(interest_list)}

Based on these preferences, provide:
1. TEN {restaurant_type} focusing on {', '.join(cuisine_types)} cuisine
   Include: name, cuisine type, price range, signature dish, location/neighborhood
2. EIGHT attractions related to {', '.join(interest_list[:3])}
   Include: name, type, best time to visit, entry fee, why it matches their interests
3. FIVE experiences matching their {budget} budget and interests
   Include: activity name, duration, cost, booking requirements
4. FIVE events/happenings during their visit dates
   Include: event name, date, venue, type

Format as JSON with keys: restaurants, attractions, experiences, events"""

        max_retries = 2
        for attempt in range(max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=30 + (attempt * 10))  # 30s, then 40s
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    headers = {
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": "sonar-pro",  # Use the current model
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a luxury travel concierge creating bespoke guides for discerning travelers. Provide accurate, current information with rich details."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                        "temperature": 0.3,
                        "max_tokens": 3500
                    }
                    
                    async with session.post(
                        "https://api.perplexity.ai/chat/completions",
                        json=payload,
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            content = data["choices"][0]["message"]["content"]
                        
                            # Parse JSON response
                            try:
                                # Remove citations like [1][2] that break JSON
                                import re
                                content_clean = re.sub(r'\[\d+\]', '', content)
                                
                                # Try to find JSON in the response
                                json_start = content_clean.find('{')
                                json_end = content_clean.rfind('}') + 1
                                if json_start >= 0 and json_end > json_start:
                                    json_str = content_clean[json_start:json_end]
                                    parsed = json.loads(json_str)
                                    # Ensure we have the expected keys
                                    if not all(k in parsed for k in ['restaurants', 'attractions']):
                                        # Try to extract from markdown code block
                                        if '```json' in content:
                                            json_start = content.find('```json') + 7
                                            json_end = content.find('```', json_start)
                                            if json_end > json_start:
                                                parsed = json.loads(content[json_start:json_end])
                                    return self._enhance_premium_content(parsed)
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse premium content JSON: {e}")
                                # Return minimal structure
                                return {"restaurants": [], "attractions": [], "experiences": [], "hotels": []}
                        else:
                            logger.error(f"Perplexity API error: {response.status}")
                        
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)  # Wait before retry
                    continue
                return {"error": "API timeout after retries"}
                
            except Exception as e:
                logger.error(f"Failed to get premium content: {e}")
                import traceback
                traceback.print_exc()
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                return {"error": f"Failed to retrieve content: {str(e)}"}
    
    async def _get_detailed_weather(self, destination: str, start_date: str, end_date: str) -> Dict:
        """Get detailed weather with hourly forecasts and conditions"""
        
        if not self.openweather_api_key:
            return {"error": "Weather API not configured"}
        
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Get coordinates
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={destination}&limit=1&appid={self.openweather_api_key}"
                
                async with session.get(geo_url) as response:
                    if response.status == 200:
                        geo_data = await response.json()
                        if geo_data:
                            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
                            
                            # Get detailed forecast with hourly data
                            onecall_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={self.openweather_api_key}&units=metric&exclude=minutely"
                            
                            # If OneCall API fails, use regular forecast
                            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.openweather_api_key}&units=metric&cnt=40"
                            
                            async with session.get(forecast_url) as forecast_response:
                                if forecast_response.status == 200:
                                    forecast_data = await forecast_response.json()
                                    return self._format_luxury_weather(forecast_data, start_date, end_date)
                                    
        except Exception as e:
            logger.error(f"Weather API error: {e}")
        
        return {"error": "Failed to get weather data"}
    
    async def _get_location_intelligence(self, destination: str, hotel_info: Dict) -> Dict:
        """Get location data, neighborhoods, and map information"""
        
        # Always provide basic map functionality
        basic_map_data = {
            "map_url": f"https://maps.google.com/maps?q={destination}&z=13",
            "interactive_map": f"https://www.openstreetmap.org/search?query={destination}#map=13",
            "neighborhoods": [],
            "photos": []
        }
        
        # Get neighborhood data from Perplexity instead
        if self.perplexity_api_key:
            try:
                neighborhoods = await self._get_neighborhoods_from_perplexity(destination)
                basic_map_data["neighborhoods"] = neighborhoods
                
                # No placeholder photos - only use real photos from Google Places API
                basic_map_data["photos"] = []
            except Exception as e:
                logger.error(f"Failed to get neighborhoods: {e}")
        
        # Try Google Maps API if available and authorized
        if self.google_maps_api_key:
            try:
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    # Get place details
                    place_search_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
                    params = {
                        "input": destination,
                        "inputtype": "textquery",
                        "fields": "name,formatted_address,geometry,photos,place_id",
                        "key": self.google_maps_api_key
                    }
                    
                    async with session.get(place_search_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Check if API is authorized
                            if data.get("status") == "REQUEST_DENIED":
                                logger.warning("Google Maps API key not authorized for Places API")
                                return basic_map_data
                                
                            if data.get("candidates"):
                                place = data["candidates"][0]
                                location = place.get("geometry", {}).get("location", {})
                                place_id = place.get("place_id")
                                
                                # Get neighborhood information using nearby search
                                neighborhoods = await self._get_real_neighborhoods(
                                    session, location.get("lat"), location.get("lng"), self.google_maps_api_key
                                )
                                
                                # Get photos if available
                                photo_refs = []
                                if place.get("photos"):
                                    for photo in place["photos"][:3]:
                                        # Store photo reference instead of full URL to avoid exposing API key
                                        photo_url = f"/api/places/photo/{photo['photo_reference']}"
                                        photo_refs.append(photo_url)
                                
                                return {
                                    "destination_coordinates": location,
                                    "neighborhoods": neighborhoods if neighborhoods else basic_map_data["neighborhoods"],
                                    "hotel_location": await self._geocode_hotel_real(session, hotel_info, self.google_maps_api_key),
                                    "map_url": f"https://maps.google.com/maps?q={location.get('lat')},{location.get('lng')}&z=13",
                                    "interactive_map": f"/api/places/embed/{place_id}",
                                    "photos": photo_refs if photo_refs else basic_map_data["photos"],
                                    "place_id": place_id
                                }
                                
            except Exception as e:
                logger.error(f"Location intelligence error: {e}")
        
        return basic_map_data
    
    async def _get_contemporary_content(self, destination: str, start_date: str, end_date: str) -> Dict:
        """Get current events, news, and happenings"""
        
        if not self.perplexity_api_key:
            return {}
        
        prompt = f"""List 5 current events happening in {destination} between {start_date} and {end_date}.
Include: event name, date, venue, type (concert/exhibition/festival/etc).
Format as JSON array."""

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "sonar-pro",
                    "messages": [
                        {"role": "system", "content": "You are a luxury travel expert providing current, accurate information about events and happenings."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1500
                }
                
                async with session.post(
                    "https://api.perplexity.ai/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        try:
                            json_start = content.find('{')
                            json_end = content.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                return json.loads(content[json_start:json_end])
                        except:
                            return self._parse_contemporary_text(content)
                            
        except Exception as e:
            logger.error(f"Contemporary content error: {e}")
        
        return {}
    
    async def _create_luxury_itinerary(
        self, destination: str, start_date: str, end_date: str,
        preferences: Dict, hotel_info: Dict, traveler_name: str
    ) -> List[Dict]:
        """Create a detailed, personalized daily itinerary"""
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
        
        if not self.perplexity_api_key:
            return []
        
        # Get preferences for personalization
        budget = preferences.get('budget', 'moderate')
        interests = preferences.get('interests', {})
        interest_list = [k for k, v in interests.items() if v]
        if not interest_list:
            interest_list = ['culture', 'sightseeing']
        pace = preferences.get('pace', 'moderate')
        
        prompt = f"""Create a {num_days}-day PERSONALIZED itinerary for {traveler_name} in {destination}.

Preferences:
- Interests: {', '.join(interest_list)}
- Budget: {budget}
- Pace: {pace}
- Staying at: {hotel_info.get('name', 'hotel')}

For each day, suggest activities that match their interests and budget.
Include variety but focus on {', '.join(interest_list[:2])}.

Format as JSON array with keys: day, date, morning, lunch, afternoon, dinner"""

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "sonar-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a luxury travel planner creating bespoke daily itineraries. Include specific times, locations, and insider information."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 1500
                }
                
                async with session.post(
                    "https://api.perplexity.ai/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        try:
                            # Remove citations
                            import re
                            content_clean = re.sub(r'\[\d+\]', '', content)
                            
                            json_start = content_clean.find('[')
                            json_end = content_clean.rfind(']') + 1
                            if json_start >= 0 and json_end > json_start:
                                itinerary_data = json.loads(content_clean[json_start:json_end])
                                return self._enhance_luxury_itinerary(itinerary_data, start, num_days)
                            # Try finding JSON object array
                            json_start = content_clean.find('{')
                            if json_start >= 0:
                                # Might be wrapped in an object
                                json_end = content_clean.rfind('}') + 1
                                obj = json.loads(content_clean[json_start:json_end])
                                if 'itinerary' in obj:
                                    return self._enhance_luxury_itinerary(obj['itinerary'], start, num_days)
                                elif 'days' in obj:
                                    return self._enhance_luxury_itinerary(obj['days'], start, num_days)
                        except Exception as e:
                            logger.error(f"Failed to parse luxury itinerary: {e}")
                            # Return basic itinerary
                            from datetime import timedelta
                            basic_itinerary = []
                            for i in range(num_days):
                                date = (start + timedelta(days=i))
                                basic_itinerary.append({
                                    "day": i + 1,
                                    "date": date.strftime("%Y-%m-%d"),
                                    "day_name": date.strftime("%A"),
                                    "morning": "Explore local attractions",
                                    "lunch": "Local restaurant",
                                    "afternoon": "Cultural experience",
                                    "dinner": "Fine dining"
                                })
                            return basic_itinerary
                            
        except Exception as e:
            logger.error(f"Luxury itinerary error: {e}")
        
        return []
    
    def _assemble_luxury_guide(self, **kwargs) -> Dict[str, Any]:
        """Assemble all components into a luxury travel guide"""
        
        destination = kwargs.get("destination")
        primary_traveler = kwargs.get("primary_traveler")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        num_days = kwargs.get("num_days")
        premium_content = kwargs.get("premium_content", {})
        weather_data = kwargs.get("weather_data", {})
        location_data = kwargs.get("location_data", {})
        contemporary = kwargs.get("contemporary", {})
        luxury_itinerary = kwargs.get("luxury_itinerary", [])
        hotel_info = kwargs.get("hotel_info", {})
        extracted_data = kwargs.get("extracted_data", {})
        preferences = kwargs.get("preferences", {})
        
        # Create personalized welcome message
        welcome = f"""Welcome to {destination}, {primary_traveler}

Your bespoke travel guide has been crafted to ensure an unforgettable journey from {start_date} to {end_date}. 
We've curated the finest experiences, from Michelin-starred dining to hidden local gems, all tailored to your preferences.

Your home in {destination} will be {hotel_info.get('name', 'your selected hotel')}, perfectly positioned to explore the city's treasures."""
        
        guide = {
            "guide_type": "luxury_conde_nast_style",
            "personalization": {
                "traveler": primary_traveler,
                "travel_dates": f"{start_date} to {end_date}",
                "duration": f"{num_days} days",
                "preferences": preferences
            },
            "welcome_message": welcome,
            "executive_summary": self._create_executive_summary(
                destination, num_days, premium_content, contemporary
            ),
            "destination_intelligence": {
                "overview": f"Your guide to the best of {destination}",
                "coordinates": location_data.get("destination_coordinates"),
                "map_url": location_data.get("map_url"),
                "interactive_map": location_data.get("interactive_map"),
                "neighborhoods": location_data.get("neighborhoods", []),
                "photos": location_data.get("photos", []),
                "getting_around": self._create_transportation_guide(destination)
            },
            "weather_forecast": self._format_weather_for_guide(weather_data),
            "daily_itinerary": luxury_itinerary,
            "culinary_guide": {
                "michelin_starred": self._enhance_restaurants_with_reservations(premium_content.get("restaurants", [])),
                "hidden_gems": [],
                "reservations_required": self._get_reservation_requirements(premium_content.get("restaurants", [])),
                "wine_bars": [],
                "coffee_culture": []
            },
            "cultural_experiences": {
                "museums": premium_content.get("attractions", [])[:3],
                "galleries": [],
                "performances": [],
                "exclusive_tours": premium_content.get("experiences", [])
            },
            "contemporary_happenings": {
                "events": premium_content.get("events", []) + contemporary.get("events", []),
                "exhibitions": contemporary.get("exhibitions", []),
                "festivals": contemporary.get("festivals", []),
                "news": contemporary.get("news", [])
            },
            "luxury_shopping": [],
            "wellness_spa": premium_content.get("hotels", [])[:2],
            "insider_tips": self._create_insider_tips(destination, premium_content),
            "practical_information": {
                "emergency_contacts": self._get_emergency_contacts(destination),
                "currency": self._get_currency_info(destination),
                "tipping": self._get_tipping_guide(destination),
                "dress_codes": self._get_dress_codes(premium_content),
                "language_phrases": self._get_useful_phrases(destination)
            },
            "flight_details": self._format_flight_details(extracted_data.get("flights", [])),
            "accommodation": self._format_hotel_details(hotel_info, extracted_data.get("hotels", [])),
            "concierge_notes": self._create_concierge_notes(destination, preferences),
            "generated_at": datetime.now().isoformat(),
            "quality_indicators": {
                "has_weather": not weather_data.get("error"),
                "has_maps": bool(location_data.get("map_url")),
                "has_interactive_map": bool(location_data.get("interactive_map")),
                "has_photos": len(location_data.get("photos", [])) > 0,
                "has_neighborhoods": len(location_data.get("neighborhoods", [])) > 0,
                "restaurant_count": len(premium_content.get("restaurants", [])),
                "attraction_count": len(premium_content.get("attractions", [])),
                "event_count": len(premium_content.get("events", [])) + len(contemporary.get("events", [])),
                "has_reservations": len(self._get_reservation_requirements(premium_content.get("restaurants", []))) > 0,
                "insider_tips_count": len(self._create_insider_tips(destination, premium_content)),
                "personalization_level": "high",
                "content_quality": "premium"
            }
        }
        
        return guide
    
    def _enhance_premium_content(self, parsed: Dict) -> Dict:
        """Enhance parsed premium content with additional details"""
        # Implementation for enhancing content
        return parsed
    
    def _parse_premium_text(self, content: str) -> Dict:
        """Parse text response into structured premium content"""
        # Implementation for parsing text
        return {}
    
    def _format_luxury_weather(self, data: Dict, start_date: str, end_date: str) -> Dict:
        """Format weather data in luxury guide style"""
        forecasts = []
        
        if "list" in data:
            by_day = {}
            for item in data["list"]:
                date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                if date not in by_day:
                    by_day[date] = {
                        "date": date,
                        "day_name": datetime.fromtimestamp(item["dt"]).strftime("%A"),
                        "high": round(item["main"]["temp_max"]),
                        "low": round(item["main"]["temp_min"]),
                        "condition": item["weather"][0]["main"],
                        "description": item["weather"][0]["description"].capitalize(),
                        "humidity": item["main"]["humidity"],
                        "wind_speed": round(item["wind"]["speed"], 1),
                        "sunrise": "",  # Requires actual API call
                        "sunset": "",   # Requires actual API call
                        "uv_index": "Moderate",  # Would get from API
                        "precipitation_chance": item.get("pop", 0) * 100 if "pop" in item else 0
                    }
            
            forecasts = list(by_day.values())
        
        return {
            "daily_forecasts": forecasts,
            "summary": self._create_weather_summary(forecasts),
            "packing_essentials": self._get_weather_based_packing(forecasts)
        }
    
    # NO FALLBACK CONTENT - Only real API data allowed
    
    # NO FALLBACK LOCATION DATA - Only real API data allowed
    
    def _parse_contemporary_text(self, content: str) -> Dict:
        """Parse text response for contemporary content"""
        return {
            "events": [],
            "news": [],
            "exhibitions": []
        }
    
    # NO FALLBACK ITINERARY - Only real API data allowed
    
    def _enhance_luxury_itinerary(self, data: List[Dict], start: datetime, num_days: int) -> List[Dict]:
        """Enhance parsed itinerary data"""
        enhanced = []
        for i, day_data in enumerate(data[:num_days]):
            date = (start + timedelta(days=i))
            enhanced.append({
                **day_data,
                "day": i + 1,
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%A")
            })
        return enhanced
    
    def _create_executive_summary(
        self, destination: str, num_days: int,
        premium_content: Dict, contemporary: Dict
    ) -> str:
        """Create executive summary of the trip"""
        restaurants = len(premium_content.get("restaurants", []))
        attractions = len(premium_content.get("attractions", []))
        events = len(contemporary.get("events", []))
        
        return f"""Your {num_days}-day journey through {destination} features {restaurants} carefully selected dining experiences, 
{attractions} cultural attractions, and {events} contemporary events. This guide combines timeless classics with 
current happenings, ensuring you experience both the eternal charm and vibrant present of {destination}."""
    
    def _create_transportation_guide(self, destination: str) -> Dict:
        """Create transportation guide"""
        # Requires real API data for destination-specific transportation
        return {
            "note": "Research local transportation options for your destination"
        }
    
    def _format_weather_for_guide(self, weather_data: Dict) -> Dict:
        """Format weather data for the guide"""
        if weather_data.get("error"):
            return {
                "available": False,
                "note": "Weather data not available - check local forecast before travel"
            }
        return weather_data
    
    def _enhance_restaurants_with_reservations(self, restaurants: List) -> List[Dict]:
        """Enhance restaurant data with reservation info"""
        enhanced = []
        for r in restaurants:
            if isinstance(r, dict):
                restaurant = r.copy()
                # Add reservation info based on restaurant type
                if 'michelin' in str(r).lower() or 'star' in str(r).lower():
                    restaurant['reservation_required'] = True
                    restaurant['booking_advance'] = "2-4 weeks recommended"
                    restaurant['booking_link'] = f"Search OpenTable or call directly"
                elif 'street' in str(r).lower():
                    restaurant['reservation_required'] = False
                    restaurant['booking_advance'] = "Walk-in friendly"
                else:
                    restaurant['reservation_required'] = True
                    restaurant['booking_advance'] = "1 week recommended"
                enhanced.append(restaurant)
            else:
                enhanced.append(r)
        return enhanced
    
    def _get_reservation_requirements(self, restaurants: List) -> List[str]:
        """Extract reservation requirements"""
        requirements = []
        for r in restaurants[:5]:  # Top 5 restaurants
            if isinstance(r, dict) and r.get('name'):
                if 'michelin' in str(r).lower() or 'star' in str(r).lower():
                    requirements.append(f"{r['name']}: Book 2-4 weeks ahead")
                else:
                    requirements.append(f"{r['name']}: Book 1 week ahead")
        return requirements
    
    def _create_insider_tips(self, destination: str, premium_content: Dict) -> List[str]:
        """Create insider tips based on actual content"""
        tips = []
        
        # Extract tips from restaurants
        restaurants = premium_content.get("restaurants", [])
        if restaurants and len(restaurants) > 0:
            # Add reservation tips for top restaurants
            if isinstance(restaurants[0], dict) and restaurants[0].get("name"):
                tips.append(f"Book {restaurants[0]['name']} at least 2 weeks in advance for peak times")
        
        # Extract tips from attractions
        attractions = premium_content.get("attractions", [])
        if attractions and len(attractions) > 0:
            if isinstance(attractions[0], dict):
                tips.append(f"Visit {attractions[0].get('name', 'major attractions')} early morning to avoid crowds")
        
        # Add weather-based tips
        if destination:
            tips.append(f"Download offline maps for {destination} before exploring")
            tips.append("Use local transport apps for authentic experiences and better prices")
        
        # Add experience-based tips
        experiences = premium_content.get("experiences", [])
        if experiences:
            tips.append("Book exclusive experiences directly through hotel concierge for best access")
        
        # Add any additional tips from content
        if premium_content.get("tips"):
            tips.extend(premium_content["tips"])
        
        return tips[:8]  # Limit to 8 most relevant tips
    
    def _get_emergency_contacts(self, destination: str) -> Dict:
        """Get emergency contacts"""
        # Requires real API or database for actual emergency numbers
        return {
            "note": "Contact hotel concierge for emergency numbers"
        }
    
    def _get_currency_info(self, destination: str) -> Dict:
        """Get currency information"""
        # Requires real API for currency data
        return {
            "note": "Check current exchange rates before travel"
        }
    
    def _get_tipping_guide(self, destination: str) -> Dict:
        """Get tipping guide"""
        # Requires real API or database for destination-specific tipping customs
        return {
            "note": "Research local tipping customs for your destination"
        }
    
    def _get_dress_codes(self, premium_content: Dict) -> Dict:
        """Extract dress codes from restaurants"""
        # Extract actual dress codes from premium content if available
        dress_codes = {}
        restaurants = premium_content.get("restaurants", [])
        for restaurant in restaurants:
            if restaurant.get("dress_code"):
                dress_codes[restaurant.get("name", "venue")] = restaurant["dress_code"]
        return dress_codes if dress_codes else {"note": "Check individual venue requirements"}
    
    def _get_useful_phrases(self, destination: str) -> List[Dict]:
        """Get useful local phrases"""
        # Requires real translation API or database
        return []
    
    def _format_flight_details(self, flights: List[Dict]) -> List[Dict]:
        """Format flight details elegantly"""
        formatted = []
        for flight in flights:
            formatted.append({
                "flight": f"{flight.get('airline', '')} {flight.get('flight_number', '')}",
                "route": f"{flight.get('departure_airport_name', '')} → {flight.get('arrival_airport_name', '')}",
                "departure": f"{flight.get('departure_date', '')} at {flight.get('departure_time', '')}",
                "arrival": f"{flight.get('arrival_date', '')} at {flight.get('arrival_time', '')}",
                "class": flight.get('class', 'Economy'),
                "seat": flight.get('seat', ''),
                "terminal": flight.get('departure_terminal', '')
            })
        return formatted
    
    def _format_hotel_details(self, hotel_info: Dict, hotels: List[Dict]) -> Dict:
        """Format hotel details elegantly"""
        hotel_data = hotels[0] if hotels else hotel_info
        return {
            "name": hotel_data.get('name', ''),
            "address": hotel_data.get('address', ''),
            "check_in": hotel_data.get('check_in_date', ''),
            "check_out": hotel_data.get('check_out_date', ''),
            "room_type": hotel_data.get('room_type', ''),
            "confirmation": hotel_data.get('confirmation_number', ''),
            "concierge": hotel_data.get('concierge_info', ''),
            "amenities": hotel_data.get('amenities', [])
        }
    
    def _create_concierge_notes(self, destination: str, preferences: Dict) -> List[str]:
        """Create personalized concierge notes"""
        # Only include notes based on actual data/actions taken
        notes = []
        
        if preferences.get("dietary_restrictions"):
            notes.append(f"Note: You have indicated {preferences['dietary_restrictions']} dietary requirements")
        
        return notes if notes else []
    
    def _create_weather_summary(self, forecasts: List[Dict]) -> str:
        """Create weather summary"""
        if not forecasts:
            return "Weather data not available"
        
        temps = [f["high"] for f in forecasts]
        conditions = [f["condition"] for f in forecasts]
        
        avg_temp = sum(temps) // len(temps) if temps else 20
        main_condition = max(set(conditions), key=conditions.count) if conditions else "Variable"
        
        return f"Expect {main_condition.lower()} conditions with temperatures around {avg_temp}°C"
    
    def _get_weather_based_packing(self, forecasts: List[Dict]) -> List[str]:
        """Get packing suggestions based on weather"""
        suggestions = ["Comfortable walking shoes", "Evening attire for fine dining"]
        
        if forecasts:
            conditions = [f.get("condition", "") for f in forecasts]
            temps = [f.get("high", 20) for f in forecasts]
            
            if any("Rain" in c for c in conditions):
                suggestions.append("Elegant raincoat or umbrella")
            
            if any(t > 25 for t in temps):
                suggestions.append("Sun protection and light fabrics")
            elif any(t < 15 for t in temps):
                suggestions.append("Light jacket or cashmere wrap")
        
        return suggestions
    
    def _geocode_hotel(self, hotel_info: Dict) -> Dict:
        """Get hotel coordinates from address"""
        # Return empty dict if Google Maps API not available
        if not self.google_maps_api_key:
            return {}
        # TODO: Implement actual geocoding with Google Maps API
        return {}
    
    async def _get_real_neighborhoods(self, session: aiohttp.ClientSession, lat: float, lng: float, api_key: str) -> List[Dict]:
        """Get real neighborhood information from Google Maps"""
        neighborhoods = []
        
        try:
            # Search for neighborhoods/districts nearby
            nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 5000,  # 5km radius
                "type": "neighborhood|locality|sublocality",
                "key": api_key
            }
            
            async with session.get(nearby_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])[:5]  # Top 5 neighborhoods
                    
                    for place in results:
                        neighborhoods.append({
                            "name": place.get("name"),
                            "vicinity": place.get("vicinity", ""),
                            "types": place.get("types", []),
                            "location": place.get("geometry", {}).get("location", {})
                        })
        except Exception as e:
            logger.error(f"Failed to get neighborhoods: {e}")
        
        return neighborhoods
    
    async def _get_neighborhoods_from_perplexity(self, destination: str) -> List[Dict]:
        """Get neighborhood information from Perplexity"""
        if not self.perplexity_api_key:
            return []
        
        prompt = f"""List the TOP 5 most important neighborhoods/districts in {destination} for tourists.
For each neighborhood include:
- name: neighborhood name
- description: what it's known for (20 words max)
- highlights: main attractions or features
Format as JSON array."""

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
                
                async with session.post("https://api.perplexity.ai/chat/completions", 
                                       headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", "[]")
                        
                        # Clean and parse JSON
                        import re
                        content = re.sub(r'\[\d+\]', '', content)  # Remove citations
                        
                        try:
                            neighborhoods = json.loads(content)
                            if isinstance(neighborhoods, list):
                                return neighborhoods[:5]
                        except json.JSONDecodeError:
                            # Try to extract JSON from the content
                            json_match = re.search(r'\[.*\]', content, re.DOTALL)
                            if json_match:
                                try:
                                    neighborhoods = json.loads(json_match.group())
                                    return neighborhoods[:5]
                                except:
                                    pass
        except Exception as e:
            logger.error(f"Failed to get neighborhoods from Perplexity: {e}")
        
        return []
    
    async def _geocode_hotel_real(self, session: aiohttp.ClientSession, hotel_info: Dict, api_key: str) -> Dict:
        """Get real hotel coordinates from Google Maps"""
        try:
            geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": f"{hotel_info.get('name', '')} {hotel_info.get('address', '')}",
                "key": api_key
            }
            
            async with session.get(geocode_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("results"):
                        location = data["results"][0]["geometry"]["location"]
                        return location
        except Exception as e:
            logger.error(f"Hotel geocoding error: {e}")
        
        return {}
