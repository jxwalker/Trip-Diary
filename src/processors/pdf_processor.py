from typing import Dict, List, Tuple, Optional
import time
from src.gpt_interfaces.gpt_interface import GPTInterface
from src.models.exceptions import PDFReadError, NoTravelContentError
from src.utils.pdf_utils import extract_text_from_pdf
from src.validators.content_validator import ContentValidator
from src.validators.json_validator import JSONValidator
import logging
from ..models.events import Passenger
import json

logger = logging.getLogger(__name__)

class PDFProcessor:
    SYSTEM_PROMPT = """You are a travel itinerary parser. Extract all flight, hotel, and passenger information into a structured format.
    
    For dates, use YYYY-MM-DD format (e.g., 2024-12-25).
    For times, use 24-hour HH:MM format (e.g., 14:30).
    For flight numbers, remove any spaces (e.g., 'BA 123' becomes 'BA123').
    
    If a date is not provided, use the closest logical date based on the itinerary sequence.
    If a time is not provided, use these defaults:
    - Hotel check-in: 15:00
    - Hotel check-out: 11:00
    
    Never return 'Not provided' for required fields - make a logical assumption based on context.
    
    For passenger names:
    - Titles must be one of: MR, MRS, MS, MISS (in uppercase)
    - First and last names should be properly capitalized
    - Remove any extra spaces"""

    @staticmethod
    def process_files(file_paths: List[str], gpt_provider: GPTInterface) -> Tuple[List[Dict], List[str], float]:
        """Process multiple PDF files and return consolidated data."""
        itineraries = []
        errors = []
        total_time = 0.0
        
        for file_path in file_paths:
            try:
                logger.info(f"\nProcessing {file_path}...")
                start_time = time.perf_counter()
                
                # Extract text from PDF
                text = extract_text_from_pdf(file_path)
                logger.info(f"Text extracted, length: {len(text)} characters")
                
                # Use GPT to extract structured data
                logger.info("Extracting structured data with GPT...")
                itinerary = PDFProcessor.extract_itinerary_with_gpt(text, gpt_provider)
                
                if itinerary:
                    # Validate the extracted data
                    logger.info("Validating extracted data...")
                    ContentValidator.validate_itinerary_data(itinerary, file_path)
                    itineraries.append(itinerary)
                    logger.info("Validation successful")
                else:
                    logger.error(f"Failed to extract valid data from {file_path}")
                
                end_time = time.perf_counter()
                file_time = end_time - start_time
                total_time += file_time
                logger.info(f"Processing time: {file_time:.2f} seconds")
                
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return itineraries, errors, total_time

    @staticmethod
    def extract_itinerary_with_gpt(text: str, gpt_provider: GPTInterface) -> Optional[Dict]:
        """Extract itinerary information using GPT."""
        try:
            response = gpt_provider.generate_text(
                prompt=f"Parse this travel itinerary:\n\n{text}",
                system=PDFProcessor.SYSTEM_PROMPT
            )
            
            # Debug: Print raw response
            print("\nRaw GPT Response:")
            print(json.dumps(response, indent=2))
            
            if not response:
                logger.error("No response from GPT")
                return None
                
            return response
            
        except Exception as e:
            logger.error(f"Error extracting itinerary: {str(e)}")
            return None

    def process_chunk(self, chunk: str, gpt_provider: GPTInterface) -> Optional[Dict]:
        """Process a single chunk of text."""
        try:
            # Changed from system_prompt to system to match interface
            structured_data = gpt_provider.generate_text(
                prompt=chunk,
                system="You are a travel itinerary parser. Extract all flight, hotel, and passenger information from the provided text. Include all details found in the text."
            )
            
            if not structured_data:
                logger.warning("No data returned from GPT provider")
                return None
                
            return structured_data

        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            print(f"Error processing chunk: {str(e)}")
            return None