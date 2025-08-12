#!/usr/bin/env python3
"""Debug why service returns empty results"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / '.env'
from dotenv import load_dotenv
load_dotenv(env_path)

from services.perplexity_search_service import PerplexitySearchService

async def test():
    service = PerplexitySearchService()
    
    print(f"API Key configured: {bool(service.api_key)}")
    print(f"Key prefix: {service.api_key[:15] if service.api_key else 'None'}")
    
    try:
        # Make a simple request
        prompt = "List 3 Italian restaurants in NYC with addresses"
        print(f"\nSending prompt: {prompt}")
        
        raw_response = await service._make_perplexity_request(prompt)
        
        print("\n=== RAW RESPONSE ===")
        print(raw_response[:500])
        print("...")
        
        # Try parsing
        parsed = service.parser.parse_restaurants(raw_response)
        print(f"\n=== PARSED: {len(parsed)} restaurants ===")
        
        for r in parsed:
            print(f"- {r.get('name')}: {r.get('address', 'no address')}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())