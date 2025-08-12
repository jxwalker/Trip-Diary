#!/usr/bin/env python3
"""
Test LLM parser with real Perplexity output
"""
import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm_parser import LLMParser

async def test_llm_parser():
    """Test parsing real Perplexity output with LLM"""
    
    print("🔍 Testing LLM Parser\n")
    print("=" * 50)
    
    # Load the test output from Perplexity
    with open('test/test_guide_output.json', 'r') as f:
        data = json.load(f)
        content = data.get('raw_content', '')
    
    if not content:
        print("❌ No raw content found in test file")
        return
    
    print(f"📄 Loaded content: {len(content)} characters")
    
    # Initialize parser
    parser = LLMParser()
    
    # Parse the content
    print("\n🤖 Parsing with LLM...")
    result = await parser.parse_guide(content)
    
    # Save parsed result
    with open('test/test_llm_parsed.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("✅ Parsed content saved to test_llm_parsed.json")
    
    # Analyze results
    print("\n📊 Analysis:")
    print(f"  - Summary: {'✅' if result.get('summary') else '❌'}")
    print(f"  - Weather: {'✅' if result.get('weather') else '❌'}")
    print(f"  - Hotels: {'✅' if result.get('hotels') else '❌'}")
    print(f"  - Restaurants: {len(result.get('restaurants', []))} found")
    print(f"  - Daily Itinerary: {len(result.get('daily_itinerary', []))} days")
    print(f"  - Attractions: {len(result.get('attractions', []))} found")
    print(f"  - Events: {len(result.get('events', []))} found")
    print(f"  - Neighborhoods: {len(result.get('neighborhoods', []))} found")
    
    # Show sample restaurants
    if result.get('restaurants'):
        print("\n🍽️ Sample Restaurants:")
        for r in result['restaurants'][:3]:
            print(f"  - {r.get('name', 'Unknown')}: {r.get('cuisine', 'N/A')} ({r.get('price_range', 'N/A')})")
    
    # Show sample itinerary
    if result.get('daily_itinerary'):
        print("\n📅 Sample Itinerary:")
        for day in result['daily_itinerary'][:2]:
            print(f"  Day {day.get('day', '?')}: {day.get('date', 'N/A')}")
            if day.get('morning'):
                print(f"    Morning: {day['morning'].get('activity', 'N/A')}")
            if day.get('lunch'):
                print(f"    Lunch: {day['lunch'].get('restaurant', 'N/A')}")
    
    print("\n" + "=" * 50)
    print("✅ LLM Parser test complete!")

if __name__ == "__main__":
    asyncio.run(test_llm_parser())