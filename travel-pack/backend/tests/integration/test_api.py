#!/usr/bin/env python3
"""Test the API endpoint for enhanced guide generation"""
import requests
import json

# Test data matching your NYC trip
data = {
    "destination": "New York",
    "start_date": "2025-08-09", 
    "end_date": "2025-08-14",
    "hotel_info": {
        "name": "Luxury Collection Manhattan Midtown",
        "address": "151 West 54th Street, New York, NY"
    },
    "preferences": {
        "travelStyle": "balanced",
        "groupType": "single",
        "walkingTolerance": 4,
        "adventureLevel": 3,
        "nightlife": 3,
        "priceRange": "$$$",
        "cuisineTypes": ["Italian", "American", "Asian"],
        "dietaryRestrictions": [],
        "specialInterests": ["museums", "architecture", "food", "theater"],
        "preferredTimes": {
            "morning": True,
            "afternoon": True,
            "evening": True
        }
    },
    "extracted_data": {
        "flights": [
            {
                "flight_number": "BA 115",
                "airline": "British Airways",
                "departure_airport": "LHR",
                "arrival_airport": "JFK",
                "departure_date": "2025-08-09"
            }
        ]
    }
}

print("🚀 Testing Enhanced Guide API Endpoint")
print("=" * 50)
print(f"Destination: {data['destination']}")
print(f"Dates: {data['start_date']} to {data['end_date']}")
print(f"Interests: {', '.join(data['preferences']['specialInterests'])}")

print("\n⏳ Calling API (this may take 30-60 seconds)...")

try:
    response = requests.post(
        "http://localhost:8000/api/generate-enhanced-guide",
        json=data,
        timeout=90
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        guide = response.json()
        
        if "error" in guide:
            print(f"\n❌ Error: {guide['error']}")
            print(f"Message: {guide.get('message', '')}")
        else:
            # Save the guide
            with open("api_test_guide.json", "w") as f:
                json.dump(guide, f, indent=2)
            
            print("\n✅ Guide generated successfully!")
            print(f"Saved to: api_test_guide.json")
            
            # Show summary
            print("\n📊 Content Summary:")
            print(f"  Restaurants: {len(guide.get('restaurants', []))}")
            print(f"  Attractions: {len(guide.get('attractions', []))}")
            print(f"  Events: {len(guide.get('events', []))}")
            print(f"  Days: {len(guide.get('daily_itinerary', []))}")
            
            # Show sample restaurant
            if guide.get('restaurants'):
                print("\n🍽️ Sample Restaurant:")
                r = guide['restaurants'][0]
                print(f"  {r.get('name', 'Unknown')}")
                if r.get('address'):
                    print(f"  📍 {r['address']}")
                if r.get('description'):
                    print(f"  ℹ️ {r['description'][:100]}...")
    else:
        print(f"\n❌ API Error: {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("\n⏱️ Request timed out (>90 seconds)")
except requests.exceptions.ConnectionError:
    print("\n❌ Could not connect to API. Is the backend server running?")
    print("Run: ./server-manager.sh backend start")
except Exception as e:
    print(f"\n❌ Error: {e}")