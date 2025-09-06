import PyPDF2
from typing import Dict, Any
import re
import json
from datetime import datetime


def parse_itinerary(text: str) -> Dict[str, Any]:
    """Parse the extracted text into structured data."""
    print("\nStarting itinerary parsing...")
    
    itinerary = {
        "booking_reference": None,
        "flights": [],
        "hotels": [],
        "passengers": []
    }
    
    # Extract booking reference
    booking_match = re.search(r'Booking reference:?\s*([A-Z0-9]{6})', text, re.IGNORECASE)
    if booking_match:
        itinerary["booking_reference"] = booking_match.group(1)
        print(f"Found booking reference: {itinerary['booking_reference']}")
    
    # Extract passengers (updated pattern)
    passenger_pattern = r'(?:^|\n)(MRS|MISS|MR)\s+([A-Z]+)\s+WALKER(?!\w)'
    passenger_matches = re.finditer(passenger_pattern, text)
    seen_passengers = set()
    
    for match in passenger_matches:
        full_name = f"{match.group(1)} {match.group(2)} WALKER"
        if full_name not in seen_passengers:
            passenger = {
                "name": full_name,
                "baggage_allowance": "Standard Economy allowance"
            }
            itinerary["passengers"].append(passenger)
            seen_passengers.add(full_name)
            print(f"Found passenger: {passenger}")
    
    # Extract flights (updated pattern)
    flight_sections = [
        section.strip() for section in re.findall(
            r'BA\d{4}[^B]+?(?=BA\d{4}|Hotel|$)',
            text,
            re.DOTALL
        )
    ]
    
    for section in flight_sections:
        # Parse each flight section
        match = re.match(
            r'BA(\d{4})'  # Flight number
            r'([^|]+?)\s*\|\s*'  # Operator
            r'([^|]+?)\s*\|\s*Confirmed\s*'  # Class
            r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s*'  # Departure date
            r'(\d{2}:\d{2})\s*'  # Departure time
            r'([^(\n]+?)(?:\s*\(([^)]+)\))?\s*'  # Departure location (city)
            r'(?:Terminal\s+(\d+))?\s*'  # Terminal
            r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s*'  # Arrival date
            r'(\d{2}:\d{2})\s*'  # Arrival time
            r'([^(\n]+?)(?:\s*\(([^)]+)\))?\s*',  # Arrival location (city)
            section
        )
        
        if match:
            flight = {
                "flight_number": f"BA{match.group(1)}",
                "operator": match.group(2).strip(),
                "class": f"{match.group(3).strip()} | Confirmed",
                "departure": {
                    "date": match.group(4),
                    "time": match.group(5),
                    "location": match.group(6).strip(),
                    "city": match.group(7).strip() if match.group(7) else None,
                    "terminal": match.group(8) if match.group(8) else None
                },
                "arrival": {
                    "date": match.group(9),
                    "time": match.group(10),
                    "location": match.group(11).strip(),
                    "city": match.group(12).strip() if match.group(12) else None
                }
            }
            itinerary["flights"].append(flight)
            print(f"Found flight: {flight}")

    # ... (keep existing hotel extraction code) ...

    return itinerary