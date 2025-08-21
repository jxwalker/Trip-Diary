#!/usr/bin/env python3
"""Test text extraction from our test file"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
from dotenv import load_dotenv
load_dotenv(root_dir / '.env')

from services.llm_extractor import LLMExtractor

# Create test file
trip_content = """
Trip: New York City
Dates: August 9-14, 2025

Flight BA 115 - British Airways
Departure: LHR Sat, Aug 9, 2025 14:40
Arrival: JFK Sat, Aug 9, 2025 17:35
Class: First, Seat: 1A

Flight BA 112 - British Airways  
Departure: JFK Thu, Aug 14, 2025 18:30
Arrival: LHR Fri, Aug 15, 2025 06:30
Class: First, Seat: 1K

Hotel: Luxury Collection Manhattan Midtown
Address: 151 West 54th Street, New York, NY 10019
Check-in: Sat, Aug 9, 2025
Check-out: Thu, Aug 14, 2025
Confirmation: 83313860
"""

import asyncio

async def test():
    extractor = LLMExtractor()
    print("Extracting from text...")
    result = await extractor.extract_travel_info(trip_content)
    
    print("\nExtracted data:")
    print(f"Destination: {result.get('destination', 'NOT FOUND')}")
    print(f"Start date: {result.get('start_date', 'NOT FOUND')}")
    print(f"End date: {result.get('end_date', 'NOT FOUND')}")
    print(f"Flights: {len(result.get('flights', []))}")
    print(f"Hotels: {len(result.get('hotels', []))}")
    
    if result.get('flights'):
        print("\nFirst flight:")
        print(result['flights'][0])
    
    if result.get('hotels'):
        print("\nHotel:")
        print(result['hotels'][0])
    
    return result

asyncio.run(test())