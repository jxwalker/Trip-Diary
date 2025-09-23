"""
Enhanced Weather Service Implementation
Real weather data integration using OpenWeatherMap API with new interface
"""
import asyncio
import aiohttp
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from .interfaces import (
    WeatherServiceInterface,
    ExternalRequest,
    ExternalResponse,
    RequestMethod,
    ServiceConfig
)
from ..core.exceptions import ServiceError, ConfigurationError, ValidationError
from ..config import get_settings
from .enhanced_redis_cache import cache_manager

logger = logging.getLogger(__name__)


class EnhancedWeatherService(WeatherServiceInterface):
    """Enhanced OpenWeatherMap weather service implementation"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        if config is None:
            settings = get_settings()
            config = ServiceConfig(
                enabled=settings.services.weather_enabled,
                timeout_seconds=settings.services.weather_timeout,
                retry_attempts=3,
                cache_enabled=True,
                cache_ttl_seconds=1800  # 30 minutes cache for weather data
            )
        
        super().__init__(config, logger)
        
        self.settings = get_settings()
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    @property
    def service_name(self) -> str:
        """Get the service name"""
        return "Enhanced OpenWeatherMap"
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the service"""
        return "https://api.openweathermap.org/data/2.5"
    
    @property
    def api_key_required(self) -> bool:
        """Check if API key is required"""
        return True
    
    async def initialize(self) -> None:
        """Initialize the weather service"""
        try:
            if not self.settings.services.weather_api_key:
                raise ConfigurationError("Weather API key not configured")
            
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            self._session = aiohttp.ClientSession(timeout=timeout)
            
            # Validate API key
            if not await self.validate_api_key():
                raise ConfigurationError("Invalid weather API key")
            
            logger.info("Enhanced weather service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced weather service: {e}")
            raise ConfigurationError(
                f"Enhanced weather service initialization failed: {e}"
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check weather service health"""
        try:
            # Test with a simple weather request
            test_weather = await self.get_current_weather(
                "London", units="metric"
            )
            
            return {
                "status": "healthy",
                "service_name": self.service_name,
                "base_url": self.base_url,
                "api_key_configured": bool(
                    self.settings.services.weather_api_key
                ),
                "test_request_success": "main" in test_weather,
                "cache_size": len(self._cache),
                "cache_enabled": self.config.cache_enabled,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service_name": self.service_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self) -> None:
        """Cleanup weather service resources"""
        if self._session:
            await self._session.close()
        
        self._cache.clear()
        logger.info("Enhanced weather service cleanup completed")
    
    async def make_request(self, request: ExternalRequest) -> ExternalResponse:
        """Make a request to the weather service"""
        try:
            if not self._session:
                raise ServiceError("Weather service not initialized")
            
            # Add API key to parameters
            request.params["appid"] = self.settings.services.weather_api_key
            
            start_time = datetime.now()
            
            async with self._session.request(
                method=request.method.value,
                url=request.url,
                params=request.params,
                json=request.data if request.method != RequestMethod.GET else None,
                headers=request.headers
            ) as response:
                response_time = (
                    (datetime.now() - start_time).total_seconds() * 1000
                )
                
                if response.status == 200:
                    data = await response.json()
                    return ExternalResponse(
                        status_code=response.status,
                        data=data,
                        response_time_ms=response_time
                    )
                else:
                    error_text = await response.text()
                    return ExternalResponse(
                        status_code=response.status,
                        error=f"Weather API error: {error_text}",
                        response_time_ms=response_time
                    )
                    
        except asyncio.TimeoutError:
            raise ServiceError(
                "Weather service request timeout", 
                service_name=self.service_name
            )
        except Exception as e:
            raise ServiceError(
                f"Weather service request failed: {e}", 
                service_name=self.service_name
            )
    
    async def validate_api_key(self) -> bool:
        """Validate the API key"""
        try:
            # Test with a simple request
            await self.get_current_weather("London", units="metric")
            return True
        except Exception:
            return False
    
    async def get_current_weather(
        self,
        location: str,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """Get current weather for location with Redis caching"""
        try:
            # Create cache key for Redis
            cache_key_data = {
                "location": location.lower(),
                "units": units,
                "type": "current"
            }
            
            # Check Redis cache first
            if self.config.cache_enabled:
                cached_data = await cache_manager.get(
                    "weather_data", cache_key_data
                )
                if cached_data:
                    logger.info(f"Redis cache HIT for weather: {location}")
                    return cached_data
            
            # Check memory cache as fallback
            memory_cache_key = f"current_{location}_{units}"
            if self.config.cache_enabled and memory_cache_key in self._cache:
                cached_data = self._cache[memory_cache_key]
                if (datetime.now() - cached_data["timestamp"] < 
                    timedelta(seconds=self.config.cache_ttl_seconds)):
                    logger.debug(f"Memory cache HIT for weather: {location}")
                    # Also store in Redis for next time
                    await cache_manager.set(
                        "weather_data", cache_key_data, cached_data["data"]
                    )
                    return cached_data["data"]
            
            # Build request
            request = self.build_request(
                endpoint="weather",
                params={
                    "q": location,
                    "units": units
                }
            )
            
            # Make request
            response = await self.make_request(request)
            
            if not response.is_success:
                raise ServiceError(f"Weather request failed: {response.error}")
            
            # Enhance response data
            enhanced_data = self._enhance_current_weather(response.data)
            
            # Cache result in both Redis and memory
            if self.config.cache_enabled:
                # Store in Redis
                await cache_manager.set("weather_data", cache_key_data, enhanced_data)
                # Store in memory cache
                self._cache[memory_cache_key] = {
                    "data": enhanced_data,
                    "timestamp": datetime.now()
                }
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Failed to get current weather for {location}: {e}")
            raise ServiceError(f"Current weather request failed: {e}")
    
    async def get_weather_forecast(
        self,
        location: str,
        days: int = 5,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """Get weather forecast for location"""
        try:
            # Validate days parameter
            if days < 1 or days > 5:
                raise ValidationError(
                    "Days must be between 1 and 5 for free tier"
                )
            
            # Check cache first
            cache_key = f"forecast_{location}_{days}_{units}"
            if self.config.cache_enabled and cache_key in self._cache:
                cached_data = self._cache[cache_key]
                if (datetime.now() - cached_data["timestamp"] < 
                    timedelta(seconds=self.config.cache_ttl_seconds)):
                    logger.debug(
                        f"Returning cached forecast data for {location}"
                    )
                    return cached_data["data"]
            
            # Build request
            request = self.build_request(
                endpoint="forecast",
                params={
                    "q": location,
                    "units": units,
                    "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
                }
            )
            
            # Make request
            response = await self.make_request(request)
            
            if not response.is_success:
                raise ServiceError(f"Forecast request failed: {response.error}")
            
            # Process forecast data
            processed_data = self._process_forecast_data(response.data, days)
            
            # Cache result
            if self.config.cache_enabled:
                self._cache[cache_key] = {
                    "data": processed_data,
                    "timestamp": datetime.now()
                }
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to get weather forecast for {location}: {e}")
            raise ServiceError(f"Weather forecast request failed: {e}")
    
    async def get_weather_for_dates(
        self,
        location: str,
        start_date: str,
        end_date: str,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """Get weather for specific date range"""
        try:
            # Parse dates
            start_dt = datetime.fromisoformat(
                start_date.replace('Z', '+00:00')
            )
            end_dt = datetime.fromisoformat(
                end_date.replace('Z', '+00:00')
            )
            
            # Check if dates are in the future (use forecast)
            now = datetime.now()
            if start_dt > now:
                days = min((end_dt - start_dt).days + 1, 5)
                forecast_data = await self.get_weather_forecast(
                    location, days, units
                )
                
                # Filter forecast to date range
                filtered_forecasts = []
                for daily in forecast_data.get("daily_forecasts", []):
                    forecast_date = datetime.fromisoformat(daily["date"])
                    if (start_dt.date() <= forecast_date.date() <= 
                        end_dt.date()):
                        filtered_forecasts.append(daily)
                
                return {
                    "location": location,
                    "start_date": start_date,
                    "end_date": end_date,
                    "forecast_days": len(filtered_forecasts),
                    "daily_forecasts": filtered_forecasts,
                    "units": units
                }
            
            # For current/past dates, get current weather
            current = await self.get_current_weather(location, units)
            
            return {
                "location": location,
                "start_date": start_date,
                "end_date": end_date,
                "current_weather": current,
                "note": "Historical weather data requires premium API access",
                "units": units
            }
            
        except Exception as e:
            logger.error(
                f"Failed to get weather for date range {start_date} to {end_date}: {e}"
            )
            raise ServiceError(f"Weather date range request failed: {e}")
    
    async def get_travel_weather_summary(
        self,
        location: str,
        start_date: str,
        end_date: str,
        units: str = "metric"
    ) -> Dict[str, Any]:
        """Get travel-specific weather summary"""
        try:
            weather_data = await self.get_weather_for_dates(location, start_date, end_date, units)
            
            # Generate travel recommendations
            recommendations = self._generate_travel_recommendations(weather_data)
            
            return {
                **weather_data,
                "travel_recommendations": recommendations,
                "packing_suggestions": self._generate_packing_suggestions(weather_data),
                "activity_recommendations": self._generate_activity_recommendations(weather_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to get travel weather summary: {e}")
            raise ServiceError(f"Travel weather summary failed: {e}")
    
    def _enhance_current_weather(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance current weather data with additional insights"""
        try:
            enhanced = raw_data.copy()
            
            # Add comfort index
            temp = raw_data["main"]["temp"]
            humidity = raw_data["main"]["humidity"]
            enhanced["comfort_index"] = self._calculate_comfort_index(temp, humidity)
            
            # Add travel suitability
            enhanced["travel_suitability"] = self._assess_travel_suitability(raw_data)
            
            # Add clothing recommendations
            enhanced["clothing_recommendations"] = self._get_clothing_recommendations(temp, raw_data["weather"][0]["main"])
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Failed to enhance weather data: {e}")
            return raw_data
    
    def _process_forecast_data(self, raw_data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Process raw forecast data into structured format"""
        try:
            forecasts = raw_data.get("list", [])
            city = raw_data.get("city", {})
            
            # Group forecasts by day
            daily_forecasts = {}
            for forecast in forecasts[:days * 8]:  # Limit to requested days
                dt = datetime.fromtimestamp(forecast["dt"])
                date_key = dt.strftime("%Y-%m-%d")
                
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = {
                        "date": date_key,
                        "forecasts": [],
                        "temp_min": float('inf'),
                        "temp_max": float('-inf'),
                        "conditions": [],
                        "precipitation_chance": 0
                    }
                
                daily_forecasts[date_key]["forecasts"].append(forecast)
                
                # Track min/max temperatures
                temp = forecast["main"]["temp"]
                daily_forecasts[date_key]["temp_min"] = min(daily_forecasts[date_key]["temp_min"], temp)
                daily_forecasts[date_key]["temp_max"] = max(daily_forecasts[date_key]["temp_max"], temp)
                
                # Collect weather conditions
                for weather in forecast["weather"]:
                    condition = weather["main"]
                    if condition not in daily_forecasts[date_key]["conditions"]:
                        daily_forecasts[date_key]["conditions"].append(condition)
                
                # Track precipitation
                if "rain" in forecast or "snow" in forecast:
                    daily_forecasts[date_key]["precipitation_chance"] = max(
                        daily_forecasts[date_key]["precipitation_chance"],
                        forecast.get("pop", 0) * 100
                    )
            
            # Add travel recommendations for each day
            for day_data in daily_forecasts.values():
                day_data["travel_recommendation"] = self._get_daily_travel_recommendation(day_data)
            
            return {
                "location": city.get("name", "Unknown"),
                "country": city.get("country", "Unknown"),
                "days": days,
                "daily_forecasts": list(daily_forecasts.values()),
                "summary": self._generate_forecast_summary(list(daily_forecasts.values()))
            }
            
        except Exception as e:
            logger.error(f"Failed to process forecast data: {e}")
            return {"error": f"Failed to process forecast data: {e}"}
    
    def _calculate_comfort_index(self, temp: float, humidity: float) -> str:
        """Calculate comfort index based on temperature and humidity"""
        # Simple comfort index calculation
        if temp < 10:
            return "Cold"
        elif temp > 30:
            return "Hot"
        elif humidity > 80:
            return "Humid"
        elif 18 <= temp <= 24 and humidity <= 60:
            return "Comfortable"
        else:
            return "Moderate"
    
    def _assess_travel_suitability(self, weather_data: Dict[str, Any]) -> str:
        """Assess travel suitability based on weather conditions"""
        main_condition = weather_data["weather"][0]["main"].lower()
        temp = weather_data["main"]["temp"]
        
        if main_condition in ["thunderstorm", "tornado"]:
            return "Poor - Severe weather"
        elif main_condition in ["rain", "drizzle"] and temp < 5:
            return "Poor - Cold and wet"
        elif main_condition == "snow":
            return "Fair - Snowy conditions"
        elif main_condition in ["rain", "drizzle"]:
            return "Fair - Rainy weather"
        elif temp < 0 or temp > 40:
            return "Fair - Extreme temperatures"
        else:
            return "Good - Suitable for travel"
    
    def _get_clothing_recommendations(self, temp: float, condition: str) -> List[str]:
        """Get clothing recommendations based on weather"""
        recommendations = []
        
        if temp < 0:
            recommendations.extend(["Heavy winter coat", "Warm layers", "Insulated boots", "Gloves and hat"])
        elif temp < 10:
            recommendations.extend(["Warm jacket", "Long pants", "Closed shoes", "Light layers"])
        elif temp < 20:
            recommendations.extend(["Light jacket", "Long or short pants", "Comfortable shoes"])
        elif temp < 30:
            recommendations.extend(["Light clothing", "Shorts or light pants", "Breathable fabrics"])
        else:
            recommendations.extend(["Very light clothing", "Shorts", "Sandals", "Sun protection"])
        
        if condition.lower() in ["rain", "drizzle", "thunderstorm"]:
            recommendations.extend(["Waterproof jacket", "Umbrella", "Waterproof shoes"])
        elif condition.lower() == "snow":
            recommendations.extend(["Waterproof boots", "Warm socks", "Snow gear"])
        
        return recommendations
    
    def _get_daily_travel_recommendation(self, day_data: Dict[str, Any]) -> str:
        """Get travel recommendation for a specific day"""
        temp_min = day_data["temp_min"]
        temp_max = day_data["temp_max"]
        conditions = day_data["conditions"]
        precipitation = day_data["precipitation_chance"]
        
        if "Thunderstorm" in conditions:
            return "Indoor activities recommended - Severe weather expected"
        elif precipitation > 70:
            return "Pack rain gear - High chance of precipitation"
        elif temp_max > 35:
            return "Stay hydrated - Very hot weather"
        elif temp_min < 0:
            return "Dress warmly - Freezing temperatures"
        elif "Clear" in conditions and 15 <= temp_max <= 25:
            return "Perfect weather for outdoor activities"
        else:
            return "Good weather for most activities"
    
    def _generate_forecast_summary(self, daily_forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of forecast period"""
        if not daily_forecasts:
            return {}
        
        temps = []
        all_conditions = []
        total_precipitation = 0
        
        for day in daily_forecasts:
            temps.extend([day["temp_min"], day["temp_max"]])
            all_conditions.extend(day["conditions"])
            total_precipitation += day["precipitation_chance"]
        
        return {
            "temp_range": {
                "min": min(temps),
                "max": max(temps)
            },
            "dominant_conditions": list(set(all_conditions)),
            "avg_precipitation_chance": total_precipitation / len(daily_forecasts),
            "overall_recommendation": self._get_overall_recommendation(daily_forecasts)
        }
    
    def _get_overall_recommendation(self, daily_forecasts: List[Dict[str, Any]]) -> str:
        """Get overall recommendation for the forecast period"""
        severe_days = sum(1 for day in daily_forecasts if "Thunderstorm" in day["conditions"])
        rainy_days = sum(1 for day in daily_forecasts if day["precipitation_chance"] > 50)
        
        if severe_days > len(daily_forecasts) / 2:
            return "Consider postponing outdoor activities - Frequent severe weather"
        elif rainy_days > len(daily_forecasts) / 2:
            return "Pack rain gear and plan indoor alternatives"
        else:
            return "Generally good weather for travel activities"
    
    def _generate_travel_recommendations(self, weather_data: Dict[str, Any]) -> List[str]:
        """Generate travel-specific recommendations"""
        recommendations = []
        
        if "daily_forecasts" in weather_data:
            for day in weather_data["daily_forecasts"]:
                if day["precipitation_chance"] > 60:
                    recommendations.append("Pack waterproof clothing and umbrella")
                    break
        
        if "current_weather" in weather_data:
            temp = weather_data["current_weather"]["main"]["temp"]
            if temp > 30:
                recommendations.append("Stay hydrated and seek shade during peak hours")
            elif temp < 5:
                recommendations.append("Dress in warm layers and protect extremities")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_packing_suggestions(self, weather_data: Dict[str, Any]) -> List[str]:
        """Generate packing suggestions based on weather"""
        suggestions = []
        
        # Add temperature-based suggestions
        if "current_weather" in weather_data:
            temp = weather_data["current_weather"]["main"]["temp"]
            suggestions.extend(self._get_clothing_recommendations(temp, "Clear"))
        
        # Add condition-based suggestions
        if "daily_forecasts" in weather_data:
            has_rain = any(day["precipitation_chance"] > 30 for day in weather_data["daily_forecasts"])
            if has_rain:
                suggestions.extend(["Waterproof jacket", "Umbrella"])
        
        return list(set(suggestions))
    
    def _generate_activity_recommendations(self, weather_data: Dict[str, Any]) -> List[str]:
        """Generate activity recommendations based on weather"""
        activities = []
        
        if "daily_forecasts" in weather_data:
            for day in weather_data["daily_forecasts"]:
                if "Clear" in day["conditions"] and day["temp_max"] < 30:
                    activities.append("Outdoor sightseeing and walking tours")
                elif day["precipitation_chance"] > 50:
                    activities.append("Museums and indoor attractions")
                elif day["temp_max"] > 30:
                    activities.append("Early morning or evening outdoor activities")
        
        return list(set(activities))
