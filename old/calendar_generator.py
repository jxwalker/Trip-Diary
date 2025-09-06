from icalendar import Calendar, Event
from datetime import datetime, timedelta
import googlemaps
from typing import Dict, Any, Optional
import os

class CalendarGenerationError(Exception):
    """Custom exception for calendar generation errors"""
    pass

def generate_calendar_events(
    itinerary_data: Dict[str, Any],
    user_address: Optional[str],
    default_airport: str
) -> None:
    """
    Generate calendar events from itinerary data.
    
    Args:
        itinerary_data (Dict[str, Any]): Processed itinerary data
        user_address (Optional[str]): User's home address for travel time calculation
        default_airport (str): Default departure airport code
    """
    try:
        # Initialize calendar
        cal = Calendar()
        cal.add('prodid', '-//British Airways Itinerary Decoder//EN')
        cal.add('version', '2.0')
        
        # Add flight events
        for flight in itinerary_data['flights']:
            add_flight_events(
                cal,
                flight,
                itinerary_data['booking_reference'],
                user_address,
                default_airport
            )
        
        # Add hotel events
        if 'hotels' in itinerary_data:
            for hotel in itinerary_data['hotels']:
                add_hotel_events(cal, hotel, itinerary_data['booking_reference'])
        
        # Write to file
        with open('calendar_events.ics', 'wb') as f:
            f.write(cal.to_ical())
            
    except Exception as e:
        raise CalendarGenerationError(f"Failed to generate calendar events: {str(e)}")

def add_flight_events(
    cal: Calendar,
    flight: Dict[str, Any],
    booking_ref: str,
    user_address: Optional[str],
    default_airport: str
) -> None:
    """
    Add flight-related events to the calendar.
    
    Args:
        cal (Calendar): Calendar object to add events to
        flight (Dict[str, Any]): Flight information
        booking_ref (str): Booking reference
        user_address (Optional[str]): User's home address
        default_airport (str): Default departure airport code
    """
    # Calculate travel time to airport if address provided
    airport_travel_time = calculate_airport_travel_time(
        user_address,
        flight['departure']['airport'],
        default_airport
    ) if user_address else timedelta(hours=2)
    
    # Create airport transfer event
    if user_address:
        transfer_event = Event()
        transfer_event.add('summary', f"Travel to {flight['departure']['airport']}")
        departure_time = datetime.fromisoformat(flight['departure']['time'])
        transfer_event.add('dtstart', departure_time - airport_travel_time)
        transfer_event.add('dtend', departure_time - timedelta(hours=2))
        transfer_event.add('location', user_address)
        cal.add_component(transfer_event)
    
    # Create flight event
    flight_event = Event()
    flight_event.add('summary', f"Flight {flight['flight_number']}")
    flight_event.add('dtstart', datetime.fromisoformat(flight['departure']['time']))
    flight_event.add('dtend', datetime.fromisoformat(flight['arrival']['time']))
    flight_event.add('location', f"{flight['departure']['airport']} Terminal {flight['departure'].get('terminal', 'N/A')}")
    flight_event.add('description', f"Booking reference: {booking_ref}\nFlight: {flight['flight_number']}")
    cal.add_component(flight_event)

def add_hotel_events(cal: Calendar, hotel: Dict[str, Any], booking_ref: str) -> None:
    """
    Add hotel-related events to the calendar.
    
    Args:
        cal (Calendar): Calendar object to add events to
        hotel (Dict[str, Any]): Hotel information
        booking_ref (str): Booking reference
    """
    hotel_event = Event()
    hotel_event.add('summary', f"Stay at {hotel['name']}")
    hotel_event.add('dtstart', datetime.fromisoformat(hotel['check_in']))
    hotel_event.add('dtend', datetime.fromisoformat(hotel['check_out']))
    hotel_event.add('location', hotel['address'])
    hotel_event.add('description', 
                   f"Booking reference: {booking_ref}\n"
                   f"Phone: {hotel.get('phone', 'N/A')}")
    cal.add_component(hotel_event)

def calculate_airport_travel_time(
    origin: str,
    destination_airport: str,
    default_airport: str
) -> timedelta:
    """
    Calculate travel time to airport using Google Maps API.
    
    Args:
        origin (str): Starting address
        destination_airport (str): Destination airport code
        default_airport (str): Default airport code
        
    Returns:
        timedelta: Estimated travel time
    """
    try:
        gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
        
        # Convert airport code to full address
        airport_address = f"{destination_airport} Airport"
        if destination_airport == default_airport:
            airport_address = "Heathrow Airport"  # Special case for default airport
            
        # Get directions
        directions = gmaps.directions(
            origin,
            airport_address,
            mode="driving",
            departure_time=datetime.now()
        )
        
        if not directions:
            return timedelta(hours=2)  # Default fallback
            
        # Extract duration in seconds and convert to timedelta
        duration_seconds = directions[0]['legs'][0]['duration']['value']
        return timedelta(seconds=duration_seconds)
        
    except Exception as e:
        print(f"Warning: Failed to calculate travel time: {str(e)}")
        return timedelta(hours=2)  # Default fallback