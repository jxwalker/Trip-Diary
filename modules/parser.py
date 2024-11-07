import PyPDF2
from typing import Dict, Any
import re
import json
from datetime import datetime

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    try:
        print(f"Opening PDF file: {file_path}")
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"PDF has {len(reader.pages)} pages")
            text = ''
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += page_text + '\n'
                print(f"Extracted {len(page_text)} characters from page {i+1}")
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

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
    
    # Debug the passenger section
    print("\nSearching for passengers in text:")
    passenger_section = re.search(r'Passenger\(s\)(.*?)(?=Flight|Baggage|$)', text, re.DOTALL)
    if passenger_section:
        print("\nFound passenger section:")
        print("=" * 50)
        print(passenger_section.group(1))
        print("=" * 50)

    # Extract passengers
    passenger_pattern = (
        r'(?:^|\n|\()'  # Start of line, newline, or opening parenthesis
        r'(MRS|MISS|MR)\s+'  # Title
        r'([A-Z]+)\s+'  # First name
        r'(WALKER)'  # Last name
        r'(?:\s|$|\))'  # Space, end of line, or closing parenthesis
    )
    passenger_matches = re.finditer(passenger_pattern, text)
    seen_passengers = set()
    
    for match in passenger_matches:
        full_name = f"{match.group(1)} {match.group(2)} {match.group(3)}"
        if full_name not in seen_passengers:
            passenger = {
                "name": full_name,
                "baggage_allowance": "Standard Economy allowance"
            }
            itinerary["passengers"].append(passenger)
            seen_passengers.add(full_name)
            print(f"Found passenger: {passenger}")
    
    # Debug the raw text for flights
    print("\nSearching for flights in text:")
    flight_matches = re.finditer(
        r'(BA\d{4}.*?)(?=BA\d{4}|Hotel|$)',
        text,
        re.DOTALL
    )
    for match in flight_matches:
        print("\nFound raw flight section:")
        print("=" * 50)
        print(match.group(1))
        print("=" * 50)

    # Extract flights
    flight_pattern = (
        r'BA(\d{4})\s*'
        r'([^|]+?)\s*\|\s*'
        r'([^|]+?)\s*\|\s*'
        r'Confirmed\s*'
        r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s*'
        r'(\d{2}:\d{2})\s*'
        r'([^(\n]+?)(?:\s*\(([^)]+)\))?\s*'
        r'(?:Terminal\s+([^\n]+))?\s*'
        r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s*'
        r'(\d{2}:\d{2})\s*'
        r'([^(\n]+?)(?:\s*\(([^)]+)\))?\s*'
    )
    
    flight_matches = re.finditer(flight_pattern, text, re.DOTALL)
    for match in flight_matches:
        flight = {
            "flight_number": f"BA{match.group(1)}",
            "operator": match.group(2).strip(),
            "class": f"{match.group(3).strip()} | Confirmed",
            "departure": {
                "date": match.group(4),
                "time": match.group(5),
                "location": match.group(6).strip(),
                "city": match.group(7).strip() if match.group(7) else None,
                "terminal": match.group(8).strip() if match.group(8) else None
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
    
    # Extract hotels
    hotel_sections = re.finditer(
        r'Hotel\s*(.*?)\s*Room\s*(.*?)\s*Check-in\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s*Check-out\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
        text,
        re.DOTALL
    )
    
    for match in hotel_sections:
        hotel = {
            "name": match.group(1).strip(),
            "room_details": match.group(2).strip(),
            "check_in": match.group(3),
            "check_out": match.group(4)
        }
        
        # Extract address if present
        address_match = re.search(r'(.*?),\s*(.*?),\s*(.*?)(?=Room|$)', match.group(1))
        if address_match:
            hotel["name"] = address_match.group(1).strip()
            hotel["city"] = address_match.group(2).strip()
            hotel["address"] = address_match.group(3).strip()
            
        itinerary["hotels"].append(hotel)
        print(f"Found hotel: {hotel}")
    
    # Extract payment information
    payment_match = re.search(r'Booking total\s*£([\d,]+\.\d{2})', text)
    if payment_match:
        itinerary["total_cost"] = payment_match.group(1)
        print(f"Found total cost: £{itinerary['total_cost']}")
    
    # Debug output for troubleshooting
    print("\nFinal parsed data:")
    print(json.dumps(itinerary, indent=2))
    
    return itinerary