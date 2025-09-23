# src/formatters/timeline_formatter.py
from typing import List
from datetime import datetime, timedelta
from ..models.events import TravelEvent, Flight, Hotel
from ..processors.time_processor import calculate_checkin_time
import logging

logger = logging.getLogger(__name__)

class TimelineFormatter:
    """Formats travel events into a chronological timeline."""
    
    @staticmethod
    def calculate_checkin_time(flight: Flight) -> str:
        """Calculate check-in time for a flight (2 hours before departure)."""
        try:
            departure_time = datetime.strptime(flight.departure.time, '%H:%M')
            checkin_time = departure_time - timedelta(hours=2)
            return checkin_time.strftime('%H:%M')
        except Exception as e:
            logger.error(
                f"Could not calculate check-in time from "
                f"{flight.departure.time}: {str(e)}"
            )
            return "00:00"  # Default time if calculation fails
    
    @staticmethod
    def format_location(location: str, terminal: str | None) -> str:
        """Format location and terminal consistently."""
        if not terminal:
            return location
        # Remove any existing "Terminal" text to avoid duplication
        location = location.replace(" Terminal", "")
        terminal = terminal.replace("Terminal ", "")
        return f"{location} Terminal {terminal}"
    
    @classmethod
    def create_flight_events(cls, flight: Flight) -> List[TravelEvent]:
        """Create check-in, departure and arrival events for a flight."""
        events = []
        try:
            # Format location names consistently
            # Remove anything in parentheses
            dep_loc = flight.departure.location.split(' (')[0]
            arr_loc = flight.arrival.location.split(' (')[0]

            # Create events
            events.extend([
                TravelEvent(
                    event_type='flight_checkin',
                    start_date=(
                        f"{flight.departure.date} "
                        f"{cls.calculate_checkin_time(flight)}"
                    ),
                    description=(
                        f"Check in for flight {flight.flight_number} at {dep_loc}"
                    )
                ),
                TravelEvent(
                    event_type='flight_departure',
                    start_date=f"{flight.departure.date} {flight.departure.time}",
                    description=(
                        f"Flight {flight.flight_number} departs {dep_loc} → {arr_loc}"
                    )
                ),
                TravelEvent(
                    event_type='flight_arrival',
                    start_date=f"{flight.arrival.date} {flight.arrival.time}",
                    description=(
                        f"Flight {flight.flight_number} arrives at {arr_loc}"
                    )
                )
            ])
        except Exception as e:
            logger.error(f"Error creating flight events: {str(e)}")
        return events
    
    @classmethod
    def create_hotel_events(cls, hotel: Hotel) -> List[TravelEvent]:
        """Create check-in and check-out events for a hotel."""
        # Standardize hotel name by removing city suffix
        hotel_name = hotel.name.split(',')[0].strip()
        
        return [
            TravelEvent(
                event_type='hotel_checkin',
                start_date=f"{hotel.check_in_date} 15:00",  # Standard check-in
                description=f"Check in at {hotel_name}, {hotel.city}"
            ),
            TravelEvent(
                event_type='hotel_checkout',
                start_date=f"{hotel.check_out_date} 11:00",  # Standard check-out
                description=f"Check out from {hotel_name}, {hotel.city}"
            )
        ]
    
    @classmethod
    def format_timeline(
        cls, flights: List[Flight], hotels: List[Hotel]
    ) -> str:
        """Create a chronological timeline of all travel events."""
        events = []
        
        try:
            # Add flight events
            for flight in flights:
                events.extend(cls.create_flight_events(flight))
            
            # Add hotel events
            for hotel in hotels:
                events.extend(cls.create_hotel_events(hotel))
            
            # Sort events chronologically
            events.sort()
            
            # Format the timeline
            timeline = ["Chronological Timeline:"]
            current_date = None
            
            for event in events:
                # Split start_date into date and time components
                date_str, time_str = event.start_date.split(" ", 1)
                
                if date_str != current_date:
                    current_date = date_str
                    timeline.append(f"\n  {current_date}:")
                
                timeline.append(f"    {time_str} - {event.description}")
            
            return "\n".join(timeline)
            
        except Exception as e:
            logger.error(f"Error formatting timeline: {str(e)}")
            return "Error creating timeline"
