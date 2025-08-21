"""
Integration tests for Maps Service
These tests make real API calls if GOOGLE_MAPS_API_KEY is set
"""

import pytest
import os
from pathlib import Path
import sys

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.maps_service import MapsService


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("GOOGLE_MAPS_API_KEY"),
    reason="GOOGLE_MAPS_API_KEY not set"
)
class TestMapsIntegration:
    @pytest.fixture
    def maps_service(self):
        return MapsService()

    @pytest.mark.asyncio
    async def test_real_travel_time(self, maps_service):
        result = await maps_service.get_travel_time(
            "Times Square, New York", "Central Park, New York", mode="walking"
        )
        # Structure assertions
        assert "distance" in result
        assert "duration" in result
        assert "duration_value" in result
        # If API responds OK, distance/duration should be non-empty
        if not result.get("error"):
            assert isinstance(result["duration_value"], int)

    @pytest.mark.asyncio
    async def test_real_place_details(self, maps_service):
        details = await maps_service.get_place_details("Eiffel Tower")
        assert details["name"]
        if not details.get("error"):
            assert details["location"] is None or (
                isinstance(details["location"], dict) and "lat" in details["location"]
            )

    @pytest.mark.asyncio
    async def test_real_geocode(self, maps_service):
        lat, lng = await maps_service.geocode_address(
            "1600 Amphitheatre Parkway, Mountain View, CA"
        )
        # Near Googleplex (approx)
        assert 37.0 <= lat <= 38.0
        assert -123.0 <= lng <= -121.0

    def test_static_map_url_builds(self, maps_service):
        url = maps_service.get_static_map_url([
            {"address": "Times Square, New York"},
            {"address": "Central Park, New York"}
        ])
        assert isinstance(url, str)
        if os.getenv("GOOGLE_MAPS_API_KEY"):
            assert "maps.googleapis.com" in url
            assert "markers" in url
