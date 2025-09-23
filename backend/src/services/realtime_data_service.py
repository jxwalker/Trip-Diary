"""
Real-time Data Service
Fetches weather, events, and current information for destinations
"""
import aiohttp
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class RealtimeDataService:
    def __init__(self):
        # You can add API keys here for weather/events services
        self.openweather_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.ticketmaster_key = os.getenv("TICKETMASTER_API_KEY", "")
        
    async def get_weather_forecast(
        self, destination: str, start_date: str, end_date: str
    ) -> Dict:
        """Get weather forecast for destination"""
        try:
            if not self.openweather_key:
                return {
                    "temperature": None,
                    "conditions": None,
                    "packing_tips": None,
                    "season": None,
                    "error": "OPENWEATHER_API_KEY not configured"
                }
            
            async with aiohttp.ClientSession() as session:
                # Get coordinates for city
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
                params = {
                    "q": destination,
                    "limit": 1,
                    "appid": self.openweather_key
                }
                
                async with session.get(geo_url, params=params) as response:
                    if response.status == 200:
                        geo_data = await response.json()
                        if geo_data:
                            lat = geo_data[0]["lat"]
                            lon = geo_data[0]["lon"]
                            
                            # Get weather forecast
                            weather_url = (
                                "https://api.openweathermap.org/data/2.5/forecast"
                            )
                            weather_params = {
                                "lat": lat,
                                "lon": lon,
                                "appid": self.openweather_key,
                                "units": "metric"
                            }
                            
                            async with session.get(
                                weather_url, params=weather_params
                            ) as weather_response:
                                if weather_response.status == 200:
                                    weather_data = await weather_response.json()
                                    return self._format_weather_data(
                                        weather_data, start_date, end_date
                                    )
        except Exception as e:
            print(f"Weather API error: {e}")
        
        return {
            "temperature": None,
            "conditions": None,
            "packing_tips": None,
            "season": None
        }
    
    # Removed typical weather generator to comply with no-mocks policy
    
    def _format_weather_data(
        self, weather_data: Dict, start_date: str, end_date: str
    ) -> Dict:
        """Format weather API data"""
        forecast_list = weather_data.get("list", [])
        
        if not forecast_list:
            return self._get_typical_weather(
                weather_data.get("city", {}).get("name", ""), start_date
            )
        
        # Get average conditions
        temps = []
        conditions = []
        
        for item in forecast_list[:10]:  # Next few days
            temps.append(item["main"]["temp"])
            conditions.append(item["weather"][0]["description"])
        
        avg_temp = sum(temps) / len(temps) if temps else 20
        most_common_condition = (
            max(set(conditions), key=conditions.count) 
            if conditions else "clear"
        )
        
        return {
            "temperature": f"{int(avg_temp-5)}-{int(avg_temp+5)}°C",
            "conditions": most_common_condition.title(),
            "packing_tips": self._get_packing_tips(
                avg_temp, most_common_condition
            ),
            "detailed_forecast": forecast_list[:5]  # First 5 time periods
        }
    
    def _get_packing_tips(self, temp: float, conditions: str) -> str:
        """Get packing tips based on weather"""
        tips = []
        
        if temp < 10:
            tips.append("warm coat and layers")
        elif temp < 20:
            tips.append("light jacket or sweater")
        else:
            tips.append("light, breathable clothes")
        
        if "rain" in conditions.lower():
            tips.append("umbrella and raincoat")
        if "snow" in conditions.lower():
            tips.append("warm boots and gloves")
        if "sun" in conditions.lower() or "clear" in conditions.lower():
            tips.append("sunglasses and sunscreen")
        
        return ", ".join(tips).capitalize()
    
    async def get_events(
        self, destination: str, start_date: str, end_date: str, 
        interests: List[str] = None
    ) -> List[Dict]:
        """Get events happening during the trip"""
        events = []
        
        # Add typical events based on destination and dates
        # No typical events; only real providers
        
        # If we have Ticketmaster API, fetch real events
        if self.ticketmaster_key:
            real_events = await self._fetch_ticketmaster_events(
                destination, start_date, end_date
            )
            events.extend(real_events)
        
        return events
    
    # Removed typical events to comply with no-mocks policy
    
    async def _fetch_ticketmaster_events(
        self, destination: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch real events from Ticketmaster API"""
        if not self.ticketmaster_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://app.ticketmaster.com/discovery/v2/events"
                params = {
                    "apikey": self.ticketmaster_key,
                    "city": destination,
                    "startDateTime": f"{start_date}T00:00:00Z",
                    "endDateTime": f"{end_date}T23:59:59Z",
                    "size": 20,
                    "sort": "relevance,desc"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        events = []
                        
                        for event in data.get("_embedded", {}).get(
                            "events", []
                        )[:10]:
                            events.append({
                                "name": event.get("name"),
                                "type": event.get("classifications", [{}])[0].get(
                                    "segment", {}
                                ).get("name", "Event"),
                                "description": event.get("info", ""),
                                "date": event.get("dates", {}).get(
                                    "start", {}
                                ).get("localDate"),
                                "time": event.get("dates", {}).get(
                                    "start", {}
                                ).get("localTime"),
                                "venue": event.get("_embedded", {}).get(
                                    "venues", [{}]
                                )[0].get("name"),
                                "ticket_info": event.get("url", "")
                            })
                        
                        return events
        except Exception as e:
            print(f"Ticketmaster API error: {e}")
        
        return []
    
    async def get_local_tips(self, destination: str) -> Dict:
        """Get local tips - should be fetched dynamically"""
        # Return empty dict - let Perplexity provide real-time local info
        return {}
