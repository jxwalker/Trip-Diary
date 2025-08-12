#!/usr/bin/env python3
"""Test NYC trip with real data generation"""
import requests
import json
import time

# Simulate uploading a trip with your NYC data
trip_data = {
    "file_name": "NYC_Trip.pdf",
    "pages": ["Flight BA 115 LHR to JFK, Hotel Luxury Collection Manhattan"],
    "content": """
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
}

print("🗽 Testing NYC Trip Upload with Real Content Generation")
print("=" * 60)

# Start upload
response = requests.post(
    "http://localhost:8000/api/upload",
    files={"file": ("nyc_trip.pdf", json.dumps(trip_data).encode(), "application/json")},
    data={"file_type": "pdf"}
)

if response.status_code == 200:
    data = response.json()
    trip_id = data["trip_id"]
    print(f"✅ Upload started: {trip_id}")
    
    # Poll for completion
    print("\n⏳ Processing (this will now include real Perplexity searches)...")
    
    for i in range(30):
        status_response = requests.get(f"http://localhost:8000/api/status/{trip_id}")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"   {status['progress']}% - {status['message']}")
            
            if status["status"] == "completed":
                print("\n✅ Processing complete!")
                break
        
        time.sleep(2)
    
    # Get the itinerary
    print("\n📋 Getting itinerary...")
    itin_response = requests.get(f"http://localhost:8000/api/itinerary/{trip_id}")
    
    if itin_response.status_code == 200:
        result = itin_response.json()
        
        # Save full result
        with open("test/nyc_trip_result.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"\n✅ Full result saved to test/nyc_trip_result.json")
        
        # Check for real content
        itinerary = result.get("itinerary", {})
        
        # Check restaurants
        restaurants = itinerary.get("restaurants", [])
        print(f"\n🍽️ RESTAURANTS: {len(restaurants)} found")
        for r in restaurants[:3]:
            print(f"  - {r.get('name', 'Unknown')}")
            if r.get('address'):
                print(f"    📍 {r['address']}")
        
        # Check attractions
        attractions = itinerary.get("attractions", [])
        print(f"\n🎭 ATTRACTIONS: {len(attractions)} found")
        for a in attractions[:3]:
            print(f"  - {a.get('name', 'Unknown')}")
            if a.get('address'):
                print(f"    📍 {a['address']}")
        
        # Check daily schedule
        daily = itinerary.get("daily_schedule", [])
        if daily and len(daily) > 1:
            print(f"\n📅 DAY 2 ACTIVITIES:")
            day2 = daily[1] if len(daily) > 1 else daily[0]
            for activity in day2.get("activities", [])[:4]:
                print(f"  • {activity}")
        
        # Check for placeholders
        full_str = json.dumps(result)
        if "Explore local attractions" in full_str:
            print("\n⚠️ WARNING: Still contains placeholders!")
        else:
            print("\n✅ NO PLACEHOLDERS DETECTED!")
        
else:
    print(f"❌ Upload failed: {response.status_code}")
    print(response.text)