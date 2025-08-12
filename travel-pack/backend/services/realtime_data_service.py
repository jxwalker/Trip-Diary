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
        
    async def get_weather_forecast(self, destination: str, start_date: str, end_date: str) -> Dict:
        """Get weather forecast for destination"""
        try:
            if not self.openweather_key:
                # Return typical weather if no API key
                return self._get_typical_weather(destination, start_date)
            
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
                            weather_url = "https://api.openweathermap.org/data/2.5/forecast"
                            weather_params = {
                                "lat": lat,
                                "lon": lon,
                                "appid": self.openweather_key,
                                "units": "metric"
                            }
                            
                            async with session.get(weather_url, params=weather_params) as weather_response:
                                if weather_response.status == 200:
                                    weather_data = await weather_response.json()
                                    return self._format_weather_data(weather_data, start_date, end_date)
        except Exception as e:
            print(f"Weather API error: {e}")
        
        return self._get_typical_weather(destination, start_date)
    
    def _get_typical_weather(self, destination: str, date_str: str) -> Dict:
        """Get typical weather based on destination and time of year"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            month = date.month
        except:
            month = datetime.now().month
        
        # Seasonal weather patterns
        weather_patterns = {
            "New York": {
                "winter": {"temp": "0-5°C", "conditions": "Cold, possible snow", "pack": "Winter coat, boots"},
                "spring": {"temp": "10-20°C", "conditions": "Mild, occasional rain", "pack": "Light jacket, umbrella"},
                "summer": {"temp": "20-30°C", "conditions": "Hot and humid", "pack": "Light clothes, sunscreen"},
                "fall": {"temp": "10-20°C", "conditions": "Cool and crisp", "pack": "Layers, light jacket"}
            },
            "London": {
                "winter": {"temp": "2-8°C", "conditions": "Cold and rainy", "pack": "Raincoat, umbrella"},
                "spring": {"temp": "8-15°C", "conditions": "Variable, showers", "pack": "Layers, raincoat"},
                "summer": {"temp": "15-23°C", "conditions": "Mild, occasional rain", "pack": "Light jacket, umbrella"},
                "fall": {"temp": "8-15°C", "conditions": "Cool and damp", "pack": "Warm layers, raincoat"}
            },
            "Paris": {
                "winter": {"temp": "3-8°C", "conditions": "Cold, occasional rain", "pack": "Warm coat, scarf"},
                "spring": {"temp": "10-18°C", "conditions": "Pleasant, some rain", "pack": "Light jacket, umbrella"},
                "summer": {"temp": "15-25°C", "conditions": "Warm and sunny", "pack": "Light clothes, sunglasses"},
                "fall": {"temp": "10-18°C", "conditions": "Cool, crisp days", "pack": "Layers, light jacket"}
            }
        }
        
        # Determine season
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "fall"
        
        # Get weather for destination or default
        city_weather = weather_patterns.get(destination, weather_patterns.get("New York"))
        seasonal_weather = city_weather[season]
        
        return {
            "temperature": seasonal_weather["temp"],
            "conditions": seasonal_weather["conditions"],
            "packing_tips": seasonal_weather["pack"],
            "season": season
        }
    
    def _format_weather_data(self, weather_data: Dict, start_date: str, end_date: str) -> Dict:
        """Format weather API data"""
        forecast_list = weather_data.get("list", [])
        
        if not forecast_list:
            return self._get_typical_weather(weather_data.get("city", {}).get("name", ""), start_date)
        
        # Get average conditions
        temps = []
        conditions = []
        
        for item in forecast_list[:10]:  # Next few days
            temps.append(item["main"]["temp"])
            conditions.append(item["weather"][0]["description"])
        
        avg_temp = sum(temps) / len(temps) if temps else 20
        most_common_condition = max(set(conditions), key=conditions.count) if conditions else "clear"
        
        return {
            "temperature": f"{int(avg_temp-5)}-{int(avg_temp+5)}°C",
            "conditions": most_common_condition.title(),
            "packing_tips": self._get_packing_tips(avg_temp, most_common_condition),
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
    
    async def get_events(self, destination: str, start_date: str, end_date: str, interests: List[str] = None) -> List[Dict]:
        """Get events happening during the trip"""
        events = []
        
        # Add typical events based on destination and dates
        events.extend(self._get_typical_events(destination, start_date, end_date, interests))
        
        # If we have Ticketmaster API, fetch real events
        if self.ticketmaster_key:
            real_events = await self._fetch_ticketmaster_events(destination, start_date, end_date)
            events.extend(real_events)
        
        return events
    
    def _get_typical_events(self, destination: str, start_date: str, end_date: str, interests: List[str] = None) -> List[Dict]:
        """Get events based on user interests - no hardcoding"""
        # This should be fetched dynamically or left empty
        # Let Perplexity handle real-time event discovery
        return []
    
    async def _fetch_ticketmaster_events(self, destination: str, start_date: str, end_date: str) -> List[Dict]:
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
                        
                        for event in data.get("_embedded", {}).get("events", [])[:10]:
                            events.append({
                                "name": event.get("name"),
                                "type": event.get("classifications", [{}])[0].get("segment", {}).get("name", "Event"),
                                "description": event.get("info", ""),
                                "date": event.get("dates", {}).get("start", {}).get("localDate"),
                                "time": event.get("dates", {}).get("start", {}).get("localTime"),
                                "venue": event.get("_embedded", {}).get("venues", [{}])[0].get("name"),
                                "ticket_info": event.get("url", "")
                            })
                        
                        return events
        except Exception as e:
            print(f"Ticketmaster API error: {e}")
        
        return []
    
    async def get_local_tips(self, destination: str) -> Dict:
        """Get local tips - should be fetched dynamically"""
        # Return empty dict - let Perplexity provide real-time local information
        return {}