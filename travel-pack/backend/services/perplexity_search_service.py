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
from .enhanced_parser import parse_restaurants_enhanced, parse_attractions_enhanced, parse_events_structured

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(env_path)

class PerplexitySearchService:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar"  # Use sonar for web search capabilities
        # Using simple parser for better reliability
        
    async def search_restaurants(
        self,
        destination: str,
        preferences: Dict,
        dates: Dict
    ) -> List[Dict]:
        """Search for real restaurants based on destination and preferences"""
        
        if not self.api_key:
            raise ValueError("Perplexity API key not configured")
        
        # Build dynamic search query based on actual preferences
        cuisine_types = preferences.get("cuisineTypes", ["Local cuisine"])
        price_range = preferences.get("priceRange", "$$")
        dietary = preferences.get("dietaryRestrictions", [])
        group_type = preferences.get("groupType", "couple")
        
        # Convert price range to descriptive text
        price_descriptions = {
            "$": "budget-friendly",
            "$$": "mid-range",
            "$$$": "upscale",
            "$$$$": "luxury fine dining"
        }
        price_desc = price_descriptions.get(price_range, "mid-range")
        
        prompt = f"""Find the best current restaurants in {destination} that match these criteria:
        - Cuisine preferences: {', '.join(cuisine_types)}
        - Price range: {price_desc}
        - Dietary restrictions: {', '.join(dietary) if dietary else 'None'}
        - Group type: {group_type}
        - Visiting dates: {dates.get('formatted', 'upcoming')}
        
        For each restaurant provide IN THIS EXACT FORMAT:
        **Restaurant Name**
        Address: [exact street address]
        Cuisine: [type of cuisine]
        Price: [price range $ to $$$$]
        Distance from hotel: [distance if hotel address provided]
        Phone: [phone number]
        Website: [restaurant website URL]
        Reservation link: [OpenTable, Resy, or restaurant booking URL]
        Hours: [operating hours]
        Why recommended: [personalized reason based on preferences]
        Signature dishes: [3-4 must-try dishes]
        Review: [recent review quote or rating]
        
        IMPORTANT: Only provide real, currently operating restaurants with actual contact info and booking links.
        Provide exactly 5-8 restaurants matching their preferences."""
        
        response = await self._make_perplexity_request(prompt)
        return parse_restaurants_enhanced(response)
    
    async def search_attractions(
        self,
        destination: str,
        preferences: Dict,
        dates: Dict
    ) -> List[Dict]:
        """Search for real attractions based on interests"""
        
        if not self.api_key:
            raise ValueError("Perplexity API key not configured")
        
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
        
        prompt = f"""Find the best attractions and activities in {destination} for someone interested in:
        {', '.join(formatted_interests)}
        
        Travel dates: {dates.get('formatted', 'upcoming')}
        Walking tolerance: {walking_tolerance}/5 (1=minimal, 5=loves walking)
        Adventure level: {adventure_level}/5 (1=tourist spots only, 5=off the beaten path)
        
        For each attraction provide IN THIS EXACT FORMAT:
        **Attraction Name** (type: Museum/Gallery/Park/etc)
        Address: [exact street address]
        Hours: [current operating hours]
        Price: [admission prices, including any discounts]
        Duration: [recommended visit time]
        Distance from hotel: [if hotel address provided]
        Why visit: [personalized reason based on their interests]
        Highlights: [main things to see/do]
        Tips: [insider tips, best time to visit, ticket purchasing advice]
        Special: [any exhibitions/events during their dates]
        Nearby: [other attractions within walking distance]
        
        IMPORTANT: Provide only real, currently operating attractions with accurate current information.
        Provide exactly 6-10 attractions matching their interests."""
        
        response = await self._make_perplexity_request(prompt)
        return parse_attractions_enhanced(response)
    
    async def search_events(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        preferences: Dict
    ) -> List[Dict]:
        """Search for real events happening during the travel dates"""
        
        if not self.api_key:
            raise ValueError("Perplexity API key not configured")
        
        interests = preferences.get("specialInterests", [])
        
        prompt = f"""Find actual events, exhibitions, shows, and festivals happening in {destination} 
        between {start_date} and {end_date} that match these specific interests: {', '.join(interests)}.
        
        IMPORTANT: Only include events that align with these preferences:
        - User interests: {', '.join(interests)}
        - Price range: {preferences.get('priceRange', '$$')}
        - Group type: {preferences.get('groupType', 'couple')}
        
        For each event provide IN THIS EXACT FORMAT:
        **Event Name**
        Date: [exact date, e.g., August 10, 2025]
        Time: [exact time, e.g., 7:30 PM]
        Venue: [venue name]
        Address: [exact venue address]
        Price: [ticket price or "Free"]
        Booking link: [direct link to buy tickets]
        Website: [event or venue website]
        Description: [what the event is about]
        Why attend: [why it matches their interests]
        
        Only include events that match their interests. Provide 5-10 relevant events.
        
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
        
        response = await self._make_perplexity_request(prompt)
        return parse_events_structured(response)
    
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
        # Return raw insights for now
        return {
            'weather': [response] if 'weather' in response.lower() else [],
            'transportation': [response] if 'transport' in response.lower() else [],
            'tips': [response]
        }
    
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
                    "content": """You are an expert travel planner with real-time web access. 
                    Always provide current, accurate information from actual sources. 
                    Never use placeholders or generic recommendations. 
                    Include specific names, addresses, prices, and current details.
                    If something is closed or unavailable on the travel dates, mention it."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Perplexity API error: {response.status} - {error_text}")