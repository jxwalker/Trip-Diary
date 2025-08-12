#!/usr/bin/env python3
"""
Test script for Perplexity API
Tests the correct model names and API functionality
"""
import asyncio
import aiohttp
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
# Load environment from project root .env
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

async def test_perplexity_api():
    """Test Perplexity API with correct model names"""
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("❌ No PERPLEXITY_API_KEY found in environment")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    # Test different model names - from official docs
    models_to_test = [
        "sonar",  # Lightweight search model
        "sonar-reasoning",  # Fast reasoning with search
        "sonar-deep-research",  # Comprehensive research
    ]
    
    for model in models_to_test:
        print(f"\n📝 Testing model: {model}")
        success = await test_single_model(api_key, model)
        if success:
            print(f"✅ Model {model} works!")
            return True
        else:
            print(f"❌ Model {model} failed")
    
    return False

async def test_single_model(api_key: str, model: str) -> bool:
    """Test a single Perplexity model"""
    
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://api.perplexity.ai/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful travel assistant."
                    },
                    {
                        "role": "user",
                        "content": "What are the top 3 restaurants in Paris right now? Please be specific with current information."
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            print(f"  Sending request to Perplexity API...")
            
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"  Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Print response
                    if "choices" in data and data["choices"]:
                        content = data["choices"][0]["message"]["content"]
                        print(f"  Response preview: {content[:200]}...")
                        
                        # Check if citations are included
                        if "citations" in data:
                            print(f"  Citations found: {len(data['citations'])}")
                        
                        return True
                    else:
                        print(f"  Unexpected response format: {json.dumps(data, indent=2)[:500]}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"  Error response: {error_text[:500]}")
                    return False
                    
    except Exception as e:
        print(f"  Exception: {e}")
        return False

async def test_travel_guide_generation():
    """Test generating a travel guide with Perplexity"""
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("❌ No PERPLEXITY_API_KEY found")
        return
    
    print("\n🌍 Testing travel guide generation...")
    
    prompt = """Create a personalized 3-day travel guide for New York City for someone who loves:
    - Art galleries and museums
    - Fine dining
    - Theater and shows
    
    For dates: December 20-22, 2024
    
    Include:
    1. Daily itinerary with specific timings
    2. Restaurant recommendations with current information
    3. Current exhibitions and shows
    4. Weather forecast for these dates
    5. Local tips and transportation
    
    Use current, real-time information from the web."""
    
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
                        "content": "You are an expert travel guide with access to current web information. Create detailed, personalized travel guides with real-time data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            print("  Sending travel guide request...")
            
            async with session.post(url, json=payload, headers=headers) as response:
                print(f"  Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if "choices" in data and data["choices"]:
                        content = data["choices"][0]["message"]["content"]
                        
                        # Save to file for inspection
                        with open("test_travel_guide_output.md", "w") as f:
                            f.write("# Perplexity Travel Guide Test Output\n\n")
                            f.write(content)
                        
                        print(f"  ✅ Travel guide generated! Saved to test_travel_guide_output.md")
                        print(f"  Preview:\n{content[:500]}...")
                        
                        # Check for key elements
                        elements = {
                            "restaurants": "restaurant" in content.lower(),
                            "museums": "museum" in content.lower() or "gallery" in content.lower(),
                            "weather": "weather" in content.lower() or "temperature" in content.lower(),
                            "schedule": "day 1" in content.lower() or "morning" in content.lower()
                        }
                        
                        print(f"\n  Content analysis:")
                        for key, found in elements.items():
                            status = "✅" if found else "❌"
                            print(f"    {status} {key.capitalize()}")
                        
                    else:
                        print(f"  ❌ Unexpected response format")
                else:
                    error_text = await response.text()
                    print(f"  ❌ Error: {error_text[:500]}")
                    
    except Exception as e:
        print(f"  ❌ Exception: {e}")

async def main():
    """Run all tests"""
    print("🧪 Testing Perplexity API Integration\n")
    print("=" * 50)
    
    # Test basic API connectivity
    api_works = await test_perplexity_api()
    
    if api_works:
        # Test travel guide generation
        await test_travel_guide_generation()
    else:
        print("\n❌ Basic API test failed. Check your API key and model names.")
    
    print("\n" + "=" * 50)
    print("🏁 Tests complete!")

if __name__ == "__main__":
    asyncio.run(main())