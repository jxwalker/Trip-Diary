"""
Recommendations Service
Generates personalized recommendations for restaurants, attractions, events
"""
from typing import Dict, List, Any
import random

class RecommendationsService:
    async def get_recommendations(self, itinerary: Dict) -> Dict:
        """
        Generate recommendations based on itinerary
        """
        destination = itinerary.get("trip_summary", {}).get("destination", "Unknown")
        
        recommendations = {
            "restaurants": self._get_restaurant_recommendations(destination),
            "attractions": self._get_attraction_recommendations(destination),
            "events": self._get_event_recommendations(destination),
            "shopping": self._get_shopping_recommendations(destination),
            "transportation": self._get_transport_tips(destination),
            "local_tips": self._get_local_tips(destination)
        }
        
        return recommendations
    
    def _get_restaurant_recommendations(self, destination: str) -> List[Dict]:
        """Get restaurant recommendations"""
        # In production, this would call Yelp API or similar
        restaurants = [
            {
                "name": "Le Bernardin",
                "cuisine": "French Seafood",
                "price_range": "$$$$",
                "rating": 4.8,
                "address": "155 West 51st Street",
                "phone": "+1 212-554-1515",
                "description": "Exquisite French seafood in elegant setting",
                "reservation_required": True,
                "distance_from_hotel": "0.8 miles",
                "must_try": ["Tuna Carpaccio", "Lobster", "Black Bass"]
            },
            {
                "name": "Joe's Pizza",
                "cuisine": "Italian",
                "price_range": "$",
                "rating": 4.5,
                "address": "7 Carmine Street",
                "phone": "+1 212-366-1182",
                "description": "Classic New York pizza joint",
                "reservation_required": False,
                "distance_from_hotel": "1.2 miles",
                "must_try": ["Cheese Pizza", "Pepperoni Slice"]
            },
            {
                "name": "Eleven Madison Park",
                "cuisine": "Contemporary American",
                "price_range": "$$$$",
                "rating": 4.9,
                "address": "11 Madison Avenue",
                "phone": "+1 212-889-0905",
                "description": "Award-winning fine dining experience",
                "reservation_required": True,
                "distance_from_hotel": "2.1 miles",
                "must_try": ["Tasting Menu"]
            },
            {
                "name": "Shake Shack",
                "cuisine": "American",
                "price_range": "$$",
                "rating": 4.3,
                "address": "Madison Square Park",
                "phone": "+1 646-747-7200",
                "description": "Gourmet burgers and shakes",
                "reservation_required": False,
                "distance_from_hotel": "1.5 miles",
                "must_try": ["ShackBurger", "Cheese Fries", "Concrete"]
            }
        ]
        
        return restaurants
    
    def _get_attraction_recommendations(self, destination: str) -> List[Dict]:
        """Get attraction recommendations"""
        attractions = [
            {
                "name": "Metropolitan Museum of Art",
                "type": "Museum",
                "price": "$30 adults",
                "rating": 4.7,
                "address": "1000 5th Avenue",
                "hours": "10:00 AM - 5:00 PM",
                "description": "One of the world's largest and most important art museums",
                "time_needed": "3-4 hours",
                "best_time": "Weekday mornings",
                "highlights": ["Egyptian Art", "American Wing", "Rooftop Garden"]
            },
            {
                "name": "Central Park",
                "type": "Park",
                "price": "Free",
                "rating": 4.8,
                "address": "Central Park",
                "hours": "6:00 AM - 1:00 AM",
                "description": "843-acre green oasis in the heart of Manhattan",
                "time_needed": "2-3 hours",
                "best_time": "Morning or late afternoon",
                "highlights": ["Bethesda Fountain", "Bow Bridge", "Strawberry Fields"]
            },
            {
                "name": "Empire State Building",
                "type": "Landmark",
                "price": "$44 adults",
                "rating": 4.6,
                "address": "350 5th Avenue",
                "hours": "10:00 AM - 12:00 AM",
                "description": "Iconic Art Deco skyscraper with observation decks",
                "time_needed": "1-2 hours",
                "best_time": "Sunset",
                "highlights": ["86th Floor Observatory", "102nd Floor Observatory"]
            },
            {
                "name": "Brooklyn Bridge",
                "type": "Landmark",
                "price": "Free",
                "rating": 4.8,
                "address": "Brooklyn Bridge",
                "hours": "24 hours",
                "description": "Historic bridge connecting Manhattan and Brooklyn",
                "time_needed": "45 minutes to walk",
                "best_time": "Sunrise or sunset",
                "highlights": ["Walking path", "Bike path", "Photo opportunities"]
            }
        ]
        
        return attractions
    
    def _get_event_recommendations(self, destination: str) -> List[Dict]:
        """Get event recommendations"""
        # In production, would call Ticketmaster/PredictHQ APIs
        events = [
            {
                "name": "Broadway Show: Hamilton",
                "type": "Theater",
                "date": "Multiple dates available",
                "venue": "Richard Rodgers Theatre",
                "address": "226 West 46th Street",
                "price_range": "$149-$849",
                "description": "Award-winning musical about Alexander Hamilton",
                "ticket_link": "https://hamiltonmusical.com",
                "duration": "2 hours 45 minutes"
            },
            {
                "name": "Yankees vs Red Sox",
                "type": "Sports",
                "date": "Check schedule",
                "venue": "Yankee Stadium",
                "address": "1 E 161st St, Bronx",
                "price_range": "$25-$300",
                "description": "Classic MLB rivalry game",
                "ticket_link": "https://mlb.com/yankees",
                "duration": "3 hours"
            },
            {
                "name": "Jazz at Lincoln Center",
                "type": "Music",
                "date": "Various performances",
                "venue": "Lincoln Center",
                "address": "10 Columbus Circle",
                "price_range": "$35-$150",
                "description": "World-class jazz performances",
                "ticket_link": "https://jazz.org",
                "duration": "2 hours"
            }
        ]
        
        return events
    
    def _get_shopping_recommendations(self, destination: str) -> List[Dict]:
        """Get shopping recommendations"""
        shopping = [
            {
                "name": "Fifth Avenue",
                "type": "Shopping District",
                "description": "Luxury shopping with flagship stores",
                "highlights": ["Tiffany & Co", "Apple Store", "Saks Fifth Avenue"],
                "best_for": "Luxury goods, flagship stores"
            },
            {
                "name": "Chelsea Market",
                "type": "Indoor Market",
                "description": "Food hall and shopping in former factory",
                "highlights": ["Local vendors", "Artisanal foods", "Unique gifts"],
                "best_for": "Food, local products, souvenirs"
            },
            {
                "name": "SoHo",
                "type": "Shopping District",
                "description": "Trendy boutiques and cast-iron architecture",
                "highlights": ["Independent boutiques", "Art galleries", "Vintage stores"],
                "best_for": "Fashion, art, unique finds"
            }
        ]
        
        return shopping
    
    def _get_transport_tips(self, destination: str) -> Dict:
        """Get transportation tips"""
        return {
            "airport_transfer": {
                "options": ["Taxi ($70)", "Uber/Lyft ($40-60)", "AirTrain + Subway ($8)", "Airport Shuttle ($20)"],
                "recommended": "Uber/Lyft for convenience",
                "time": "45-90 minutes depending on traffic"
            },
            "local_transport": {
                "subway": {
                    "price": "$2.90 per ride",
                    "tip": "Buy a 7-day unlimited MetroCard for $34"
                },
                "taxi": {
                    "initial_fare": "$3.50",
                    "tip": "Yellow cabs are metered, tip 15-20%"
                },
                "walking": {
                    "tip": "Manhattan is very walkable, especially Midtown"
                }
            }
        }
    
    def _get_local_tips(self, destination: str) -> List[str]:
        """Get local tips"""
        return [
            "Tipping: 18-20% at restaurants, $1-2 per drink at bars",
            "Weather: Check forecast daily, layers recommended",
            "Safety: Stay aware in crowded areas, keep valuables secure",
            "Best views: Top of the Rock, One World Observatory, Brooklyn Bridge",
            "Free WiFi: Available at most cafes, libraries, and parks",
            "Happy hours: Many bars offer deals 4-7 PM on weekdays",
            "Museum free hours: Many museums have free or pay-what-you-wish hours",
            "Broadway tickets: Try lottery or rush tickets for discounts"
        ]
    
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