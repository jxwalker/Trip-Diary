"""
Perplexity Search Service
Uses Perplexity API to get real-time, dynamic content for travel guides
NO MOCKS, NO PLACEHOLDERS - REAL DATA ONLY
"""

import os
import json
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
# Remove dependency on regex-based parsers - use LLM parsing instead

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(env_path)

class PerplexitySearchService:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        # Use the pro model for better results if available
        self.model = os.getenv("PERPLEXITY_MODEL", "sonar-pro")  # sonar-pro has better web search

        # Initialize OpenAI client for LLM parsing
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            import openai
            self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None

    async def _parse_with_llm(self, content: str, data_type: str) -> List[Dict]:
        """Parse Perplexity response using LLM instead of regex"""
        if not self.openai_client:
            print(f"[DEBUG] No OpenAI client available for parsing {data_type}")
            return []

        try:
            if data_type == "restaurants":
                template = '''[
  {
    "name": "Restaurant Name",
    "cuisine": "Cuisine Type",
    "price_range": "€25-40",
    "address": "Full Address",
    "phone": "+33 1 23 45 67 89",
    "website": "https://website.com",
    "description": "Brief description",
    "specialties": ["dish1", "dish2"],
    "reservations": "Required/Recommended/Not needed"
  }
]'''
            elif data_type == "attractions":
                template = '''[
  {
    "name": "Attraction Name",
    "type": "Museum/Monument/Park/etc",
    "address": "Full Address",
    "description": "Brief description",
    "hours": "Opening hours",
    "price": "Admission price",
    "website": "https://website.com",
    "time_needed": "2-3 hours",
    "best_time": "Morning/Afternoon/Evening"
  }
]'''
            elif data_type == "events":
                template = '''[
  {
    "name": "Event Name",
    "type": "Concert/Exhibition/Festival/etc",
    "date": "2025-01-15",
    "time": "20:00",
    "venue": "Venue Name",
    "address": "Full Address",
    "price": "Ticket price",
    "description": "Brief description",
    "website": "https://website.com"
  }
]'''
            else:
                return []

            prompt = f"""Extract {data_type} information from this travel content and return ONLY a JSON array in this exact format:

{template}

Content to parse:
{content}

Return ONLY the JSON array, no markdown, no explanations."""

            model = os.getenv("PRIMARY_MODEL", "xai/grok-4-fast-free")
            
            # Use OpenRouter endpoint for OpenRouter models
            if "/" in model and (model.startswith(("x-ai/", "meta-llama/", "anthropic/", "google/", "deepseek/")) or ":" in model):
                from openai import AsyncOpenAI
                openrouter_client = AsyncOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv("OPENROUTER_API_KEY", os.getenv("OPENAI_API_KEY"))
                )
                client = openrouter_client
            else:
                client = self.openai_client
            
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": f"You are a travel data parser. Extract {data_type} information and return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content

            # Parse the JSON
            import json
            if result_text.strip().startswith('['):
                parsed_data = json.loads(result_text)
            else:
                # If wrapped in object, extract the array
                parsed_obj = json.loads(result_text)
                if isinstance(parsed_obj, dict):
                    # Find the array in the object
                    for key, value in parsed_obj.items():
                        if isinstance(value, list):
                            parsed_data = value
                            break
                    else:
                        parsed_data = []
                else:
                    parsed_data = parsed_obj

            print(f"[DEBUG] LLM parsed {len(parsed_data)} {data_type}")
            return parsed_data

        except Exception as e:
            print(f"[DEBUG] Error parsing {data_type} with LLM: {e}")
            return []

    async def search_restaurants(
        self,
        destination: str,
        preferences: Dict,
        dates: Dict
    ) -> List[Dict]:
        """Search for real restaurants based on destination and preferences"""
        
        if not self.api_key:
            print(f"[WARNING] Perplexity API key not configured, returning empty list")
            return []
        
        # Build dynamic search query based on actual preferences
        cuisine_types = preferences.get("cuisineTypes", ["Local cuisine"])
        price_range = preferences.get("priceRange", "")
        dietary = preferences.get("dietaryRestrictions", [])
        group_type = preferences.get("groupType", "couple")
        
        # Convert price range to descriptive text
        price_descriptions = {
            "$": "budget-friendly casual restaurants under $20 per person",
            "$$": "mid-range restaurants $20-40 per person",
            "$$$": "upscale restaurants $40-80 per person",
            "$$$$": "luxury fine dining over $80 per person"
        }
        price_desc = price_descriptions.get(price_range, "mid-range restaurants")
        
        prompt = f"""Search the web for the BEST restaurants in {destination} operating in {dates.get('formatted', 'the current season')}.

CRITERIA:
- Cuisine types: {', '.join(cuisine_types) if cuisine_types else 'All cuisines'}
- Price range: {price_desc}
- Dietary needs: {', '.join(dietary) if dietary else 'No restrictions'}
- Group: {group_type}

Find 8 highly-rated restaurants that are CURRENTLY OPEN and provide this EXACT information for each:

**[Restaurant Name]**
Address: [Full street address with zip code]
Cuisine: [Specific cuisine type]
Price: [$ to $$$$]
Phone: [Phone number with area code]
Website: [Restaurant's official website]
Reservation link: [Direct OpenTable, Resy, or restaurant booking URL]
Hours: [Current operating hours]
Why recommended: [Why this matches their preferences]
Signature dishes: [3-4 specific must-try dishes with descriptions]
Review: [Recent review quote from Google/Yelp/TripAdvisor with rating]

IMPORTANT: 
- Include ONLY restaurants that are currently operating and accepting reservations
- Provide real phone numbers and working website URLs
- Include actual booking links from OpenTable, Resy, Tock, or restaurant websites
- Focus on highly-rated places (4+ stars) with recent positive reviews"""
        
        try:
            print(f"[DEBUG] Searching restaurants in {destination}...")
            response = await self._make_perplexity_request(prompt)
            print(f"[DEBUG] Got Perplexity response, parsing restaurants...")
            items = await self._parse_with_llm(response, "restaurants")
            print(f"[DEBUG] Parsed {len(items)} restaurants")
            
            # Filter out obvious placeholders and incomplete entries
            filtered = [
                r for r in items
                if r.get('name') and r.get('address') and 
                not str(r.get('name')).lower().startswith(('sample', 'placeholder', 'example'))
            ]
            print(f"[DEBUG] Filtered to {len(filtered)} valid restaurants")
            return filtered
        except Exception as e:
            print(f"[ERROR] Restaurant search failed: {e}")
            return []
    
    async def search_attractions(
        self,
        destination: str,
        preferences: Dict,
        dates: Dict
    ) -> List[Dict]:
        """Search for real attractions based on interests"""
        
        if not self.api_key:
            print(f"[WARNING] Perplexity API key not configured, returning empty list")
            return []
        
        interests = preferences.get("specialInterests", [])
        walking_tolerance = preferences.get("walkingTolerance", 3)
        adventure_level = preferences.get("adventureLevel", 3)
        
        # Convert interests to readable format
        interest_descriptions = {
            "museums": "museums and galleries",
            "architecture": "architectural landmarks",
            "nature": "parks and nature",
            "shopping": "shopping districts",
            "history": "historical sites",
            "food": "food markets and culinary experiences",
            "nightlife": "bars and nightlife",
            "photography": "photogenic locations",
            "local_culture": "local cultural experiences",
            "sports": "sports venues and activities",
            "theater": "theater and performing arts"
        }
        
        formatted_interests = [interest_descriptions.get(i, i) for i in interests]
        
        prompt = f"""Search the web for the TOP tourist attractions and things to do in {destination}.

Visitor Profile:
- Interests: {', '.join(formatted_interests) if formatted_interests else 'General sightseeing'}
- Dates: {dates.get('formatted', 'Current season')}
- Walking: {walking_tolerance}/5 scale (1=minimal, 5=loves walking)
- Adventure: {adventure_level}/5 scale (1=main tourist spots, 5=hidden gems)

Find 10 MUST-SEE attractions and provide this information for each:

**[Attraction Name]**
Type: [Museum/Park/Monument/Gallery/Market/etc]
Address: [Full street address with zip]
Hours: [Current operating hours, note any seasonal changes]
Price: [Adult admission price, note discounts available]
Duration: [Typical visit time like "2-3 hours"]
Why visit: [What makes this special and worth visiting]
Highlights: [Top 3-4 things to see/experience there]
Tips: [Insider advice - best time to visit, skip lines, photo spots]
Website: [Official website for tickets/info]
Nearby: [Other attractions within 10-minute walk]

Include a mix of:
- Famous must-see landmarks
- Museums and galleries
- Parks and outdoor spaces
- Markets and shopping areas
- Viewpoints and photo spots
- Unique local experiences

Focus on places that are CURRENTLY OPEN and accessible."""
        
        try:
            print(f"[DEBUG] Searching attractions in {destination}...")
            response = await self._make_perplexity_request(prompt)
            print(f"[DEBUG] Got Perplexity response for attractions, parsing...")
            items = await self._parse_with_llm(response, "attractions")
            print(f"[DEBUG] Parsed {len(items)} attractions")
            
            # More lenient filtering
            filtered = [a for a in items if a.get('name')]
            print(f"[DEBUG] Filtered to {len(filtered)} valid attractions")
            return filtered
        except Exception as e:
            print(f"[ERROR] Attraction search failed: {e}")
            return []
    
    async def search_events(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        preferences: Dict
    ) -> List[Dict]:
        """Search for real events happening during the travel dates"""
        
        if not self.api_key:
            print(f"[WARNING] Perplexity API key not configured, returning empty list")
            return []
        
        interests = preferences.get("specialInterests", [])
        
        prompt = f"""Search the web for ACTUAL events, concerts, shows, exhibitions, and activities happening in {destination} between {start_date} and {end_date}.

I need REAL events with ticket links, not generic suggestions. Search for:
1. Concerts and live music performances
2. Theater shows and performances  
3. Museum exhibitions and gallery openings
4. Festivals and special events
5. Sports games and matches
6. Comedy shows and entertainment
7. Food and wine events
8. Cultural celebrations

User interests: {', '.join(interests) if interests else 'General entertainment'}
Budget: {preferences.get('priceRange', '$$')}
Group: {preferences.get('groupType', 'couple')}

For EACH event found, provide this EXACT format:

**[Event Name]**
Date: [Specific date like "August 10, 2025" or date range]
Time: [Start time like "7:30 PM"]
Venue: [Venue name]
Address: [Full venue address]
Price: [Ticket price or "Free" - include price range if variable]
Booking link: [Direct Ticketmaster/StubHub/venue ticket URL]
Website: [Event or venue website]
Description: [What the event is about]
Why attend: [Why this matches their interests]

CRITICAL:
- Only include events ACTUALLY HAPPENING during {start_date} to {end_date}
- Include working ticket purchase links
- Search Ticketmaster, StubHub, venue websites, TimeOut, Eventbrite
- Provide 8-12 real events with variety
        
        Traveler interests: {', '.join(interests)}
        
        Include:
        1. Concerts and live music
        2. Theater and performing arts
        3. Museum exhibitions
        4. Festivals and markets
        5. Sports events
        6. Cultural events
        7. Special seasonal events
        
        For each event provide:
        1. Event name and type
        2. Exact dates and times
        3. Venue name and address
        4. Ticket prices and availability
        5. How to purchase tickets
        6. Why it's worth attending
        
        Format with event names in **bold**.
        IMPORTANT: Only include REAL events actually happening during these specific dates."""
        
        try:
            print(f"[DEBUG] Searching events in {destination} from {start_date} to {end_date}...")
            response = await self._make_perplexity_request(prompt)
            print(f"[DEBUG] Got Perplexity response for events, parsing...")
            items = await self._parse_with_llm(response, "events")
            print(f"[DEBUG] Parsed {len(items)} events")
            
            # More lenient filtering - just need a name and either date or description
            filtered = [e for e in items if e.get('name') and (e.get('date') or e.get('description'))]
            print(f"[DEBUG] Filtered to {len(filtered)} valid events")
            return filtered
        except Exception as e:
            print(f"[ERROR] Event search failed: {e}")
            return []
    
    async def search_daily_itinerary(
        self,
        destination: str,
        day_number: int,
        date: str,
        hotel_address: str,
        preferences: Dict,
        previous_days: List[str] = []
    ) -> Dict:
        """Generate a real, detailed itinerary for a specific day"""
        
        if not self.api_key:
            raise ValueError("Perplexity API key not configured")
        
        # Parse date for day of week
        day_date = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = day_date.strftime("%A")
        
        previous_context = ""
        if previous_days:
            previous_context = f"Previous days covered: {', '.join(previous_days)}. Avoid repeating these."
        
        prompt = f"""Create a detailed, realistic itinerary for Day {day_number} ({day_of_week}, {date}) in {destination}.
        
        Hotel location: {hotel_address}
        Preferences: {json.dumps(preferences, indent=2)}
        {previous_context}
        
        Create a full day schedule with:
        
        MORNING (8:00 AM - 12:00 PM):
        - Breakfast recommendation (specific place near hotel)
        - Morning activity (with exact location and timing)
        
        LUNCH (12:00 PM - 2:00 PM):
        - Specific restaurant recommendation
        - Why it's good for lunch
        
        AFTERNOON (2:00 PM - 6:00 PM):
        - Main afternoon activity
        - Alternative if weather is bad
        
        EVENING (6:00 PM - 10:00 PM):
        - Dinner restaurant (with reservation notes)
        - Evening activity or entertainment
        
        For each item include:
        - Specific venue/location name
        - Address
        - Walking/transit time from previous location
        - Cost estimate
        - Reservation/ticket requirements
        - Why it fits their preferences
        
        IMPORTANT: Everything must be real, currently operating venues. 
        Consider {day_of_week} specifically (some places may be closed).
        Account for realistic travel times between locations."""
        
        response = await self._make_perplexity_request(prompt)
        # Simple parsing for daily itinerary
        itinerary = {
            'day': day_number,
            'date': date,
            'day_of_week': day_of_week,
            'morning': [],
            'afternoon': [],
            'evening': [],
            'raw_content': response
        }
        
        # Extract key activities from response
        lines = response.split('\n')
        current_section = None
        for line in lines:
            line = line.strip()
            if 'morning' in line.lower():
                current_section = 'morning'
            elif 'afternoon' in line.lower():
                current_section = 'afternoon'
            elif 'evening' in line.lower():
                current_section = 'evening'
            elif current_section and line and not line.lower().startswith(('morning', 'afternoon', 'evening')):
                itinerary[current_section].append(line.strip('- '))
        
        return itinerary
    
    async def search_local_insights(
        self,
        destination: str,
        dates: Dict
    ) -> Dict:
        """Get real, current local insights and practical information"""
        
        if not self.api_key:
            raise ValueError("Perplexity API key not configured")
        
        prompt = f"""Provide current, practical local insights for visiting {destination} during {dates.get('formatted', 'upcoming')}:
        
        1. WEATHER & PACKING:
        - Current weather forecast for these dates
        - What to pack specifically
        - Any weather-related closures or considerations
        
        2. TRANSPORTATION:
        - Best apps for local transport
        - Current public transport prices
        - Areas to avoid certain times
        - Airport transfer options and costs
        
        3. MONEY & COSTS:
        - ATM locations and fees
        - Tipping culture and amounts
        - Average meal costs
        - Credit card acceptance
        
        4. CULTURAL TIPS:
        - Local customs to be aware of
        - Common tourist mistakes to avoid
        - Useful local phrases
        - Best neighborhoods to explore
        
        5. CURRENT UPDATES:
        - Any construction or closures
        - Safety considerations
        - Local events affecting travel
        - Seasonal considerations
        
        IMPORTANT: Provide only current, accurate information. 
        Include specific details like actual app names, real prices, and current conditions."""
        
        response = await self._make_perplexity_request(prompt)
        # Split insights into sections to improve fidelity
        sections = {
            'weather': [],
            'transportation': [],
            'money': [],
            'cultural': [],
            'updates': [],
            'tips': []
        }
        for block in response.split('\n\n'):
            low = block.lower()
            if any(k in low for k in ['weather', 'pack']):
                sections['weather'].append(block.strip())
            elif any(k in low for k in ['transport', 'metro', 'bus', 'uber', 'taxi']):
                sections['transportation'].append(block.strip())
            elif any(k in low for k in ['money', 'cost', 'tipping', 'price']):
                sections['money'].append(block.strip())
            elif any(k in low for k in ['custom', 'cultural', 'phrase']):
                sections['cultural'].append(block.strip())
            elif any(k in low for k in ['closure', 'safety', 'construction', 'update']):
                sections['updates'].append(block.strip())
            else:
                sections['tips'].append(block.strip())
        return sections
    
    async def _make_perplexity_request(self, prompt: str) -> str:
        """Make a request to Perplexity API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are a travel expert with real-time web access. Your job is to search the internet and provide ACCURATE, CURRENT information about restaurants, attractions, and events.

RULES:
1. Use real-time web search to find actual businesses and events
2. Include real addresses, phone numbers, and websites
3. Provide working booking/ticket links from OpenTable, Resy, Ticketmaster, etc
4. Include current prices and operating hours
5. Never make up information - only report what you find online
6. Format responses exactly as requested with ** for names"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Lower temperature for more factual responses
            "max_tokens": 4000,  # More tokens for comprehensive responses
            # Optional: Add domain filters if needed
            # "search_domain_filter": ["opentable.com", "resy.com", "tripadvisor.com", "yelp.com", "ticketmaster.com", "timeout.com", "viator.com"],
            # "search_recency_filter": "month"  # Focus on recent information
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Perplexity API error: {response.status} - {error_text}")
