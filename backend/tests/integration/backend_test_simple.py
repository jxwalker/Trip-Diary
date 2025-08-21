#!/usr/bin/env python3
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment from project root .env
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

api_key = os.getenv("PERPLEXITY_API_KEY")
print(f"Testing with key: {api_key[:15]}...")

response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are a travel assistant."},
            {"role": "user", "content": "List 2 famous NYC restaurants with addresses."}
        ],
        "max_tokens": 200
    }
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print("\nResponse:")
    print(content)
else:
    print(f"Error: {response.text}")