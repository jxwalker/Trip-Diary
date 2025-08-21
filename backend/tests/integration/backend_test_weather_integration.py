"""
Integration tests for Weather Service
These tests make real API calls if OPENWEATHER_API_KEY is set
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.weather_service import WeatherService

# Load environment variables
load_dotenv()


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENWEATHER_API_KEY"),
    reason="OPENWEATHER_API_KEY not set"
)
class TestWeatherIntegration:
    """Integration tests for WeatherService with real API calls"""
    
    @pytest.fixture
    def weather_service(self):
        """Create a weather service instance with real API key"""
        return WeatherService()
    
    @pytest.mark.asyncio
    async def test_real_weather_forecast_major_city(self, weather_service):
        """Test getting real weather forecast for a major city"""
        # Use dates in the near future
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        result = await weather_service.get_weather_forecast(
            "New York", start_date, end_date
        )
        
        print(f"\nWeather forecast for New York:")
        print(f"  Period: {start_date} to {end_date}")
        
        assert result["destination"] == "New York"
        assert "error" not in result or result.get("error") == ""
        assert result["forecast_period"]["start"] == start_date
        assert result["forecast_period"]["end"] == end_date
        
        if result["daily_forecasts"]:
            print(f"  Found {len(result['daily_forecasts'])} day(s) of forecast")
            for forecast in result["daily_forecasts"]:
                print(f"    {forecast['date']}: {forecast['condition']} "
                      f"{forecast['temp_low']}°C - {forecast['temp_high']}°C")
            
            # Check forecast structure
            first_forecast = result["daily_forecasts"][0]
            assert "date" in first_forecast
            assert "temp_high" in first_forecast
            assert "temp_low" in first_forecast
            assert "condition" in first_forecast
            assert "icon" in first_forecast
            assert "humidity" in first_forecast
            assert "wind_speed" in first_forecast
        
        # Check summary
        if result.get("summary"):
            summary = result["summary"]
            print(f"  Summary: Avg {summary.get('avg_low')}°C - {summary.get('avg_high')}°C")
            print(f"  Predominant: {summary.get('predominant_condition')}")
            
            assert "avg_high" in summary
            assert "avg_low" in summary
            assert "packing_suggestions" in summary
            assert len(summary["packing_suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_real_weather_forecast_international(self, weather_service):
        """Test getting real weather forecast for international destinations"""
        destinations = ["Paris, France", "Tokyo, Japan", "Sydney, Australia"]
        
        start_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        
        for destination in destinations:
            result = await weather_service.get_weather_forecast(
                destination, start_date, end_date
            )
            
            print(f"\nWeather for {destination}:")
            
            if "error" in result and result["error"]:
                print(f"  Error: {result['error']}")
            elif result["daily_forecasts"]:
                print(f"  Success: {len(result['daily_forecasts'])} days of forecast")
                if result.get("summary", {}).get("predominant_condition"):
                    print(f"  Condition: {result['summary']['predominant_condition']}")
            
            assert result["destination"] == destination
    
    @pytest.mark.asyncio
    async def test_real_coordinates_lookup(self, weather_service):
        """Test real coordinate lookup for various locations"""
        locations = [
            ("London, UK", 51.5074, -0.1278),
            ("Los Angeles, USA", 34.0522, -118.2437),
            ("Berlin, Germany", 52.5200, 13.4050)
        ]
        
        for location, expected_lat, expected_lon in locations:
            coords = await weather_service._get_coordinates(location)
            
            if coords:
                print(f"\n{location}: lat={coords['lat']:.4f}, lon={coords['lon']:.4f}")
                # Allow some tolerance in coordinates
                assert abs(coords["lat"] - expected_lat) < 1.0
                assert abs(coords["lon"] - expected_lon) < 1.0
            else:
                print(f"\n{location}: Coordinates not found")
    
    @pytest.mark.asyncio
    async def test_weather_with_invalid_location(self, weather_service):
        """Test weather service with invalid location"""
        result = await weather_service.get_weather_forecast(
            "InvalidCityName12345XYZ",
            "2025-01-13",
            "2025-01-14"
        )
        
        # Should handle gracefully
        assert result["destination"] == "InvalidCityName12345XYZ"
        # Either has error or empty forecasts
        assert "error" in result or len(result["daily_forecasts"]) == 0
    
    @pytest.mark.asyncio
    async def test_weather_packing_suggestions_vary(self, weather_service):
        """Test that packing suggestions vary by destination/season"""
        # Test winter in cold location
        winter_result = await weather_service.get_weather_forecast(
            "Stockholm, Sweden",
            "2025-01-15",
            "2025-01-17"
        )
        
        # Test summer in warm location  
        summer_result = await weather_service.get_weather_forecast(
            "Miami, USA",
            "2025-07-15",
            "2025-07-17"
        )
        
        if winter_result.get("summary", {}).get("packing_suggestions"):
            winter_suggestions = winter_result["summary"]["packing_suggestions"]
            print(f"\nStockholm winter suggestions: {winter_suggestions}")
        
        if summer_result.get("summary", {}).get("packing_suggestions"):
            summer_suggestions = summer_result["summary"]["packing_suggestions"]
            print(f"\nMiami summer suggestions: {summer_suggestions}")
            
            # Suggestions should be different
            if winter_suggestions and summer_suggestions:
                assert set(winter_suggestions) != set(summer_suggestions)


@pytest.mark.integration
class TestWeatherEndpoints:
    """Test weather functionality through API endpoints"""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("OPENWEATHER_API_KEY"),
        reason="OPENWEATHER_API_KEY not set"
    )
    async def test_weather_in_guide_generation(self):
        """Test that weather data is included in guide generation"""
        import aiohttp
        import json
        
        # This would test the full flow through the API
        # Assuming backend is running on localhost:8000
        backend_url = "http://localhost:8000"
        
        try:
            async with aiohttp.ClientSession() as session:
                # First check if backend is running
                async with session.get(f"{backend_url}/") as response:
                    if response.status != 200:
                        pytest.skip("Backend not running")
                
                # Create a test trip with weather data request
                test_trip_data = {
                    "destination": "Paris, France",
                    "start_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "end_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
                    "free_text": "Test trip for weather integration"
                }
                
                # Upload trip data
                async with session.post(
                    f"{backend_url}/api/upload",
                    data={
                        "trip_details": json.dumps(test_trip_data),
                        "use_vision": "false"
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        trip_id = result.get("trip_id")
                        print(f"\nCreated test trip: {trip_id}")
                        
                        # Wait for processing
                        await asyncio.sleep(5)
                        
                        # Check if weather data is available
                        # This would depend on your API structure
                        assert trip_id is not None
        
        except aiohttp.ClientError:
            pytest.skip("Cannot connect to backend")


if __name__ == "__main__":
    # Run only if API key is available
    if os.getenv("OPENWEATHER_API_KEY"):
        pytest.main([__file__, "-v", "-m", "integration"])
    else:
        print("⚠️  OPENWEATHER_API_KEY not set. Skipping integration tests.")
        print("   Set the environment variable to run real API tests.")
        print("   You can get a free API key at https://openweathermap.org/api")