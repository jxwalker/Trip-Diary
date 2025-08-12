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

# Load .env from backend directory
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)

class LLMExtractor:
    def __init__(self):
        # Try OpenAI first, then Claude
        self.openai_client = None
        self.claude_client = None
        
        if os.getenv("OPENAI_API_KEY"):
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif os.getenv("ANTHROPIC_API_KEY"):
            self.claude_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def extract_travel_info(self, text: str) -> Dict[str, Any]:
        """
        Extract structured travel information from text using LLM
        """
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

        prompt = f"""Extract ALL travel information from this travel document. Be extremely thorough and precise.

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
                system_prompt = """You are an expert travel document parser specialized in extracting structured data from flight tickets, hotel bookings, and itineraries.
                Your task is to extract ALL information with 100% accuracy. Parse dates carefully, extract complete flight details including times and flight numbers.
                Return ONLY a valid JSON object with no additional text, no markdown formatting, no explanations."""
                
                try:
                    # Try with response_format first (only works with newer models)
                    response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt.format(text=text[:8000])}  # Increased text length
                        ],
                        temperature=0.1,
                        response_format={"type": "json_object"}
                    )
                except Exception as format_error:
                    print(f"Using fallback without response_format")
                    # Fallback without response_format
                    response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt.format(text=text[:8000])}  # Increased text length
                        ],
                        temperature=0.1
                    )
                
                result = response.choices[0].message.content
                print(f"OpenAI response: {result[:500]}")  # Debug log
                
                # Clean up response if needed (remove markdown code blocks)
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]
                    
                return json.loads(result.strip())
                
            elif self.claude_client:
                response = await self.claude_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=2000,
                    temperature=0.1,
                    messages=[
                        {"role": "user", "content": prompt.format(text=text[:4000])}
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
            print(f"LLM extraction error: {e}")
            return self._basic_extraction(text)
    
    def _basic_extraction(self, text: str) -> Dict[str, Any]:
        """
        Improved basic extraction without LLM (fallback)
        """
        import re
        from datetime import datetime
        
        extracted = {
            "flights": [],
            "hotels": [],
            "destination": None,
            "dates": {},
            "travelers": [],
            "confirmation_numbers": []
        }
        
        # Improved flight pattern - matches airline codes + flight numbers
        flight_patterns = [
            r'\b([A-Z]{2})\s*(\d{3,4})\b',  # BA 4794 or BA4794
            r'\b([A-Z]{2})(\d{3,4})\b',      # BA4794
            r'Flight\s+([A-Z]{2})\s*(\d{3,4})',  # Flight BA 4794
        ]
        
        for pattern in flight_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:4]:  # Limit to 4 flights
                if isinstance(match, tuple):
                    flight_num = f"{match[0]}{match[1]}"
                else:
                    flight_num = match
                extracted["flights"].append({
                    "flight_number": flight_num,
                    "airline": match[0] if isinstance(match, tuple) else "Unknown"
                })
        
        # Better date extraction - multiple formats
        date_patterns = [
            r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{2,4})\b',
            r'\b(\d{4}-\d{2}-\d{2})\b',
            r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',
            r'\b(\d{1,2}-\d{1,2}-\d{2,4})\b',
        ]
        
        found_dates = []
        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            found_dates.extend(dates)
        
        if found_dates:
            # Try to parse and sort dates
            parsed_dates = []
            for date in found_dates:
                if isinstance(date, tuple):
                    # Handle "09 Aug 25" format
                    try:
                        date_str = f"{date[0]} {date[1]} {date[2]}"
                        parsed_dates.append(date_str)
                    except:
                        pass
                else:
                    parsed_dates.append(date)
            
            if parsed_dates:
                extracted["dates"]["start_date"] = parsed_dates[0]
                extracted["dates"]["end_date"] = parsed_dates[-1] if len(parsed_dates) > 1 else parsed_dates[0]
        
        # Look for confirmation/PNR numbers
        conf_patterns = [
            r'PNR[:\s]+([A-Z0-9]{6})',
            r'Confirmation[:\s]+([A-Z0-9]{6,})',
            r'\b([A-Z0-9]{6})\b(?=\s*$)',  # Standalone 6-char codes
        ]
        
        for pattern in conf_patterns:
            confirmations = re.findall(pattern, text, re.IGNORECASE)
            extracted["confirmation_numbers"].extend(confirmations[:5])
        
        # Look for cities/destinations
        # Common travel destinations and airports
        city_patterns = [
            r'(?:to|from|at|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z]{3})\s+to\s+([A-Z]{3})',  # Airport codes
            r'Destination[:\s]+([^\n]+)',
        ]
        
        for pattern in city_patterns:
            cities = re.findall(pattern, text, re.IGNORECASE)
            if cities:
                if isinstance(cities[0], tuple):
                    extracted["destination"] = f"{cities[0][0]} to {cities[0][1]}"
                else:
                    extracted["destination"] = cities[0]
                break
        
        return extracted