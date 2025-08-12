#!/usr/bin/env python3
"""Debug what's actually stored for a trip"""
import requests
import json

# Get all trips to find one
response = requests.get("http://localhost:8000/api/trips")
if response.status_code == 200:
    trips = response.json()
    print(f"Found {len(trips)} trips")
    
    if trips:
        # Get the first trip
        trip_id = trips[0]["trip_id"]
        print(f"\nChecking trip: {trip_id}")
        
        # Get itinerary
        itin_response = requests.get(f"http://localhost:8000/api/itinerary/{trip_id}")
        if itin_response.status_code == 200:
            data = itin_response.json()
            
            # Save full data
            with open("test/debug_trip_data.json", "w") as f:
                json.dump(data, f, indent=2)
            
            print("\n=== DAILY SCHEDULE ===")
            if "itinerary" in data and "daily_schedule" in data["itinerary"]:
                for day in data["itinerary"]["daily_schedule"][:2]:
                    print(f"\nDay {day.get('day')}:")
                    for key, value in day.items():
                        if key != "day":
                            print(f"  {key}: {value}")
            
            print("\nFull data saved to test/debug_trip_data.json")
        else:
            print(f"Failed to get itinerary: {itin_response.status_code}")
else:
    print(f"Failed to get trips: {response.status_code}")