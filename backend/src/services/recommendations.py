"""
Recommendations Service
Generates personalized recommendations for restaurants, attractions, events

NOTE: This service must not return mocked content. It will:
- Prefer real data already attached to the itinerary (e.g., from ImmediateGuideGenerator)
- Otherwise, return empty lists, to comply with the no-mocks policy
"""
from typing import Dict, List, Any

class RecommendationsService:
    async def get_recommendations(self, itinerary: Dict) -> Dict:
        """
        Generate recommendations based on itinerary using available REAL data only.
        """
        # Prefer recommendations already added to the itinerary by real services
        restaurants = itinerary.get("restaurants", []) or []
        attractions = itinerary.get("attractions", []) or []
        events = itinerary.get("events", []) or []

        recommendations = {
            "restaurants": restaurants,
            "attractions": attractions,
            "events": events,
            "shopping": [],
            "transportation": {},
            "local_tips": []
        }
        
        return recommendations
    
    async def update_with_preferences(self, recommendations: Dict, preferences: Dict) -> Dict:
        """
        Update recommendations based on user preferences
        """
        # Filter based on preferences
        if preferences.get("budget"):
            # Filter by price range
            budget = preferences["budget"]
            if budget == "low":
                recommendations["restaurants"] = [r for r in recommendations["restaurants"] 
                                                if r["price_range"] in ["$", "$$"]]
            elif budget == "high":
                recommendations["restaurants"] = [r for r in recommendations["restaurants"] 
                                                if r["price_range"] in ["$$$", "$$$$"]]
        
        if preferences.get("cuisine_preferences"):
            # Filter by cuisine type
            cuisines = preferences["cuisine_preferences"]
            recommendations["restaurants"] = [r for r in recommendations["restaurants"] 
                                            if any(c.lower() in r["cuisine"].lower() for c in cuisines)]
        
        if preferences.get("interests"):
            # Prioritize attractions based on interests
            interests = preferences["interests"]
            if "art" in interests:
                # Move art attractions to top
                recommendations["attractions"] = sorted(
                    recommendations["attractions"],
                    key=lambda x: "museum" in x["type"].lower() or "art" in x["name"].lower(),
                    reverse=True
                )
        
        return recommendations