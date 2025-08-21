#!/usr/bin/env python3
"""Test the actual upload API to see what returns"""
import requests
import json
import time

# Create a test file with NYC trip data
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

# Create file
with open('/tmp/test_trip.txt', 'w') as f:
    f.write(trip_content)

# Upload it
print("1. Uploading trip document...")
with open('/tmp/test_trip.txt', 'rb') as f:
    files = {'file': ('test_trip.txt', f, 'text/plain')}
    data = {'use_vision': 'false'}
    response = requests.post('http://localhost:8000/api/upload-single', files=files, data=data)

if response.status_code != 200:
    print(f"Upload failed: {response.status_code}")
    print(response.text)
    exit(1)

upload_data = response.json()
trip_id = upload_data['trip_id']
print(f"✓ Upload successful! Trip ID: {trip_id}")

# Wait for processing
print("\n2. Waiting for processing...")
for i in range(30):
    status_response = requests.get(f'http://localhost:8000/api/status/{trip_id}')
    if status_response.ok:
        status_data = status_response.json()
        print(f"   {status_data['progress']}% - {status_data['message']}")
        if status_data['status'] == 'completed':
            break
    time.sleep(2)

# Get the itinerary
print("\n3. Fetching itinerary...")
itinerary_response = requests.get(f'http://localhost:8000/api/itinerary/{trip_id}')
if not itinerary_response.ok:
    print(f"Failed to get itinerary: {itinerary_response.status_code}")
    exit(1)

itinerary_data = itinerary_response.json()

print("\n4. ANALYZING RESPONSE:")
print("=" * 60)

# Check for restaurants
restaurants = itinerary_data.get('itinerary', {}).get('restaurants', [])
print(f"\nRESTAURANTS FOUND: {len(restaurants)}")
for i, r in enumerate(restaurants[:3]):
    print(f"  {i+1}. {r.get('name', 'NO NAME')}")
    print(f"     Address: {r.get('address', 'NO ADDRESS')}")

# Check for attractions
attractions = itinerary_data.get('itinerary', {}).get('attractions', [])
print(f"\nATTRACTIONS FOUND: {len(attractions)}")
for i, a in enumerate(attractions[:3]):
    print(f"  {i+1}. {a.get('name', 'NO NAME')}")
    print(f"     Address: {a.get('address', 'NO ADDRESS')}")

# Check daily schedule
daily = itinerary_data.get('itinerary', {}).get('daily_schedule', [])
if daily and len(daily) > 1:
    day2 = daily[1]
    print(f"\nDAY 2 ACTIVITIES:")
    for activity in day2.get('activities', []):
        print(f"  • {activity}")

# Look for placeholder text
print("\n5. CHECKING FOR PLACEHOLDERS:")
response_str = json.dumps(itinerary_data)
placeholders = [
    "Explore local attractions",
    "Try local cuisine",
    "Cultural activities",
    "Evening: Dinner and entertainment",
    "Morning activities",
    "Afternoon exploration"
]

found_placeholders = []
for placeholder in placeholders:
    if placeholder in response_str:
        found_placeholders.append(placeholder)

if found_placeholders:
    print(f"❌ FOUND PLACEHOLDER TEXT:")
    for p in found_placeholders:
        print(f"   - {p}")
else:
    print("✓ No placeholder text found!")

# Save full response for inspection
with open('/tmp/api_response.json', 'w') as f:
    json.dump(itinerary_data, f, indent=2)
print(f"\nFull response saved to /tmp/api_response.json")
print(f"View at: http://localhost:3000/itinerary-simple?tripId={trip_id}")