"""
Enhanced Recommendations Service with Booking URLs
Adds booking links and reservation information to all recommendations
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime
import urllib.parse

class EnhancedRecommendationsService:
    """
    Service to enhance recommendations with booking URLs and additional info
    """
    
    def __init__(self):
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
    
    def generate_search_url(self, name: str, address: str, category: str) -> str:
        """Generate a Google search URL for finding the venue"""
        query = f"{name} {address} {category}"
        encoded_query = urllib.parse.quote(query)
        return f"https://www.google.com/search?q={encoded_query}"
    
    def generate_maps_url(self, name: str, address: str) -> str:
        """Generate a Google Maps URL for the venue"""
        query = f"{name}, {address}"
        encoded_query = urllib.parse.quote(query)
        return f"https://www.google.com/maps/search/{encoded_query}"
    
    def generate_booking_urls(self, restaurant: Dict) -> Dict:
        """Generate various booking URLs for a restaurant"""
        name = restaurant.get("name", "")
        address = restaurant.get("address", "")
        cuisine = restaurant.get("cuisine", "restaurant")
        
        # URL encode the parameters
        encoded_name = urllib.parse.quote(name)
        encoded_address = urllib.parse.quote(address)
        location_query = urllib.parse.quote(f"{name} {address}")
        
        urls = {
            "google_maps": f"https://www.google.com/maps/search/{location_query}",
            "opentable": f"https://www.opentable.com/s?term={encoded_name}&location={encoded_address}",
            "yelp": f"https://www.yelp.com/search?find_desc={encoded_name}&find_loc={encoded_address}",
            "tripadvisor": f"https://www.tripadvisor.com/Search?q={encoded_name}+{encoded_address}",
            "google_search": f"https://www.google.com/search?q={location_query}+reservation",
            "resy": f"https://resy.com/cities/search?query={encoded_name}",
            "website_search": f"https://www.google.com/search?q={location_query}+official+website"
        }
        
        return urls
    
    def generate_attraction_urls(self, attraction: Dict) -> Dict:
        """Generate booking and info URLs for an attraction"""
        name = attraction.get("name", "")
        address = attraction.get("address", "")
        attraction_type = attraction.get("type", "attraction")
        
        encoded_name = urllib.parse.quote(name)
        encoded_address = urllib.parse.quote(address)
        location_query = urllib.parse.quote(f"{name} {address}")
        
        urls = {
            "google_maps": f"https://www.google.com/maps/search/{location_query}",
            "tripadvisor": f"https://www.tripadvisor.com/Search?q={encoded_name}+{encoded_address}",
            "viator": f"https://www.viator.com/searchResults/all?text={encoded_name}",
            "get_your_guide": f"https://www.getyourguide.com/s/?q={encoded_name}",
            "google_search": f"https://www.google.com/search?q={location_query}+tickets",
            "official_website": f"https://www.google.com/search?q={location_query}+official+website",
            "klook": f"https://www.klook.com/en-US/search/?query={encoded_name}"
        }
        
        # Add specific URLs based on attraction type
        if "museum" in attraction_type.lower():
            urls["museum_tickets"] = f"https://www.google.com/search?q={location_query}+museum+tickets+online"
        elif "park" in attraction_type.lower():
            urls["park_info"] = f"https://www.google.com/search?q={location_query}+park+hours+admission"
        elif "theater" in attraction_type.lower() or "show" in attraction_type.lower():
            urls["ticketmaster"] = f"https://www.ticketmaster.com/search?q={encoded_name}"
        
        return urls
    
    def generate_hotel_urls(self, hotel: Dict) -> Dict:
        """Generate booking URLs for a hotel"""
        name = hotel.get("name", "")
        address = hotel.get("address", "")
        check_in = hotel.get("check_in", "")
        check_out = hotel.get("check_out", "")
        
        encoded_name = urllib.parse.quote(name)
        encoded_address = urllib.parse.quote(address)
        location_query = urllib.parse.quote(f"{name} {address}")
        
        # Parse dates if available
        date_params = ""
        if check_in and check_out:
            try:
                # Format dates for URL parameters
                ci_date = datetime.strptime(check_in, "%Y-%m-%d").strftime("%Y-%m-%d")
                co_date = datetime.strptime(check_out, "%Y-%m-%d").strftime("%Y-%m-%d")
                date_params = f"&checkin={ci_date}&checkout={co_date}"
            except:
                date_params = ""
        
        urls = {
            "google_maps": f"https://www.google.com/maps/search/{location_query}",
            "booking_com": f"https://www.booking.com/search.html?ss={encoded_name}{date_params}",
            "hotels_com": f"https://www.hotels.com/search.do?q={encoded_name}{date_params}",
            "expedia": f"https://www.expedia.com/Hotel-Search?destination={encoded_name}{date_params}",
            "agoda": f"https://www.agoda.com/search?city={encoded_address}&q={encoded_name}",
            "tripadvisor": f"https://www.tripadvisor.com/Search?q={encoded_name}+hotel",
            "google_hotels": f"https://www.google.com/travel/hotels/search?q={location_query}{date_params}",
            "official_website": f"https://www.google.com/search?q={location_query}+official+website+booking"
        }
        
        return urls
    
    def generate_event_urls(self, event: Dict) -> Dict:
        """Generate ticket and info URLs for an event"""
        name = event.get("name", "")
        venue = event.get("venue", "")
        date = event.get("date", "")
        event_type = event.get("type", "event")
        
        encoded_name = urllib.parse.quote(name)
        encoded_venue = urllib.parse.quote(venue)
        search_query = urllib.parse.quote(f"{name} {venue} {date}")
        
        urls = {
            "google_search": f"https://www.google.com/search?q={search_query}+tickets",
            "ticketmaster": f"https://www.ticketmaster.com/search?q={encoded_name}",
            "stubhub": f"https://www.stubhub.com/find/s/?q={encoded_name}",
            "eventbrite": f"https://www.eventbrite.com/d/search/?q={encoded_name}",
            "venue_website": f"https://www.google.com/search?q={encoded_venue}+official+website",
            "seatgeek": f"https://seatgeek.com/search?search={encoded_name}"
        }
        
        # Add specific URLs based on event type
        if "concert" in event_type.lower() or "music" in event_type.lower():
            urls["bandsintown"] = f"https://www.bandsintown.com/?q={encoded_name}"
        elif "sports" in event_type.lower():
            urls["sports_tickets"] = f"https://www.google.com/search?q={search_query}+sports+tickets"
        elif "theater" in event_type.lower():
            urls["theater_tickets"] = f"https://www.google.com/search?q={search_query}+theater+tickets"
        
        return urls
    
    async def enhance_restaurant(self, restaurant: Dict) -> Dict:
        """Enhance a restaurant with booking URLs and additional info"""
        enhanced = restaurant.copy()
        
        # Generate all booking URLs
        urls = self.generate_booking_urls(restaurant)
        enhanced["booking_urls"] = urls
        
        # Add quick booking link (primary recommendation)
        enhanced["primary_booking_url"] = urls["opentable"]
        enhanced["map_url"] = urls["google_maps"]
        
        # Add reservation info if not present
        if "reservation_needed" not in enhanced:
            price = restaurant.get("price_range", "$$")
            if price in ["$$$", "$$$$"]:
                enhanced["reservation_needed"] = "Recommended"
            elif price == "$$":
                enhanced["reservation_needed"] = "Optional"
            else:
                enhanced["reservation_needed"] = "Usually not needed"
        
        # Add best time to visit if not present
        if "best_time" not in enhanced:
            enhanced["best_time"] = self._suggest_best_time(restaurant)
        
        return enhanced
    
    async def enhance_attraction(self, attraction: Dict) -> Dict:
        """Enhance an attraction with booking URLs and additional info"""
        enhanced = attraction.copy()
        
        # Generate all URLs
        urls = self.generate_attraction_urls(attraction)
        enhanced["booking_urls"] = urls
        
        # Set primary URLs
        enhanced["primary_booking_url"] = urls["viator"]
        enhanced["map_url"] = urls["google_maps"]
        enhanced["info_url"] = urls["tripadvisor"]
        
        # Add ticket info if not present
        if "ticket_info" not in enhanced:
            enhanced["ticket_info"] = "Check official website for current prices and hours"
        
        # Add visit duration if not present
        if "visit_duration" not in enhanced:
            enhanced["visit_duration"] = self._suggest_visit_duration(attraction)
        
        return enhanced
    
    async def enhance_hotel(self, hotel: Dict) -> Dict:
        """Enhance a hotel with booking URLs"""
        enhanced = hotel.copy()
        
        # Generate all booking URLs
        urls = self.generate_hotel_urls(hotel)
        enhanced["booking_urls"] = urls
        
        # Set primary booking URL
        enhanced["primary_booking_url"] = urls["booking_com"]
        enhanced["map_url"] = urls["google_maps"]
        enhanced["compare_prices_url"] = urls["google_hotels"]
        
        return enhanced
    
    async def enhance_event(self, event: Dict) -> Dict:
        """Enhance an event with ticket URLs"""
        enhanced = event.copy()
        
        # Generate all URLs
        urls = self.generate_event_urls(event)
        enhanced["ticket_urls"] = urls
        
        # Set primary ticket URL
        enhanced["primary_ticket_url"] = urls["ticketmaster"]
        enhanced["venue_info_url"] = urls["venue_website"]
        
        return enhanced
    
    async def enhance_all_recommendations(self, guide: Dict) -> Dict:
        """Enhance all recommendations in a guide with URLs"""
        enhanced_guide = guide.copy()
        
        # Enhance restaurants
        if "restaurants" in enhanced_guide:
            enhanced_restaurants = []
            for restaurant in enhanced_guide["restaurants"]:
                enhanced = await self.enhance_restaurant(restaurant)
                enhanced_restaurants.append(enhanced)
            enhanced_guide["restaurants"] = enhanced_restaurants
        
        # Enhance attractions
        if "attractions" in enhanced_guide:
            enhanced_attractions = []
            for attraction in enhanced_guide["attractions"]:
                enhanced = await self.enhance_attraction(attraction)
                enhanced_attractions.append(enhanced)
            enhanced_guide["attractions"] = enhanced_attractions
        
        # Enhance hotels
        if "hotels" in enhanced_guide:
            enhanced_hotels = []
            for hotel in enhanced_guide["hotels"]:
                enhanced = await self.enhance_hotel(hotel)
                enhanced_hotels.append(enhanced)
            enhanced_guide["hotels"] = enhanced_hotels
        
        # Enhance events
        if "events" in enhanced_guide:
            enhanced_events = []
            for event in enhanced_guide["events"]:
                enhanced = await self.enhance_event(event)
                enhanced_events.append(enhanced)
            enhanced_guide["events"] = enhanced_events
        
        # Enhance daily itinerary items
        if "daily_itinerary" in enhanced_guide:
            for day in enhanced_guide["daily_itinerary"]:
                if "activities" in day:
                    for activity in day["activities"]:
                        # Add quick booking link based on activity type
                        if "restaurant" in activity.get("type", "").lower():
                            activity["booking_url"] = self.generate_booking_urls(activity).get("opentable")
                        elif "attraction" in activity.get("type", "").lower():
                            activity["booking_url"] = self.generate_attraction_urls(activity).get("viator")
                        
                        # Add map URL for all activities
                        activity["map_url"] = self.generate_maps_url(
                            activity.get("name", ""),
                            activity.get("address", "")
                        )
        
        return enhanced_guide
    
    def _suggest_best_time(self, restaurant: Dict) -> str:
        """Suggest best time to visit a restaurant"""
        cuisine = restaurant.get("cuisine", "").lower()
        price = restaurant.get("price_range", "$$")
        
        if "breakfast" in cuisine or "brunch" in cuisine:
            return "8:00 AM - 11:00 AM"
        elif "cafe" in cuisine or "coffee" in cuisine:
            return "9:00 AM - 11:00 AM or 2:00 PM - 4:00 PM"
        elif price in ["$$$", "$$$$"]:
            return "7:00 PM - 9:00 PM (dinner reservation recommended)"
        elif "lunch" in restaurant.get("name", "").lower():
            return "12:00 PM - 2:00 PM"
        else:
            return "12:00 PM - 2:00 PM (lunch) or 6:00 PM - 8:00 PM (dinner)"
    
    def _suggest_visit_duration(self, attraction: Dict) -> str:
        """Suggest visit duration for an attraction"""
        attraction_type = attraction.get("type", "").lower()
        
        if "museum" in attraction_type:
            return "2-3 hours"
        elif "park" in attraction_type:
            return "1-2 hours"
        elif "beach" in attraction_type:
            return "2-4 hours"
        elif "tour" in attraction_type:
            return "3-4 hours"
        elif "market" in attraction_type:
            return "1-2 hours"
        elif "landmark" in attraction_type:
            return "30-60 minutes"
        else:
            return "1-2 hours"
    
    async def generate_quick_booking_card(self, item: Dict, item_type: str) -> Dict:
        """Generate a quick booking card with essential URLs and info"""
        card = {
            "name": item.get("name"),
            "type": item_type,
            "quick_info": item.get("description", "")[:200]
        }
        
        if item_type == "restaurant":
            urls = self.generate_booking_urls(item)
            card["book_now"] = urls["opentable"]
            card["view_menu"] = urls["yelp"]
            card["get_directions"] = urls["google_maps"]
            card["price_range"] = item.get("price_range", "$$")
            card["cuisine"] = item.get("cuisine", "Various")
        
        elif item_type == "attraction":
            urls = self.generate_attraction_urls(item)
            card["book_tickets"] = urls["viator"]
            card["read_reviews"] = urls["tripadvisor"]
            card["get_directions"] = urls["google_maps"]
            card["duration"] = self._suggest_visit_duration(item)
        
        elif item_type == "hotel":
            urls = self.generate_hotel_urls(item)
            card["book_now"] = urls["booking_com"]
            card["compare_prices"] = urls["google_hotels"]
            card["get_directions"] = urls["google_maps"]
            card["check_in"] = item.get("check_in")
            card["check_out"] = item.get("check_out")
        
        elif item_type == "event":
            urls = self.generate_event_urls(item)
            card["buy_tickets"] = urls["ticketmaster"]
            card["venue_info"] = urls["venue_website"]
            card["find_tickets"] = urls["stubhub"]
            card["date"] = item.get("date")
            card["venue"] = item.get("venue")
        
        return card