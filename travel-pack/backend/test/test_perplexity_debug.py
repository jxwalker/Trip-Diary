#!/usr/bin/env python3
"""Debug Perplexity API response"""
import asyncio
import os
import sys
import aiohttp
from dotenv import load_dotenv
from pathlib import Path

# Load environment
# Load environment from project root .env
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

async def test_raw():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    print(f"Using API key: {api_key[:15]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a travel expert. Provide specific, real information."
            },
            {
                "role": "user",
                "content": """List the 3 best Italian restaurants in Manhattan, NYC. For each provide:
                1. Restaurant name
                2. Full address
                3. Price range
                4. Why it's recommended
                
                Format each as:
                Restaurant Name
                Address: [full address]
                Price: [price range]
                Description: [why recommended]"""
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.perplexity.ai/chat/completions",
            json=payload,
            headers=headers
        ) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                print("\n=== RAW RESPONSE ===")
                print(content)
                print("\n=== END RESPONSE ===")
                
                # Check for citations
                if "citations" in data:
                    print(f"\nCitations: {len(data['citations'])} sources")
            else:
                error = await response.text()
                print(f"Error: {error}")

if __name__ == "__main__":
    asyncio.run(test_raw())