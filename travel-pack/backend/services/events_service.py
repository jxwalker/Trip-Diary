"""
Events Service for Trip Diary
Discovers concerts, festivals, sports events, and local happenings
"""

import os
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class EventsService:
    def __init__(self):
        # API keys for various event services
        self.ticketmaster_api_key = os.getenv("TICKETMASTER_API_KEY", "")
        self.predicthq_api_key = os.getenv("PREDICTHQ_API_KEY", "")
        
    async def get_events(
        self,
        location: str,
        start_date: str,
        end_date: str,
        preferences: Dict
    ) -> Dict:
        """
        Get events happening during the trip
        
        Args:
            location: City or location name
            start_date: Trip start date (YYYY-MM-DD)
            end_date: Trip end date (YYYY-MM-DD)
            preferences: User preferences for filtering events
            
        Returns:
            Categorized events with details
        """
        
        # For now, return mock data
        # In production, would integrate with Ticketmaster, Eventbrite, etc.
        return self._get_mock_events(location, start_date, end_date, preferences)
    
    async def get_local_news(self, location: str, start_date: str) -> List[Dict]:
        """
        Get local news and updates for the destination
        
        Args:
            location: City or location name
            start_date: When the trip starts
            
        Returns:
            List of relevant news items
        """
        
        # Mock implementation
        return self._get_mock_news(location)
    
    def _get_mock_events(
        self,
        location: str,
        start_date: str,
        end_date: str,
        preferences: Dict
    ) -> Dict:
        """Return mock event data for development"""
        
        events = {
            "concerts": [],
            "festivals": [],
            "sports": [],
            "theater": [],
            "exhibitions": [],
            "local_events": []
        }
        
        # Add concerts if user likes music
        if preferences.get("music", 0) > 2:
            events["concerts"] = [
                {
                    "name": "Jazz Night at Blue Note",
                    "date": start_date,
                    "time": "20:00",
                    "venue": f"Blue Note {location}",
                    "address": f"123 Music Street, {location}",
                    "description": "An evening of smooth jazz featuring local and international artists",
                    "ticket_price": "$45-$75",
                    "ticket_url": "https://example.com/tickets",
                    "genre": "Jazz",
                    "artists": ["Local Jazz Ensemble"],
                    "duration": "2 hours"
                },
                {
                    "name": f"{location} Symphony Orchestra",
                    "date": start_date,
                    "time": "19:30",
                    "venue": f"{location} Concert Hall",
                    "address": f"456 Symphony Way, {location}",
                    "description": "Classical concert featuring works by Mozart and Beethoven",
                    "ticket_price": "$35-$120",
                    "ticket_url": "https://example.com/tickets",
                    "genre": "Classical",
                    "artists": [f"{location} Symphony Orchestra"],
                    "duration": "2.5 hours"
                }
            ]
        
        # Add cultural events if user likes art/culture
        if preferences.get("artCulture", 0) > 2:
            events["exhibitions"] = [
                {
                    "name": "Modern Art Exhibition: Beyond Boundaries",
                    "date_range": f"{start_date} to {end_date}",
                    "venue": f"{location} Museum of Contemporary Art",
                    "address": f"789 Art District, {location}",
                    "description": "Featuring works from emerging international artists",
                    "admission": "$15 adults, $10 students",
                    "opening_hours": "10:00 - 18:00",
                    "highlights": ["Interactive installations", "Virtual reality experiences"],
                    "curator_tours": "Daily at 14:00"
                }
            ]
            
            events["theater"] = [
                {
                    "name": "Shakespeare's Hamlet",
                    "dates": [start_date],
                    "times": ["19:00"],
                    "venue": f"{location} Royal Theater",
                    "address": f"100 Theater Plaza, {location}",
                    "description": "A modern interpretation of Shakespeare's classic",
                    "ticket_price": "$40-$85",
                    "ticket_url": "https://example.com/tickets",
                    "duration": "3 hours (with intermission)",
                    "dress_code": "Smart casual"
                }
            ]
        
        # Add local festivals
        events["festivals"] = [
            {
                "name": f"{location} Food & Wine Festival",
                "date_range": f"{start_date} to {end_date}",
                "location": f"{location} Waterfront",
                "description": "Annual celebration of local cuisine and wines",
                "admission": "Free entry, pay per tasting",
                "highlights": [
                    "50+ local restaurants",
                    "Wine tastings from regional vineyards",
                    "Live cooking demonstrations",
                    "Live music stages"
                ],
                "schedule": {
                    "friday": "17:00 - 23:00",
                    "saturday": "12:00 - 23:00",
                    "sunday": "12:00 - 20:00"
                },
                "family_friendly": True
            }
        ]
        
        # Add sports events if interested
        if preferences.get("specialInterests", []):
            if "Sports Events" in preferences.get("specialInterests", []):
                events["sports"] = [
                    {
                        "name": f"{location} FC vs. Rivals United",
                        "sport": "Football/Soccer",
                        "date": start_date,
                        "time": "19:45",
                        "venue": f"{location} Stadium",
                        "address": f"1 Stadium Drive, {location}",
                        "ticket_price": "$30-$150",
                        "ticket_url": "https://example.com/tickets",
                        "teams": [f"{location} FC", "Rivals United"],
                        "league": "Premier League"
                    }
                ]
        
        # Add local events
        events["local_events"] = [
            {
                "name": f"{location} Farmers Market",
                "type": "Market",
                "dates": ["Every Saturday and Sunday"],
                "time": "08:00 - 14:00",
                "location": "Town Square",
                "description": "Local produce, crafts, and street food",
                "admission": "Free",
                "highlights": ["Organic produce", "Local crafts", "Street performers"]
            },
            {
                "name": "Historical Walking Tour",
                "type": "Tour",
                "dates": ["Daily"],
                "times": ["10:00", "14:00", "16:00"],
                "meeting_point": "Tourist Information Center",
                "description": f"2-hour guided tour of {location}'s historic district",
                "price": "$20 per person",
                "booking": "Recommended",
                "languages": ["English", "Spanish", "French"]
            }
        ]
        
        return events
    
    def _get_mock_news(self, location: str) -> List[Dict]:
        """Return mock news data for development"""
        
        return [
            {
                "headline": f"New Metro Line Opens in {location}",
                "summary": "The new Blue Line connecting downtown to the airport is now operational, making travel more convenient for visitors.",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "category": "Transportation",
                "relevance": "high"
            },
            {
                "headline": f"{location} Ranked Top Destination for Food Lovers",
                "summary": f"Travel magazine ranks {location} as one of the top 10 culinary destinations worldwide.",
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "category": "Tourism",
                "relevance": "medium"
            },
            {
                "headline": "Weather Advisory: Sunny Week Ahead",
                "summary": "Meteorologists predict clear skies and pleasant temperatures for the coming week.",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "category": "Weather",
                "relevance": "high"
            }
        ]