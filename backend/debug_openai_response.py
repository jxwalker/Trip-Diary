#!/usr/bin/env python3
"""
Debug script to test OpenAI response structure directly
"""
import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def debug_openai_response():
    """Debug what OpenAI is actually returning"""
    print("Debugging OpenAI Response Structure...")
    print("=" * 60)
    
    try:
        from services.unified_guide_service import UnifiedGuideService, GuideGenerationContext, PersonaType
        
        service = UnifiedGuideService()
        
        context = GuideGenerationContext(
            destination="Paris, France",
            start_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            end_date=(datetime.now() + timedelta(days=33)).strftime("%Y-%m-%d"),
            duration_days=4,
            persona=PersonaType.CULTURAL_ENTHUSIAST,
            preferences={"interests": ["culture", "food"], "budget": "moderate"},
            hotel_info={"name": "Test Hotel", "address": "Paris, France"}
        )
        
        print(f"Testing OpenAI generation for: {context.destination}")
        print(f"Dates: {context.start_date} to {context.end_date}")
        
        openai_response = await service._generate_with_openai(context)
        
        print("\n=== OpenAI Response Structure ===")
        print(f"Response type: {type(openai_response)}")
        print(f"Response keys: {list(openai_response.keys()) if isinstance(openai_response, dict) else 'Not a dict'}")
        
        if isinstance(openai_response, dict):
            if openai_response.get("error"):
                print(f"❌ OpenAI Error: {openai_response['error']}")
                return False
            
            required_fields = ["summary", "destination_insights", "daily_itinerary", "restaurants", "attractions"]
            
            for field in required_fields:
                if field in openai_response:
                    content = openai_response[field]
                    if isinstance(content, str):
                        print(f"✓ {field}: {len(content)} characters")
                        if len(content) > 0:
                            print(f"  Preview: {content[:100]}...")
                    elif isinstance(content, list):
                        print(f"✓ {field}: {len(content)} items")
                        if len(content) > 0:
                            print(f"  First item: {content[0]}")
                    else:
                        print(f"✓ {field}: {type(content)}")
                else:
                    print(f"❌ Missing field: {field}")
            
            print("\n=== Testing Data Fetching Pipeline ===")
            combined_data = await service._fetch_all_data_concurrently(context)
            
            print(f"Combined data type: {type(combined_data)}")
            print(f"Combined data keys: {list(combined_data.keys()) if isinstance(combined_data, dict) else 'Not a dict'}")
            
            if isinstance(combined_data, dict):
                for field in required_fields:
                    if field in combined_data:
                        content = combined_data[field]
                        if isinstance(content, str):
                            print(f"✓ Combined {field}: {len(content)} characters")
                        elif isinstance(content, list):
                            print(f"✓ Combined {field}: {len(content)} items")
                        else:
                            print(f"✓ Combined {field}: {type(content)}")
                    else:
                        print(f"❌ Missing in combined: {field}")
            
            return True
        else:
            print(f"❌ OpenAI response is not a dict: {openai_response}")
            return False
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_openai_response())
    sys.exit(0 if success else 1)
