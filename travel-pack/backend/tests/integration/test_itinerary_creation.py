#!/usr/bin/env python3
"""Test itinerary creation from extracted data"""
import sys
import os
from pathlib import Path
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
from dotenv import load_dotenv
load_dotenv(root_dir / '.env')

from services.itinerary_generator import ItineraryGenerator

async def test():
    # This is what LLMExtractor returns (from our previous test)
    extracted_data = {
        "text_extraction": {
            "flights": [
                {
                    "flight_number": "BA115",
                    "airline": "British Airways",
                    "departure_airport": "LHR",
                    "arrival_airport": "JFK",
                    "departure_date": "2025-08-09",
                    "departure_time": "14:40",
                    "arrival_date": "2025-08-09",
                    "arrival_time": "17:35",
                    "seat": "1A",
                    "class": "First"
                },
                {
                    "flight_number": "BA112",
                    "airline": "British Airways",
                    "departure_airport": "JFK",
                    "arrival_airport": "LHR",
                    "departure_date": "2025-08-14",
                    "departure_time": "18:30",
                    "arrival_date": "2025-08-15",
                    "arrival_time": "06:30",
                    "seat": "1K",
                    "class": "First"
                }
            ],
            "hotels": [
                {
                    "name": "Luxury Collection Manhattan Midtown",
                    "address": "151 West 54th Street",
                    "city": "New York",
                    "postal_code": "10019",
                    "check_in_date": "2025-08-09",
                    "check_out_date": "2025-08-14",
                    "nights": 5,
                    "confirmation_number": "83313860"
                }
            ],
            "destination": None,  # This is what was extracted (missing!)
            "dates": {}
        }
    }
    
    generator = ItineraryGenerator()
    print("Creating itinerary from extracted data...")
    itinerary = await generator.create_itinerary(extracted_data)
    
    print("\nTrip Summary:")
    summary = itinerary.get("trip_summary", {})
    print(f"  Destination: {summary.get('destination', 'NOT SET')}")
    print(f"  Start Date: {summary.get('start_date', 'NOT SET')}")
    print(f"  End Date: {summary.get('end_date', 'NOT SET')}")
    print(f"  Duration: {summary.get('duration', 'NOT SET')}")
    
    print(f"\nDaily Schedule: {len(itinerary.get('daily_schedule', []))} days")
    
    return itinerary

result = asyncio.run(test())

# Now test if immediate guide generator would work with this
if result.get("trip_summary", {}).get("destination") not in [None, "Unknown Destination", "TBD"]:
    print("\n✅ Destination is set! Immediate guide generator would work!")
else:
    print("\n❌ No destination! Immediate guide generator won't be able to search!")
    print("   Destination value:", result.get("trip_summary", {}).get("destination"))