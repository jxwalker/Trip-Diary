from openai import OpenAI
import json
from typing import Dict, Any
from dotenv import load_dotenv
import os
import time

def extract_itinerary_with_gpt(text: str) -> Dict[str, Any]:
    """Use GPT to extract structured itinerary data from text."""
    
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    print("Preparing GPT request...")
    
    # Truncate text if it's too long (GPT-3.5 has a smaller context window)
    max_length = 12000
    if len(text) > max_length:
        print(f"Truncating text from {len(text)} to {max_length} characters...")
        text = text[:max_length]
    
    system_prompt = """You are a travel itinerary parser. Extract the following from the BA itinerary as JSON:
    - booking_reference
    - flights (BA numbers, times, locations)
    - hotels (names, dates, rooms)
    - passengers (WALKER family)
    - total_cost"""

    try:
        print("Sending request to GPT-3.5-turbo...")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using 3.5 instead of 4
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=1000,  # Limit response size
            timeout=10  # Shorter timeout
        )
        
        elapsed_time = time.time() - start_time
        print(f"Response received in {elapsed_time:.2f} seconds")
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"\nError: {type(e).__name__}: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response}")
        return None