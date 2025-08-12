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
import os
from pathlib import Path
from .perplexity_response_parser import PerplexityResponseParser

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(env_path)

class PerplexitySearchService:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar"  # Use sonar for web search capabilities
        self.parser = PerplexityResponseParser()
        
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
        
        For each restaurant provide:
        1. Restaurant name
        2. Exact address
        3. Cuisine type
        4. Price range
        5. Why it's recommended for this traveler
        6. Signature dishes
        7. Current hours of operation
        8. Reservation requirements
        9. Recent reviews or ratings
        
        IMPORTANT: Only provide real, currently operating restaurants with actual addresses and current information. Include a mix of popular favorites and hidden gems."""
        
        response = await self._make_perplexity_request(prompt)
        return self.parser.parse_restaurants(response)
    
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
            "sports": "sports venues and activities"
        }
        
        formatted_interests = [interest_descriptions.get(i, i) for i in interests]
        
        prompt = f"""Find the best attractions and activities in {destination} for someone interested in:
        {', '.join(formatted_interests)}
        
        Travel dates: {dates.get('formatted', 'upcoming')}
        Walking tolerance: {walking_tolerance}/5 (1=minimal, 5=loves walking)
        Adventure level: {adventure_level}/5 (1=tourist spots only, 5=off the beaten path)
        
        For each attraction provide:
        1. Name and type of attraction
        2. Exact address
        3. Current admission prices
        4. Current opening hours
        5. Time needed to visit
        6. Why it matches their interests
        7. Any special exhibitions or events during their visit dates
        8. Accessibility information
        9. Best time of day to visit
        10. Nearby attractions or combo tickets
        
        IMPORTANT: Provide only real, currently operating attractions with accurate current information. Include both must-see spots and lesser-known gems that match their interests."""
        
        response = await self._make_perplexity_request(prompt)
        return self.parser.parse_attractions(response)
    
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
        between {start_date} and {end_date}.
        
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
        
        IMPORTANT: Only include REAL events actually happening during these specific dates. 
        Check current event calendars and provide accurate information."""
        
        response = await self._make_perplexity_request(prompt)
        return self.parser.parse_events(response)
    
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
        parsed = self.parser.parse_daily_itinerary(response)
        # Add metadata
        parsed['day'] = day_number
        parsed['date'] = date
        parsed['day_of_week'] = day_of_week
        return parsed
    
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
        return self.parser.parse_local_insights(response)
    
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
    
    # Parser methods have been moved to PerplexityResponseParser class
    # Old broken parsing methods removed - see perplexity_response_parser.py
        current_restaurant = {}
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                if current_restaurant.get('name'):
                    restaurants.append(current_restaurant)
                    current_restaurant = {}
                continue
            
            # Look for restaurant names in bold (common in responses)
            if '**' in line and not line.startswith('Address:') and not line.startswith('Price:'):
                if current_restaurant.get('name'):
                    restaurants.append(current_restaurant)
                # Extract name from bold text
                import re
                bold_match = re.search(r'\*\*(.+?)\*\*', line)
                if bold_match:
                    name = bold_match.group(1).strip()
                    current_restaurant = {'name': name, 'details': []}
                    # Check if there's text after the name on the same line
                    remaining = line[bold_match.end():].strip()
                    if remaining:
                        current_restaurant['details'].append(remaining)
            elif current_restaurant:
                # Parse restaurant details
                if 'Address:' in line:
                    current_restaurant['address'] = line.split('Address:', 1)[1].strip()
                elif 'Price:' in line:
                    current_restaurant['price'] = line.split('Price:', 1)[1].strip()
                elif 'Description:' in line:
                    current_restaurant['description'] = line.split('Description:', 1)[1].strip()
                elif 'Cuisine:' in line:
                    current_restaurant['cuisine'] = line.split('Cuisine:', 1)[1].strip()
                elif 'Hours:' in line or 'Open:' in line:
                    current_restaurant['hours'] = line.split(':', 1)[1].strip()
                elif line.startswith('-'):
                    current_restaurant['details'].append(line[1:].strip())
                elif not line.startswith('#') and not line.startswith('*'):
                    # Add as description if not already set
                    if 'description' not in current_restaurant:
                        current_restaurant['description'] = line
                    else:
                        current_restaurant['details'].append(line)
        
        if current_restaurant.get('name'):
            restaurants.append(current_restaurant)
        
        return restaurants
    
    def _parse_attraction_response(self, response: str) -> List[Dict]:
        """Parse attraction search response"""
        attractions = []
        current_attraction = {}
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                if current_attraction.get('name'):
                    attractions.append(current_attraction)
                    current_attraction = {}
                continue
            
            # Look for attraction markers
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                if current_attraction.get('name'):
                    attractions.append(current_attraction)
                name_part = line.split('.', 1)[1].strip()
                if '**' in name_part:
                    name = name_part.replace('**', '').strip()
                else:
                    name = name_part.split('-')[0].strip() if '-' in name_part else name_part
                current_attraction = {'name': name, 'details': []}
            elif current_attraction:
                if 'Address:' in line or 'Location:' in line:
                    current_attraction['address'] = line.split(':', 1)[1].strip()
                elif 'Price:' in line or 'Admission:' in line or 'Cost:' in line:
                    current_attraction['price'] = line.split(':', 1)[1].strip()
                elif 'Hours:' in line or 'Open:' in line:
                    current_attraction['hours'] = line.split(':', 1)[1].strip()
                elif 'Duration:' in line or 'Time needed:' in line:
                    current_attraction['duration'] = line.split(':', 1)[1].strip()
                elif line.startswith('-'):
                    current_attraction['details'].append(line[1:].strip())
                elif not line.startswith('#'):
                    if 'description' not in current_attraction:
                        current_attraction['description'] = line
                    else:
                        current_attraction['details'].append(line)
        
        if current_attraction.get('name'):
            attractions.append(current_attraction)
        
        return attractions
    
    def _parse_event_response(self, response: str) -> List[Dict]:
        """Parse event search response"""
        events = []
        current_event = {}
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                if current_event.get('name'):
                    events.append(current_event)
                    current_event = {}
                continue
            
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                if current_event.get('name'):
                    events.append(current_event)
                name_part = line.split('.', 1)[1].strip()
                if '**' in name_part:
                    name = name_part.replace('**', '').strip()
                else:
                    name = name_part.split('-')[0].strip() if '-' in name_part else name_part
                current_event = {'name': name, 'details': []}
            elif current_event:
                if 'Date:' in line or 'When:' in line:
                    current_event['date'] = line.split(':', 1)[1].strip()
                elif 'Venue:' in line or 'Location:' in line:
                    current_event['venue'] = line.split(':', 1)[1].strip()
                elif 'Price:' in line or 'Tickets:' in line:
                    current_event['price'] = line.split(':', 1)[1].strip()
                elif line.startswith('-'):
                    current_event['details'].append(line[1:].strip())
                elif not line.startswith('#'):
                    if 'description' not in current_event:
                        current_event['description'] = line
                    else:
                        current_event['details'].append(line)
        
        if current_event.get('name'):
            events.append(current_event)
        
        return events
    
    def _parse_daily_itinerary_response(self, response: str, day_number: int, date: str, day_of_week: str) -> Dict:
        """Parse daily itinerary response"""
        itinerary = {
            "day": day_number,
            "date": date,
            "day_of_week": day_of_week,
            "morning": [],
            "lunch": [],
            "afternoon": [],
            "evening": [],
            "tips": []
        }
        
        current_section = None
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if 'MORNING' in line.upper() or '8:00' in line or '9:00' in line:
                current_section = 'morning'
            elif 'LUNCH' in line.upper() or '12:00' in line or '1:00' in line:
                current_section = 'lunch'
            elif 'AFTERNOON' in line.upper() or '2:00' in line or '3:00' in line:
                current_section = 'afternoon'
            elif 'EVENING' in line.upper() or '6:00' in line or '7:00' in line:
                current_section = 'evening'
            elif 'TIP' in line.upper() or 'NOTE' in line.upper():
                current_section = 'tips'
            elif current_section and not line.startswith('#'):
                # Add content to current section
                if line.startswith('-'):
                    line = line[1:].strip()
                if line:
                    itinerary[current_section].append(line)
        
        return itinerary
    
    def _parse_insights_response(self, response: str) -> Dict:
        """Parse local insights response"""
        insights = {
            "weather": [],
            "transportation": [],
            "money": [],
            "cultural": [],
            "updates": [],
            "tips": []
        }
        
        current_section = 'tips'
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify sections
            if 'WEATHER' in line.upper() or 'PACKING' in line.upper():
                current_section = 'weather'
            elif 'TRANSPORT' in line.upper():
                current_section = 'transportation'
            elif 'MONEY' in line.upper() or 'COST' in line.upper():
                current_section = 'money'
            elif 'CULTURAL' in line.upper() or 'CUSTOM' in line.upper():
                current_section = 'cultural'
            elif 'UPDATE' in line.upper() or 'CURRENT' in line.upper():
                current_section = 'updates'
            elif not line.startswith('#'):
                # Add content to current section
                if line.startswith('-'):
                    line = line[1:].strip()
                if line and not line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    insights[current_section].append(line)
        
        return insights