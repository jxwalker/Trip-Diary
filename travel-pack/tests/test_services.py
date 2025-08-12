"""
Test service modules
"""
import pytest
import os
import sys
from pathlib import Path
import json
from unittest.mock import Mock, patch, AsyncMock

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from backend.services.pdf_processor import PDFProcessor
from backend.services.llm_extractor import LLMExtractor
from backend.services.itinerary_generator import ItineraryGenerator
from backend.services.recommendations import RecommendationsService
from backend.services.pdf_generator import TravelPackGenerator
from backend.services.maps_service import MapsService

class TestPDFProcessor:
    """Test PDF processing service."""
    
    def test_extract_text(self, sample_pdf_path):
        """Test PDF text extraction."""
        processor = PDFProcessor()
        text = processor.extract_text(sample_pdf_path)
        assert text is not None
        assert len(text) > 0
        assert "Flight" in text
        assert "AA123" in text
    
    def test_extract_metadata(self, sample_pdf_path):
        """Test PDF metadata extraction."""
        processor = PDFProcessor()
        metadata = processor.extract_metadata(sample_pdf_path)
        assert isinstance(metadata, dict)
        assert "pages" in metadata

class TestLLMExtractor:
    """Test LLM extraction service."""
    
    @pytest.mark.asyncio
    async def test_basic_extraction(self):
        """Test basic extraction without LLM."""
        extractor = LLMExtractor()
        text = "Flight AA123 from JFK to CDG on 12/15/2024. Confirmation: ABC123XYZ"
        
        # Force basic extraction by not having API clients
        extractor.openai_client = None
        extractor.claude_client = None
        
        result = await extractor.extract_travel_info(text)
        assert "flights" in result
        assert "confirmation_numbers" in result
        assert len(result["flights"]) > 0
        assert result["flights"][0]["flight_number"] == "AA123"
    
    @pytest.mark.asyncio
    @patch.dict(os.environ, {"OPENAI_MODEL": "gpt-4o-mini"})
    async def test_openai_extraction(self, mock_openai_response):
        """Test extraction with OpenAI (mocked)."""
        extractor = LLMExtractor()
        
        if extractor.openai_client:
            with patch.object(extractor.openai_client.chat.completions, 'create', 
                            new_callable=AsyncMock) as mock_create:
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = json.dumps(mock_openai_response)
                mock_create.return_value = mock_response
                
                text = "Flight AA123 from JFK to CDG"
                result = await extractor.extract_travel_info(text)
                assert "flights" in result
                assert len(result["flights"]) > 0

class TestItineraryGenerator:
    """Test itinerary generation service."""
    
    @pytest.mark.asyncio
    async def test_create_itinerary(self, mock_openai_response):
        """Test itinerary creation from extracted data."""
        generator = ItineraryGenerator()
        extracted_data = {
            "source1": mock_openai_response,
            "manual_input": {
                "destination": "Paris",
                "start_date": "2024-12-15",
                "end_date": "2024-12-20"
            }
        }
        
        itinerary = await generator.create_itinerary(extracted_data)
        assert "trip_summary" in itinerary
        assert "daily_schedule" in itinerary
        assert "flights" in itinerary
        assert "accommodations" in itinerary
        assert itinerary["trip_summary"]["destination"] == "Paris"
    
    def test_calculate_duration(self):
        """Test duration calculation."""
        generator = ItineraryGenerator()
        duration = generator._calculate_duration("2024-12-15", "2024-12-20")
        assert duration == "6 days"
        
        # Test with different format
        duration = generator._calculate_duration("12/15/2024", "12/20/2024")
        assert duration == "6 days"
    
    def test_get_currency(self):
        """Test currency detection."""
        generator = ItineraryGenerator()
        assert generator._get_currency("Paris") == "Euro (EUR)"
        assert generator._get_currency("London") == "British Pound (GBP)"
        assert generator._get_currency("New York") == "US Dollar (USD)"
        assert generator._get_currency("Tokyo") == "Japanese Yen (JPY)"

