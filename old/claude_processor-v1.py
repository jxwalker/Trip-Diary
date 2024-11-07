from anthropic import Anthropic
import json
from typing import Dict, Any
from dotenv import load_dotenv
import os
import time

def clean_json_response(response_text: str) -> str:
    """Clean the JSON response from Claude by removing markdown code blocks."""
    if response_text.startswith('```'):
        start = response_text.find('\n', 3) + 1
        end = response_text.rfind('```')
        if end > start:
            response_text = response_text[start:end]
    return response_text.strip()

def format_itinerary_summary(data: Dict[str, Any]) -> str:
    """Create a human-readable summary of the parsed itinerary."""
    if not data:
        return "No itinerary data available"
        
    summary = []
    summary.append(f"Booking Reference: {data.get('booking_reference', 'N/A')}\n")
    
    # Passengers
    if data.get('passengers'):
        summary.append("Passengers:")
        for p in data['passengers']:
            summary.append(f"- {p.get('name', 'N/A')}")
        summary.append("")
    
    # Flights
    if data.get('flights'):
        summary.append("Flights:")
        for f in data['flights']:
            dep = f.get('departure', {})
            arr = f.get('arrival', {})
            baggage = f.get('baggage_allowance', {})
            
            # Format terminals properly
            dep_terminal = f" Terminal {dep.get('terminal', '').replace('Terminal ', '')}" if dep.get('terminal') else ""
            arr_terminal = f" Terminal {arr.get('terminal', '').replace('Terminal ', '')}" if arr.get('terminal') else ""
            
            # Format baggage info
            checked_baggage = baggage.get('checked_baggage', 'N/A')
            hand_baggage = baggage.get('hand_baggage', 'N/A')
            baggage_info = []
            if checked_baggage != 'N/A':
                baggage_info.append(f"Checked: {checked_baggage}")
            if hand_baggage != 'N/A':
                baggage_info.append(f"Hand: {hand_baggage}")
            baggage_str = " | ".join(baggage_info) if baggage_info else "N/A"
            
            summary.append(
                f"- {f.get('flight_number', 'N/A')} ({f.get('operator', 'N/A')})\n"
                f"  {dep.get('location', 'N/A')}{dep_terminal} → "
                f"{arr.get('location', 'N/A')}{arr_terminal}\n"
                f"  {dep.get('date', 'N/A')} {dep.get('time', 'N/A')} → "
                f"{arr.get('date', 'N/A')} {arr.get('time', 'N/A')}\n"
                f"  Class: {f.get('class', 'N/A')}\n"
                f"  Baggage: {baggage_str}"
            )
        summary.append("")
    
    # Hotels (if present)
    if data.get('hotels'):
        summary.append("Hotels:")
        for h in data['hotels']:
            summary.append(
                f"- {h.get('name', 'N/A')}\n"
                f"  {h.get('city', 'N/A')}: {h.get('check_in', 'N/A')} to {h.get('check_out', 'N/A')}\n"
                f"  {h.get('room_details', 'N/A')}"
            )
        summary.append("")
    
    return "\n".join(summary)

def extract_itinerary_with_claude(text: str) -> Dict[str, Any]:
    """Use Claude to extract structured itinerary data from text."""
    
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in .env file")
        return None
        
    anthropic = Anthropic(api_key=api_key)
    
    print("Preparing Claude request...")
    
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
        "passengers": [{
            "name": string  # Must include title (MR/MRS/MISS)
        }],
        "hotels": [{ # Optional section
            "name": string,
            "room_details": string,
            "check_in": "YYYY-MM-DD",
            "check_out": "YYYY-MM-DD",
            "city": string,
            "address": string
        }]
    }

    Important extraction rules:
    1. Format all dates as YYYY-MM-DD
    2. Format all times as HH:MM
    3. For flights:
       - Include terminal information if available
       - Extract baggage allowance from any relevant section
       - Use shortened airport names:
         * "Phuket" instead of "Phuket International Airport"
         * "Bangkok Don Mueang" instead of "Don Mueang International Airport"
         * Keep city names for clarity
       - For Air Asia flights:
         * Look for baggage in fare details and add-ons
         * Include both included and purchased baggage
    4. For hotels (if present):
       - Include full room details
       - Keep complete address
    5. For passengers:
       - ALWAYS include title (MR/MRS/MISS)
       - For Air Asia, check passenger details section carefully for titles
       - If title is not found, use context (e.g., first name) to determine
    
    Return only valid JSON with no additional text."""

    try:
        print("Sending request to Claude...")
        start_time = time.time()
        
        message = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Parse this airline itinerary and extract all details:\n\n{text}"
                }
            ]
        )
        
        elapsed_time = time.time() - start_time
        print(f"Response received in {elapsed_time:.2f} seconds")
        
        # Clean and parse JSON response
        response_text = message.content[0].text
        cleaned_json = clean_json_response(response_text)
        
        try:
            parsed_data = json.loads(cleaned_json)
            
            # Basic validation of required fields
            required_fields = ["booking_reference", "flights", "passengers"]
            missing_fields = [field for field in required_fields if field not in parsed_data]
            
            if missing_fields:
                print(f"Warning: Missing required fields: {', '.join(missing_fields)}")
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            print("Error: Could not parse JSON from Claude's response")
            print(f"JSON Error: {str(e)}")
            print("Raw response:", response_text)
            print("\nCleaned JSON:", cleaned_json)
            return None
            
    except Exception as e:
        print(f"\nError during Claude request: {type(e).__name__}: {str(e)}")
        return None