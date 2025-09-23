"""
LLM Extractor Service
Uses OpenAI/Claude to extract structured travel information from text
"""
import os
import json
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
import anthropic
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root directory
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

class LLMExtractor:
    def __init__(self):
        # Try OpenAI first, then Claude
        self.openai_client = None
        self.claude_client = None
        
        if os.getenv("OPENAI_API_KEY"):
            self.openai_client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif os.getenv("ANTHROPIC_API_KEY"):
            self.claude_client = anthropic.AsyncAnthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
    
    async def extract_travel_info(self, text: str) -> Dict[str, Any]:
        """
        Extract structured travel information from text using LLM
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Starting LLM extraction with text length: {len(text)}")
        logger.info(
            f"OpenAI client available: {self.openai_client is not None}"
        )
        logger.info(
            f"Claude client available: {self.claude_client is not None}"
        )
        json_template = """{{
  "flights": [
    {{
      "flight_number": "BA115",
      "airline": "British Airways",
      "departure_airport": "LHR",
      "departure_airport_name": "London Heathrow",
      "departure_terminal": "Terminal 5",
      "arrival_airport": "JFK",
      "arrival_airport_name": "New York J F Kennedy", 
      "arrival_terminal": "Terminal 8",
      "departure_date": "2025-08-09",
      "departure_time": "14:40",
      "arrival_date": "2025-08-09",
      "arrival_time": "17:35",
      "seat": "1A",
      "class": "First",
      "duration": "7h 55m",
      "aircraft": "Boeing 777-300er",
      "booking_reference": "Z28XKT",
      "ticket_number": "1252972777762"
    }}
  ],
  "hotels": [
    {{
      "name": "Luxury Collection Manhattan Midtown",
      "address": "151 West 54th Street",
      "city": "New York",
      "postal_code": "10019",
      "phone": "1 9175905400",
      "check_in_date": "2025-08-09",
      "check_out_date": "2025-08-14", 
      "nights": 5,
      "confirmation_number": "83313860",
      "room_type": "Suite",
      "rate_per_night": 641.00,
      "currency": "USD",
      "total_amount": 3205.00
    }}
  ],
  "passengers": [
    {{
      "full_name": "Peter James Lloyd Walker",
      "first_name": "Peter James Lloyd",
      "last_name": "Walker",
      "frequent_flyer": "BA47940415"
    }}
  ],
  "trip_details": {{
    "trip_locator": "ONTRLU",
    "booking_date": "2025-07-25",
    "total_price": 3865.92,
    "currency": "GBP"
  }}
}}"""

        prompt = f"""Extract ALL travel information from this travel document. 
Be extremely thorough and precise.

Return a JSON object with this exact structure:
{json_template}

IMPORTANT RULES:
- Parse ALL flights in the document (both outbound and return flights)
- Extract exact times in 24-hour format (14:40 not 2:40 PM)
- Extract full flight numbers (BA115 not just 115)
- Convert dates to YYYY-MM-DD format (Aug 09 becomes 2025-08-09)
- Include all passenger names exactly as shown in the document
- Extract complete hotel information including all rates and dates
- Include ALL confirmation numbers, PNRs, and booking references
- If a field is not found in the document, set it to null

Text to parse:
{{text}}

Return ONLY the JSON object, no markdown, no explanations."""
        
        try:
            if self.openai_client:
                # Use cheap model for testing
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                
                # More specific prompt for better extraction
                system_prompt = """You are an expert travel document parser 
specialized in extracting structured data from flight tickets, hotel bookings, 
and itineraries. Your task is to extract ALL information with 100% accuracy. 
Parse dates carefully, extract complete flight details including times and 
flight numbers. Return ONLY a valid JSON object with no additional text, 
no markdown formatting, no explanations."""
                
                print(
                    f"[EXTRACTION] 🚀 Starting LLM extraction for "
                    f"{len(text)} characters of text"
                )
                print(f"[EXTRACTION] 📄 Text preview: {text[:200]}...")

                try:
                    # Try with response_format first (only works with newer models)
                    response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {
                                "role": "user", 
                                "content": prompt.format(text=text[:8000])
                            }
                        ],
                        temperature=0.1,
                        response_format={"type": "json_object"}
                    )
                except Exception as format_error:
                    print(
                        "[EXTRACTION] ⚠️  Using fallback without response_format"
                    )
                    # Fallback without response_format
                    response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {
                                "role": "user", 
                                "content": prompt.format(text=text[:8000])
                            }
                        ],
                        temperature=0.1
                    )

                result = response.choices[0].message.content
                print(f"[EXTRACTION] 🤖 OpenAI response: {result[:500]}...")

                # Clean up response if needed (remove markdown code blocks)
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]

                parsed_data = json.loads(result.strip())

                # Normalize null values to empty lists
                if parsed_data.get('flights') is None:
                    parsed_data['flights'] = []
                if parsed_data.get('hotels') is None:
                    parsed_data['hotels'] = []
                if parsed_data.get('passengers') is None:
                    parsed_data['passengers'] = []

                # Log extracted data summary
                print(f"[EXTRACTION] ✅ Extraction successful!")
                print(f"[EXTRACTION] 📊 Summary:")
                print(
                    f"[EXTRACTION]   • Flights: "
                    f"{len(parsed_data.get('flights', []))}"
                )
                print(
                    f"[EXTRACTION]   • Hotels: "
                    f"{len(parsed_data.get('hotels', []))}"
                )
                print(
                    f"[EXTRACTION]   • Passengers: "
                    f"{len(parsed_data.get('passengers', []))}"
                )

                # Log detailed flight info
                for i, flight in enumerate(parsed_data.get('flights', [])):
                    print(
                        f"[EXTRACTION] ✈️  Flight {i+1}: "
                        f"{flight.get('airline')} {flight.get('flight_number')} - "
                        f"{flight.get('departure_airport')} → "
                        f"{flight.get('arrival_airport')} on "
                        f"{flight.get('departure_date')} at "
                        f"{flight.get('departure_time')}"
                    )

                # Log detailed hotel info
                for i, hotel in enumerate(parsed_data.get('hotels', [])):
                    print(
                        f"[EXTRACTION] 🏨 Hotel {i+1}: {hotel.get('name')} "
                        f"in {hotel.get('city')} ({hotel.get('check_in_date')} "
                        f"to {hotel.get('check_out_date')})"
                    )

                # Log passenger info
                for i, passenger in enumerate(parsed_data.get('passengers', [])):
                    print(
                        f"[EXTRACTION] 👤 Passenger {i+1}: "
                        f"{passenger.get('full_name')}"
                    )

                return parsed_data
                
            elif self.claude_client:
                response = await self.claude_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2000,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "user", 
                            "content": prompt.format(text=text[:4000])
                        }
                    ]
                )
                
                result = response.content[0].text
                # Extract JSON from Claude's response
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            # Fallback: basic extraction without LLM
            return self._basic_extraction(text)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"LLM extraction error: {e}", exc_info=True)
            print(f"LLM extraction error: {e}")
            return self._basic_extraction(text)
    
    def _basic_extraction(self, text: str) -> Dict[str, Any]:
        """
        NO REGEX FALLBACK - Return error instead of using regex parsing
        """
        return {
            "flights": [],
            "hotels": [],
            "destination": None,
            "dates": {},
            "travelers": [],
            "confirmation_numbers": [],
            "error": "LLM extraction failed and no fallback parsing "
                     "available. Please check your API configuration."
        }
