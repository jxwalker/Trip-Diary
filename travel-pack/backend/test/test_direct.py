#!/usr/bin/env python3
"""Direct test - bypass upload and test the processing pipeline directly"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
from dotenv import load_dotenv
load_dotenv(root_dir / '.env')

from services.llm_extractor import LLMExtractor
from services.itinerary_generator import ItineraryGenerator
from services.immediate_guide_generator import ImmediateGuideGenerator

trip_text = """
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

async def test_direct():
    print("=" * 60)
    print("DIRECT TEST - COMPLETE PIPELINE")
    print("=" * 60)
    
    # Step 1: Extract travel info
    print("\n1. Extracting travel info from text...")
    extractor = LLMExtractor()
    extracted = await extractor.extract_travel_info(trip_text)
    
    print(f"   Flights extracted: {len(extracted.get('flights', []))}")
    print(f"   Hotels extracted: {len(extracted.get('hotels', []))}")
    
    # Step 2: Create itinerary
    print("\n2. Creating itinerary...")
    generator = ItineraryGenerator()
    extracted_data = {"text_extraction": extracted}
    itinerary = await generator.create_itinerary(extracted_data)
    
    summary = itinerary.get('trip_summary', {})
    print(f"   Destination: {summary.get('destination', 'NOT SET')}")
    print(f"   Dates: {summary.get('start_date')} to {summary.get('end_date')}")
    
    # Step 3: Enhance with real content
    print("\n3. Enhancing with real content from Perplexity...")
    enhancer = ImmediateGuideGenerator()
    enhanced = await enhancer.enhance_itinerary_immediately(itinerary)
    
    restaurants = enhanced.get('restaurants', [])
    attractions = enhanced.get('attractions', [])
    
    print(f"   Restaurants: {len(restaurants)}")
    print(f"   Attractions: {len(attractions)}")
    
    # Show results
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    
    if restaurants:
        print("\n🍽️ RESTAURANTS:")
        for i, r in enumerate(restaurants[:3]):
            print(f"  {i+1}. {r.get('name', 'NO NAME')}")
            print(f"     {r.get('address', 'NO ADDRESS')}")
    else:
        print("\n❌ NO RESTAURANTS!")
    
    if attractions:
        print("\n🎭 ATTRACTIONS:")
        for i, a in enumerate(attractions[:3]):
            print(f"  {i+1}. {a.get('name', 'NO NAME')}")
            print(f"     {a.get('address', 'NO ADDRESS')}")
    else:
        print("\n❌ NO ATTRACTIONS!")
    
    # Check daily schedule
    daily = enhanced.get('daily_schedule', [])
    if daily and len(daily) > 1:
        print(f"\n📅 DAY 2 ACTIVITIES:")
        day2 = daily[1]
        for activity in day2.get('activities', []):
            print(f"  • {activity}")
    
    return enhanced

if __name__ == "__main__":
    result = asyncio.run(test_direct())
    
    print("\n" + "=" * 60)
    if result.get('restaurants') and result.get('attractions'):
        print("✅ SUCCESS - Real content generated!")
    else:
        print("❌ FAILED - No real content")