class TestRecommendationsService:
    """Test recommendations service."""
    
    @pytest.mark.asyncio
    async def test_get_recommendations(self):
        """Test getting recommendations."""
        service = RecommendationsService()
        itinerary = {
            "trip_summary": {
                "destination": "Paris, France"
            }
        }
        
        recommendations = await service.get_recommendations(itinerary)
        assert "restaurants" in recommendations
        assert "attractions" in recommendations
        assert "events" in recommendations
        assert "shopping" in recommendations
        assert "transportation" in recommendations
        assert "local_tips" in recommendations
        
        assert len(recommendations["restaurants"]) > 0
        assert len(recommendations["attractions"]) > 0
    
    @pytest.mark.asyncio
    async def test_update_with_preferences(self):
        """Test updating recommendations with preferences."""
        service = RecommendationsService()
        recommendations = {
            "restaurants": [
                {"name": "Restaurant 1", "price_range": "$", "cuisine": "French"},
                {"name": "Restaurant 2", "price_range": "$$$$", "cuisine": "Italian"},
                {"name": "Restaurant 3", "price_range": "$$", "cuisine": "Japanese"}
            ],
            "attractions": [
                {"name": "Museum", "type": "Museum"},
                {"name": "Park", "type": "Park"}
            ]
        }
        
        preferences = {
            "budget": "low",
            "cuisine_preferences": ["French"],
            "interests": ["art"]
        }
        
        updated = await service.update_with_preferences(recommendations, preferences)
        
        # Check that expensive restaurants are filtered out
        for restaurant in updated["restaurants"]:
            assert restaurant["price_range"] in ["$", "$$"]

class TestMapsService:
    """Test maps service."""
    
    @pytest.mark.asyncio
    async def test_mock_travel_time(self):
        """Test mock travel time calculation."""
        service = MapsService()
        service.client = None  # Force mock mode
        
        result = await service.get_travel_time("Hotel", "Airport", "driving")
        assert "distance" in result
        assert "duration" in result
        assert "duration_value" in result
        assert "15 miles" in result["distance"]
    
    @pytest.mark.asyncio
    async def test_mock_place_details(self):
        """Test mock place details."""
        service = MapsService()
        service.client = None  # Force mock mode
        
        details = await service.get_place_details("Restaurant XYZ")
        assert details["name"] == "Restaurant XYZ"
        assert "address" in details
        assert "rating" in details
        assert "hours" in details
    
    def test_static_map_url(self):
        """Test static map URL generation."""
        service = MapsService()
        service.api_key = "test_key"
        
        locations = [
            {"lat": 40.7128, "lng": -74.0060},
            {"address": "Times Square, New York"}
        ]
        
        url = service.get_static_map_url(locations)
        assert "maps.googleapis.com" in url
        assert "test_key" in url
        assert "markers" in url

class TestPDFGenerator:
    """Test PDF generation service."""
    
    @pytest.mark.asyncio
    async def test_pdf_generation(self, tmp_path):
        """Test PDF generation."""
        generator = TravelPackGenerator()
        
        itinerary = {
            "trip_summary": {
                "destination": "Paris, France",
                "start_date": "2024-12-15",
                "end_date": "2024-12-20",
                "duration": "6 days",
                "total_flights": 2,
                "total_hotels": 1
            },
            "flights": [
                {
                    "flight_number": "AA123",
                    "airline": "American Airlines",
                    "departure": {"airport": "JFK", "time": "10:00 PM", "date": "2024-12-15"},
                    "arrival": {"airport": "CDG", "time": "11:30 AM"},
                    "status": "Confirmed"
                }
            ],
            "accommodations": [
                {
                    "name": "Hotel Plaza",
                    "address": "123 Main St",
                    "check_in": "2024-12-15",
                    "check_out": "2024-12-20",
                    "confirmation": "HTL123"
                }
            ],
            "daily_schedule": [
                {
                    "day": 1,
                    "date": "2024-12-15",
                    "day_name": "Sunday",
                    "activities": ["Arrival", "Check-in"]
                }
            ],
            "important_info": {
                "currency": "Euro (EUR)",
                "check_in_time": "3:00 PM"
            }
        }
        
        recommendations = {
            "restaurants": [
                {
                    "name": "Le Restaurant",
                    "cuisine": "French",
                    "price_range": "$$$",
                    "address": "456 Ave",
                    "rating": 4.5,
                    "distance_from_hotel": "0.5 miles",
                    "must_try": ["Dish 1", "Dish 2"]
                }
            ],
            "attractions": [
                {
                    "name": "Eiffel Tower",
                    "type": "Landmark",
                    "address": "Champ de Mars",
                    "price": "€25",
                    "hours": "9:00 AM - 11:00 PM",
                    "time_needed": "2 hours"
                }
            ]
        }
        
        # Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Generate PDF without mocking Path since we have a real directory
        generator.output_dir = output_dir
        pdf_path = await generator.generate("test_trip", itinerary, recommendations)
        assert pdf_path is not None
        assert "test_trip" in pdf_path