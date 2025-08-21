from typing import Dict, List, Tuple, Optional, Union
import time
from pathlib import Path
import logging
from src.models.exceptions import PDFReadError, NoTravelContentError
from src.validators.content_validator import ContentValidator

logger = logging.getLogger(__name__)

class MultimodalProcessor:
    """Process travel documents using multimodal LLM capabilities."""
    
    @staticmethod
    def process_files(file_paths: List[str], multimodal_provider) -> Tuple[List[Dict], List[str], float]:
        """Process multiple files using multimodal capabilities."""
        itineraries = []
        errors = []
        total_time = 0.0
        
        for file_path in file_paths:
            try:
                logger.info(f"\nProcessing {file_path} with multimodal...")
                start_time = time.perf_counter()
                
                # Process document directly with vision
                result = multimodal_provider.process_document(document_path=file_path)
                
                if result and 'error' not in result:
                    # Validate the extracted data
                    logger.info("Validating extracted data...")
                    ContentValidator.validate_itinerary_data(result, file_path)
                    itineraries.append(result)
                    logger.info(f"Successfully extracted: {len(result.get('flights', []))} flights, "
                              f"{len(result.get('hotels', []))} hotels, "
                              f"{len(result.get('passengers', []))} passengers")
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'No result'
                    logger.error(f"Failed to extract data: {error_msg}")
                    errors.append(f"{file_path}: {error_msg}")
                
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
    def process_mixed_documents(documents: List[Union[str, bytes]], multimodal_provider) -> Dict:
        """Process a mix of file paths and raw image data."""
        all_results = {
            'flights': [],
            'hotels': [],
            'passengers': [],
            'other': []
        }
        
        for doc in documents:
            try:
                if isinstance(doc, str):
                    # File path
                    result = multimodal_provider.process_document(document_path=doc)
                else:
                    # Raw bytes
                    result = multimodal_provider.process_document(image_data=doc)
                
                if result and 'error' not in result:
                    all_results['flights'].extend(result.get('flights', []))
                    all_results['hotels'].extend(result.get('hotels', []))
                    all_results['passengers'].extend(result.get('passengers', []))
                    all_results['other'].extend(result.get('other', []))
                    
            except Exception as e:
                logger.error(f"Error processing document: {e}")
        
        # Deduplicate
        all_results = MultimodalProcessor._deduplicate_results(all_results)
        
        return all_results
    
    @staticmethod
    def _deduplicate_results(results: Dict) -> Dict:
        """Remove duplicate entries from results."""
        # Deduplicate flights
        seen_flights = set()
        unique_flights = []
        for flight in results['flights']:
            key = f"{flight.get('flight_number', '')}{flight.get('departure', {}).get('date', '')}"
            if key not in seen_flights:
                seen_flights.add(key)
                unique_flights.append(flight)
        results['flights'] = unique_flights
        
        # Deduplicate hotels
        seen_hotels = set()
        unique_hotels = []
        for hotel in results['hotels']:
            key = f"{hotel.get('name', '')}{hotel.get('check_in_date', '')}"
            if key not in seen_hotels:
                seen_hotels.add(key)
                unique_hotels.append(hotel)
        results['hotels'] = unique_hotels
        
        # Deduplicate passengers
        seen_passengers = set()
        unique_passengers = []
        for passenger in results['passengers']:
            key = f"{passenger.get('first_name', '')}{passenger.get('last_name', '')}"
            if key not in seen_passengers:
                seen_passengers.add(key)
                unique_passengers.append(passenger)
        results['passengers'] = unique_passengers
        
        return results
    
    @staticmethod
    def supports_document_type(file_path: str) -> bool:
        """Check if document type is supported."""
        supported_extensions = {
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp',
            '.tiff', '.webp', '.heic', '.heif'
        }
        ext = Path(file_path).suffix.lower()
        return ext in supported_extensions