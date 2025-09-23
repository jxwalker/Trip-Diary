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
        
        # If no API key, provide helpful error message
        if not self.api_key:
            print("[WARNING] OPENWEATHER_API_KEY not found in environment "
                  "variables")
            print("[INFO] To enable weather forecasts, get a free API key "
                  "from: https://openweathermap.org/api")
            print("[INFO] Then set OPENWEATHER_API_KEY in your environment "
                  "or .env file")
        
    async def get_weather_forecast(self, destination: str, 
                                   start_date: str, end_date: str) -> Dict:
        """
        Get weather forecast for a destination during trip dates

        Args:
            destination: City name or location
            start_date: Trip start date (YYYY-MM-DD)
            end_date: Trip end date (YYYY-MM-DD)

        Returns:
            Weather forecast data with daily conditions
        """
        
        # If no API key, return helpful information with setup instructions
        if not self.api_key:
            return {
                "destination": destination,
                "forecast_period": {"start": start_date, "end": end_date},
                "daily_forecasts": [],
                "summary": {
                    "setup_required": True,
                    "message": "Weather forecasts require an OpenWeatherMap "
                               "API key",
                    "instructions": "Get a free API key from "
                                    "https://openweathermap.org/api and set "
                                    "OPENWEATHER_API_KEY in your environment"
                },
                "error": "OPENWEATHER_API_KEY not configured"
            }
        
        # Check if dates are in the past or too far in the future
        today = datetime.now().date()
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # If trip is in the past, return historical weather info
        if end_dt < today:
            return {
                "destination": destination,
                "forecast_period": {"start": start_date, "end": end_date},
                "daily_forecasts": [],
                "summary": {
                    "message": f"Historical weather data for {destination} "
                               f"during {start_date} to {end_date}",
                    "note": "This trip occurred in the past. For current "
                            "weather forecasts, please use current or future "
                            "dates.",
                    "typical_weather": self._get_typical_weather(
                        destination, start_dt.month)
                },
                "historical": True
            }
        
        # If trip is more than 5 days in the future, return typical weather
        if start_dt > today + timedelta(days=5):
            return {
                "destination": destination,
                "forecast_period": {"start": start_date, "end": end_date},
                "daily_forecasts": [],
                "summary": {
                    "message": f"Typical weather for {destination} during "
                               f"{start_date} to {end_date}",
                    "note": "Detailed forecasts are only available for the "
                            "next 5 days. Showing typical weather patterns.",
                    "typical_weather": self._get_typical_weather(
                        destination, start_dt.month)
                },
                "typical_weather": True
            }
        
        try:
            # Check if dates are within 5-day forecast range
            # (OpenWeather free tier limitation)
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            today = datetime.now()
            days_ahead = (start_dt - today).days

            if days_ahead > 5:
                # For dates beyond 5 days, provide seasonal weather estimates
                return await self._get_seasonal_weather_estimate(
                    destination, start_date, end_date)

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
            forecast_url = (f"{self.base_url}/forecast?"
                            f"lat={coords['lat']}&lon={coords['lon']}&"
                            f"appid={self.api_key}&units=metric")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(forecast_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_forecast(
                            data, destination, start_date, end_date)
                    else:
                        return {
                            "destination": destination,
                            "forecast_period": {"start": start_date, 
                                                "end": end_date},
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
        geo_url = (f"http://api.openweathermap.org/geo/1.0/direct?"
                   f"q={location}&limit=1&appid={self.api_key}")
        
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

    async def _get_seasonal_weather_estimate(self, destination: str, 
                                             start_date: str, 
                                             end_date: str) -> Dict:
        """
        Provide seasonal weather estimates for dates beyond 5-day forecast
        Based on historical climate data for major destinations
        """
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Generate daily forecasts based on seasonal patterns
        daily_forecasts = []
        current_date = start_dt

        while current_date <= end_dt:
            month = current_date.month
            day_name = current_date.strftime("%A")

            # Get seasonal weather for this destination and month
            seasonal_data = self._get_seasonal_data(destination.lower(), month)

            daily_forecast = {
                "date": current_date.strftime("%Y-%m-%d"),
                "day_name": day_name,
                "temperature": {
                    "high": seasonal_data["temp_high"],
                    "low": seasonal_data["temp_low"],
                    "unit": "°C"
                },
                "condition": seasonal_data["condition"],
                "description": seasonal_data["description"],
                "precipitation_chance": seasonal_data["precipitation"],
                "humidity": seasonal_data["humidity"],
                "wind_speed": seasonal_data["wind_speed"],
                "source": "seasonal_estimate"
            }
            daily_forecasts.append(daily_forecast)
            current_date += timedelta(days=1)

        # Create summary
        avg_high = (sum(d["temperature"]["high"] for d in daily_forecasts) 
                    / len(daily_forecasts))
        avg_low = (sum(d["temperature"]["low"] for d in daily_forecasts) 
                   / len(daily_forecasts))

        condition = daily_forecasts[0]["condition"] if daily_forecasts else ""
        summary = {
            "average_high": round(avg_high, 1),
            "average_low": round(avg_low, 1),
            "general_conditions": condition,
            "packing_suggestions": self._get_packing_suggestions(
                avg_high, avg_low, condition),
            "note": "Weather estimates based on seasonal patterns"
        }

        return {
            "destination": destination,
            "forecast_period": {"start": start_date, "end": end_date},
            "daily_forecasts": daily_forecasts,
            "summary": summary
        }

    def _get_seasonal_data(self, destination: str, month: int) -> Dict:
        """Get seasonal weather data for destination and month"""

        # Seasonal patterns for major destinations
        seasonal_patterns = {
            "paris": {
                1: {"temp_high": 7, "temp_low": 2, "condition": "Cloudy", 
                    "description": "Cool and often rainy", "precipitation": 70, 
                    "humidity": 80, "wind_speed": 15},
                2: {"temp_high": 9, "temp_low": 3, "condition": "Partly Cloudy", 
                    "description": "Cool with occasional rain", "precipitation": 60, 
                    "humidity": 75, "wind_speed": 12},
                3: {"temp_high": 13, "temp_low": 5, "condition": "Partly Cloudy", 
                    "description": "Mild spring weather", "precipitation": 50, 
                    "humidity": 70, "wind_speed": 10},
                4: {"temp_high": 17, "temp_low": 8, "condition": "Partly Cloudy", 
                    "description": "Pleasant spring weather", "precipitation": 45, 
                    "humidity": 65, "wind_speed": 8},
                5: {"temp_high": 21, "temp_low": 12, "condition": "Sunny", 
                    "description": "Warm and pleasant", "precipitation": 40, 
                    "humidity": 60, "wind_speed": 8},
                6: {"temp_high": 24, "temp_low": 15, "condition": "Sunny", 
                    "description": "Warm summer weather", "precipitation": 35, 
                    "humidity": 55, "wind_speed": 7},
                7: {"temp_high": 26, "temp_low": 17, "condition": "Sunny", 
                    "description": "Warm and dry", "precipitation": 30, 
                    "humidity": 50, "wind_speed": 7},
                8: {"temp_high": 26, "temp_low": 17, "condition": "Sunny", 
                    "description": "Warm summer weather", "precipitation": 35, 
                    "humidity": 55, "wind_speed": 7},
                9: {"temp_high": 22, "temp_low": 13, "condition": "Partly Cloudy", 
                    "description": "Pleasant autumn weather", "precipitation": 45, 
                    "humidity": 65, "wind_speed": 9},
                10: {"temp_high": 17, "temp_low": 9, "condition": "Cloudy", 
                     "description": "Cool autumn weather", "precipitation": 55, 
                     "humidity": 75, "wind_speed": 12},
                11: {"temp_high": 11, "temp_low": 5, "condition": "Cloudy", "description": "Cool and often rainy", "precipitation": 65, "humidity": 80, "wind_speed": 14},
                12: {"temp_high": 8, "temp_low": 3, "condition": "Cloudy", "description": "Cold winter weather", "precipitation": 70, "humidity": 85, "wind_speed": 15}
            }
        }

        # Default pattern for unknown destinations (temperate climate)
        default_pattern = {
            1: {"temp_high": 5, "temp_low": 0, "condition": "Cloudy", "description": "Cool winter weather", "precipitation": 60, "humidity": 75, "wind_speed": 12},
            2: {"temp_high": 7, "temp_low": 1, "condition": "Partly Cloudy", "description": "Cool late winter", "precipitation": 55, "humidity": 70, "wind_speed": 10},
            3: {"temp_high": 12, "temp_low": 4, "condition": "Partly Cloudy", "description": "Mild spring weather", "precipitation": 50, "humidity": 65, "wind_speed": 8},
            4: {"temp_high": 16, "temp_low": 7, "condition": "Partly Cloudy", "description": "Pleasant spring", "precipitation": 45, "humidity": 60, "wind_speed": 7},
            5: {"temp_high": 20, "temp_low": 11, "condition": "Sunny", "description": "Warm late spring", "precipitation": 40, "humidity": 55, "wind_speed": 6},
            6: {"temp_high": 23, "temp_low": 14, "condition": "Sunny", "description": "Warm summer weather", "precipitation": 35, "humidity": 50, "wind_speed": 5},
            7: {"temp_high": 25, "temp_low": 16, "condition": "Sunny", "description": "Warm and pleasant", "precipitation": 30, "humidity": 45, "wind_speed": 5},
            8: {"temp_high": 24, "temp_low": 15, "condition": "Sunny", "description": "Late summer warmth", "precipitation": 35, "humidity": 50, "wind_speed": 6},
            9: {"temp_high": 20, "temp_low": 11, "condition": "Partly Cloudy", "description": "Pleasant autumn", "precipitation": 45, "humidity": 60, "wind_speed": 7},
            10: {"temp_high": 15, "temp_low": 7, "condition": "Cloudy", "description": "Cool autumn weather", "precipitation": 55, "humidity": 70, "wind_speed": 9},
            11: {"temp_high": 9, "temp_low": 3, "condition": "Cloudy", "description": "Cool late autumn", "precipitation": 60, "humidity": 75, "wind_speed": 11},
            12: {"temp_high": 6, "temp_low": 1, "condition": "Cloudy", "description": "Cold winter weather", "precipitation": 65, "humidity": 80, "wind_speed": 12}
        }

        # Check for specific destination patterns
        for dest_key in seasonal_patterns:
            if dest_key in destination:
                return seasonal_patterns[dest_key].get(month, default_pattern[month])

        return default_pattern[month]

    def _get_packing_suggestions(self, avg_high: float, avg_low: float, condition: str) -> List[str]:
        """Generate packing suggestions based on weather"""
        suggestions = []

        # Temperature-based suggestions
        if avg_high >= 25:
            suggestions.extend(["Light, breathable clothing", "Sunscreen", "Hat", "Sunglasses"])
        elif avg_high >= 20:
            suggestions.extend(["Light layers", "Comfortable walking shoes", "Light jacket for evenings"])
        elif avg_high >= 15:
            suggestions.extend(["Layers for varying temperatures", "Light sweater", "Comfortable jacket"])
        elif avg_high >= 10:
            suggestions.extend(["Warm layers", "Jacket or coat", "Long pants"])
        else:
            suggestions.extend(["Warm clothing", "Heavy coat", "Warm accessories"])

        # Condition-based suggestions
        if "cloudy" in condition.lower() or "rain" in condition.lower():
            suggestions.extend(["Umbrella or rain jacket", "Waterproof shoes"])

        if avg_low <= 5:
            suggestions.extend(["Warm sleepwear", "Extra layers for cold mornings"])

        return suggestions
    
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
            "packing_suggestions": self._get_packing_suggestions(
                round(sum(temps) / len(temps)),
                round(sum([f["temp_low"] for f in forecasts]) / len(forecasts)),
                max(set(conditions), key=conditions.count)
            )
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
    
    def _get_typical_weather(self, destination: str, month: int) -> Dict:
        """Get typical weather patterns for a destination and month - NO HARDCODED DATA"""
        # NO HARDCODED WEATHER DATA - This is a placeholder that should be replaced with real API calls
        # For now, return a generic message indicating weather data is not available
        return {
            "temp_high": None,
            "temp_low": None,
            "condition": "Weather data unavailable",
            "description": f"Weather forecast not available for {destination} in month {month}. Please check weather services directly.",
            "icon": "❓",
            "note": "No hardcoded weather data - real API integration required"
        }
    