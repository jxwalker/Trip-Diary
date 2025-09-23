"""
Fast Travel Guide Service - Optimized for 10-20 second generation
Uses parallel processing, smaller prompts, and caching
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
from .guide_validator import GuideValidator

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class FastGuideService:
    """Ultra-fast guide generation - targets 10-20 seconds total"""
    
    def __init__(self):
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY", "")
        
        # Cache for common destinations (in production, use Redis)
        self.destination_cache = {}
        
    async def generate_fast_guide(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        progress_callback=None,
        timeout: int = 45
    ) -> Dict:
        """Generate guide with proper timeouts and progress tracking"""
        
        if progress_callback:
            await progress_callback(5, "Starting fast generation")
        
        # Check cache first
        cache_key = f"{destination}_{start_date}_{end_date}"
        if cache_key in self.destination_cache:
            cached = self.destination_cache[cache_key]
            # Personalize cached content with preferences
            return self._personalize_cached_guide(cached, preferences)
        
        # Prepare all tasks to run in PARALLEL
        tasks = []
        
        # Task 1: Get essential info (restaurants, attractions, events)
        tasks.append(self._get_essential_content(
            destination, start_date, end_date, preferences))
        
        # Task 2: Get weather (lightweight, fast)
        tasks.append(self._get_fast_weather(destination, start_date, end_date))
        
        # Task 3: Get quick itinerary
        tasks.append(self._get_quick_itinerary(
            destination, start_date, end_date, preferences))
        
        if progress_callback:
            await progress_callback(20, "Fetching data in parallel")
        
        # Execute ALL tasks in parallel with aggressive timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=15.0  # 15 second hard timeout
            )
        except asyncio.TimeoutError:
            # Return partial results if timeout
            results = [{"error": "timeout"}, {}, {}]
        
        if progress_callback:
            await progress_callback(80, "Assembling guide")
        
        # Unpack results
        essential_content = (results[0] 
                             if not isinstance(results[0], Exception) 
                             else {})
        weather_data = (results[1] 
                       if not isinstance(results[1], Exception) 
                       else {})
        itinerary_result = (results[2] 
                           if not isinstance(results[2], Exception) 
                           else [])
        
        # Check if itinerary is an error response
        if (isinstance(itinerary_result, dict) and 
            itinerary_result.get("error")):
            # Itinerary generation failed, use empty list
            itinerary = []
        elif isinstance(itinerary_result, list):
            itinerary = itinerary_result
        else:
            itinerary = []
        
        # Check for API failures and return error if no real content
        restaurants = essential_content.get("restaurants", [])
        attractions = essential_content.get("attractions", [])
        events = essential_content.get("events", [])
        weather_forecasts = weather_data.get("forecasts", [])

        # If essential content failed, return error - NO FALLBACK CONTENT
        if essential_content.get("error"):
            return {
                "error": essential_content["error"],
                "message": (f"Failed to generate guide for {destination}. "
                           f"Please check your API configuration."),
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "timestamp": datetime.now().isoformat(),
                "generated_with": "fast_guide_service"
            }

        # Create comprehensive summary
        summary_parts = [f"Your personalized travel guide to {destination}"]
        if weather_forecasts:
            avg_temp = (sum(f.get("temp_high", 20) for f in weather_forecasts) 
                       // len(weather_forecasts))
            summary_parts.append(f"Expect temperatures around {avg_temp}°C")
        if restaurants:
            summary_parts.append(
                f"featuring {len(restaurants)} restaurant recommendations")
        if attractions:
            summary_parts.append(
                f"and {len(attractions)} must-see attractions")

        # Build destination insights
        insights_parts = [
            f"Discover the best of {destination} with our curated "
            f"recommendations."]
        if essential_content.get("error"):
            insights_parts.append(f"Note: {essential_content['error']}")
        else:
            insights_parts.append(
                "All recommendations are based on current local information "
                "and your preferences.")

        # Integrate weather into itinerary
        enhanced_itinerary = self._integrate_weather_into_itinerary(
            itinerary, weather_forecasts)

        guide = {
            "summary": " ".join(summary_parts),
            "destination_insights": " ".join(insights_parts),
            "weather": weather_forecasts,
            "weather_summary": self._create_weather_summary(weather_forecasts),
            "daily_itinerary": enhanced_itinerary,
            "restaurants": restaurants[:10],  # Limit to 10
            "attractions": attractions[:10],  # Limit to 10
            "events": events[:5],  # Limit to 5
            "neighborhoods": [],
            "practical_info": {
                "transportation": essential_content.get("transportation", []),
                "money": [],
                "cultural": [],
                "tips": essential_content.get("tips", []),
                "packing": self._generate_packing_suggestions(weather_forecasts)
            },
            "hidden_gems": [],
            "citations": ["Perplexity AI search results", 
                         "OpenWeather API", "Local travel expertise"],
            "generated_with": "fast_guide_service",
            "generated_in_seconds": 15,
            "timestamp": datetime.now().isoformat(),
            "has_real_data": not essential_content.get("error", False)
        }
        
        # CRITICAL: Validate guide completeness before returning
        is_valid, errors, validation_details = (
            GuideValidator.validate_guide(guide))

        if not is_valid:
            print(f"Guide validation failed: {errors}")
            # Return error instead of fallback content
            return {
                "error": "Guide validation failed",
                "message": (f"Generated guide for {destination} is "
                           f"incomplete: {', '.join(errors)}"),
                "validation_errors": errors,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "timestamp": datetime.now().isoformat(),
                "generated_with": "fast_guide_service"
            }
        else:
            guide["validation_passed"] = True

        # Log validation results
        GuideValidator.log_validation_results(
            guide, is_valid, errors, validation_details)

        # Cache for future use
        self.destination_cache[cache_key] = guide

        if progress_callback:
            await progress_callback(100, "Guide ready!")

        return guide
    
    async def _get_essential_content(self, destination: str, 
                                    start_date: str, end_date: str, 
                                    preferences: Dict) -> Dict:
        """Get restaurants, attractions, and events with retry logic"""
        
        if not self.perplexity_api_key:
            # Return error instead of empty data
            return {
                "error": "Perplexity API key not configured",
                "restaurants": [],
                "attractions": [],
                "events": [],
                "transportation": []
            }
        
        # Smaller, focused prompt
        prompt = (f"For {destination} from {start_date} to {end_date}, "
                 f"provide:")

1. TOP 5 RESTAURANTS:
- Name, cuisine, price ($/$$/$$$), address, why recommended
- Focus on: {preferences.get('cuisineTypes', ['local cuisine'])}

2. TOP 5 ATTRACTIONS:
- Name, type, address, hours, admission price

3. CURRENT EVENTS during the dates

4. TRANSPORTATION: How to get around

Format as JSON with keys: restaurants, attractions, events, transportation
BE CONCISE - one line per item."""

        # Fast retry logic with shorter timeouts
        max_retries = 2
        base_timeout = 12  # Start with 12 seconds - much faster

        for attempt in range(max_retries):
            try:
                timeout = aiohttp.ClientTimeout(
                    total=base_timeout + (attempt * 5))  # 12s, 17s
                print(f"Attempt {attempt + 1}/{max_retries} for Perplexity API (timeout: {timeout.total}s)")
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    headers = {
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": "sonar",  # Use faster model
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a travel API. Return ONLY JSON data, no explanations."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,  # Lower for consistency
                        "max_tokens": 2000  # Smaller response
                    }
                    
                    async with session.post("https://api.perplexity.ai/chat/completions", 
                                           json=payload, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            content = data["choices"][0]["message"]["content"]
                            
                            # Try to parse JSON from response
                            try:
                                # Find JSON in response
                                json_start = content.find('{')
                                json_end = content.rfind('}') + 1
                                if json_start >= 0 and json_end > json_start:
                                    parsed = json.loads(content[json_start:json_end])
                                    print(f"Successfully retrieved content for {destination}")
                                    return parsed
                            except json.JSONDecodeError as je:
                                print(f"JSON parse error: {je}")
                                # Try text parsing as fallback
                                parsed = self._parse_text_response(content)
                                if parsed.get('restaurants') or parsed.get('attractions'):
                                    return parsed
                        else:
                            error_text = await response.text()
                            print(f"Perplexity API error {response.status}: {error_text[:200]}")
                            
            except asyncio.TimeoutError:
                print(f"Perplexity timeout for {destination} (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
            except Exception as e:
                print(f"Perplexity error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        
        # All retries failed - return error
        return {
            "error": f"Failed to get content for {destination} after {max_retries} attempts",
            "restaurants": [],
            "attractions": [],
            "events": [],
            "transportation": []
        }
    
    async def _get_fast_weather(self, destination: str, start_date: str, end_date: str) -> Dict:
        """Get weather data with proper duration coverage"""
        
        if not self.openweather_api_key:
            return {
                "forecasts": [],
                "summary": {"error": "OpenWeather API key not configured"}
            }
        
        try:
            # Calculate number of days for the trip
            from datetime import datetime
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            num_days = (end - start).days + 1
            
            # Weather API timeout
            timeout = aiohttp.ClientTimeout(total=5)  # 5 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Get coordinates
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={destination}&limit=1&appid={self.openweather_api_key}"
                async with session.get(geo_url) as response:
                    if response.status == 200:
                        geo_data = await response.json()
                        if geo_data:
                            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
                            
                            # Get forecast - max 40 data points (5 days * 8 per day)
                            # cnt = min(40, num_days * 8) to get as much as possible
                            cnt = min(40, num_days * 8)
                            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.openweather_api_key}&units=metric&cnt={cnt}"
                            
                            async with session.get(forecast_url) as forecast_response:
                                if forecast_response.status == 200:
                                    forecast_data = await forecast_response.json()
                                    return self._format_fast_weather(forecast_data, num_days)
                                else:
                                    print(f"Weather API error: {forecast_response.status}")
                        else:
                            print(f"Could not find coordinates for {destination}")
                    else:
                        print(f"Geocoding API error: {response.status}")
                        
        except asyncio.TimeoutError:
            print(f"Weather API timeout for {destination}")
        except Exception as e:
            print(f"Weather API error: {e}")
        
        return {
            "forecasts": [],
            "summary": {"error": f"Failed to get weather for {destination}"}
        }
    
    def _format_fast_weather(self, data: Dict, requested_days: int) -> Dict:
        """Format weather data for all trip days"""
        forecasts = []
        if "list" in data:
            # Group by day, process all available data
            by_day = {}
            for item in data["list"]:
                date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                if date not in by_day:
                    by_day[date] = {
                        "date": date,
                        "temp_high": round(item["main"]["temp_max"]),
                        "temp_low": round(item["main"]["temp_min"]),
                        "condition": item["weather"][0]["main"],
                        "description": item["weather"][0]["description"],
                        "humidity": item["main"]["humidity"],
                        "wind_speed": round(item["wind"]["speed"], 1)
                    }
                else:
                    # Update with max/min temps for the day
                    by_day[date]["temp_high"] = max(by_day[date]["temp_high"], round(item["main"]["temp_max"]))
                    by_day[date]["temp_low"] = min(by_day[date]["temp_low"], round(item["main"]["temp_min"]))
            
            forecasts = list(by_day.values())[:requested_days]
        
        return {
            "forecasts": forecasts,
            "summary": {
                "days_available": len(forecasts),
                "days_requested": requested_days,
                "overview": forecasts[0]["condition"] if forecasts else "No data",
                "note": f"Weather data available for {len(forecasts)} of {requested_days} days" if len(forecasts) < requested_days else "Complete forecast available"
            }
        }
    
    async def _get_quick_itinerary(self, destination: str, start_date: str, end_date: str, preferences: Dict) -> List[Dict]:
        """Generate a detailed daily itinerary with real activities"""

        if not self.perplexity_api_key:
            return {
                "error": "Perplexity API key not configured",
                "message": "Cannot generate itinerary without Perplexity API key. Please configure PERPLEXITY_API_KEY in your .env file."
            }

        # Calculate days
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1

        # Create focused prompt for itinerary
        interests = preferences.get('interests', {})
        active_interests = [k for k, v in interests.items() if v]
        interest_text = ", ".join(active_interests) if active_interests else "general sightseeing"

        prompt = f"""Create a detailed {num_days}-day itinerary for {destination} from {start_date} to {end_date}.

Traveler interests: {interest_text}
Budget: {preferences.get('budget', 'moderate')}
Pace: {preferences.get('pace', 'moderate')}

For each day, provide:
- Morning activity (9-12 PM) with specific location and timing
- Lunch recommendation with restaurant name and location
- Afternoon activity (2-5 PM) with specific location and timing
- Evening activity/dinner (7-9 PM) with specific restaurant name

Format as JSON array with keys: date, day, morning, lunch, afternoon, evening
Include specific times, addresses, and activity names."""

        try:
            timeout = aiohttp.ClientTimeout(total=12)  # Reduced from 20 to 12 seconds
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a travel itinerary expert. Return detailed daily schedules as JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.4,
                    "max_tokens": 3000
                }

                async with session.post("https://api.perplexity.ai/chat/completions",
                                       json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]

                        # Parse JSON response
                        try:
                            json_start = content.find('[')
                            json_end = content.rfind(']') + 1
                            if json_start >= 0 and json_end > json_start:
                                itinerary_data = json.loads(content[json_start:json_end])
                                return self._format_itinerary(itinerary_data, start, num_days)
                        except json.JSONDecodeError:
                            print("Failed to parse itinerary JSON, using text parsing")
                            return self._parse_itinerary_text(content, start, num_days)
                    else:
                        print(f"Itinerary API error: {response.status}")

        except Exception as e:
            print(f"Itinerary generation error: {e}")

        # Return error - NO FALLBACK CONTENT
        return {
            "error": "Failed to generate itinerary",
            "message": "Unable to create itinerary due to API failure. Please check your Perplexity API key configuration."
        }



    def _format_itinerary(self, itinerary_data: List[Dict], start_date: datetime, num_days: int) -> List[Dict]:
        """Format parsed itinerary data"""
        formatted = []

        for i, day_data in enumerate(itinerary_data[:num_days]):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

            # Extract activities from the parsed data
            activities = []
            if day_data.get('morning'):
                activities.append(f"Morning: {day_data['morning']}")
            if day_data.get('lunch'):
                activities.append(f"Lunch: {day_data['lunch']}")
            if day_data.get('afternoon'):
                activities.append(f"Afternoon: {day_data['afternoon']}")
            if day_data.get('evening'):
                activities.append(f"Evening: {day_data['evening']}")

            formatted.append({
                "date": date,
                "day": i + 1,
                "theme": day_data.get('theme', f"Day {i + 1}"),
                "activities": activities,
                "meals": {
                    "breakfast": "Hotel or local café",
                    "lunch": day_data.get('lunch', 'Local restaurant'),
                    "dinner": day_data.get('evening', 'Recommended restaurant')
                },
                "transportation": ["Walking", "Public transport"]
            })

        return formatted

    def _parse_itinerary_text(self, content: str, start_date: datetime, num_days: int) -> List[Dict]:
        """NO REGEX - Use LLM parsing for itinerary instead"""
        # This method should not use regex parsing
        # Return empty list - itinerary should be parsed by LLM services
        return []

    def _integrate_weather_into_itinerary(self, itinerary: List[Dict], weather_forecasts: List[Dict]) -> List[Dict]:
        """Integrate weather information into daily itinerary"""
        if not weather_forecasts or not itinerary:
            return itinerary if itinerary else []

        enhanced_itinerary = []
        for i, day in enumerate(itinerary):
            # Ensure day is a dictionary
            if not isinstance(day, dict):
                continue
                
            enhanced_day = day.copy()

            # Find matching weather forecast
            weather_for_day = None
            for forecast in weather_forecasts:
                if forecast.get("date") == day.get("date"):
                    weather_for_day = forecast
                    break

            if weather_for_day:
                # Add weather info to the day
                enhanced_day["weather"] = {
                    "condition": weather_for_day.get("condition", "Unknown"),
                    "temp_high": weather_for_day.get("temp_high", 20),
                    "temp_low": weather_for_day.get("temp_low", 15),
                    "description": weather_for_day.get("description", ""),
                    "icon": self._get_weather_icon(weather_for_day.get("condition", "Unknown"))
                }

                # Add weather-appropriate suggestions to activities
                if weather_for_day.get("condition") in ["Rain", "Thunderstorm"]:
                    enhanced_day["weather_note"] = "Indoor activities recommended due to rain"
                    # Modify activities to be more indoor-focused
                    activities = enhanced_day.get("activities", [])
                    enhanced_day["activities"] = [
                        activity.replace("walk", "visit indoor attractions").replace("outdoor", "indoor")
                        for activity in activities
                    ]
                elif weather_for_day.get("temp_high", 20) > 25:
                    enhanced_day["weather_note"] = "Hot weather - stay hydrated and seek shade"
                elif weather_for_day.get("temp_high", 20) < 10:
                    enhanced_day["weather_note"] = "Cold weather - dress warmly"

            enhanced_itinerary.append(enhanced_day)

        return enhanced_itinerary

    def _get_weather_icon(self, condition: str) -> str:
        """Get weather icon for condition"""
        icons = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️"
        }
        return icons.get(condition, "🌤️")

    def _create_weather_summary(self, weather_forecasts: List[Dict]) -> Dict:
        """Create weather summary from forecasts"""
        if not weather_forecasts:
            return {"note": "Weather data not available"}

        temps_high = [f.get("temp_high", 20) for f in weather_forecasts]
        temps_low = [f.get("temp_low", 15) for f in weather_forecasts]
        conditions = [f.get("condition", "Unknown") for f in weather_forecasts]

        # Find most common condition
        condition_counts = {}
        for condition in conditions:
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
        predominant_condition = max(condition_counts, key=condition_counts.get) if condition_counts else "Mixed"

        return {
            "avg_high": round(sum(temps_high) / len(temps_high)),
            "avg_low": round(sum(temps_low) / len(temps_low)),
            "predominant_condition": predominant_condition,
            "days_covered": len(weather_forecasts),
            "packing_suggestions": self._generate_packing_suggestions(weather_forecasts)
        }

    def _generate_packing_suggestions(self, weather_forecasts: List[Dict]) -> List[str]:
        """Generate packing suggestions based on weather"""
        if not weather_forecasts:
            return ["Comfortable walking shoes", "Weather-appropriate clothing", "Umbrella"]

        suggestions = ["Comfortable walking shoes"]

        temps_high = [f.get("temp_high", 20) for f in weather_forecasts]
        temps_low = [f.get("temp_low", 15) for f in weather_forecasts]
        conditions = [f.get("condition", "Unknown") for f in weather_forecasts]

        avg_high = sum(temps_high) / len(temps_high)
        avg_low = sum(temps_low) / len(temps_low)

        # Temperature-based suggestions
        if avg_high > 25:
            suggestions.extend(["Light, breathable clothing", "Sun hat", "Sunscreen", "Water bottle"])
        elif avg_high > 15:
            suggestions.extend(["Light layers", "Light jacket for evenings"])
        else:
            suggestions.extend(["Warm layers", "Winter jacket", "Gloves and hat"])

        # Condition-based suggestions
        if any(cond in ["Rain", "Drizzle", "Thunderstorm"] for cond in conditions):
            suggestions.append("Waterproof jacket or umbrella")

        if any(cond == "Snow" for cond in conditions):
            suggestions.extend(["Warm boots", "Winter accessories"])

        return suggestions


    
    def _parse_text_response(self, content: str) -> Dict:
        """Parse text response into structured data"""
        result = {
            "restaurants": [],
            "attractions": [],
            "events": [],
            "transportation": []
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if 'RESTAURANT' in line.upper() or 'DINING' in line.upper():
                current_section = 'restaurants'
            elif 'ATTRACTION' in line.upper() or 'SIGHT' in line.upper():
                current_section = 'attractions'
            elif 'EVENT' in line.upper():
                current_section = 'events'
            elif 'TRANSPORT' in line.upper():
                current_section = 'transportation'
            elif current_section and line.startswith(('-', '•', '*', '1', '2', '3', '4', '5')):
                # Extract item
                item_text = line.lstrip('-•*123456789. ')
                if current_section == 'restaurants':
                    result['restaurants'].append({
                        "name": item_text.split(',')[0].split(':')[0].strip(),
                        "description": item_text,
                        "cuisine": "Local",
                        "price_range": "$$"
                    })
                elif current_section == 'attractions':
                    result['attractions'].append({
                        "name": item_text.split(',')[0].split(':')[0].strip(),
                        "description": item_text,
                        "type": "Attraction"
                    })
                elif current_section == 'events':
                    result['events'].append({
                        "name": item_text.split(',')[0].split(':')[0].strip(),
                        "description": item_text
                    })
                elif current_section == 'transportation':
                    result['transportation'].append(item_text)
        
        return result
    
    # Removed fallback content to comply with no mocks policy
    
    def _personalize_cached_guide(self, cached_guide: Dict, preferences: Dict) -> Dict:
        """Personalize a cached guide based on user preferences"""
        guide = cached_guide.copy()
        
        # Filter restaurants by cuisine preference
        if preferences.get('cuisineTypes'):
            preferred_cuisines = [c.lower() for c in preferences['cuisineTypes'] if c]
            guide['restaurants'] = [
                r for r in guide.get('restaurants', [])
                if any(pref in (r.get('cuisine') or '').lower() for pref in preferred_cuisines)
            ][:10]
        
        # Filter by price preference
        if preferences.get('budget'):
            budget_map = {'budget': '$', 'moderate': '$$', 'luxury': '$$$'}
            max_price = budget_map.get(preferences['budget'], '$$')
            guide['restaurants'] = [
                r for r in guide.get('restaurants', [])
                if len(r.get('price_range', '$$')) <= len(max_price)
            ]
        
        return guide
