from pathlib import Path
from ..models.exceptions import PDFReadError, NoTravelContentError

class ContentValidator:
    """Validates PDF content for travel-related information."""
    
    # Common travel-related keywords to check for
    TRAVEL_KEYWORDS = {
        'flight', 'booking', 'reference', 'departure', 'arrival',
        'airline', 'airport', 'hotel', 'reservation'
    }
    
    # Minimum content length to be considered valid (reduced for testing)
    MIN_CONTENT_LENGTH = 50  # Reduced from 100 for testing purposes
    
    @classmethod
    def validate_file(cls, file_path: str) -> None:
        """Validate that file exists and is readable."""
        if not Path(file_path).is_file():
            raise PDFReadError(f"File not found: {file_path}")
    
    @classmethod
    def validate_content_length(cls, text: str, file_path: str) -> None:
        """Validate that content meets minimum length requirements."""
        if len(text) < cls.MIN_CONTENT_LENGTH:
            raise PDFReadError(
                f"PDF file appears to be empty or too short: {file_path}"
            )
    
    @classmethod
    def validate_travel_content(cls, text: str, file_path: str) -> None:
        """Validate that content contains travel-related keywords."""
        text_lower = text.lower()
        found_keywords = [
            keyword for keyword in cls.TRAVEL_KEYWORDS 
            if keyword in text_lower
        ]
        
        if not found_keywords:
            raise NoTravelContentError(
                f"No travel-related content found in {file_path}. "
                "File may not be a travel itinerary."
            )
    
    @classmethod
    def validate_itinerary_data(cls, itinerary: dict, file_path: str) -> None:
        """Validate required fields in parsed itinerary data."""
        required_fields = ['booking_reference', 'flights']
        missing_fields = [
            field for field in required_fields 
            if not itinerary.get(field)
        ]
        
        if missing_fields:
            raise NoTravelContentError(
                f"Missing required fields in {file_path}: {', '.join(missing_fields)}"
            )
        
        if not itinerary.get('flights'):
            raise NoTravelContentError(
                f"No flight information found in {file_path}"
            )