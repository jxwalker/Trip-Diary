#!/usr/bin/env python3
"""Quick test of Perplexity API"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment from project root .env
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(env_path)

from services.perplexity_search_service import PerplexitySearchService

async def test():
    print("Testing Perplexity API with your key...")
    service = PerplexitySearchService()
    
    if not service.api_key:
        print("❌ No API key found")
        return
    
    print(f"✅ Found key: {service.api_key[:15]}...")
    
    # Quick restaurant search
    try:
        print("\nSearching for real NYC restaurants...")
        restaurants = await service.search_restaurants(
            destination="New York",
            preferences={
                "cuisineTypes": ["Italian", "American"],
                "priceRange": "$$$",
                "dietaryRestrictions": [],
                "groupType": "single"
            },
            dates={"formatted": "August 9-14, 2025"}
        )
        
        print(f"\n✅ Found {len(restaurants)} real restaurants:")
        for i, r in enumerate(restaurants[:3], 1):
            print(f"\n{i}. {r.get('name', 'Unknown')}")
            if r.get('address'):
                print(f"   📍 {r['address']}")
            if r.get('description'):
                print(f"   ℹ️  {r['description'][:100]}...")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())