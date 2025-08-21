#!/usr/bin/env python3
"""
Test the full travel guide generation pipeline
"""
import asyncio
import aiohttp
import os
import json
import sys
sys.path.append('..')
from services.enhanced_guide_service import EnhancedGuideService
from dotenv import load_dotenv
from pathlib import Path

# Load environment from project root .env
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

async def test_full_guide():
    """Test generating a complete travel guide"""
    
    # Sample trip data as would come from extraction
    trip_data = {
        "destination": "New York",
        "start_date": "2024-12-20",
        "end_date": "2024-12-23",
        "hotel_info": {
            "name": "The Plaza Hotel",
            "address": "768 5th Ave, New York, NY 10019",
            "check_in": "2024-12-20",
            "check_out": "2024-12-23"
        },
        "preferences": {
            "interests": {
                "artGalleries": True,
                "museums": True,
                "historicalSites": True,
                "theater": True,
                "liveMusic": True,
                "fineDining": True,
                "localCuisine": True
            },
            "cuisines": ["Italian", "French", "Japanese", "American"],
            "dietary": [],
            "priceRange": ["moderate", "expensive"],
            "pace": "moderate",
            "walkingLevel": 3,
            "groupType": "couple",
            "nightlife": True,
            "preferredTimes": {
                "morning": True,
                "afternoon": True,
                "evening": True
            }
        },
        "extracted_data": {
            "flights": [
                {
                    "flight_number": "BA115",
                    "departure": {"airport": "LHR", "date": "2024-12-20", "time": "09:00"},
                    "arrival": {"airport": "JFK", "date": "2024-12-20", "time": "12:00"}
                }
            ]
        }
    }
    
    print("🧪 Testing Full Travel Guide Generation\n")
    print("=" * 60)
    
    # Initialize service
    service = EnhancedGuideService()
    
    print("\n📝 Input Data:")
    print(f"  Destination: {trip_data['destination']}")
    print(f"  Dates: {trip_data['start_date']} to {trip_data['end_date']}")
    print(f"  Hotel: {trip_data['hotel_info']['name']}")
    print(f"  Interests: {', '.join([k for k,v in trip_data['preferences']['interests'].items() if v])}")
    
    print("\n🚀 Generating enhanced guide...")
    
    try:
        guide = await service.generate_enhanced_guide(
            destination=trip_data["destination"],
            start_date=trip_data["start_date"],
            end_date=trip_data["end_date"],
            hotel_info=trip_data["hotel_info"],
            preferences=trip_data["preferences"],
            extracted_data=trip_data["extracted_data"]
        )
        
        print("\n✅ Guide generated successfully!")
        
        # Analyze the response
        print("\n📊 Content Analysis:")
        print(f"  Has summary: {bool(guide.get('summary'))}")
        print(f"  Has daily itinerary: {bool(guide.get('daily_itinerary'))}")
        print(f"  Days in itinerary: {len(guide.get('daily_itinerary', []))}")
        print(f"  Has restaurants: {bool(guide.get('restaurants'))}")
        print(f"  Restaurant count: {len(guide.get('restaurants', []))}")
        print(f"  Has attractions: {bool(guide.get('attractions'))}")
        print(f"  Attraction count: {len(guide.get('attractions', []))}")
        print(f"  Has events: {bool(guide.get('events'))}")
        print(f"  Event count: {len(guide.get('events', []))}")
        print(f"  Has weather: {bool(guide.get('weather'))}")
        print(f"  Has local tips: {bool(guide.get('local_tips'))}")
        print(f"  Has raw content: {bool(guide.get('raw_content'))}")
        
        # Save the output for inspection
        with open("test_guide_output.json", "w") as f:
            json.dump(guide, f, indent=2)
        print("\n💾 Full guide saved to test_guide_output.json")
        
        # Show preview of content
        if guide.get('summary'):
            print(f"\n📖 Summary Preview:")
            print(f"  {guide['summary'][:300]}...")
        
        if guide.get('daily_itinerary') and len(guide['daily_itinerary']) > 0:
            print(f"\n📅 First Day Activities:")
            day1 = guide['daily_itinerary'][0]
            for activity in day1.get('activities', [])[:3]:
                print(f"  • {activity}")
        
        if guide.get('restaurants') and len(guide['restaurants']) > 0:
            print(f"\n🍽️ Top Restaurants:")
            for rest in guide['restaurants'][:3]:
                print(f"  • {rest.get('name', 'Unknown')}: {rest.get('description', '')[:100]}")
        
        if guide.get('raw_content'):
            print(f"\n📄 Raw content length: {len(guide['raw_content'])} characters")
            
            # Check for key content in raw
            raw = guide['raw_content'].lower()
            checks = {
                "Weather mentioned": "weather" in raw or "temperature" in raw,
                "Hotel mentioned": "plaza" in raw,
                "Restaurants mentioned": "restaurant" in raw,
                "Museums mentioned": "museum" in raw or "gallery" in raw,
                "Daily schedule": "day 1" in raw or "morning" in raw
            }
            
            print("\n🔍 Raw Content Checks:")
            for check, found in checks.items():
                status = "✅" if found else "❌"
                print(f"  {status} {check}")
        
    except Exception as e:
        print(f"\n❌ Error generating guide: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to debug the issue
        print("\n🔍 Debugging info:")
        print(f"  PERPLEXITY_API_KEY present: {bool(os.getenv('PERPLEXITY_API_KEY'))}")
        print(f"  OPENAI_API_KEY present: {bool(os.getenv('OPENAI_API_KEY'))}")

async def test_perplexity_direct():
    """Test Perplexity API directly with a simple prompt"""
    
    print("\n\n🔬 Testing Perplexity API Directly")
    print("=" * 60)
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("❌ No PERPLEXITY_API_KEY found")
        return
    
    prompt = """Create a 3-day travel guide for New York City (December 20-23, 2024) for someone staying at The Plaza Hotel.

Include:
1. Daily itinerary with specific times
2. Top 5 restaurants for fine dining
3. Current exhibitions at museums
4. Weather forecast
5. Broadway shows currently running

Use current real-time information from the web."""
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.perplexity.ai/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert travel guide with access to real-time web information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 3000
            }
            
            print("📤 Sending request to Perplexity...")
            
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"📥 Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    print("\n✅ Success! Response preview:")
                    print(content[:500] + "...")
                    
                    # Save full response
                    with open("test_perplexity_raw.md", "w") as f:
                        f.write(content)
                    print("\n💾 Full response saved to test_perplexity_raw.md")
                    
                    # Check content quality
                    checks = {
                        "Has daily schedule": "day 1" in content.lower(),
                        "Has restaurants": "restaurant" in content.lower(),
                        "Has weather": "weather" in content.lower() or "temperature" in content.lower(),
                        "Has museums": "museum" in content.lower(),
                        "Has specific times": any(x in content.lower() for x in ["am", "pm", ":00"]),
                        "Mentions Plaza Hotel": "plaza" in content.lower()
                    }
                    
                    print("\n🔍 Content Quality Checks:")
                    for check, found in checks.items():
                        status = "✅" if found else "❌"
                        print(f"  {status} {check}")
                    
                else:
                    error_text = await response.text()
                    print(f"\n❌ Error: {error_text}")
                    
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    
    # First test Perplexity directly
    await test_perplexity_direct()
    
    # Then test the full guide generation
    await test_full_guide()
    
    print("\n" + "=" * 60)
    print("🏁 All tests complete!")

if __name__ == "__main__":
    asyncio.run(main())