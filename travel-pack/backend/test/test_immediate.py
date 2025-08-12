#!/usr/bin/env python3
"""Test immediate guide generation"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
from dotenv import load_dotenv
load_dotenv(root_dir / '.env')

from services.immediate_guide_generator import ImmediateGuideGenerator

async def test():
    print("🚀 Testing Immediate Guide Generation")
    print("=" * 60)
    
    # Sample itinerary (like what would be generated from your trip)
    itinerary = {
        "trip_summary": {
            "destination": "New York",
            "start_date": "2025-08-09",
            "end_date": "2025-08-14",
            "duration": "6 days"
        },
        "accommodations": [{
            "name": "Luxury Collection Manhattan Midtown",
            "address": "151 West 54th Street, New York, NY"
        }],
        "daily_schedule": [
            {"day": 1, "date": "2025-08-09", "day_name": "Saturday"},
            {"day": 2, "date": "2025-08-10", "day_name": "Sunday"},
            {"day": 3, "date": "2025-08-11", "day_name": "Monday"},
            {"day": 4, "date": "2025-08-12", "day_name": "Tuesday"},
            {"day": 5, "date": "2025-08-13", "day_name": "Wednesday"},
            {"day": 6, "date": "2025-08-14", "day_name": "Thursday"}
        ]
    }
    
    generator = ImmediateGuideGenerator()
    
    print("\n⏳ Generating real content from Perplexity...")
    enhanced = await generator.enhance_itinerary_immediately(itinerary)
    
    # Check results
    print("\n✅ RESULTS:")
    print(f"  Restaurants: {len(enhanced.get('restaurants', []))}")
    print(f"  Attractions: {len(enhanced.get('attractions', []))}")
    
    # Show Day 2 activities
    if enhanced.get('daily_schedule') and len(enhanced['daily_schedule']) > 1:
        day2 = enhanced['daily_schedule'][1]
        print(f"\n📅 Day 2 Activities:")
        for activity in day2.get('activities', []):
            print(f"  • {activity}")
    
    # Check for real content
    if enhanced.get('restaurants'):
        print(f"\n🍽️ Sample Restaurant:")
        r = enhanced['restaurants'][0]
        print(f"  {r.get('name', 'Unknown')}")
        print(f"  {r.get('address', 'No address')}")
    
    return enhanced

if __name__ == "__main__":
    result = asyncio.run(test())
    print("\n" + "=" * 60)
    if result.get('restaurants') or result.get('attractions'):
        print("✅ SUCCESS - Real content generated!")
    else:
        print("❌ Failed to generate real content")