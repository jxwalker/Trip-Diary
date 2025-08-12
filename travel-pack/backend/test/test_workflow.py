#!/usr/bin/env python3
"""Test the complete workflow with manual trip entry"""
import requests
import json
import time

print("🧪 Testing Complete Workflow with Real Perplexity")
print("=" * 60)

# Step 1: Create a trip with manual entry
print("\n1️⃣ Creating trip with manual entry...")

manual_data = {
    "destination": "New York",
    "start_date": "2025-08-09",
    "end_date": "2025-08-14",
    "passengers": [{"name": "Traveler"}],
    "flights": [
        {
            "flight_number": "BA 115",
            "airline": "British Airways",
            "departure_airport": "LHR",
            "arrival_airport": "JFK",
            "departure_date": "2025-08-09",
            "departure_time": "14:40",
            "arrival_time": "17:35"
        }
    ],
    "hotels": [
        {
            "name": "Luxury Collection Manhattan Midtown",
            "address": "151 West 54th Street, New York, NY",
            "check_in_date": "2025-08-09",
            "check_out_date": "2025-08-14"
        }
    ]
}

try:
    response = requests.post(
        "http://localhost:8000/api/manual-entry",
        json=manual_data
    )
    
    if response.status_code == 200:
        result = response.json()
        trip_id = result.get("trip_id")
        print(f"✅ Trip created: {trip_id}")
    else:
        print(f"❌ Failed to create trip: {response.status_code}")
        print(response.text)
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Set preferences
print("\n2️⃣ Setting preferences...")

preferences = {
    "travelStyle": "balanced",
    "groupType": "single",
    "walkingTolerance": 4,
    "adventureLevel": 3,
    "nightlife": 3,
    "priceRange": "$$$",
    "cuisineTypes": ["Italian", "American", "Japanese"],
    "dietaryRestrictions": [],
    "specialInterests": ["museums", "architecture", "food", "theater", "shopping"],
    "preferredTimes": {
        "morning": True,
        "afternoon": True,
        "evening": True
    }
}

response = requests.post(
    f"http://localhost:8000/api/preferences/{trip_id}",
    json=preferences
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Preferences set and guide generated")
    print(f"   Summary: {result.get('guide_preview', {}).get('has_summary')}")
    print(f"   Days: {result.get('guide_preview', {}).get('itinerary_days')}")
    print(f"   Restaurants: {result.get('guide_preview', {}).get('restaurants_found')}")
    print(f"   Attractions: {result.get('guide_preview', {}).get('attractions_found')}")
    print(f"   Events: {result.get('guide_preview', {}).get('events_found')}")
else:
    print(f"❌ Failed to set preferences: {response.status_code}")
    print(response.text[:500])

# Step 3: Get the enhanced guide
print("\n3️⃣ Retrieving enhanced guide...")

response = requests.get(f"http://localhost:8000/api/enhanced-guide/{trip_id}")

if response.status_code == 200:
    guide = response.json()
    
    # Save the guide
    with open("workflow_test_guide.json", "w") as f:
        json.dump(guide, f, indent=2)
    
    print(f"✅ Guide retrieved and saved to workflow_test_guide.json")
    
    # Display sample content
    print("\n📊 Guide Content Analysis:")
    print("=" * 40)
    
    # Check for real content
    if guide.get("restaurants"):
        print(f"\n🍽️ Restaurants ({len(guide['restaurants'])} found):")
        for i, r in enumerate(guide["restaurants"][:3], 1):
            print(f"  {i}. {r.get('name', 'Unknown')}")
            if r.get('address'):
                print(f"     📍 {r['address']}")
    
    if guide.get("attractions"):
        print(f"\n🎭 Attractions ({len(guide['attractions'])} found):")
        for i, a in enumerate(guide["attractions"][:3], 1):
            print(f"  {i}. {a.get('name', 'Unknown')}")
    
    if guide.get("daily_itinerary"):
        print(f"\n📅 Daily Itinerary ({len(guide['daily_itinerary'])} days):")
        if guide["daily_itinerary"]:
            day = guide["daily_itinerary"][0]
            print(f"  Day 1: {day.get('date')} ({day.get('day_of_week', '')})")
            if day.get("morning"):
                print(f"    Morning activities: {len(day['morning'])}")
            if day.get("afternoon"):
                print(f"    Afternoon activities: {len(day['afternoon'])}")
    
    # Check for placeholder text
    guide_str = json.dumps(guide).lower()
    placeholders = ["explore local", "try local cuisine", "top restaurant", "experience"]
    found_placeholders = [p for p in placeholders if p in guide_str]
    
    if found_placeholders:
        print(f"\n⚠️ Warning: Found potential placeholders: {', '.join(found_placeholders)}")
    else:
        print(f"\n✅ No obvious placeholders detected!")
    
    # Check for real indicators
    real_indicators = {
        "Street addresses": "street" in guide_str or "avenue" in guide_str,
        "Specific prices": "$" in guide_str,
        "Real venues": not any(p in guide_str for p in ["top restaurant", "experience"])
    }
    
    print("\n✅ Real Content Indicators:")
    for indicator, found in real_indicators.items():
        status = "✅" if found else "❌"
        print(f"  {status} {indicator}")
        
else:
    print(f"❌ Failed to get guide: {response.status_code}")

print("\n" + "=" * 60)
print("🏁 Workflow test complete!")
print("\nCheck workflow_test_guide.json for full guide content")