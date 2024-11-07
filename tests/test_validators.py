import pytest
from src.validators.content_validator import ContentValidator
from src.models.exceptions import PDFReadError, NoTravelContentError

def test_validate_content_length():
    """Test content length validation."""
    with pytest.raises(PDFReadError):
        ContentValidator.validate_content_length("short", "test.pdf")
    
    # Should not raise an exception
    ContentValidator.validate_content_length("x" * 100, "test.pdf")

def test_validate_travel_content():
    """Test travel content validation."""
    valid_content = "This is a flight booking with reference number"
    invalid_content = "This is a regular document about programming"
    
    # Should not raise an exception
    ContentValidator.validate_travel_content(valid_content, "test.pdf")
    
    with pytest.raises(NoTravelContentError):
        ContentValidator.validate_travel_content(invalid_content, "test.pdf")

def test_validate_itinerary_data(sample_itinerary):
    """Test itinerary data validation."""
    # Should not raise an exception
    ContentValidator.validate_itinerary_data(sample_itinerary, "test.pdf")
    
    # Test missing required fields
    invalid_itinerary = {"some_field": "value"}
    with pytest.raises(NoTravelContentError):
        ContentValidator.validate_itinerary_data(invalid_itinerary, "test.pdf")

def test_validate_itinerary_empty_flights():
    """Test validation of itinerary with empty flights list."""
    itinerary = {
        "booking_reference": "ABC123",
        "flights": []
    }
    
    with pytest.raises(NoTravelContentError) as exc_info:
        ContentValidator.validate_itinerary_data(itinerary, "test.pdf")
    assert "Missing required fields" in str(exc_info.value)

def test_validate_file_not_found():
    """Test validation of non-existent file."""
    with pytest.raises(PDFReadError) as exc_info:
        ContentValidator.validate_file("nonexistent.pdf")
    assert "File not found" in str(exc_info.value)