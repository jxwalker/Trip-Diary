"""
Test configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_client():
    """Create a test client for synchronous tests."""
    return TestClient(app)

@pytest.fixture
def sample_trip_data():
    """Sample trip data for testing."""
    return {
        "destination": "Paris, France",
        "start_date": "2024-12-15",
        "end_date": "2024-12-20",
        "travelers": 2,
        "flights": {
            "outbound": "AA123 - JFK to CDG",
            "return": "AA456 - CDG to JFK"
        },
        "hotels": [
            {
                "name": "Hotel Plaza Athénée",
                "check_in": "2024-12-15",
                "check_out": "2024-12-20"
            }
        ]
    }

@pytest.fixture
def sample_pdf_path():
    """Create a sample PDF for testing."""
    import tempfile
    from reportlab.pdfgen import canvas
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        c = canvas.Canvas(tmp.name)
        c.drawString(100, 750, "Flight Confirmation")
        c.drawString(100, 730, "Flight: AA123")
        c.drawString(100, 710, "From: JFK to CDG")
        c.drawString(100, 690, "Date: December 15, 2024")
        c.drawString(100, 670, "Passenger: John Doe")
        c.save()
        return tmp.name

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "flights": [
            {
                "flight_number": "AA123",
                "airline": "American Airlines",
                "departure_airport": "JFK",
                "arrival_airport": "CDG",
                "departure_time": "10:00 PM",
                "arrival_time": "11:30 AM",
                "date": "2024-12-15"
            }
        ],
        "hotels": [
            {
                "name": "Hotel Plaza Athénée",
                "address": "25 Avenue Montaigne, Paris",
                "check_in_date": "2024-12-15",
                "check_out_date": "2024-12-20",
                "confirmation_number": "HTL123456"
            }
        ],
        "destination": "Paris, France",
        "dates": {
            "start_date": "2024-12-15",
            "end_date": "2024-12-20"
        },
        "travelers": [
            {"name": "John Doe", "type": "adult"}
        ],
        "confirmation_numbers": ["AA123456", "HTL123456"]
    }