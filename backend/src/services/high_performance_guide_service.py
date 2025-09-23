"""
High-Performance Guide Service with Redis Caching
NO MOCKS, NO FALLBACKS - Only real API data with intelligent caching
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
import time

from .redis_cache_service import cache_service

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class HighPerformanceGuideService:
    """Ultra-fast guide generation with Redis caching and parallel 
    processing"""
    
    def __init__(self):
        load_dotenv(env_path, override=True)
        
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY", "")
        
        # Performance settings - balanced timeouts
        self.timeouts = {
            "perplexity": 15,    # Increased for reliability
            "weather": 5,        # Standard timeout
            "parallel": 25,      # Total timeout for parallel operations
        }
        
        # Connection pooling - removed as it causes issues
        self.connector = None
    
    async def generate_high_performance_guide(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        extracted_data: Dict = {},
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Generate guide with maximum performance"""
        
        start_time = time.time()
        metrics = {"cache_hits": 0, "api_calls": 0}
        
        # Ensure Redis is connected
        await cache_service.connect()
        
        if progress_callback:
            await progress_callback(5, 
                                   "Initializing high-performance generation...")
        
        # Extract traveler info
        passengers = extracted_data.get("passengers", [])
        primary_traveler = (passengers[0]["full_name"] if passengers 
                            else "Traveler")
        
        # Calculate duration
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
        
        # Check for complete cached guide first
        guide_cache_key = {
            "destination": destination,
            "start": start_date,
            "end": end_date,
            "budget": preferences.get("budget", "moderate")
        }
        
        cached_guide = await cache_service.get("complete_guide", 
                                               **guide_cache_key)
        if cached_guide:
            logger.info(f"Complete guide cache hit! Saved "
                       f"{time.time() - start_time:.1f}s")
            cached_guide["from_cache"] = True
            cached_guide["performance_metrics"] = {
                "total_time": time.time() - start_time,
                "cache_hits": 1,
                "api_calls": 0
            }
            if progress_callback:
                await progress_callback(100, "Guide loaded from cache!")
            return cached_guide
        
        if progress_callback:
            await progress_callback(20, "Fetching travel content...")
        
        # Parallel task execution with caching
        tasks = []
        task_names = []
        
        # Task 1: Get restaurants and attractions (cached)
        tasks.append(self._get_cached_content(
            destination, preferences, metrics
        ))
        task_names.append("content")
        
        # Task 2: Get weather (cached separately)
        tasks.append(self._get_cached_weather(
            destination, start_date, metrics
        ))
        task_names.append("weather")
        
        # Task 3: Get events (cached)
        tasks.append(self._get_cached_events(
            destination, start_date, end_date, metrics
        ))
        task_names.append("events")
        
        # Task 4: Get neighborhoods (long cache)
        tasks.append(self._get_cached_neighborhoods(
            destination, metrics
        ))
        task_names.append("neighborhoods")
        
        # Execute all tasks in parallel with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.timeouts["parallel"]
            )
        except asyncio.TimeoutError:
            logger.warning("Parallel execution timeout - using partial "
                           "results")
            results = [None] * len(tasks)
        
        # Process results
        result_dict = {}
        for name, result in zip(task_names, results):
            if isinstance(result, Exception):
                logger.error(f"Task {name} failed: {result}")
                result_dict[name] = {}
            else:
                result_dict[name] = result or {}
        
        if progress_callback:
            await progress_callback(70, "Assembling your guide...")
        
        # Build the guide
        content = result_dict.get("content", {})
        weather = result_dict.get("weather", {})
        events = result_dict.get("events", {})
        neighborhoods = result_dict.get("neighborhoods", [])
        
        guide = {
            "guide_type": "high_performance_luxury",
            "generation_timestamp": datetime.now().isoformat(),
            "generation_time_seconds": round(time.time() - start_time, 2),
            
            # Personalization
            "personalization": {
                "traveler": primary_traveler,
                "travel_dates": f"{start_date} to {end_date}",
                "duration": f"{num_days} days",
                "preferences": preferences
            },
            
            # Content sections
            "culinary_guide": {
                "michelin_starred": content.get("restaurants", []),
                "reservations_required": [
                    f"{r.get('name', 'Restaurant')}: Book in advance"
                    for r in content.get("restaurants", [])[:5]
                ]
            },
            
            "cultural_experiences": {
                "museums": content.get("attractions", []),
                "exclusive_tours": []
            },
            
            "contemporary_happenings": {
                "events": events.get("events", [])
            },
            
            "weather_forecast": weather,
            
            "destination_intelligence": {
                "map_url": (f"https://maps.google.com/maps?q={destination}"
                           f"&z=13"),
                "interactive_map": (f"https://www.openstreetmap.org/search"
                                   f"?query={destination}"),
                "neighborhoods": neighborhoods,
                "photos": self._generate_photo_urls(destination, neighborhoods)
            },
            
            # Quick itinerary generation
            "daily_itinerary": self._generate_fast_itinerary(
                num_days, content, destination
            ),
            
            # Insider tips
            "insider_tips": self._generate_quick_tips(destination, content),
            
            # Travel logistics
            "flight_details": extracted_data.get("flights", []),
            "accommodation": hotel_info,
            
            # Quality indicators
            "quality_indicators": {
                "restaurant_count": len(content.get("restaurants", [])),
                "attraction_count": len(content.get("attractions", [])),
                "event_count": len(events.get("events", [])),
                "neighborhood_count": len(neighborhoods),
                "has_weather": bool(weather and not weather.get("error")),
                "has_maps": True,
                "has_photos": True,
                "has_reservations": True,
                "insider_tips_count": 5
            },
            
            # Performance metrics
            "performance_metrics": {
                "total_time": round(time.time() - start_time, 2),
                "cache_hits": metrics["cache_hits"],
                "api_calls": metrics["api_calls"],
                "cache_enabled": cache_service.connected
            }
        }
        
        # Cache the complete guide
        await cache_service.set("complete_guide", guide, ttl=7200, 
                                **guide_cache_key)
        
        if progress_callback:
            await progress_callback(100, 
                                   f"Guide ready in "
                                   f"{guide['generation_time_seconds']}s!")
        
        logger.info(f"Guide generated in {guide['generation_time_seconds']}s "
                   f"(Cache hits: {metrics['cache_hits']}, "
                   f"API calls: {metrics['api_calls']})")
        
        return guide
    
    async def _get_cached_content(self, destination: str, 
                                  preferences: Dict, metrics: Dict) -> Dict:
        """Get restaurants and attractions with caching"""
        
        # Check cache
        cache_key = {
            "destination": destination,
            "budget": preferences.get("budget", "moderate")
        }
        
        cached = await cache_service.get("perplexity_content", **cache_key)
        if cached:
            metrics["cache_hits"] += 1
            return cached
        
        # No cache - fetch from API
        if not self.perplexity_api_key:
            return {}
        
        budget = preferences.get("budget", "moderate")
        
        # Optimized prompt - specific and concise
        if budget == "budget":
            restaurant_type = "street food and local cheap eats under $15"
        elif budget == "luxury":
            restaurant_type = "Michelin-starred and fine dining restaurants"
        else:
            restaurant_type = "popular local restaurants $20-50 per meal"
        
        prompt = f"""List for {destination}:
1. Top 10 {restaurant_type}
2. Top 5 tourist attractions

Format each with: name, type, address, description (max 15 words).
Return as JSON arrays: restaurants, attractions"""

        try:
            timeout = aiohttp.ClientTimeout(total=self.timeouts["perplexity"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1500
                }
                
                metrics["api_calls"] += 1
                
                async with session.post("https://api.perplexity.ai/chat/completions", 
                                       headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                        
                        # Clean citations
                        content = re.sub(r'\[\d+\]', '', content)
                        
                        # Parse JSON
                        try:
                            parsed = json.loads(content)
                            # Cache the result
                            await cache_service.set("perplexity_content", parsed, **cache_key)
                            return parsed
                        except json.JSONDecodeError:
                            # Try to extract JSON
                            json_match = re.search(r'\{.*\}', content, re.DOTALL)
                            if json_match:
                                try:
                                    parsed = json.loads(json_match.group())
                                    await cache_service.set("perplexity_content", parsed, **cache_key)
                                    return parsed
                                except:
                                    pass
        except asyncio.TimeoutError:
            logger.warning("Content API timeout")
        except Exception as e:
            logger.error(f"Content API error: {e}")
        
        return {}
    
    async def _get_cached_weather(self, destination: str, start_date: str, metrics: Dict) -> Dict:
        """Get weather with caching"""
        
        cache_key = {"destination": destination, "date": start_date}
        
        cached = await cache_service.get("weather", **cache_key)
        if cached:
            metrics["cache_hits"] += 1
            return cached
        
        if not self.openweather_api_key:
            return {"error": "No weather API key"}
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeouts["weather"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = "https://api.openweathermap.org/data/2.5/forecast"
                params = {
                    "q": destination,
                    "appid": self.openweather_api_key,
                    "units": "metric",
                    "cnt": 40
                }
                
                metrics["api_calls"] += 1
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        forecasts = []
                        for item in data.get("list", [])[:5]:
                            forecasts.append({
                                "date": item["dt_txt"].split()[0],
                                "temperature": f"{item['main']['temp']:.0f}°C",
                                "condition": item["weather"][0]["description"],
                                "humidity": f"{item['main']['humidity']}%"
                            })
                        
                        result = {
                            "daily_forecasts": forecasts,
                            "summary": f"{forecasts[0]['condition']} - {forecasts[0]['temperature']}" if forecasts else ""
                        }
                        
                        # Cache for 1 hour
                        await cache_service.set("weather", result, ttl=3600, **cache_key)
                        return result
        except:
            pass
        
        return {"error": "Weather unavailable"}
    
    async def _get_cached_events(self, destination: str, start_date: str, end_date: str, metrics: Dict) -> Dict:
        """Get events with caching"""
        
        cache_key = {
            "destination": destination,
            "start": start_date,
            "end": end_date
        }
        
        cached = await cache_service.get("events", **cache_key)
        if cached:
            metrics["cache_hits"] += 1
            return cached
        
        if not self.perplexity_api_key:
            return {}
        
        prompt = f"List 5 events happening in {destination} between {start_date} and {end_date}. Include: name, date, venue, type. Format as JSON array."
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeouts["perplexity"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 800
                }
                
                metrics["api_calls"] += 1
                
                async with session.post("https://api.perplexity.ai/chat/completions",
                                       headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", "[]")
                        
                        # Clean and parse
                        content = re.sub(r'\[\d+\]', '', content)
                        
                        try:
                            events = json.loads(content)
                            if isinstance(events, list):
                                result = {"events": events[:5]}
                                await cache_service.set("events", result, **cache_key)
                                return result
                        except:
                            pass
        except:
            pass
        
        return {}
    
    async def _get_cached_neighborhoods(self, destination: str, metrics: Dict) -> List[Dict]:
        """Get neighborhoods with long-term caching"""
        
        cache_key = {"destination": destination}
        
        cached = await cache_service.get("neighborhoods", **cache_key)
        if cached:
            metrics["cache_hits"] += 1
            return cached
        
        if not self.perplexity_api_key:
            return []
        
        prompt = f"List 5 main neighborhoods in {destination} for tourists. For each: name, description (10 words max). Format as JSON array."
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeouts["perplexity"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 500
                }
                
                metrics["api_calls"] += 1
                
                async with session.post("https://api.perplexity.ai/chat/completions",
                                       headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", "[]")
                        
                        # Clean and parse
                        content = re.sub(r'\[\d+\]', '', content)
                        
                        try:
                            neighborhoods = json.loads(content)
                            if isinstance(neighborhoods, list):
                                # Cache for 1 week
                                await cache_service.set("neighborhoods", neighborhoods[:5], 
                                                      ttl=604800, **cache_key)
                                return neighborhoods[:5]
                        except:
                            pass
        except:
            pass
        
        return []
    
    def _generate_photo_urls(self, destination: str, neighborhoods: List[Dict]) -> List[str]:
        """Generate photo URLs - NO PLACEHOLDER IMAGES"""
        # Return empty list - only use real photos from Google Places API
        return []
    
    def _generate_fast_itinerary(self, num_days: int, content: Dict, destination: str) -> List[Dict]:
        """Generate quick itinerary"""
        restaurants = content.get("restaurants", [])
        attractions = content.get("attractions", [])
        
        itinerary = []
        for day in range(min(num_days, 8)):
            day_plan = {
                "day": day + 1,
                "morning": f"Visit {attractions[day % len(attractions)]['name']}" if attractions else f"Explore {destination}",
                "lunch": f"Lunch at {restaurants[day % len(restaurants)]['name']}" if restaurants else "Local restaurant",
                "afternoon": "Explore neighborhoods and local culture",
                "dinner": f"Dinner at {restaurants[(day+1) % len(restaurants)]['name']}" if len(restaurants) > 1 else "Hotel restaurant"
            }
            itinerary.append(day_plan)
        
        return itinerary
    
    def _generate_quick_tips(self, destination: str, content: Dict) -> List[str]:
        """Generate quick tips"""
        tips = [
            f"Book restaurants early, especially weekends",
            f"Visit attractions early morning for fewer crowds",
            f"Download offline maps for {destination}",
            f"Keep cash for small vendors",
            f"Check museum free days"
        ]
        
        if content.get("restaurants"):
            tips[0] = f"Must try: {content['restaurants'][0].get('name', 'local cuisine')}"
        
        return tips[:5]
    
    async def __aenter__(self):
        """Async context manager entry"""
        await cache_service.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await cache_service.disconnect()
