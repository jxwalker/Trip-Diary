#!/usr/bin/env python3
"""Debug guide generation error"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
import traceback
from src.services.optimized_guide_service import OptimizedGuideService
from src.utils.trip_data_extractor import extract_trip_info, extract_hotel_info

async def debug_generation():
    # Load the trip
    with open('src/data/trips/2c7fa1b4-7819-4169-9db6-c83740c44d96.json', 'r') as f:
        trip = json.load(f)
    
    itinerary = trip['itinerary']
    preferences = trip.get('preferences', {})
    
    print("Input data:")
    print(f"  Itinerary type: {type(itinerary)}")
    print(f"  Preferences type: {type(preferences)}")
    
    # Extract trip info
    destination, start_date, end_date = extract_trip_info(itinerary)
    hotel_info = extract_hotel_info(itinerary, destination)
    
    print(f"  Destination: {destination}")
    print(f"  Hotel info type: {type(hotel_info)}")
    
    # Try to generate
    service = OptimizedGuideService()
    
    try:
        print("\nCalling generate_optimized_guide...")
        result = await service.generate_optimized_guide(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            hotel_info=hotel_info,
            preferences=preferences,
            extracted_data=itinerary
        )
        
        if 'error' in result:
            print(f"Error in result: {result['error']}")
            print(f"Full error: {json.dumps(result, indent=2)}")
        else:
            print("Success!")
            print(f"  Summary length: {len(result.get('summary', ''))}")
            
    except Exception as e:
        print(f"Exception: {e}")
        print(f"Exception type: {type(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_generation())