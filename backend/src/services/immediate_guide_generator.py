"""
Immediate Guide Generator
Generates real content using Perplexity as soon as trip is uploaded
NO WAITING FOR PREFERENCES - REAL CONTENT IMMEDIATELY
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .perplexity_search_service import PerplexitySearchService
from ..utils.environment import load_project_env, get_required_api_key
from ..utils.error_handling import safe_execute, APIError

# Load environment variables
load_project_env()

logger = logging.getLogger(__name__)

class ImmediateGuideGenerator:
    """
    Service for generating immediate travel guides without waiting for user
    preferences
    """

    def __init__(self):
        """Initialize the immediate guide generator"""
        self.logger = logger
        self.perplexity = PerplexitySearchService()

        # Validate required API key
        try:
            get_required_api_key("perplexity")
        except ValueError as e:
            raise APIError(
                f"Perplexity API key required for immediate guide "
                f"generation: {e}"
            )
    
    async def enhance_itinerary_immediately(self, itinerary: Dict) -> Dict:
        """
        Enhance the itinerary with real content immediately
        Don't wait for preferences - use sensible defaults
        """
        try:
            # Extract trip details
            trip_summary = itinerary.get("trip_summary", {})
            destination = trip_summary.get("destination", "New York")
            start_date = trip_summary.get("start_date", "")
            end_date = trip_summary.get("end_date", "")
            
            # Get hotel info
            hotels = itinerary.get("accommodations", [])
            hotel_address = hotels[0]["address"] if hotels else ""
            
            # Use provided preferences or minimal defaults
            default_preferences = preferences or {}
            
            dates_dict = {
                "start": start_date,
                "end": end_date,
                "formatted": f"{start_date} to {end_date}"
            }
            
            print(f"Generating immediate guide for {destination}")
            
            # Get real restaurants
            try:
                restaurants = await self.perplexity.search_restaurants(
                    destination=destination,
                    preferences=default_preferences,
                    dates=dates_dict
                )
                itinerary["restaurants"] = restaurants[:6]  # Top 6 restaurants
            except Exception as e:
                print(f"Error getting restaurants: {e}")
                itinerary["restaurants"] = []
            
            # Get real attractions
            try:
                attractions = await self.perplexity.search_attractions(
                    destination=destination,
                    preferences=default_preferences,
                    dates=dates_dict
                )
                itinerary["attractions"] = attractions[:8]  # Top 8 attractions
            except Exception as e:
                print(f"Error getting attractions: {e}")
                itinerary["attractions"] = []
            
            # Generate real daily activities
            if "daily_schedule" in itinerary:
                for day in itinerary["daily_schedule"]:
                    day_num = day.get("day", 1)
                    date = day.get("date", "")
                    
                    # Generate real activities for this day
                    real_activities = await self._generate_day_activities(
                        destination, day_num, date, hotel_address, 
                        restaurants, attractions
                    )
                    
                    # Replace placeholder with real activities
                    day["activities"] = real_activities
                    
                    # Add meal recommendations
                    if restaurants:
                        day["meals"] = {
                            "breakfast": (
                                f"Start your day at {restaurants[0]['name']}"
                                if restaurants else "Hotel breakfast"
                            ),
                            "lunch": (
                                f"Try {restaurants[1]['name']}"
                                if len(restaurants) > 1 else "Local cafe"
                            ),
                            "dinner": (
                                f"Dine at {restaurants[2]['name']}"
                                if len(restaurants) > 2 
                                else "Restaurant near hotel"
                            )
                        }
            
            return itinerary
            
        except Exception as e:
            print(f"Error enhancing itinerary: {e}")
            return itinerary
    
    async def _generate_day_activities(
        self, 
        destination: str, 
        day_num: int, 
        date: str,
        hotel_address: str,
        restaurants: List[Dict],
        attractions: List[Dict]
    ) -> List[str]:
        """Generate real activities for a specific day"""
        
        activities = []
        
        # Day 1 - Arrival day
        if day_num == 1:
            activities.append("✈️ Arrive at airport, take taxi/train to hotel")
            activities.append(f"Check in to hotel at {hotel_address}")
            if restaurants:
                activities.append(
                    f"Evening: Welcome dinner at "
                    f"{restaurants[0].get('name', 'local restaurant')}"
                )
                if restaurants[0].get('address'):
                    activities.append(
                        f"📍 Location: {restaurants[0]['address']}"
                    )
            else:
                activities.append(f"Evening: Explore neighborhood and find dinner")
        
        # Middle days - real attractions
        elif day_num > 1 and attractions:
            # Rotate through attractions
            morning_idx = (day_num - 2) * 2 % len(attractions)
            afternoon_idx = (morning_idx + 1) % len(attractions)
            
            morning_attraction = (
                attractions[morning_idx] 
                if morning_idx < len(attractions) else None
            )
            afternoon_attraction = (
                attractions[afternoon_idx] 
                if afternoon_idx < len(attractions) else None
            )
            
            if morning_attraction:
                activities.append(
                    f"Morning: Visit "
                    f"{morning_attraction.get('name', 'attraction')}"
                )
                if morning_attraction.get('address'):
                    activities.append(f"📍 {morning_attraction['address']}")
            
            # Lunch
            lunch_idx = (day_num - 1) % len(restaurants) if restaurants else 0
            if restaurants and lunch_idx < len(restaurants):
                activities.append(
                    f"Lunch: "
                    f"{restaurants[lunch_idx].get('name', 'local restaurant')}"
                )
            
            if afternoon_attraction:
                activities.append(
                    f"Afternoon: Explore "
                    f"{afternoon_attraction.get('name', 'attraction')}"
                )
                if afternoon_attraction.get('address'):
                    activities.append(f"📍 {afternoon_attraction['address']}")
            
            # Dinner
            dinner_idx = (day_num) % len(restaurants) if restaurants else 0
            if restaurants and dinner_idx < len(restaurants):
                activities.append(
                    f"Dinner: "
                    f"{restaurants[dinner_idx].get('name', 'restaurant')}"
                )
        
        # Last day - Departure
        elif day_num > 1:
            activities.append("Morning: Check out from hotel")
            activities.append("Last-minute shopping or sightseeing")
            activities.append("✈️ Depart for airport")
        
        # If no real content available, at least be specific
        if not activities:
            activities = [
                f"Explore {destination} city center",
                f"Visit main attractions in {destination}",
                f"Enjoy local cuisine at recommended restaurants",
                f"Evening entertainment in {destination}"
            ]
        
        return activities
