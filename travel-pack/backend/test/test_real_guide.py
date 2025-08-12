#!/usr/bin/env python3
"""
Test script to verify real guide generation without mocks
"""
import asyncio
import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.enhanced_guide_service import EnhancedGuideService
from services.perplexity_search_service import PerplexitySearchService
from dotenv import load_dotenv
from pathlib import Path

# Load environment from project root .env
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

async def test_real_guide_generation():
    """Test generating a real guide with actual data"""
    
    print("🚀 Testing Real Guide Generation (NO MOCKS)")
    print("=" * 60)
    
    # Check if API key is configured
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("❌ PERPLEXITY_API_KEY not found in .env file")
        print("Please add: PERPLEXITY_API_KEY=your_key_here")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    # Set up test data based on your example
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
    
    preferences = {
        "travelStyle": "balanced",
        "groupType": "single",
        "walkingTolerance": 4,
        "adventureLevel": 3,
        "nightlife": 3,
        "priceRange": "$$$",
        "cuisineTypes": ["American", "Italian", "Asian Fusion"],
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
        ],
        "hotels": [hotel_info],
        "passengers": [{"name": "Traveler"}]
    }
    
    print("\n📍 Trip Details:")
    print(f"  Destination: {destination}")
    print(f"  Dates: {start_date} to {end_date}")
    print(f"  Hotel: {hotel_info['name']}")
    print(f"  Interests: {', '.join(preferences['specialInterests'])}")
    
    # Initialize the service
    print("\n🔧 Initializing Enhanced Guide Service...")
    service = EnhancedGuideService()
    
    # Generate the guide
    print("\n📝 Generating real travel guide (this may take 30-60 seconds)...")
    
    try:
        guide = await service.generate_enhanced_guide(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            hotel_info=hotel_info,
            preferences=preferences,
            extracted_data=extracted_data
        )
        
        # Check for errors
        if "error" in guide:
            print(f"\n❌ Error: {guide['error']}")
            print(f"   Message: {guide.get('message', '')}")
            return False
        
        # Save the guide for inspection
        output_file = "test_real_guide_output.json"
        with open(output_file, 'w') as f:
            json.dump(guide, f, indent=2)
        
        print(f"\n✅ Guide generated successfully! Saved to {output_file}")
        
        # Analyze the content
        print("\n📊 Content Analysis:")
        print("=" * 40)
        
        # Check restaurants
        if guide.get("restaurants"):
            print(f"✅ Restaurants: {len(guide['restaurants'])} found")
            for i, restaurant in enumerate(guide['restaurants'][:3], 1):
                print(f"   {i}. {restaurant.get('name', 'Unknown')}")
                if restaurant.get('address'):
                    print(f"      📍 {restaurant['address']}")
        else:
            print("❌ No restaurants found")
        
        # Check attractions
        if guide.get("attractions"):
            print(f"\n✅ Attractions: {len(guide['attractions'])} found")
            for i, attraction in enumerate(guide['attractions'][:3], 1):
                print(f"   {i}. {attraction.get('name', 'Unknown')}")
                if attraction.get('address'):
                    print(f"      📍 {attraction['address']}")
        else:
            print("❌ No attractions found")
        
        # Check events
        if guide.get("events"):
            print(f"\n✅ Events: {len(guide['events'])} found")
            for i, event in enumerate(guide['events'][:3], 1):
                print(f"   {i}. {event.get('name', event.get('description', 'Unknown'))[:60]}...")
        else:
            print("⚠️  No events found (this may be normal)")
        
        # Check daily itinerary
        if guide.get("daily_itinerary"):
            print(f"\n✅ Daily Itinerary: {len(guide['daily_itinerary'])} days")
            for day in guide['daily_itinerary'][:2]:
                print(f"   Day {day.get('day', '?')}: {day.get('date', '')} ({day.get('day_of_week', '')})")
                if day.get('morning'):
                    print(f"      Morning: {len(day['morning'])} activities")
                if day.get('afternoon'):
                    print(f"      Afternoon: {len(day['afternoon'])} activities")
                if day.get('evening'):
                    print(f"      Evening: {len(day['evening'])} activities")
        else:
            print("❌ No daily itinerary found")
        
        # Check for placeholder text (should not exist)
        print("\n🔍 Checking for placeholder text...")
        guide_str = json.dumps(guide).lower()
        placeholders = [
            "explore local",
            "try local cuisine",
            "cultural activities",
            "top restaurant",
            "highly rated",
            "experience",
            "tbd",
            "typical"
        ]
        
        found_placeholders = []
        for placeholder in placeholders:
            if placeholder in guide_str:
                found_placeholders.append(placeholder)
        
        if found_placeholders:
            print(f"⚠️  Found potential placeholders: {', '.join(found_placeholders)}")
        else:
            print("✅ No obvious placeholders detected!")
        
        # Check for real content indicators
        print("\n✅ Real Content Indicators:")
        real_indicators = {
            "Specific addresses": any("street" in str(guide).lower() or "avenue" in str(guide).lower()),
            "Current prices": "$" in str(guide),
            "Opening hours": any(word in str(guide).lower() for word in ["am", "pm", "monday", "tuesday"]),
            "Real venue names": not any(ph in str(guide) for ph in ["Top Restaurant", "Experience"])
        }
        
        for indicator, found in real_indicators.items():
            status = "✅" if found else "❌"
            print(f"   {status} {indicator}")
        
        # Display a sample of the content
        print("\n📄 Sample Content:")
        print("=" * 40)
        
        if guide.get("restaurants") and len(guide["restaurants"]) > 0:
            restaurant = guide["restaurants"][0]
            print(f"Restaurant Example: {restaurant.get('name', 'N/A')}")
            if restaurant.get('description'):
                print(f"  {restaurant['description'][:200]}...")
        
        if guide.get("daily_itinerary") and len(guide["daily_itinerary"]) > 0:
            day = guide["daily_itinerary"][0]
            print(f"\nDay 1 Morning Activities:")
            for activity in day.get("morning", [])[:2]:
                print(f"  - {activity[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_perplexity_search_directly():
    """Test the Perplexity search service directly"""
    
    print("\n\n🔬 Testing Perplexity Search Service Directly")
    print("=" * 60)
    
    service = PerplexitySearchService()
    
    if not service.api_key:
        print("❌ No API key configured")
        return False
    
    print("Testing restaurant search for New York...")
    
    try:
        restaurants = await service.search_restaurants(
            destination="New York",
            preferences={
                "cuisineTypes": ["Italian", "American"],
                "priceRange": "$$$",
                "dietaryRestrictions": [],
                "groupType": "couple"
            },
            dates={"formatted": "August 9-14, 2025"}
        )
        
        print(f"✅ Found {len(restaurants)} restaurants")
        for i, restaurant in enumerate(restaurants[:3], 1):
            print(f"   {i}. {restaurant.get('name', 'Unknown')}")
            if restaurant.get('address'):
                print(f"      Address: {restaurant['address']}")
            if restaurant.get('cuisine'):
                print(f"      Cuisine: {restaurant['cuisine']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Run all tests"""
    
    print("🧪 REAL TRAVEL GUIDE GENERATION TEST")
    print("=" * 60)
    print("This test verifies that the system generates real content")
    print("using Perplexity search, not placeholders or mocks.")
    print("=" * 60)
    
    # Test direct search first
    search_works = await test_perplexity_search_directly()
    
    if search_works:
        # Test full guide generation
        await test_real_guide_generation()
    else:
        print("\n❌ Direct search test failed. Check your API configuration.")
    
    print("\n" + "=" * 60)
    print("🏁 Tests complete!")
    print("\nIf successful, check the generated files:")
    print("  - test_real_guide_output.json (full guide)")
    print("\nThe guide should contain:")
    print("  ✓ Real restaurant names and addresses")
    print("  ✓ Actual attractions with current hours")
    print("  ✓ Specific daily activities")
    print("  ✓ Current local information")
    print("  ✗ NO generic placeholders")
    print("  ✗ NO 'Explore local' or 'Try cuisine' text")

if __name__ == "__main__":
    asyncio.run(main())