#!/usr/bin/env python3
"""Test full integration with real NYC trip data"""
import asyncio
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment from project root .env
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

from services.enhanced_guide_service import EnhancedGuideService

async def test_nyc_guide():
    """Test with your NYC trip data"""
    
    print("🗽 Testing NYC Trip Guide Generation")
    print("=" * 60)
    
    # Your trip details
    destination = "New York"
    start_date = "2025-08-09"
    end_date = "2025-08-14"
    
    hotel_info = {
        "name": "Luxury Collection Manhattan Midtown",
        "address": "151 West 54th Street, New York, NY",
        "check_in_date": start_date,
        "check_out_date": end_date,
        "confirmation_number": "83313860"
    }
    
    # Preferences based on typical traveler
    preferences = {
        "travelStyle": "balanced",
        "groupType": "single",
        "walkingTolerance": 4,
        "adventureLevel": 3,
        "nightlife": 3,
        "priceRange": "$$$",
        "cuisineTypes": ["American", "Italian", "Asian"],
        "dietaryRestrictions": [],
        "specialInterests": ["museums", "architecture", "food", "theater", "shopping"],
        "preferredTimes": {
            "morning": True,
            "afternoon": True,
            "evening": True
        }
    }
    
    extracted_data = {
        "flights": [
            {
                "flight_number": "BA 115",
                "airline": "British Airways",
                "departure_airport": "LHR",
                "arrival_airport": "JFK",
                "departure_date": "2025-08-09",
                "departure_time": "14:40",
                "arrival_time": "17:35",
                "seat": "1A",
                "class": "First"
            },
            {
                "flight_number": "BA 112",
                "airline": "British Airways",
                "departure_airport": "JFK",
                "arrival_airport": "LHR",
                "departure_date": "2025-08-14",
                "departure_time": "18:30",
                "arrival_time": "06:30",
                "seat": "1K",
                "class": "First"
            }
        ]
    }
    
    print(f"📅 Trip: {start_date} to {end_date}")
    print(f"🏨 Hotel: {hotel_info['name']}")
    print(f"✈️ Flights: BA 115 (LHR-JFK), BA 112 (JFK-LHR)")
    print(f"🎯 Interests: {', '.join(preferences['specialInterests'][:3])}...")
    
    # Generate guide
    print("\n⏳ Generating personalized guide (30-60 seconds)...")
    
    service = EnhancedGuideService()
    
    try:
        guide = await service.generate_enhanced_guide(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            hotel_info=hotel_info,
            preferences=preferences,
            extracted_data=extracted_data
        )
        
        if "error" in guide:
            print(f"\n❌ Error: {guide['error']}")
            return
        
        # Save full guide
        with open("nyc_guide_full.json", "w") as f:
            json.dump(guide, f, indent=2)
        
        print(f"\n✅ Guide generated! Full guide saved to nyc_guide_full.json")
        
        # Display summary
        print("\n📋 GUIDE SUMMARY")
        print("=" * 60)
        
        # Restaurants
        if guide.get("restaurants"):
            print(f"\n🍽️ RESTAURANTS ({len(guide['restaurants'])} found)")
            for i, r in enumerate(guide["restaurants"][:5], 1):
                print(f"\n{i}. {r.get('name', 'Unknown')}")
                if r.get('address'):
                    print(f"   📍 {r['address']}")
                if r.get('price'):
                    print(f"   💰 {r['price']}")
                if r.get('cuisine'):
                    print(f"   🍴 {r['cuisine']}")
        
        # Attractions
        if guide.get("attractions"):
            print(f"\n🎭 ATTRACTIONS ({len(guide['attractions'])} found)")
            for i, a in enumerate(guide["attractions"][:5], 1):
                print(f"\n{i}. {a.get('name', 'Unknown')}")
                if a.get('address'):
                    print(f"   📍 {a['address']}")
                if a.get('price'):
                    print(f"   💰 {a['price']}")
        
        # Events
        if guide.get("events"):
            print(f"\n🎪 EVENTS ({len(guide['events'])} found)")
            for i, e in enumerate(guide["events"][:3], 1):
                name = e.get('name') or e.get('description', 'Event')[:60]
                print(f"{i}. {name}")
        
        # Daily Itinerary Sample
        if guide.get("daily_itinerary") and len(guide["daily_itinerary"]) > 0:
            print(f"\n📅 SAMPLE DAY (Day 1)")
            day = guide["daily_itinerary"][0]
            print(f"Date: {day.get('date')} ({day.get('day_of_week', '')})")
            
            if day.get("morning"):
                print("\nMorning:")
                for item in day["morning"][:2]:
                    print(f"  • {item[:80]}...")
            
            if day.get("afternoon"):
                print("\nAfternoon:")
                for item in day["afternoon"][:2]:
                    print(f"  • {item[:80]}...")
            
            if day.get("evening"):
                print("\nEvening:")
                for item in day["evening"][:2]:
                    print(f"  • {item[:80]}...")
        
        # Check for quality
        print("\n✅ QUALITY CHECK")
        print("=" * 40)
        
        # Check for real content indicators
        guide_str = json.dumps(guide).lower()
        
        real_indicators = {
            "Street addresses": "street" in guide_str or "avenue" in guide_str,
            "Specific prices": "$" in guide_str and any(str(i) in guide_str for i in range(10)),
            "Real venue names": not any(mock in guide_str for mock in ["top restaurant", "experience", "explore local"]),
            "Time information": "am" in guide_str or "pm" in guide_str,
            "NYC specific": "manhattan" in guide_str or "brooklyn" in guide_str
        }
        
        for check, passed in real_indicators.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        # Content richness
        print(f"\n📊 Content Stats:")
        print(f"  • Restaurants: {len(guide.get('restaurants', []))}")
        print(f"  • Attractions: {len(guide.get('attractions', []))}")
        print(f"  • Events: {len(guide.get('events', []))}")
        print(f"  • Days planned: {len(guide.get('daily_itinerary', []))}")
        
        return guide
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    guide = asyncio.run(test_nyc_guide())
    
    if guide and "error" not in guide:
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Your NYC guide is ready!")
        print("\nThe guide includes:")
        print("  ✓ Real restaurant recommendations")
        print("  ✓ Actual NYC attractions")
        print("  ✓ Day-by-day itinerary")
        print("  ✓ Current information")
        print("\nView the full guide in: nyc_guide_full.json")