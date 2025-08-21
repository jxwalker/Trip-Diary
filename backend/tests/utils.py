"""
Test utilities for TripCraft AI
Common testing functions, mocks, and helpers
"""
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, patch, MagicMock
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date


class TestFileManager:
    """Manages test files and cleanup"""
    
    def __init__(self):
        self.temp_dirs = []
        self.temp_files = []
    
    def create_temp_dir(self) -> Path:
        """Create a temporary directory"""
        temp_dir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def create_temp_file(self, content: str, suffix: str = ".txt") -> Path:
        """Create a temporary file with content"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        temp_path = Path(temp_file.name)
        self.temp_files.append(temp_path)
        return temp_path
    
    def create_test_pdf(self, content: str = "Test PDF content") -> Path:
        """Create a test PDF file"""
        # For testing, we'll create a simple text file with .pdf extension
        # In real tests, you might want to create actual PDF content
        return self.create_temp_file(content, suffix=".pdf")
    
    def create_test_image(self, format: str = "jpg") -> Path:
        """Create a test image file"""
        # For testing, we'll create a simple text file with image extension
        # In real tests, you might want to create actual image content
        return self.create_temp_file("Test image content", suffix=f".{format}")
    
    def cleanup(self):
        """Clean up all temporary files and directories"""
        for temp_file in self.temp_files:
            if temp_file.exists():
                temp_file.unlink()
        
        for temp_dir in self.temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        
        self.temp_files.clear()
        self.temp_dirs.clear()


class MockAPIResponse:
    """Mock API response for external services"""
    
    def __init__(self, status_code: int = 200, json_data: Optional[Dict] = None, text: str = ""):
        self.status_code = status_code
        self.json_data = json_data or {}
        self.text = text
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class MockLLMService:
    """Mock LLM service for testing"""
    
    def __init__(self, responses: Optional[Dict[str, Any]] = None):
        self.responses = responses or {}
        self.call_count = 0
        self.last_prompt = None
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        self.last_prompt = prompt
        
        # Return predefined response or default
        if "extract" in prompt.lower():
            return json.dumps(self.responses.get("extraction", {
                "flights": [],
                "hotels": [],
                "passengers": []
            }))
        elif "itinerary" in prompt.lower():
            return json.dumps(self.responses.get("itinerary", {
                "trip_summary": {"destination": "Test City", "start_date": "2024-01-01", "end_date": "2024-01-03"},
                "daily_itineraries": []
            }))
        else:
            return self.responses.get("default", "Mock response")


def create_sample_trip_data() -> Dict[str, Any]:
    """Create sample trip data for testing"""
    return {
        "trip_id": "test-trip-123",
        "extracted_data": {
            "flights": [
                {
                    "flight_number": "AA123",
                    "airline": "American Airlines",
                    "departure_airport": "JFK",
                    "arrival_airport": "LAX",
                    "departure_time": "2024-01-01T10:00:00",
                    "arrival_time": "2024-01-01T13:00:00"
                }
            ],
            "hotels": [
                {
                    "name": "Test Hotel",
                    "city": "Los Angeles",
                    "check_in": "2024-01-01",
                    "check_out": "2024-01-03",
                    "confirmation_code": "TEST123"
                }
            ],
            "passengers": [
                {
                    "name": "John Doe",
                    "email": "john@example.com"
                }
            ]
        },
        "itinerary": {
            "trip_summary": {
                "destination": "Los Angeles",
                "start_date": "2024-01-01",
                "end_date": "2024-01-03",
                "duration": "3 days"
            },
            "flights": [],
            "accommodations": [],
            "daily_itineraries": []
        },
        "preferences": {
            "dining": {"cuisine_types": ["italian", "mexican"]},
            "interests": {"culture": {"museums": True, "art_galleries": True}},
            "travel_style": {"pace": "moderate", "group_type": "couple"}
        }
    }


def create_sample_preferences() -> Dict[str, Any]:
    """Create sample user preferences for testing"""
    return {
        "dining": {
            "cuisineTypes": ["italian", "mexican", "asian"],
            "dietaryRestrictions": ["vegetarian"],
            "priceRanges": ["moderate", "upscale"]
        },
        "interests": {
            "culture": {
                "museums": True,
                "art_galleries": True,
                "historical_sites": True,
                "local_festivals": False
            },
            "outdoor": {
                "hiking": True,
                "beaches": True,
                "parks": True,
                "water_sports": False
            },
            "entertainment": {
                "nightlife": False,
                "live_music": True,
                "theater": True,
                "shopping": True
            }
        },
        "travel_style": {
            "pace": "moderate",
            "groupType": "couple",
            "activityLevel": "moderate",
            "adventureLevel": "low"
        },
        "budget": {
            "range": "moderate",
            "priorities": ["experiences", "food"]
        }
    }


def assert_response_structure(response_data: Dict[str, Any], expected_keys: List[str]):
    """Assert that response has expected structure"""
    for key in expected_keys:
        assert key in response_data, f"Missing key '{key}' in response"


def assert_trip_data_structure(trip_data: Dict[str, Any]):
    """Assert that trip data has correct structure"""
    required_keys = ["trip_id", "extracted_data", "itinerary"]
    assert_response_structure(trip_data, required_keys)
    
    # Check extracted_data structure
    extracted = trip_data["extracted_data"]
    assert isinstance(extracted.get("flights", []), list)
    assert isinstance(extracted.get("hotels", []), list)
    assert isinstance(extracted.get("passengers", []), list)
    
    # Check itinerary structure
    itinerary = trip_data["itinerary"]
    assert "trip_summary" in itinerary
    assert isinstance(itinerary.get("daily_itineraries", []), list)


def mock_external_service(service_name: str, response_data: Any = None):
    """Create a mock for external services"""
    if service_name == "openai":
        mock = Mock()
        mock.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps(response_data or {})))]
        )
        return mock
    
    elif service_name == "anthropic":
        mock = Mock()
        mock.messages.create.return_value = Mock(
            content=[Mock(text=json.dumps(response_data or {}))]
        )
        return mock
    
    elif service_name == "perplexity":
        mock = Mock()
        mock.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps(response_data or {})))]
        )
        return mock
    
    else:
        return Mock()


@pytest.fixture
def file_manager():
    """Pytest fixture for file management"""
    manager = TestFileManager()
    yield manager
    manager.cleanup()


@pytest.fixture
def sample_trip():
    """Pytest fixture for sample trip data"""
    return create_sample_trip_data()


@pytest.fixture
def sample_preferences():
    """Pytest fixture for sample preferences"""
    return create_sample_preferences()


@pytest.fixture
def mock_llm_service():
    """Pytest fixture for mock LLM service"""
    return MockLLMService()


def create_test_client_with_mocks(app, mock_services: Optional[Dict[str, Any]] = None):
    """Create test client with mocked services"""
    client = TestClient(app)
    
    if mock_services:
        # Apply mocks to the app's dependency overrides
        for service_name, mock_service in mock_services.items():
            # This would need to be implemented based on your dependency injection setup
            pass
    
    return client


class AsyncMock(MagicMock):
    """Async mock for testing async functions"""
    
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


def create_async_mock(return_value=None):
    """Create an async mock with return value"""
    mock = AsyncMock()
    mock.return_value = return_value
    return mock
