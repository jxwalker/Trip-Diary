import os
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class RealEventsService:
    """
    Service to fetch real, specific events happening during travel dates
    Integrates with multiple event APIs to find concerts, shows, 
    exhibitions, etc.
    """
    
    def __init__(self):
        self.ticketmaster_key = os.getenv("TICKETMASTER_API_KEY", "")
        self.eventbrite_key = os.getenv("EVENTBRITE_API_KEY", "")
        self.seatgeek_key = os.getenv("SEATGEEK_API_KEY", "")
        
        # Fallback to Perplexity for additional event discovery
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
        
        self.timeout = aiohttp.ClientTimeout(total=10)
        
    async def get_events_for_dates(
        self, 
        destination: str, 
        start_date: str, 
        end_date: str, 
        preferences: Dict
    ) -> List[Dict]:
        """
        Get real events happening during the specific travel dates
        """
        logger.info(f"Fetching real events for {destination} from "
                    f"{start_date} to {end_date}")
        
        # Run all event sources in parallel
        tasks = []
        
        # Task 1: Ticketmaster events (concerts, sports, theater)
        if self.ticketmaster_key:
            tasks.append(self._fetch_ticketmaster_events(
                destination, start_date, end_date))
        
        # Task 2: Eventbrite events (local events, workshops, festivals)
        if self.eventbrite_key:
            tasks.append(self._fetch_eventbrite_events(
                destination, start_date, end_date))
        
        # Task 3: SeatGeek events (sports, concerts)
        if self.seatgeek_key:
            tasks.append(self._fetch_seatgeek_events(
                destination, start_date, end_date))
        
        # Task 4: Perplexity search for additional events 
        # (museums, galleries, etc.)
        if self.perplexity_key:
            tasks.append(self._fetch_perplexity_events(
                destination, start_date, end_date, preferences))
        
        # Execute all tasks in parallel
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            results = []
        
        # Combine and deduplicate events
        all_events = []
        for result in results:
            if isinstance(result, list):
                all_events.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Event source failed: {result}")
        
        # Deduplicate and filter events
        unique_events = self._deduplicate_events(all_events)
        filtered_events = self._filter_events_by_preferences(
            unique_events, preferences)
        
        logger.info(f"Found {len(filtered_events)} unique events")
        return filtered_events[:12]  # Return top 12 events
    
    async def _fetch_ticketmaster_events(
        self, destination: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Fetch events from Ticketmaster API"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Use destination as-is - no hardcoded city mappings
                city = destination
                
                url = "https://app.ticketmaster.com/discovery/v2/events"
                params = {
                    "apikey": self.ticketmaster_key,
                    "city": city,
                    # Remove hardcoded state code - let API handle 
                    # location detection
                    "startDateTime": f"{start_date}T00:00:00Z",
                    "endDateTime": f"{end_date}T23:59:59Z",
                    "size": 20,
                    "sort": "relevance,desc",
                    "classificationName": "music,sports,arts&theatre"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        events = []
                        
                        for event in data.get("_embedded", {}).get(
                            "events", []):
                            # Extract event details
                            event_data = {
                                "name": event.get("name", ""),
                                "type": self._get_event_type(event),
                                "date": event.get("dates", {}).get(
                                    "start", {}).get("localDate", ""),
                                "time": event.get("dates", {}).get(
                                    "start", {}).get("localTime", ""),
                                "venue": event.get("_embedded", {}).get("venues", [{}])[0].get("name", ""),
                                "address": self._get_venue_address(event),
                                "price_range": self._get_price_range(event),
                                "description": event.get("info", ""),
                                "booking_url": event.get("url", ""),
                                "image_url": self._get_event_image(event),
                                "source": "Ticketmaster"
                            }
                            
                            if event_data["name"] and event_data["date"]:
                                events.append(event_data)
                        
                        logger.info(f"Ticketmaster: Found {len(events)} events")
                        return events
                    else:
                        logger.warning(f"Ticketmaster API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Ticketmaster fetch error: {e}")
        
        return []
    
    async def _fetch_eventbrite_events(self, destination: str, start_date: str, end_date: str) -> List[Dict]:
        """Fetch events from Eventbrite API"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Eventbrite uses different date format
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                
                url = "https://www.eventbriteapi.com/v3/events/search/"
                params = {
                    "token": self.eventbrite_key,
                    "location.address": destination,
                    "start_date.range_start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "start_date.range_end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "expand": "venue",
                    "categories": "103,104,105,106,108,110",  # Arts, Music, Food, Sports, etc.
                    "sort_by": "relevance"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        events = []
                        
                        for event in data.get("events", []):
                            event_data = {
                                "name": event.get("name", {}).get("text", ""),
                                "type": self._get_eventbrite_type(event),
                                "date": event.get("start", {}).get("local", "").split("T")[0],
                                "time": event.get("start", {}).get("local", "").split("T")[1][:5] if "T" in event.get("start", {}).get("local", "") else "",
                                "venue": event.get("venue", {}).get("name", ""),
                                "address": self._get_eventbrite_address(event),
                                "price_range": self._get_eventbrite_price(event),
                                "description": event.get("description", {}).get("text", "")[:200] + "..." if event.get("description", {}).get("text") else "",
                                "booking_url": event.get("url", ""),
                                "image_url": event.get("logo", {}).get("url", ""),
                                "source": "Eventbrite"
                            }
                            
                            if event_data["name"] and event_data["date"]:
                                events.append(event_data)
                        
                        logger.info(f"Eventbrite: Found {len(events)} events")
                        return events
                    else:
                        logger.warning(f"Eventbrite API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Eventbrite fetch error: {e}")
        
        return []
    
    async def _fetch_seatgeek_events(self, destination: str, start_date: str, end_date: str) -> List[Dict]:
        """Fetch events from SeatGeek API"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = "https://api.seatgeek.com/2/events"
                params = {
                    "client_id": self.seatgeek_key,
                    "venue.city": destination,
                    "datetime_utc.gte": f"{start_date}T00:00:00",
                    "datetime_utc.lte": f"{end_date}T23:59:59",
                    "per_page": 20,
                    "sort": "score.desc"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        events = []
                        
                        for event in data.get("events", []):
                            event_data = {
                                "name": event.get("title", ""),
                                "type": event.get("type", ""),
                                "date": event.get("datetime_utc", "").split("T")[0],
                                "time": event.get("datetime_utc", "").split("T")[1][:5] if "T" in event.get("datetime_utc", "") else "",
                                "venue": event.get("venue", {}).get("name", ""),
                                "address": self._get_seatgeek_address(event),
                                "price_range": self._get_seatgeek_price(event),
                                "description": f"{event.get('type', 'Event')} at {event.get('venue', {}).get('name', '')}",
                                "booking_url": event.get("url", ""),
                                "image_url": event.get("performers", [{}])[0].get("image", ""),
                                "source": "SeatGeek"
                            }
                            
                            if event_data["name"] and event_data["date"]:
                                events.append(event_data)
                        
                        logger.info(f"SeatGeek: Found {len(events)} events")
                        return events
                    else:
                        logger.warning(f"SeatGeek API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"SeatGeek fetch error: {e}")
        
        return []
    
    async def _fetch_perplexity_events(self, destination: str, start_date: str, end_date: str, preferences: Dict) -> List[Dict]:
        """Use Perplexity to find additional events like museum exhibitions, gallery shows, etc."""
        try:
            interests = preferences.get("specialInterests", ["culture", "art", "music"])
            
            prompt = f"""Find specific events happening in {destination} from {start_date} to {end_date}:

Focus on:
- Museum exhibitions and gallery openings
- Cultural festivals and seasonal events
- Local theater productions
- Food and wine events
- Art shows and installations
- Literary events and book signings

Interests: {', '.join(interests)}

For each event provide:
- Exact event name
- Specific date and time
- Venue name and address
- Ticket price or admission info
- Brief description
- How to attend or book

Return as JSON array with keys: name, type, date, time, venue, address, price_range, description, booking_url, source

IMPORTANT: Only include REAL events with specific dates during {start_date} to {end_date}."""
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1000
                }
                
                async with session.post("https://api.perplexity.ai/chat/completions",
                                       headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", "[]")
                        
                        from .llm_parser import LLMParser
                        llm_parser = LLMParser()
                        
                        citation_cleaning_prompt = f"""Remove citation markers from this text and return clean JSON:

INPUT:
{content}

INSTRUCTIONS:
- Remove all citation markers like [1], [2], etc.
- Keep the JSON structure intact
- Return only the cleaned JSON

OUTPUT:"""
                        
                        try:
                            try:
                                cleaned_content = await llm_parser._parse_with_openai(citation_cleaning_prompt)
                                if isinstance(cleaned_content, str):
                                    content = cleaned_content
                                elif isinstance(cleaned_content, dict) and 'events' in cleaned_content:
                                    events = cleaned_content['events']
                                    return events[:10] if len(events) > 10 else events
                            except:
                                # Fallback to basic cleaning
                                import re
                                content = re.sub(r'\[\d+\]', '', content)
                            
                            events = json.loads(content)
                            if isinstance(events, list):
                                # Add source info
                                for event in events:
                                    event["source"] = "Perplexity"
                                logger.info(f"Perplexity: Found {len(events)} events")
                                return events
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse Perplexity events JSON")
                            
        except Exception as e:
            logger.error(f"Perplexity events fetch error: {e}")
        
        return []
    
    def _deduplicate_events(self, events: List[Dict]) -> List[Dict]:
        """Remove duplicate events based on name and date"""
        seen = set()
        unique_events = []
        
        for event in events:
            # Create a key based on name and date
            key = (event.get("name", "").lower().strip(), event.get("date", ""))
            if key not in seen and event.get("name"):
                seen.add(key)
                unique_events.append(event)
        
        return unique_events
    
    def _filter_events_by_preferences(self, events: List[Dict], preferences: Dict) -> List[Dict]:
        """Filter events based on user preferences"""
        interests = preferences.get("specialInterests", [])
        
        # If no specific interests, return all events
        if not interests:
            return events
        
        # Score events based on interests
        scored_events = []
        for event in events:
            score = 0
            event_type = event.get("type", "").lower()
            event_name = event.get("name", "").lower()
            
            # Score based on interests
            for interest in interests:
                interest_lower = interest.lower()
                if interest_lower in event_type or interest_lower in event_name:
                    score += 1
                elif interest_lower in ["music", "concerts"] and any(word in event_type for word in ["music", "concert", "band"]):
                    score += 1
                elif interest_lower in ["art", "culture"] and any(word in event_type for word in ["art", "museum", "gallery", "exhibition"]):
                    score += 1
                elif interest_lower in ["sports"] and any(word in event_type for word in ["sports", "game", "match"]):
                    score += 1
            
            if score > 0:
                event["relevance_score"] = score
                scored_events.append(event)
        
        # Sort by relevance score and return
        scored_events.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return scored_events
    
    def _get_event_type(self, event: Dict) -> str:
        """Extract event type from Ticketmaster event"""
        classifications = event.get("classifications", [])
        if classifications:
            segment = classifications[0].get("segment", {}).get("name", "")
            genre = classifications[0].get("genre", {}).get("name", "")
            if segment and genre:
                return f"{segment} - {genre}"
            return segment or genre or "Event"
        return "Event"
    
    def _get_venue_address(self, event: Dict) -> str:
        """Extract venue address from Ticketmaster event"""
        venues = event.get("_embedded", {}).get("venues", [])
        if venues:
            venue = venues[0]
            address = venue.get("address", {}).get("line1", "")
            city = venue.get("city", {}).get("name", "")
            state = venue.get("state", {}).get("name", "")
            if address and city:
                return f"{address}, {city}, {state}"
        return ""
    
    def _get_price_range(self, event: Dict) -> str:
        """Extract price range from Ticketmaster event"""
        price_ranges = event.get("priceRanges", [])
        if price_ranges:
            min_price = price_ranges[0].get("min", 0)
            max_price = price_ranges[0].get("max", 0)
            currency = price_ranges[0].get("currency", "USD")
            if min_price == max_price:
                return f"${min_price} {currency}"
            else:
                return f"${min_price}-${max_price} {currency}"
        return "Price varies"
    
    def _get_event_image(self, event: Dict) -> str:
        """Extract event image from Ticketmaster event"""
        images = event.get("images", [])
        for image in images:
            if image.get("ratio") == "16_9" and image.get("width") >= 640:
                return image.get("url", "")
        return images[0].get("url", "") if images else ""
    
    def _get_eventbrite_type(self, event: Dict) -> str:
        """Extract event type from Eventbrite event"""
        category = event.get("category", {})
        if category:
            return category.get("name", "Event")
        return "Event"
    
    def _get_eventbrite_address(self, event: Dict) -> str:
        """Extract venue address from Eventbrite event"""
        venue = event.get("venue", {})
        if venue:
            address = venue.get("address", {})
            return f"{address.get('address_1', '')}, {address.get('city', '')}, {address.get('region', '')}"
        return ""
    
    def _get_eventbrite_price(self, event: Dict) -> str:
        """Extract price from Eventbrite event"""
        ticket_availability = event.get("ticket_availability", {})
        if ticket_availability.get("is_free"):
            return "Free"
        
        # Try to get price from ticket classes
        ticket_classes = event.get("ticket_classes", [])
        if ticket_classes:
            prices = [tc.get("cost", {}).get("display", "") for tc in ticket_classes if tc.get("cost")]
            if prices:
                return prices[0]
        
        return "Price varies"
    
    def _get_seatgeek_address(self, event: Dict) -> str:
        """Extract venue address from SeatGeek event"""
        venue = event.get("venue", {})
        if venue:
            return f"{venue.get('address', '')}, {venue.get('city', '')}, {venue.get('state', '')}"
        return ""
    
    def _get_seatgeek_price(self, event: Dict) -> str:
        """Extract price from SeatGeek event"""
        stats = event.get("stats", {})
        min_price = stats.get("lowest_price")
        max_price = stats.get("highest_price")
        
        if min_price and max_price:
            if min_price == max_price:
                return f"${min_price}"
            else:
                return f"${min_price}-${max_price}"
        elif min_price:
            return f"From ${min_price}"
        
        return "Price varies"
