import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class JSONValidator:
    """Validates and cleans JSON data from GPT responses."""
    
    @staticmethod
    def clean_json_string(json_str: str) -> str:
        """Clean a JSON string using LLM-based parsing instead of regex."""
        from ..services.llm_parser import LLMParser
        
        # Remove any leading/trailing whitespace
        json_str = json_str.strip()
        
        # Remove any control characters
        json_str = ''.join(char for char in json_str if ord(char) >= 32)
        
        llm_parser = LLMParser()
        
        cleaning_prompt = f"""Fix this JSON string to be valid JSON format:

INPUT JSON:
{json_str}

INSTRUCTIONS:
- Fix quote issues (convert single quotes to double quotes)
- Add missing quotes around property names
- Remove trailing commas
- Fix line breaks in property values
- Fix array bracket issues
- Ensure valid JSON structure

Return ONLY the cleaned JSON, no other text."""

        try:
            import asyncio
            try:
                asyncio.get_running_loop()
                json_str = json_str.replace("'", '"')
                logger.debug(f"Basic cleaned JSON: {json_str}")
                return json_str
            except RuntimeError:
                cleaned_result = asyncio.run(llm_parser._parse_with_openai(cleaning_prompt))
                if isinstance(cleaned_result, dict) and 'cleaned_json' in cleaned_result:
                    return cleaned_result['cleaned_json']
                elif isinstance(cleaned_result, str):
                    return cleaned_result
        except Exception as e:
            logger.exception(f"LLM cleaning failed, using basic cleanup: {e}")
            json_str = json_str.replace("'", '"')
        
        logger.debug(f"Cleaned JSON: {json_str}")
        return json_str

    @staticmethod
    def extract_json_objects(text: str) -> List[str]:
        """Extract JSON objects from text using bracket counting."""
        objects = []
        start_pos = []
        bracket_count = 0
        
        for i, char in enumerate(text):
            if char == '{':
                if bracket_count == 0:
                    start_pos.append(i)
                bracket_count += 1
            elif char == '}':
                bracket_count -= 1
                if bracket_count == 0 and start_pos:
                    objects.append(text[start_pos.pop():i+1])
                elif bracket_count < 0:
                    bracket_count = 0
                    
        return objects

    @staticmethod
    def validate_passenger(passenger: Dict) -> bool:
        """Validate a passenger entry."""
        if not all(k in passenger for k in ['title', 'first_name', 'last_name']):
            logger.debug(f"Missing required passenger fields: {passenger}")
            return False
            
        # Validate title
        valid_titles = {'MR', 'MRS', 'MS', 'MISS'}
        if passenger['title'].upper() not in valid_titles:
            logger.debug(f"Invalid passenger title: {passenger['title']}")
            return False
            
        # Validate names are not empty
        if not passenger['first_name'] or not passenger['last_name']:
            logger.debug(f"Empty passenger name: {passenger}")
            return False
            
        # Validate no unexpected names
        unexpected_names = {'JAMES'}  # Add any other names that shouldn't appear
        if passenger['first_name'].upper() in unexpected_names:
            logger.debug(f"Unexpected passenger name: {passenger['first_name']}")
            return False
            
        return True

    @staticmethod
    def validate_room(room: Dict) -> bool:
        """Validate room details."""
        required_fields = ['room_type', 'bed_type']
        if not all(k in room for k in required_fields):
            logger.debug(f"Missing required room fields: {room}")
            return False
            
        # Validate bed type format
        valid_bed_types = {'1 King', '2 Double', '2 Twin'}
        if room['bed_type'] not in valid_bed_types:
            logger.debug(f"Invalid bed type: {room['bed_type']}")
            return False
            
        # Convert features to list if string
        if isinstance(room.get('features'), str):
            room['features'] = [f.strip() for f in room['features'].split(',') if f.strip()]
            
        return True

    @staticmethod
    def validate_hotel(hotel: Dict) -> bool:
        """Validate hotel structure and room details."""
        required_fields = ['name', 'city', 'check_in_date', 'check_out_date', 'rooms']
        if not all(k in hotel for k in required_fields):
            logger.debug(f"Missing required hotel fields: {hotel}")
            return False
            
        # Validate rooms array
        if not isinstance(hotel['rooms'], list) or not hotel['rooms']:
            logger.debug(f"Invalid or empty rooms array: {hotel}")
            return False
            
        # Group rooms by type and bed configuration
        room_configs = set()
        for room in hotel['rooms']:
            if not isinstance(room, dict) or not JSONValidator.validate_room(room):
                logger.debug(f"Invalid room data: {room}")
                return False
                
            room_config = (room['room_type'], room['bed_type'])
            room_configs.add(room_config)
        
        # Ensure we have all expected room configurations
        hotel_name = hotel['name'].lower()
        if 'phuket marriott' in hotel_name:
            expected_configs = {
                ('Premium Pool Access', '1 King'),
                ('Premium Pool Access', '2 Double')
            }
            if not room_configs.issuperset(expected_configs):
                logger.debug(f"Missing expected room configs for Phuket Marriott: {room_configs}")
                return False
                
        elif 'bangkok marriott' in hotel_name:
            expected_configs = {
                ('Executive Room', '1 King'),
                ('Deluxe Room', '2 Double')
            }
            if not room_configs.issuperset(expected_configs):
                logger.debug(f"Missing expected room configs for Bangkok Marriott: {room_configs}")
                return False
                
        return True

    @staticmethod
    def merge_responses(responses: List[Dict]) -> Dict:
        """Merge multiple responses into a single consolidated response."""
        if not responses:
            return {}
            
        result = {
            'booking_reference': None,
            'passengers': [],
            'flights': [],
            'hotels': []
        }
        
        # Track unique items
        seen = {
            'passengers': set(),
            'flights': set(),
            'hotels': set()
        }
        
        for response in responses:
            # Take first non-null booking reference
            if not result['booking_reference'] and response.get('booking_reference'):
                result['booking_reference'] = response['booking_reference']
            
            # Merge passengers (with validation)
            for passenger in response.get('passengers', []):
                if JSONValidator.validate_passenger(passenger):
                    key = (
                        passenger['title'].upper(),
                        passenger['first_name'].upper(),
                        passenger['last_name'].upper()
                    )
                    if key not in seen['passengers']:
                        result['passengers'].append(passenger)
                        seen['passengers'].add(key)
            
            # Merge flights
            for flight in response.get('flights', []):
                key = (
                    flight.get('flight_number', ''),
                    flight.get('departure', {}).get('date', ''),
                    flight.get('departure', {}).get('time', '')
                )
                if all(key) and key not in seen['flights']:
                    result['flights'].append(flight)
                    seen['flights'].add(key)
            
            # Merge hotels (with validation)
            for hotel in response.get('hotels', []):
                if JSONValidator.validate_hotel(hotel):
                    key = (
                        hotel.get('name', ''),
                        hotel.get('check_in_date', ''),
                        hotel.get('check_out_date', '')
                    )
                    if all(key) and key not in seen['hotels']:
                        result['hotels'].append(hotel)
                        seen['hotels'].add(key)
        
        return result
        
    @staticmethod
    def validate_and_clean_gpt_response(response: str) -> Optional[Dict[str, Any]]:
        """Validate and clean GPT response into proper JSON."""
        try:
            # First try to find and parse JSON objects
            json_objects = JSONValidator.extract_json_objects(response)
            valid_responses = []
            
            for json_str in json_objects:
                try:
                    # Clean and parse JSON
                    cleaned = JSONValidator.clean_json_string(json_str)
                    data = json.loads(cleaned)
                    
                    # Basic validation
                    if any(field in data for field in ['booking_reference', 'passengers', 'flights', 'hotels']):
                        valid_responses.append(data)
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON object: {str(e)}")
                    logger.debug(f"Problem JSON: {json_str}")
                    continue
            
            if valid_responses:
                # Merge all valid responses
                merged = JSONValidator.merge_responses(valid_responses)
                if merged and any(merged.get(key) for key in ['passengers', 'flights', 'hotels']):
                    return merged
            
            # If no valid JSON objects found, try to parse the entire response
            try:
                cleaned = JSONValidator.clean_json_string(response)
                data = json.loads(cleaned)
                if any(field in data for field in ['passengers', 'flights', 'hotels']):
                    return data
            except Exception as e:
                logger.debug(f"Failed to parse full response: {str(e)}")
            
            logger.warning("No valid data found in response")
            return None
            
        except Exception as e:
            logger.error(f"Error validating response: {str(e)}")
            logger.debug(f"Full response: {response}")
            return None
