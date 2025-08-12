#!/usr/bin/env python3
"""Debug why parser isn't extracting data from Perplexity responses"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment from project root .env
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / '.env'
from dotenv import load_dotenv
load_dotenv(env_path)

from services.perplexity_search_service import PerplexitySearchService

async def test_with_debug():
    """Test and debug the parsing"""
    
    service = PerplexitySearchService()
    
    # First, let's make a raw request and see what we get
    prompt = """List the 5 best restaurants in New York City for Italian food. 
    For each restaurant provide:
    - Restaurant name
    - Full street address
    - Price range
    - Why it's recommended
    - Signature dishes
    
    Format your response clearly with each restaurant as a separate section."""
    
    print("1️⃣ Making Perplexity request...")
    raw_response = await service._make_perplexity_request(prompt)
    
    print("\n2️⃣ RAW RESPONSE FROM PERPLEXITY:")
    print("=" * 60)
    print(raw_response)
    print("=" * 60)
    
    # Now test the parser
    print("\n3️⃣ Testing parser on this response...")
    parsed = service._parse_restaurant_response(raw_response)
    
    print(f"\n4️⃣ PARSED RESULT: {len(parsed)} restaurants found")
    for i, r in enumerate(parsed, 1):
        print(f"\nRestaurant {i}:")
        for key, value in r.items():
            print(f"  {key}: {value}")
    
    # Now test the full search_restaurants method
    print("\n5️⃣ Testing full search_restaurants method...")
    restaurants = await service.search_restaurants(
        destination="New York",
        preferences={
            "cuisineTypes": ["Italian"],
            "priceRange": "$$$",
            "dietaryRestrictions": [],
            "groupType": "couple"
        },
        dates={"formatted": "August 9-14, 2025"}
    )
    
    print(f"\n6️⃣ FULL METHOD RESULT: {len(restaurants)} restaurants")
    for i, r in enumerate(restaurants[:3], 1):
        print(f"\nRestaurant {i}:")
        for key, value in r.items():
            if key != 'details' or value:  # Only show details if not empty
                print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_with_debug())