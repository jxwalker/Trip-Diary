import os
from typing import Dict, List, Tuple, Optional
import json
from src.gpt_interfaces.gpt_interface import GPTInterface
from src.models.exceptions import PDFReadError, NoTravelContentError
from src.utils.pdf_utils import extract_text_from_pdf
import time
from src.validators.content_validator import ContentValidator

class PDFProcessor:
    @staticmethod
    def process_files(file_paths: List[str], gpt_provider: GPTInterface) -> Tuple[List[Dict], List[str], float]:
        """Process multiple PDF files and return consolidated data."""
        itineraries = []
        errors = []
        total_time = 0.0
        
        for file_path in file_paths:
            try:
                print(f"\nProcessing {file_path}...")
                start_time = time.perf_counter()
                
                # Extract text from PDF
                text = extract_text_from_pdf(file_path)
                print(f"Text extracted, length: {len(text)} characters")
                
                # Use GPT to extract structured data
                print("Extracting structured data with GPT...")
                itinerary = PDFProcessor.extract_itinerary_with_gpt(text, gpt_provider)
                
                if itinerary:
                    # Validate the extracted data
                    print("Validating extracted data...")
                    ContentValidator.validate_itinerary_data(itinerary, file_path)
                    itineraries.append(itinerary)
                    print("Validation successful")
                
                end_time = time.perf_counter()
                file_time = end_time - start_time
                total_time += file_time
                print(f"Processing time: {file_time:.2f} seconds")
                
            except Exception as e:
                errors.append(f"Error processing {file_path}: {str(e)}")
                print(f"Error: {str(e)}")
        
        return itineraries, errors, total_time

    @staticmethod
    def process_file(file_path: str, gpt_provider: GPTInterface) -> Optional[Dict]:
        """Process a single PDF file and extract travel details."""
        try:
            text = extract_text_from_pdf(file_path)
            itinerary = PDFProcessor.extract_itinerary_with_gpt(text, gpt_provider)
            
            if not itinerary:
                raise PDFReadError("Failed to parse travel details")
                
            itinerary['source_file'] = file_path
            return itinerary
            
        except Exception as e:
            raise PDFReadError(f"Error processing PDF: {str(e)}")

    @staticmethod
    def extract_itinerary_with_gpt(text: str, gpt_provider: GPTInterface) -> Optional[Dict]:
        """Extract structured itinerary data using GPT."""
        system_prompt = """You are a travel itinerary parser. Extract the following details as a JSON object:
        {
            "booking_reference": "string",
            "passengers": [
                {
                    "title": "string (MR/MRS/MISS/MS only)",
                    "first_name": "string (use only the first given name, ignore middle names)",
                    "last_name": "string (use only the final surname)"
                }
            ],
            "flights": [
                {
                    "flight_number": "string",
                    "operator": "string",
                    "departure": {
                        "location": "string",
                        "terminal": "string",
                        "date": "YYYY-MM-DD",
                        "time": "HH:mm"
                    },
                    "arrival": {
                        "location": "string",
                        "terminal": "string",
                        "date": "YYYY-MM-DD",
                        "time": "HH:mm"
                    },
                    "travel_class": "string",
                    "baggage_allowance": {
                        "checked_baggage": "string",
                        "hand_baggage": "string"
                    }
                }
            ],
            "hotels": [
                {
                    "name": "string",
                    "city": "string",
                    "check_in_date": "YYYY-MM-DD",
                    "check_out_date": "YYYY-MM-DD",
                    "room_type": "string",
                    "room_features": "string"
                }
            ]
        }

        IMPORTANT: 
        1. Follow the exact structure above
        2. For passenger names:
           - Use only the first given name (ignore middle names)
           - Use only the final surname
           - Example: "Peter James Lloyd Walker" becomes first_name: "Peter", last_name: "Walker"
        3. Format all dates as YYYY-MM-DD
        4. Format all times as HH:mm
        5. For city names, use only the main city name
        6. Ensure the JSON is valid and can be parsed directly"""

        try:
            response = gpt_provider.generate_text(f"Parse this travel itinerary:\n\n{text}", system_prompt)
            
            # Extract and parse JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                parsed_response = json.loads(json_str)
                
                # Basic validation
                required_fields = ['booking_reference', 'passengers', 'flights', 'hotels']
                if all(field in parsed_response for field in required_fields):
                    return parsed_response
                    
            return None
                
        except Exception as e:
            print(f"Error extracting itinerary: {str(e)}")
            return None