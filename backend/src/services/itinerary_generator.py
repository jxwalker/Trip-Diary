"""
Itinerary Generator Service
Creates structured itinerary from extracted data
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json

class ItineraryGenerator:
    async def create_itinerary(self, extracted_data: Dict) -> Dict:
        """
        Generate a structured itinerary from extracted data
        """
        itinerary = {
            "trip_summary": {},
            "passengers": [],
            "daily_schedule": [],
            "flights": [],
            "accommodations": [],
            "transportation": [],
            "important_info": {},
            "trip_details": {}
        }
        
        # Process all extracted data sources
        all_flights = []
        all_hotels = []
        all_passengers = []
        destination = None
        dates = {}
        
        for source, data in extracted_data.items():
            if isinstance(data, dict):
                # Collect flights
                if "flights" in data and data["flights"]:
                    all_flights.extend(data["flights"])
                
                # Collect hotels
                if "hotels" in data and data["hotels"]:
                    all_hotels.extend(data["hotels"])
                
                # Collect passengers
                if "passengers" in data and data["passengers"]:
                    all_passengers.extend(data["passengers"])
                
                # Get destination
                if "destination" in data and data["destination"]:
                    destination = data["destination"]
                
                # Get dates from the data structure
                if "dates" in data and data["dates"]:
                    if "start_date" in data["dates"]:
                        dates["start"] = data["dates"]["start_date"]
                    if "end_date" in data["dates"]:
                        dates["end"] = data["dates"]["end_date"]
                
                # Try to infer dates from flights if not set
                if not dates.get("start") and all_flights:
                    # Get earliest departure date
                    for flight in all_flights:
                        if flight.get("departure_date"):
                            if (not dates.get("start") or 
                                flight["departure_date"] < dates["start"]):
                                dates["start"] = flight["departure_date"]
                        
                # Try to infer dates from hotels if not set
                if not dates.get("start") and all_hotels:
                    for hotel in all_hotels:
                        if hotel.get("check_in_date"):
                            dates["start"] = hotel["check_in_date"]
                            break
                if not dates.get("end") and all_hotels:
                    for hotel in all_hotels:
                        if hotel.get("check_out_date"):
                            dates["end"] = hotel["check_out_date"]
                
                # Manual input handling
                if source == "manual_input":
                    if "destination" in data:
                        destination = data["destination"]
                    if "start_date" in data:
                        dates["start"] = data["start_date"]
                    if "end_date" in data:
                        dates["end"] = data["end_date"]
        
        # Add passengers to itinerary
        itinerary["passengers"] = all_passengers
        
        # Build trip summary
        itinerary["trip_summary"] = {
            "destination": (destination or 
                           self._infer_destination(all_flights, all_hotels)),
            "start_date": dates.get("start", ""),
            "end_date": dates.get("end", ""),
            "duration": self._calculate_duration(
                dates.get("start"), dates.get("end")),
            "total_flights": len(all_flights),
            "total_hotels": len(all_hotels),
            "total_passengers": len(all_passengers)
        }
        
        # Add flights
        itinerary["flights"] = self._process_flights(all_flights)
        
        # Add accommodations
        itinerary["accommodations"] = self._process_hotels(all_hotels)
        
        # Generate daily schedule
        itinerary["daily_schedule"] = self._generate_daily_schedule(
            dates.get("start"),
            dates.get("end"),
            all_flights,
            all_hotels
        )
        
        # Add important info - will be enhanced with real data from Perplexity
        itinerary["important_info"] = {
            "destination": destination,
            "currency": self._get_currency(destination),
            "dates": {
                "start": dates.get("start", ""),
                "end": dates.get("end", "")
            },
            "note": "Details will be populated with real-time information"
        }
        
        return itinerary
    
    def _infer_destination(self, flights: List[Dict], 
                          hotels: List[Dict]) -> str:
        """Infer destination from flights and hotels"""

        print(f"[DESTINATION] 🎯 Inferring destination from extracted data...")
        print(f"[DESTINATION] 📊 Input: {len(flights)} flights, "
              f"{len(hotels)} hotels")

        # Try to get destination from hotels first
        if hotels:
            for i, hotel in enumerate(hotels):
                city = hotel.get("city")
                print(f"[DESTINATION] 🏨 Hotel {i+1}: "
                      f"{hotel.get('name')} in city '{city}'")
                if city:
                    print(f"[DESTINATION] ✅ Found destination from hotel: "
                          f"'{city}'")
                    return city

        # Try to get from flight arrival
        if flights:
            for i, flight in enumerate(flights):
                arrival_city = flight.get("arrival_city")
                arrival_airport = flight.get("arrival_airport")
                print(f"[DESTINATION] ✈️  Flight {i+1}: "
                      f"{flight.get('flight_number')} → {arrival_airport} "
                      f"(city: {arrival_city})")

                if arrival_city:
                    print(f"[DESTINATION] ✅ Found destination from flight "
                          f"arrival city: '{arrival_city}'")
                    return arrival_city
                elif arrival_airport:
                    # Map common airport codes to cities
                    airport_map = {
                        "JFK": "New York", "LGA": "New York", 
                        "EWR": "New York",
                        "LAX": "Los Angeles", "SFO": "San Francisco",
                        "ORD": "Chicago", "MDW": "Chicago",
                        "LHR": "London", "LGW": "London", "STN": "London",
                        "CDG": "Paris", "ORY": "Paris",
                        "DXB": "Dubai", "HND": "Tokyo", "NRT": "Tokyo"
                    }
                    if arrival_airport in airport_map:
                        destination = airport_map[arrival_airport]
                        print(f"[DESTINATION] ✅ Mapped airport "
                              f"'{arrival_airport}' to destination: "
                              f"'{destination}'")
                        return destination
                    else:
                        print(f"[DESTINATION] ❓ Airport '{arrival_airport}' "
                              f"not in mapping")

        print(f"[DESTINATION] ⚠️  Could not determine destination, using 'Unknown Destination'")
        return "Unknown Destination"
    
    def _calculate_duration(self, start_date: str, end_date: str) -> str:
        """Calculate trip duration"""
        try:
            if start_date and end_date and start_date != "" and end_date != "":
                # Try different date formats
                for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d %b %Y"]:
                    try:
                        start = datetime.strptime(start_date, fmt)
                        end = datetime.strptime(end_date, fmt)
                        duration = (end - start).days + 1
                        return f"{duration} days"
                    except:
                        continue
        except:
            pass
        return "Unknown duration"
    
    def _process_flights(self, flights: List[Dict]) -> List[Dict]:
        """Process and standardize flight information"""
        processed = []
        for flight in flights:
            if isinstance(flight, dict):
                processed.append({
                    "flight_number": flight.get("flight_number", "Unknown"),
                    "airline": flight.get("airline", "Unknown Airline"),
                    "departure": {
                        "airport": flight.get("departure_airport", ""),
                        "airport_name": flight.get("departure_airport_name", ""),
                        "terminal": flight.get("departure_terminal", ""),
                        "time": flight.get("departure_time", ""),
                        "date": flight.get("departure_date", flight.get("date", ""))
                    },
                    "arrival": {
                        "airport": flight.get("arrival_airport", ""),
                        "airport_name": flight.get("arrival_airport_name", ""),
                        "terminal": flight.get("arrival_terminal", ""),
                        "time": flight.get("arrival_time", ""),
                        "date": flight.get("arrival_date", "")
                    },
                    "seat": flight.get("seat", ""),
                    "class": flight.get("class", ""),
                    "duration": flight.get("duration", ""),
                    "aircraft": flight.get("aircraft", ""),
                    "booking_reference": flight.get("booking_reference", ""),
                    "ticket_number": flight.get("ticket_number", ""),
                    "status": "Confirmed"
                })
        return processed
    
    def _process_hotels(self, hotels: List[Dict]) -> List[Dict]:
        """Process and standardize hotel information"""
        processed = []
        for hotel in hotels:
            if isinstance(hotel, dict):
                processed.append({
                    "name": hotel.get("name", "Hotel"),
                    "address": hotel.get("address", "Address TBD"),
                    "city": hotel.get("city", ""),
                    "postal_code": hotel.get("postal_code", ""),
                    "check_in": hotel.get("check_in_date", ""),
                    "check_out": hotel.get("check_out_date", ""),
                    "nights": hotel.get("nights", ""),
                    "confirmation": hotel.get("confirmation_number", ""),
                    "room_type": hotel.get("room_type", ""),
                    "rate_per_night": hotel.get("rate_per_night", ""),
                    "currency": hotel.get("currency", ""),
                    "total_amount": hotel.get("total_amount", ""),
                    "amenities": hotel.get("amenities", []),  # Get actual amenities from data
                    "contact": hotel.get("phone", "")
                })
        return processed
    
    def _generate_daily_schedule(self, start_date: str, end_date: str, 
                                flights: List, hotels: List) -> List[Dict]:
        """Generate day-by-day schedule structure (details filled by enhanced guide service)"""
        schedule = []
        
        try:
            # Parse dates
            start = None
            end = None
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                try:
                    if start_date:
                        start = datetime.strptime(start_date, fmt)
                    if end_date:
                        end = datetime.strptime(end_date, fmt)
                    if start and end:
                        break
                except:
                    continue
            
            if not start or not end:
                # Return minimal structure if dates can't be parsed
                return [{"day": 1, "date": "", "error": "Date parsing failed"}]
            
            # Generate schedule structure for each day
            current = start
            day_num = 1
            
            while current <= end:
                day_schedule = {
                    "day": day_num,
                    "date": current.strftime("%Y-%m-%d"),
                    "day_name": current.strftime("%A"),
                    "is_arrival": day_num == 1,
                    "is_departure": current == end,
                    "flights": [],
                    "note": ""
                }
                
                # Add actual flight information for relevant days
                current_date_str = current.strftime("%Y-%m-%d")
                for flight in flights:
                    if flight.get("departure_date") == current_date_str:
                        day_schedule["flights"].append({
                            "type": "departure",
                            "flight": flight
                        })
                    if flight.get("arrival_date") == current_date_str:
                        day_schedule["flights"].append({
                            "type": "arrival",
                            "flight": flight
                        })
                
                schedule.append(day_schedule)
                current += timedelta(days=1)
                day_num += 1
                
        except Exception as e:
            print(f"Error generating schedule: {e}")
            # Return minimal structure
            schedule = [{"day": 1, "date": "", "error": str(e)}]
        
        return schedule
    
    def _get_currency(self, destination: str) -> str:
        """Get currency for destination"""
        if not destination:
            return "Local currency"
        
        destination_lower = destination.lower()
        
        currency_map = {
            "france": "Euro (EUR)",
            "paris": "Euro (EUR)",
            "london": "British Pound (GBP)",
            "uk": "British Pound (GBP)",
            "japan": "Japanese Yen (JPY)",
            "tokyo": "Japanese Yen (JPY)",
            "usa": "US Dollar (USD)",
            "new york": "US Dollar (USD)",
            "canada": "Canadian Dollar (CAD)",
            "australia": "Australian Dollar (AUD)",
            "mexico": "Mexican Peso (MXN)",
            "india": "Indian Rupee (INR)",
            "china": "Chinese Yuan (CNY)",
            "thailand": "Thai Baht (THB)",
            "singapore": "Singapore Dollar (SGD)"
        }
        
        for location, currency in currency_map.items():
            if location in destination_lower:
                return currency
        
        return "Local currency"
