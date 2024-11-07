import os
from typing import Dict, List, Tuple, Optional
import json
from src.gpt_interfaces.gpt_interface import GPTInterface
from src.models.exceptions import PDFReadError, NoTravelContentError
from src.utils.pdf_utils import extract_text_from_pdf

class PDFProcessor:
    @staticmethod
    def process_files(file_paths: List[str], gpt_provider: GPTInterface) -> Tuple[List[Dict], List[str]]:
        """Process multiple PDF files and return consolidated itineraries and errors."""
        itineraries = []
        errors = []
        
        for file_path in file_paths:
            try:
                itinerary = PDFProcessor.process_file(file_path, gpt_provider)
                if itinerary:
                    itineraries.append(itinerary)
            except (PDFReadError, NoTravelContentError) as e:
                errors.append(f"Error processing {file_path}: {str(e)}")
            except Exception as e:
                errors.append(f"Unexpected error processing {file_path}: {str(e)}")
        
        return itineraries, errors

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
        """Use GPT to extract structured itinerary information from text."""
        system_prompt = """You are a travel itinerary parser. Extract these travel details as JSON:
        {
            "booking_reference": string,
            "flights": [{
                "flight_number": string,
                "operator": string,
                "class": string,
                "departure": {
                    "date": "YYYY-MM-DD",
                    "time": "HH:MM",
                    "location": string,
                    "terminal": string | null
                },
                "arrival": {
                    "date": "YYYY-MM-DD", 
                    "time": "HH:MM",
                    "location": string,
                    "terminal": string | null
                },
                "baggage_allowance": {
                    "hand_baggage": string | null,
                    "checked_baggage": string | null
                }
            }],
            "hotels": [{ 
                "name": string,
                "city": string,
                "booking_reference": string | null,
                "room_details": string,
                "check_in": "YYYY-MM-DD",
                "check_out": "YYYY-MM-DD",
                "address": string | null
            }]
        }

        Important rules:
        1. Return ONLY valid JSON, no markdown or additional text
        2. Use null for missing values
        3. Format all dates as YYYY-MM-DD
        4. Format all times as HH:MM
        5. Use airport codes for locations (e.g., LHR, BKK)
        6. Include all baggage information
        7. For hotels, always include city and booking reference (use null if not found)"""

        prompt = f"Parse this travel itinerary:\n\n{text}"

        try:
            response = gpt_provider.generate_text(prompt, system_prompt)
            response = response.strip()
            
            # Clean the response
            if response.startswith('```'):
                start = response.find('\n', 3) + 1
                end = response.rfind('```')
                if end > start:
                    response = response[start:end].strip()
                    if response.lower().startswith('json'):
                        response = '\n'.join(response.split('\n')[1:])
            
            try:
                import json
                parsed_response = json.loads(response)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {str(e)}")
                print(f"Raw response: {response}")
                return None
                
            if not parsed_response.get('booking_reference') or not parsed_response.get('flights'):
                print("Missing required fields in response")
                return None
                
            if 'hotels' not in parsed_response:
                parsed_response['hotels'] = []
                
            return parsed_response
            
        except Exception as e:
            print(f"Error extracting itinerary: {str(e)}")
            return None