"""
Combined integration tests for Weather + Maps services
Runs only when both OPENWEATHER_API_KEY and GOOGLE_MAPS_API_KEY are set
"""

import pytest
import os
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.weather_service import WeatherService
from services.maps_service import MapsService


both_keys_present = bool(os.getenv("OPENWEATHER_API_KEY") and os.getenv("GOOGLE_MAPS_API_KEY"))


@pytest.mark.integration
@pytest.mark.skipif(not both_keys_present, reason="Both API keys not set")
class TestWeatherMapCombined:
    @pytest.mark.asyncio
    async def test_weather_then_travel_time(self):
        weather = WeatherService()
        maps = MapsService()

        start = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

        forecast = await weather.get_weather_forecast("Paris, France", start, end)
        assert forecast["destination"] == "Paris, France"
        assert "daily_forecasts" in forecast

        # Use two well-known POIs for travel time lookup
        travel = await maps.get_travel_time("Louvre Museum, Paris", "Eiffel Tower, Paris", mode="transit")
        assert "duration_value" in travel
        # Do not assert exact values; just ensure structure
        if not travel.get("error"):
            assert isinstance(travel["duration_value"], int)
