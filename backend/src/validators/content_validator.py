from pathlib import Path
import logging
from typing import Dict, Any
from pydantic import ValidationError
from ..models.exceptions import PDFReadError, NoTravelContentError
from ..parsers import TravelDataParser

logger = logging.getLogger(__name__)

class ContentValidator:
    """Validates PDF content and parsed itinerary data."""


    # Common travel-related keywords to check for
    TRAVEL_KEYWORDS = {
        'flight', 'booking', 'reference', 'departure', 'arrival',
        'airline', 'airport', 'hotel', 'reservation'
    }


    # Minimum content length to be considered valid
    MIN_CONTENT_LENGTH = 50


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
    def validate_itinerary_data(
        cls, itinerary: Dict[str, Any], file_path: str
    ) -> None:
        """
        Validate parsed itinerary data against our models.


        Args:
            itinerary: Dictionary containing parsed itinerary data
            file_path: Source file path for error messages


        Raises:
            ValueError: If validation fails
        """
        try:
            # Use parser to validate structure
            parsed_data = TravelDataParser.parse_itinerary(itinerary)


            # Check for parsing errors
            if parsed_data['errors']:
                raise ValueError(
                    f"Validation errors in {file_path}:\n" +
                    "\n".join(f"- {error}" for error in parsed_data['errors'])
                )


            # Ensure we have basic required data
            if not parsed_data['passengers']:
                raise ValueError(
                    f"No valid passenger information found in {file_path}"
                )


            if not parsed_data['flights']:
                raise ValueError(
                    f"No valid flight information found in {file_path}"
                )


        except ValidationError as e:
            # Handle Pydantic validation errors
            error_messages = []
            for error in e.errors():
                location = " -> ".join(str(loc) for loc in error["loc"])
                error_messages.append(f"{location}: {error['msg']}")


            raise ValueError(
                f"Data validation failed for {file_path}:\n" +
                "\n".join(f"- {msg}" for msg in error_messages)
            )
            
        except Exception as e:
            raise ValueError(f"Validation failed for {file_path}: {str(e)}")


    @staticmethod
    def validate_dates(start_date: str, end_date: str, context: str) -> None:
        """
        Validate that dates are in correct order.


        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            context: Context for error message


        Raises:
            ValueError: If dates are invalid
        """
        if start_date > end_date:
            raise ValueError(
                f"Invalid date range in {context}: "
                f"start date {start_date} is after end date {end_date}"
            )
