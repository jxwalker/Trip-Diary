"""
Places Service for Trip Diary
Provides restaurant, attraction, and venue recommendations
"""

import os
import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime
import googlemaps
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class PlacesService:
    def __init__(self):
        # Google Maps API key
        self.google_api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        if self.google_api_key:
            self.gmaps = googlemaps.Client(key=self.google_api_key)
        else:
            self.gmaps = None
            
        # Yelp API key (optional)
        self.yelp_api_key = os.getenv("YELP_API_KEY", "")
        
    async def get_restaurant_recommendations(
        self,
        location: str,
        preferences: Dict,
        hotel_address: Optional[str] = None
    ) -> List[Dict]:
        """
        Get restaurant recommendations based on user preferences
        
        Args:
            location: City or area name
            preferences: User preferences (cuisines, price_range, dietary)
            hotel_address: Hotel address for distance calculations
            
        Returns:
            List of recommended restaurants with details
        """
        
        if not self.google_api_key:
            return self._get_mock_restaurants(location, preferences)
        
        try:
            restaurants = []
            
            # Search for restaurants based on cuisine preferences
            cuisines = preferences.get("cuisineTypes", ["restaurant"])
            price_level = self._convert_price_range(preferences.get("priceRange", "$$"))
            
            for cuisine in cuisines[:3]:  # Limit to top 3 cuisines
                query = f"{cuisine} restaurant in {location}"
                
                # Use Google Places API
                places_result = self.gmaps.places(
                    query=query,
                    type='restaurant',
                    min_price=price_level[0] if price_level else None,
                    max_price=price_level[1] if price_level else None
                )
                
                for place in places_result.get('results', [])[:3]:  # Top 3 per cuisine
                    # Get detailed information
                    details = self.gmaps.place(place['place_id'])['result']
                    
                    restaurant = {
                        "name": details.get('name'),
                        "cuisine": cuisine,
                        "address": details.get('formatted_address'),
                        "phone": details.get('formatted_phone_number', ''),
                        "rating": details.get('rating', 0),
                        "price_level": self._format_price_level(details.get('price_level', 2)),
                        "opening_hours": self._format_hours(details.get('opening_hours', {})),
                        "website": details.get('website', ''),
                        "google_maps_url": details.get('url', ''),
                        "reviews_summary": self._get_review_summary(details.get('reviews', [])),
                        "specialties": [],  # Would need additional API or scraping
                        "reservation_recommended": details.get('rating', 0) > 4.3,
                        "distance_from_hotel": None  # Calculate if hotel address provided
                    }
                    
                    # Calculate distance from hotel if possible
                    if hotel_address and self.gmaps:
                        try:
                            distance = self.gmaps.distance_matrix(
                                origins=[hotel_address],
                                destinations=[restaurant["address"]]
                            )
                            if distance['rows'][0]['elements'][0]['status'] == 'OK':
                                restaurant["distance_from_hotel"] = distance['rows'][0]['elements'][0]['distance']['text']
                                restaurant["walking_time"] = distance['rows'][0]['elements'][0]['duration']['text']
                        except:
                            pass
                    
                    restaurants.append(restaurant)
            
            # Sort by rating
            restaurants.sort(key=lambda x: x.get('rating', 0), reverse=True)
            return restaurants[:10]  # Return top 10
            
        except Exception as e:
            print(f"Places API error: {e}")
            return self._get_mock_restaurants(location, preferences)
    
    async def get_attractions(
        self,
        location: str,
        preferences: Dict,
        hotel_address: Optional[str] = None
    ) -> List[Dict]:
        """
        Get attraction recommendations based on user interests
        
        Args:
            location: City or area name
            preferences: User preferences (interests, activity level)
            hotel_address: Hotel address for distance calculations
            
        Returns:
            List of recommended attractions with details
        """
        
        if not self.google_api_key:
            return self._get_mock_attractions(location, preferences)
        
        try:
            attractions = []
            
            # Map user interests to Google Places types
            interest_mapping = {
                "artCulture": ["museum", "art_gallery"],
                "history": ["museum", "church", "monument"],
                "nature": ["park", "natural_feature"],
                "shopping": ["shopping_mall", "store"],
                "nightlife": ["night_club", "bar"]
            }
            
            # Get relevant place types based on interests
            types_to_search = []
            for interest, level in preferences.items():
                if interest in interest_mapping and level > 2:  # Interest level > 2
                    types_to_search.extend(interest_mapping[interest])
            
            # Also add tourist attractions
            types_to_search.append("tourist_attraction")
            
            # Search for each type
            for place_type in set(types_to_search):
                places_result = self.gmaps.places_nearby(
                    location=location,
                    type=place_type,
                    rank_by='prominence'
                )
                
                for place in places_result.get('results', [])[:3]:  # Top 3 per type
                    # Get detailed information
                    details = self.gmaps.place(place['place_id'])['result']
                    
                    attraction = {
                        "name": details.get('name'),
                        "type": place_type.replace('_', ' ').title(),
                        "address": details.get('formatted_address'),
                        "rating": details.get('rating', 0),
                        "opening_hours": self._format_hours(details.get('opening_hours', {})),
                        "website": details.get('website', ''),
                        "google_maps_url": details.get('url', ''),
                        "description": self._generate_attraction_description(details),
                        "entry_fee": None,  # Would need additional data source
                        "typical_duration": self._estimate_duration(place_type),
                        "best_time_to_visit": self._suggest_visit_time(place_type),
                        "distance_from_hotel": None
                    }
                    
                    # Calculate distance from hotel
                    if hotel_address and self.gmaps:
                        try:
                            distance = self.gmaps.distance_matrix(
                                origins=[hotel_address],
                                destinations=[attraction["address"]]
                            )
                            if distance['rows'][0]['elements'][0]['status'] == 'OK':
                                attraction["distance_from_hotel"] = distance['rows'][0]['elements'][0]['distance']['text']
                                attraction["travel_time"] = distance['rows'][0]['elements'][0]['duration']['text']
                        except:
                            pass
                    
                    attractions.append(attraction)
            
            # Remove duplicates and sort by rating
            seen = set()
            unique_attractions = []
            for attr in attractions:
                if attr['name'] not in seen:
                    seen.add(attr['name'])
                    unique_attractions.append(attr)
            
            unique_attractions.sort(key=lambda x: x.get('rating', 0), reverse=True)
            return unique_attractions[:15]  # Return top 15
            
        except Exception as e:
            print(f"Attractions API error: {e}")
            return self._get_mock_attractions(location, preferences)
    
    def _convert_price_range(self, price_str: str) -> Optional[tuple]:
        """Convert $ symbols to Google price levels (0-4)"""
        mapping = {
            "$": (0, 1),
            "$$": (1, 2),
            "$$$": (2, 3),
            "$$$$": (3, 4)
        }
        return mapping.get(price_str)
    
    def _format_price_level(self, level: int) -> str:
        """Convert Google price level to $ symbols"""
        return "$" * (level + 1) if level is not None else "$$"
    
    def _format_hours(self, hours_data: Dict) -> List[str]:
        """Format opening hours from Google Places data"""
        if 'weekday_text' in hours_data:
            return hours_data['weekday_text']
        return ["Hours not available"]
    
    def _get_review_summary(self, reviews: List[Dict]) -> str:
        """Extract a summary from reviews"""
        if not reviews:
            return ""
        
        # Get the most helpful review
        top_review = max(reviews, key=lambda x: x.get('rating', 0))
        text = top_review.get('text', '')
        
        # Truncate if too long
        if len(text) > 200:
            text = text[:197] + "..."
        
        return text
    
    def _generate_attraction_description(self, details: Dict) -> str:
        """Generate a description for an attraction"""
        # In production, this could use an AI service to generate better descriptions
        types = details.get('types', [])
        name = details.get('name', '')
        
        if 'museum' in types:
            return f"{name} is a must-visit museum showcasing local culture and history."
        elif 'park' in types:
            return f"{name} offers beautiful green spaces perfect for relaxation and recreation."
        elif 'art_gallery' in types:
            return f"{name} features impressive art collections and exhibitions."
        else:
            return f"{name} is a popular attraction worth exploring during your visit."
    
    def _estimate_duration(self, place_type: str) -> str:
        """Estimate typical visit duration based on place type"""
        durations = {
            "museum": "2-3 hours",
            "art_gallery": "1-2 hours",
            "park": "1-2 hours",
            "monument": "30-60 minutes",
            "shopping_mall": "2-3 hours",
            "tourist_attraction": "1-2 hours"
        }
        return durations.get(place_type, "1-2 hours")
    
    def _suggest_visit_time(self, place_type: str) -> str:
        """Suggest best time to visit based on place type"""
        suggestions = {
            "museum": "Morning or early afternoon",
            "art_gallery": "Afternoon",
            "park": "Morning or late afternoon",
            "monument": "Morning for best photos",
            "shopping_mall": "Afternoon or evening",
            "night_club": "Late evening",
            "bar": "Evening"
        }
        return suggestions.get(place_type, "Any time")
    
    def _get_mock_restaurants(self, location: str, preferences: Dict) -> List[Dict]:
        """Return mock restaurant data for development"""
        
        mock_restaurants = [
            {
                "name": "The Local Kitchen",
                "cuisine": "Local Cuisine",
                "address": f"123 Main Street, {location}",
                "phone": "+1 555-0101",
                "rating": 4.6,
                "price_level": "$$",
                "opening_hours": [
                    "Monday: 11:00 AM – 10:00 PM",
                    "Tuesday: 11:00 AM – 10:00 PM",
                    "Wednesday: 11:00 AM – 10:00 PM",
                    "Thursday: 11:00 AM – 10:00 PM",
                    "Friday: 11:00 AM – 11:00 PM",
                    "Saturday: 10:00 AM – 11:00 PM",
                    "Sunday: 10:00 AM – 9:00 PM"
                ],
                "website": "https://example.com/local-kitchen",
                "google_maps_url": "https://maps.google.com",
                "reviews_summary": "Amazing local dishes with fresh ingredients. The atmosphere is cozy and service is excellent.",
                "specialties": ["Farm-to-table cuisine", "Seasonal menu", "Local wines"],
                "reservation_recommended": True,
                "distance_from_hotel": "0.5 km",
                "walking_time": "6 mins"
            },
            {
                "name": "Bella Vista Italian",
                "cuisine": "Italian",
                "address": f"456 Restaurant Row, {location}",
                "phone": "+1 555-0102",
                "rating": 4.5,
                "price_level": "$$$",
                "opening_hours": [
                    "Monday: Closed",
                    "Tuesday: 5:00 PM – 10:00 PM",
                    "Wednesday: 5:00 PM – 10:00 PM",
                    "Thursday: 5:00 PM – 10:00 PM",
                    "Friday: 5:00 PM – 11:00 PM",
                    "Saturday: 5:00 PM – 11:00 PM",
                    "Sunday: 4:00 PM – 9:00 PM"
                ],
                "website": "https://example.com/bella-vista",
                "google_maps_url": "https://maps.google.com",
                "reviews_summary": "Authentic Italian cuisine with an extensive wine list. Perfect for a romantic dinner.",
                "specialties": ["Homemade pasta", "Wood-fired pizza", "Tiramisu"],
                "reservation_recommended": True,
                "distance_from_hotel": "1.2 km",
                "walking_time": "15 mins"
            },
            {
                "name": "Sakura Sushi Bar",
                "cuisine": "Japanese",
                "address": f"789 Asia District, {location}",
                "phone": "+1 555-0103",
                "rating": 4.7,
                "price_level": "$$$",
                "opening_hours": [
                    "Monday: 11:30 AM – 2:30 PM, 5:00 PM – 10:00 PM",
                    "Tuesday: 11:30 AM – 2:30 PM, 5:00 PM – 10:00 PM",
                    "Wednesday: 11:30 AM – 2:30 PM, 5:00 PM – 10:00 PM",
                    "Thursday: 11:30 AM – 2:30 PM, 5:00 PM – 10:00 PM",
                    "Friday: 11:30 AM – 2:30 PM, 5:00 PM – 11:00 PM",
                    "Saturday: 12:00 PM – 11:00 PM",
                    "Sunday: 12:00 PM – 10:00 PM"
                ],
                "website": "https://example.com/sakura-sushi",
                "google_maps_url": "https://maps.google.com",
                "reviews_summary": "Fresh sushi and authentic Japanese dishes. The omakase menu is highly recommended.",
                "specialties": ["Omakase", "Fresh sashimi", "Sake selection"],
                "reservation_recommended": True,
                "distance_from_hotel": "0.8 km",
                "walking_time": "10 mins"
            }
        ]
        
        return mock_restaurants
    
    def _get_mock_attractions(self, location: str, preferences: Dict) -> List[Dict]:
        """Return mock attraction data for development"""
        
        mock_attractions = [
            {
                "name": f"{location} Museum of Art",
                "type": "Museum",
                "address": f"100 Museum Plaza, {location}",
                "rating": 4.7,
                "opening_hours": [
                    "Monday: Closed",
                    "Tuesday: 10:00 AM – 5:00 PM",
                    "Wednesday: 10:00 AM – 5:00 PM",
                    "Thursday: 10:00 AM – 8:00 PM",
                    "Friday: 10:00 AM – 5:00 PM",
                    "Saturday: 10:00 AM – 6:00 PM",
                    "Sunday: 11:00 AM – 5:00 PM"
                ],
                "website": "https://example.com/art-museum",
                "google_maps_url": "https://maps.google.com",
                "description": "World-renowned art museum featuring both classical and contemporary collections.",
                "entry_fee": "$25 adults, $15 students",
                "typical_duration": "2-3 hours",
                "best_time_to_visit": "Morning or early afternoon",
                "distance_from_hotel": "2.5 km",
                "travel_time": "8 mins by car"
            },
            {
                "name": "Historic Old Town",
                "type": "Tourist Attraction",
                "address": f"Old Town Square, {location}",
                "rating": 4.6,
                "opening_hours": ["Open 24 hours"],
                "website": "https://example.com/old-town",
                "google_maps_url": "https://maps.google.com",
                "description": "Charming historic district with cobblestone streets, local shops, and cafes.",
                "entry_fee": "Free",
                "typical_duration": "2-3 hours",
                "best_time_to_visit": "Morning for best photos",
                "distance_from_hotel": "1.0 km",
                "travel_time": "12 mins walking"
            },
            {
                "name": "Central Park",
                "type": "Park",
                "address": f"Park Avenue, {location}",
                "rating": 4.5,
                "opening_hours": ["Open 6:00 AM – 10:00 PM"],
                "website": "https://example.com/central-park",
                "google_maps_url": "https://maps.google.com",
                "description": "Beautiful urban park perfect for walking, jogging, or picnicking.",
                "entry_fee": "Free",
                "typical_duration": "1-2 hours",
                "best_time_to_visit": "Morning or late afternoon",
                "distance_from_hotel": "0.7 km",
                "travel_time": "8 mins walking"
            }
        ]
        
        return mock_attractions