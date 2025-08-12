#!/usr/bin/env python3
import asyncio
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

root_dir = Path(__file__).parent.parent.parent.parent
from dotenv import load_dotenv
load_dotenv(root_dir / '.env')

from services.perplexity_search_service import PerplexitySearchService

async def test():
    service = PerplexitySearchService()
    print(f"API Key: {service.api_key[:15] if service.api_key else 'NONE'}")
    
    print("\nSearching NYC restaurants...")
    restaurants = await service.search_restaurants(
        destination="New York", 
        preferences={"cuisineTypes": ["Italian"], "priceRange": "$$"},
        dates={"formatted": "Aug 9-14, 2025"}
    )
    
    print(f"Found: {len(restaurants)} restaurants")
    for r in restaurants[:2]:
        print(f"- {r.get('name')}: {r.get('address', 'no addr')}")

asyncio.run(test())