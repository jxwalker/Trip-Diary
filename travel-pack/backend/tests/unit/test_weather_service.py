"""
Unit tests for Weather Service
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.weather_service import WeatherService


class TestWeatherService:
    """Test suite for WeatherService"""
    
    @pytest.fixture
    def weather_service(self):
        """Create a weather service instance"""
        service = WeatherService()
        service.api_key = "test_api_key"
        return service
    
    @pytest.fixture
    def sample_openweather_response(self):
        """Sample OpenWeatherMap API response"""
        return {
            "list": [
                {
                    "dt": 1736697600,  # 2025-01-13 00:00:00
                    "main": {
                        "temp": 15.5,
                        "humidity": 65
                    },
                    "weather": [{
                        "main": "Clear",
                        "description": "clear sky"
                    }],
                    "wind": {"speed": 3.5}
                },
                {
                    "dt": 1736708400,  # 2025-01-13 03:00:00
                    "main": {
                        "temp": 13.2,
                        "humidity": 70
                    },
                    "weather": [{
                        "main": "Clear",
                        "description": "clear sky"
                    }],
                    "wind": {"speed": 2.8}
                },
                {
                    "dt": 1736719200,  # 2025-01-13 06:00:00
                    "main": {
                        "temp": 18.7,
                        "humidity": 60
                    },
                    "weather": [{
                        "main": "Clouds",
                        "description": "few clouds"
                    }],
                    "wind": {"speed": 4.2}
                }
            ]
        }
    
    @pytest.fixture
    def sample_geocoding_response(self):
        """Sample geocoding API response"""
        return [
            {
                "name": "Paris",
                "lat": 48.8566,
                "lon": 2.3522,
                "country": "FR"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_get_weather_forecast_no_api_key(self):
        """Test weather forecast without API key"""
        service = WeatherService()
        service.api_key = ""
        
        result = await service.get_weather_forecast(
            "Paris", "2025-01-13", "2025-01-14"
        )
        
        assert "error" in result
        assert result["error"] == "OPENWEATHER_API_KEY not configured"
        assert result["daily_forecasts"] == []
    
    @pytest.mark.asyncio
    async def test_get_weather_forecast_success(self, weather_service, sample_openweather_response, sample_geocoding_response):
        """Test successful weather forecast retrieval"""
        
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock the context manager and responses
            mock_response_geo = AsyncMock()
            mock_response_geo.status = 200
            mock_response_geo.json = AsyncMock(return_value=sample_geocoding_response)
            
            mock_response_weather = AsyncMock()
            mock_response_weather.status = 200
            mock_response_weather.json = AsyncMock(return_value=sample_openweather_response)
            
            # Setup the mock session
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            # Mock get method to return different responses based on URL
            async def mock_get(url):
                if "geo" in url:
                    return mock_response_geo
                else:
                    return mock_response_weather
            
            mock_session_instance.get = mock_get
            
            result = await weather_service.get_weather_forecast(
                "Paris", "2025-01-13", "2025-01-14"
            )
            
            assert result["destination"] == "Paris"
            assert result["forecast_period"]["start"] == "2025-01-13"
            assert result["forecast_period"]["end"] == "2025-01-14"
            assert len(result["daily_forecasts"]) > 0
            assert "summary" in result
    
    @pytest.mark.asyncio
    async def test_get_weather_forecast_api_error(self, weather_service):
        """Test weather forecast with API error"""
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 401  # Unauthorized
            
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            
            result = await weather_service.get_weather_forecast(
                "Paris", "2025-01-13", "2025-01-14"
            )
            
            assert "error" in result or len(result["daily_forecasts"]) == 0
    
    def test_format_forecast(self, weather_service, sample_openweather_response):
        """Test forecast formatting"""
        result = weather_service._format_forecast(
            sample_openweather_response,
            "Paris",
            "2025-01-13",
            "2025-01-14"
        )
        
        assert result["destination"] == "Paris"
        assert len(result["daily_forecasts"]) == 1
        
        forecast = result["daily_forecasts"][0]
        assert forecast["date"] == "2025-01-13"
        assert forecast["temp_high"] == 19  # Rounded from 18.7
        assert forecast["temp_low"] == 13  # Rounded from 13.2
        assert forecast["condition"] == "Clear"  # Most common
        assert forecast["icon"] == "☀️"
    
    def test_get_weather_icon(self, weather_service):
        """Test weather icon mapping"""
        assert weather_service._get_weather_icon("Clear") == "☀️"
        assert weather_service._get_weather_icon("Clouds") == "☁️"
        assert weather_service._get_weather_icon("Rain") == "🌧️"
        assert weather_service._get_weather_icon("Snow") == "❄️"
        assert weather_service._get_weather_icon("Unknown") == "🌤️"  # Default
    
    def test_generate_weather_summary(self, weather_service):
        """Test weather summary generation"""
        forecasts = [
            {
                "temp_high": 25,
                "temp_low": 15,
                "condition": "Clear"
            },
            {
                "temp_high": 23,
                "temp_low": 14,
                "condition": "Clouds"
            },
            {
                "temp_high": 24,
                "temp_low": 16,
                "condition": "Clear"
            }
        ]
        
        summary = weather_service._generate_weather_summary(forecasts)
        
        assert summary["avg_high"] == 24  # (25+23+24)/3
        assert summary["avg_low"] == 15  # (15+14+16)/3
        assert summary["predominant_condition"] == "Clear"
        assert len(summary["packing_suggestions"]) > 0
    
    def test_get_packing_suggestions_cold(self, weather_service):
        """Test packing suggestions for cold weather"""
        forecasts = [
            {"temp_high": 5, "temp_low": -2, "condition": "Clear"},
            {"temp_high": 8, "temp_low": 0, "condition": "Clouds"}
        ]
        
        suggestions = weather_service._get_packing_suggestions(forecasts)
        
        assert "Warm jacket" in suggestions
        assert "Gloves" in suggestions
        assert "Scarf" in suggestions
    
    def test_get_packing_suggestions_hot(self, weather_service):
        """Test packing suggestions for hot weather"""
        forecasts = [
            {"temp_high": 32, "temp_low": 22, "condition": "Clear"},
            {"temp_high": 35, "temp_low": 24, "condition": "Clear"}
        ]
        
        suggestions = weather_service._get_packing_suggestions(forecasts)
        
        assert "Light clothing" in suggestions
        assert "Shorts" in suggestions
        assert "Sunscreen" in suggestions
    
    def test_get_packing_suggestions_rainy(self, weather_service):
        """Test packing suggestions for rainy weather"""
        forecasts = [
            {"temp_high": 20, "temp_low": 15, "condition": "Rain"},
            {"temp_high": 18, "temp_low": 14, "condition": "Drizzle"}
        ]
        
        suggestions = weather_service._get_packing_suggestions(forecasts)
        
        assert "Umbrella" in suggestions
        assert "Rain jacket" in suggestions
    
    @pytest.mark.asyncio
    async def test_get_coordinates_success(self, weather_service, sample_geocoding_response):
        """Test successful coordinate retrieval"""
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=sample_geocoding_response)
            
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            
            coords = await weather_service._get_coordinates("Paris")
            
            assert coords is not None
            assert coords["lat"] == 48.8566
            assert coords["lon"] == 2.3522
    
    @pytest.mark.asyncio
    async def test_get_coordinates_not_found(self, weather_service):
        """Test coordinate retrieval for unknown location"""
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=[])  # Empty response
            
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            mock_session_instance.get.return_value.__aenter__.return_value = mock_response
            
            coords = await weather_service._get_coordinates("UnknownPlace12345")
            
            assert coords is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])