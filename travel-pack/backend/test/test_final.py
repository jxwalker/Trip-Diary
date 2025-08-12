#!/usr/bin/env python3
"""Final test - upload NYC trip and verify real content is generated"""
import requests
import json
import time

# Create NYC trip file
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

print("=" * 60)
print("FINAL TEST - NYC TRIP WITH REAL CONTENT")
print("=" * 60)

# Create file
with open('/tmp/nyc_trip.txt', 'w') as f:
    f.write(trip_content)

# Upload
print("\n1. Uploading NYC trip document...")
with open('/tmp/nyc_trip.txt', 'rb') as f:
    files = {'file': ('nyc_trip.txt', f, 'text/plain')}
    data = {'file_type': 'pdf'}
    response = requests.post('http://localhost:8000/api/upload', files=files, data=data)

if response.status_code != 200:
    print(f"❌ Upload failed: {response.status_code}")
    print(response.text)
    exit(1)

upload_data = response.json()
trip_id = upload_data['trip_id']
print(f"✓ Trip ID: {trip_id}")

# Wait for processing
print("\n2. Waiting for backend processing...")
max_attempts = 30
for i in range(max_attempts):
    status_response = requests.get(f'http://localhost:8000/api/status/{trip_id}')
    if status_response.ok:
        status_data = status_response.json()
        print(f"   {status_data['progress']}% - {status_data['message']}")
        if status_data['status'] == 'completed':
            break
        elif status_data['status'] == 'error':
            print(f"❌ Error: {status_data['message']}")
            exit(1)
    time.sleep(2)

# Get itinerary
print("\n3. Fetching processed itinerary...")
itinerary_response = requests.get(f'http://localhost:8000/api/itinerary/{trip_id}')
if not itinerary_response.ok:
    print(f"❌ Failed to get itinerary: {itinerary_response.status_code}")
    exit(1)

data = itinerary_response.json()
itinerary = data.get('itinerary', {})

print("\n" + "=" * 60)
print("RESULTS:")
print("=" * 60)

# Check trip summary
summary = itinerary.get('trip_summary', {})
print(f"\nTRIP SUMMARY:")
print(f"  Destination: {summary.get('destination', 'NOT SET')}")
print(f"  Dates: {summary.get('start_date', 'NOT SET')} to {summary.get('end_date', 'NOT SET')}")
print(f"  Duration: {summary.get('duration', 'NOT SET')}")

# Check flights
flights = itinerary.get('flights', [])
print(f"\nFLIGHTS: {len(flights)} found")
if flights:
    f = flights[0]
    print(f"  First flight: {f.get('flight_number', 'NO NUMBER')} - {f.get('airline', 'NO AIRLINE')}")
    print(f"  Route: {f.get('departure', {}).get('airport')} → {f.get('arrival', {}).get('airport')}")

# Check hotels
hotels = itinerary.get('accommodations', [])
print(f"\nHOTELS: {len(hotels)} found")
if hotels:
    h = hotels[0]
    print(f"  Hotel: {h.get('name', 'NO NAME')}")
    print(f"  Address: {h.get('address', 'NO ADDRESS')}")

# THE CRITICAL TEST - Real restaurants from Perplexity
restaurants = itinerary.get('restaurants', [])
print(f"\n🍽️ RESTAURANTS: {len(restaurants)} found")
if restaurants:
    for i, r in enumerate(restaurants[:3]):
        print(f"\n  Restaurant #{i+1}:")
        print(f"    Name: {r.get('name', 'NO NAME')}")
        print(f"    Address: {r.get('address', 'NO ADDRESS')}")
        print(f"    Cuisine: {r.get('cuisine', 'NO CUISINE')}")
else:
    print("  ❌ NO RESTAURANTS FOUND!")

# Attractions
attractions = itinerary.get('attractions', [])
print(f"\n🎭 ATTRACTIONS: {len(attractions)} found")
if attractions:
    for i, a in enumerate(attractions[:3]):
        print(f"\n  Attraction #{i+1}:")
        print(f"    Name: {a.get('name', 'NO NAME')}")
        print(f"    Address: {a.get('address', 'NO ADDRESS')}")
        print(f"    Type: {a.get('type', 'NO TYPE')}")
else:
    print("  ❌ NO ATTRACTIONS FOUND!")

# Check for placeholder text
print("\n" + "=" * 60)
print("PLACEHOLDER CHECK:")
print("=" * 60)
response_str = json.dumps(data)
bad_phrases = [
    "Explore local attractions",
    "Try local cuisine", 
    "Cultural activities",
    "Morning activities",
    "Afternoon exploration"
]

found_bad = []
for phrase in bad_phrases:
    if phrase in response_str:
        found_bad.append(phrase)

if found_bad:
    print("❌ FOUND PLACEHOLDER TEXT:")
    for p in found_bad:
        print(f"   - {p}")
else:
    print("✅ No placeholder text found!")

# Final verdict
print("\n" + "=" * 60)
if restaurants and attractions and not found_bad:
    print("✅✅✅ SUCCESS! Real content generated!")
    print(f"View at: http://localhost:3000/itinerary-simple?tripId={trip_id}")
else:
    print("❌ FAILED - Still getting placeholders or no content")
    if not restaurants:
        print("  - No restaurants generated")
    if not attractions:
        print("  - No attractions generated")
    if found_bad:
        print("  - Found placeholder text")

# Save for inspection
with open('/tmp/final_test_response.json', 'w') as f:
    json.dump(data, f, indent=2)
print(f"\nFull response saved to /tmp/final_test_response.json")