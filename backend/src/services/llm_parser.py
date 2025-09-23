"""
LLM-based parser for travel guide content
Uses AI to extract structured data from unstructured text
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import aiohttp
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class LLMParser:
    """Use LLMs to parse travel guide content into structured data"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
    async def parse_guide(self, content: str) -> Dict:
        """Parse travel guide content using LLM"""
        
        # Create extraction prompt
        extraction_prompt = self._create_extraction_prompt(content)
        
        # Try OpenAI first, then Anthropic
        if self.openai_api_key:
            result = await self._parse_with_openai(extraction_prompt)
        elif self.anthropic_api_key:
            result = await self._parse_with_anthropic(extraction_prompt)
        else:
            # Fallback to basic extraction
            result = self._basic_extraction(content)
        
        # Ensure required keys exist to improve data fidelity for frontend
        result.setdefault("summary", "")
        result.setdefault("restaurants", [])
        result.setdefault("attractions", [])
        result.setdefault("events", [])
        result.setdefault("daily_itinerary", [])
        result.setdefault("neighborhoods", [])
        result.setdefault("practical_info", {})
        result.setdefault("citations", [])
        # Backward compatibility for keys
        if "practical_tips" in result and not result.get("practical_info"):
            result["practical_info"] = result.pop("practical_tips")
        return result
    
    def _create_extraction_prompt(self, content: str) -> str:
        """Create prompt for structured data extraction"""
        
        prompt = f"""Extract structured information from this travel guide and \
return it as JSON.
        
CONTENT TO PARSE:
{content}

REQUIRED JSON STRUCTURE:
{{
    "summary": "Executive summary of the travel guide",
    "weather": {{
        "temperature_range": "e.g., 40-50°F",
        "conditions": "e.g., Partly cloudy with chance of rain",
        "forecast_details": ["Day 1: ...", "Day 2: ...", "Day 3: ..."],
        "packing_tips": ["Item 1", "Item 2", ...]
    }},
    "hotels": {{
        "name": "Hotel name",
        "address": "Full address",
        "description": "Brief description",
        "amenities": ["Amenity 1", "Amenity 2"],
        "nearby_attractions": ["Attraction 1", "Attraction 2"]
    }},
    "restaurants": [
        {{
            "name": "Restaurant name",
            "cuisine": "Type of cuisine",
            "price_range": "$$ or $$$ or $$$$",
            "ambiance": "Description of atmosphere",
            "must_try_dishes": ["Dish 1", "Dish 2"],
            "reservations": "Required/Recommended/Not needed",
            "website": "https://...",
            "reservation_link": "https://...",
            "address": "Full address",
            "phone": "Phone number",
            "distance_from_hotel": "e.g., 0.5 miles"
        }}
    ],
    "daily_itinerary": [
        {{
            "day": 1,
            "date": "December 20, 2024",
            "morning": {{
                "time": "9:00 AM - 12:00 PM",
                "activity": "Activity name",
                "location": "Location",
                "description": "What to do",
                "tips": "Insider tips"
            }},
            "lunch": {{
                "time": "12:30 PM - 2:00 PM",
                "restaurant": "Restaurant name",
                "location": "Address"
            }},
            "afternoon": {{
                "time": "2:30 PM - 5:00 PM",
                "activity": "Activity name",
                "location": "Location",
                "description": "What to do"
            }},
            "dinner": {{
                "time": "7:00 PM - 9:00 PM",
                "restaurant": "Restaurant name",
                "location": "Address"
            }},
            "evening": {{
                "time": "9:30 PM - 11:00 PM",
                "activity": "Activity name",
                "location": "Location"
            }}
        }}
    ],
    "attractions": [
        {{
            "name": "Attraction name",
            "type": "Museum/Park/Gallery/Monument",
            "description": "Brief description",
            "address": "Full address",
            "website": "https://...",
            "hours": "Operating hours",
            "tickets": "Ticket info",
            "tips": "Insider tips"
        }}
    ],
    "events": [
        {{
            "name": "Event name",
            "type": "Concert/Show/Exhibition",
            "date": "Date",
            "time": "Time",
            "venue": "Venue name",
            "tickets": "Ticket info",
            "booking_link": "https://...",
            "description": "Brief description"
        }}
    ],
    "neighborhoods": [
        {{
            "name": "Neighborhood name",
            "character": "Brief character description",
            "highlights": ["Highlight 1", "Highlight 2"],
            "distance_from_hotel": "e.g., 2 miles"
        }}
    ],
    "transportation": {{
        "getting_around": ["Tip 1", "Tip 2"],
        "from_airport": "How to get from airport",
        "public_transit": "Public transit info",
        "taxi_uber": "Taxi/Uber availability and cost"
    }},
    "practical_tips": {{
        "tipping": "Tipping guidelines",
        "currency": "Currency info",
        "language": "Language tips",
        "safety": ["Safety tip 1", "Safety tip 2"],
        "emergency": "Emergency contacts"
    }},
    "hidden_gems": [
        {{
            "name": "Place name",
            "description": "Why it's special",
            "location": "Where to find it",
            "best_time": "Best time to visit"
        }}
    ]
}}

IMPORTANT:
- Extract ALL restaurants mentioned (especially from tables)
- Include ALL days of the itinerary
- Capture specific dates, times, and addresses when available
- If information is not available, use null or empty array []
- Ensure valid JSON format
- Extract actual data, don't use placeholder text

Return ONLY the JSON object, no other text."""
        
        return prompt
    
    async def _parse_with_openai(self, prompt: str) -> Dict:
        """Use OpenAI to parse content"""
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": ("You are a data extraction expert. "
                                       "Extract structured data from travel "
                                       "guides and return valid JSON.")
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1,  # Low temperature for consistent
                    "response_format": {"type": "json_object"}
                }
                
                url = "https://api.openai.com/v1/chat/completions"
                
                async with session.post(
                    url, json=payload, headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result_text = data["choices"][0]["message"]["content"]
                        return json.loads(result_text)
                    else:
                        print(f"OpenAI API error: {response.status}")
                        return self._basic_extraction("")
                        
        except Exception as e:
            print(f"Error parsing with OpenAI: {e}")
            return self._basic_extraction("")
    
    async def _parse_with_anthropic(self, prompt: str) -> Dict:
        """Use Anthropic Claude to parse content"""
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 4000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1
                }
                
                url = "https://api.anthropic.com/v1/messages"
                
                async with session.post(
                    url, json=payload, headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result_text = data["content"][0]["text"]
                        # Claude might return text with JSON, extract it
                        json_start = result_text.find('{')
                        json_end = result_text.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = result_text[json_start:json_end]
                            return json.loads(json_str)
                    else:
                        print(f"Anthropic API error: {response.status}")
                        return self._basic_extraction("")
                        
        except Exception as e:
            print(f"Error parsing with Anthropic: {e}")
            return self._basic_extraction("")
    
    def _basic_extraction(self, content: str) -> Dict:
        """Basic extraction without LLM"""
        
        return {
            "summary": "",
            "weather": {},
            "hotels": {},
            "restaurants": [],
            "daily_itinerary": [],
            "attractions": [],
            "events": [],
            "neighborhoods": [],
            "transportation": {},
            "practical_tips": {},
            "hidden_gems": []
        }
