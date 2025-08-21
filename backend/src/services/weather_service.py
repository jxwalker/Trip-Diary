"""
Weather Service for Trip Diary
Provides weather forecasts and historical weather data for destinations
"""

import os
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class WeatherService:
    def __init__(self):
        # OpenWeatherMap API key - can be obtained free at openweathermap.org
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    async def get_weather_forecast(self, destination: str, start_date: str, end_date: str) -> Dict:
        """
        Get weather forecast for a destination during trip dates
        
        Args:
            destination: City name or location
            start_date: Trip start date (YYYY-MM-DD)
            end_date: Trip end date (YYYY-MM-DD)
            
        Returns:
            Weather forecast data with daily conditions
        """
        
        # If no API key, return empty with error (no mocks)
        if not self.api_key:
            return {
                "destination": destination,
                "forecast_period": {"start": start_date, "end": end_date},
                "daily_forecasts": [],
                "summary": {},
                "error": "OPENWEATHER_API_KEY not configured"
            }
        
        try:
            # Get coordinates for the destination
            coords = await self._get_coordinates(destination)
            if not coords:
                return {
                    "destination": destination,
                    "forecast_period": {"start": start_date, "end": end_date},
                    "daily_forecasts": [],
                    "summary": {},
                    "error": f"Location '{destination}' not found"
                }
            
            # Get forecast data
            forecast_url = f"{self.base_url}/forecast?lat={coords['lat']}&lon={coords['lon']}&appid={self.api_key}&units=metric"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(forecast_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_forecast(data, destination, start_date, end_date)
                    else:
                        return {
                            "destination": destination,
                            "forecast_period": {"start": start_date, "end": end_date},
                            "daily_forecasts": [],
                            "summary": {},
                            "error": "OpenWeather forecast unavailable"
                        }
                        
        except Exception as e:
            print(f"Weather API error: {e}")
            return {
                "destination": destination,
                "forecast_period": {"start": start_date, "end": end_date},
                "daily_forecasts": [],
                "summary": {},
                "error": str(e)
            }
    
    async def _get_coordinates(self, location: str) -> Optional[Dict]:
        """Get latitude and longitude for a location"""
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(geo_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:
                            return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
        except:
            pass
        return None
    
    def _format_forecast(self, data: Dict, destination: str, start_date: str, end_date: str) -> Dict:
        """Format OpenWeatherMap data into our structure"""
        daily_forecasts = []
        
        # Group forecasts by day
        by_day = {}
        for item in data.get("list", []):
            date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
            if date not in by_day:
                by_day[date] = []
            by_day[date].append(item)
        
        # Process each day
        for date_str in sorted(by_day.keys()):
            if start_date <= date_str <= end_date:
                day_data = by_day[date_str]
                
                # Calculate daily summary
                temps = [d["main"]["temp"] for d in day_data]
                conditions = [d["weather"][0]["main"] for d in day_data]
                
                # Most common condition
                most_common_condition = max(set(conditions), key=conditions.count)
                
                daily_forecasts.append({
                    "date": date_str,
                    "temp_high": round(max(temps)),
                    "temp_low": round(min(temps)),
                    "condition": most_common_condition,
                    "description": day_data[0]["weather"][0]["description"],
                    "humidity": sum([d["main"]["humidity"] for d in day_data]) // len(day_data),
                    "wind_speed": sum([d["wind"]["speed"] for d in day_data]) / len(day_data),
                    "icon": self._get_weather_icon(most_common_condition)
                })
        
        return {
            "destination": destination,
            "forecast_period": {
                "start": start_date,
                "end": end_date
            },
            "daily_forecasts": daily_forecasts,
            "summary": self._generate_weather_summary(daily_forecasts)
        }
    
    def _get_weather_icon(self, condition: str) -> str:
        """Map weather conditions to emoji icons"""
        icons = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️",
            "Haze": "🌫️"
        }
        return icons.get(condition, "🌤️")
    
    def _generate_weather_summary(self, forecasts: List[Dict]) -> Dict:
        """Generate a summary of the weather forecast"""
        if not forecasts:
            return {}
        
        temps = [f["temp_high"] for f in forecasts]
        conditions = [f["condition"] for f in forecasts]
        
        return {
            "avg_high": round(sum(temps) / len(temps)),
            "avg_low": round(sum([f["temp_low"] for f in forecasts]) / len(forecasts)),
            "predominant_condition": max(set(conditions), key=conditions.count),
            "packing_suggestions": self._get_packing_suggestions(forecasts)
        }
    
    def _get_packing_suggestions(self, forecasts: List[Dict]) -> List[str]:
        """Generate packing suggestions based on weather"""
        suggestions = ["Comfortable walking shoes", "Sunglasses"]
        
        # Check temperatures
        temps = [f["temp_high"] for f in forecasts] + [f["temp_low"] for f in forecasts]
        avg_temp = sum(temps) / len(temps)
        
        if avg_temp < 10:
            suggestions.extend(["Warm jacket", "Gloves", "Scarf"])
        elif avg_temp < 20:
            suggestions.extend(["Light jacket", "Long pants", "Sweater"])
        else:
            suggestions.extend(["Light clothing", "Shorts", "T-shirts"])
        
        # Check for rain
        if any("rain" in f["condition"].lower() for f in forecasts):
            suggestions.extend(["Umbrella", "Rain jacket"])
        
        # Check for sun
        if any(f["condition"] == "Clear" for f in forecasts):
            suggestions.append("Sunscreen")
        
        return list(set(suggestions))  # Remove duplicates
    