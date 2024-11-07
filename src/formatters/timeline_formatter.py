from typing import List, Tuple
from datetime import datetime
from ..models.events import TravelEvent, Flight, Hotel
from ..processors.time_processor import calculate_checkin_time

class TimelineFormatter:
    """Formats travel events into a chronological timeline."""
    
    @classmethod
    def create_flight_events(cls, flight: Flight) -> List[TravelEvent]:
        """Create check-in, departure, and arrival events for a flight."""
        events = []
        
        # Calculate check-in time
        checkin_date, checkin_time = calculate_checkin_time(
            flight.departure_date, 
            flight.departure_time
        )
        
        # Add check-in event
        events.append(TravelEvent(
            date=checkin_date,
            time=checkin_time,
            type='flight_checkin',
            description=f"Check in for flight {flight.flight_number} at {flight.departure_location}"
        ))
        
        # Add departure event
        events.append(TravelEvent(
            date=flight.departure_date,
            time=flight.departure_time,
            type='flight_departure',
            description=f"Flight {flight.flight_number} departs {flight.departure_location} → {flight.arrival_location}"
        ))
        
        # Add arrival event
        events.append(TravelEvent(
            date=flight.arrival_date,
            time=flight.arrival_time,
            type='flight_arrival',
            description=f"Flight {flight.flight_number} arrives at {flight.arrival_location}"
        ))
        
        return events
    
    @classmethod
    def create_hotel_events(cls, hotel: Hotel) -> List[TravelEvent]:
        """Create check-in and check-out events for a hotel."""
        return [
            TravelEvent(
                date=hotel.check_in_date,
                time='15:00',
                type='hotel_checkin',
                description=f"Check in to {hotel.name}, {hotel.city}"
            ),
            TravelEvent(
                date=hotel.check_out_date,
                time='12:00',
                type='hotel_checkout',
                description=f"Check out from {hotel.name}, {hotel.city}"
            )
        ]
    
    @classmethod
    def check_transfer_times(cls, events: List[TravelEvent]) -> List[str]:
        """Check for short or impossible transfer times between flights."""
        warnings = []
        last_arrival = None
        min_transfer_time = 90  # minutes for international transfers
        
        for i, event in enumerate(events):
            if event.type == 'flight_arrival':
                last_arrival = event
                # Look ahead for next check-in and departure
                for next_event in events[i+1:]:
                    if next_event.type == 'flight_checkin':
                        checkin_dt = datetime.strptime(f"{next_event.date} {next_event.time}", "%Y-%m-%d %H:%M")
                        arrival_dt = datetime.strptime(f"{last_arrival.date} {last_arrival.time}", "%Y-%m-%d %H:%M")
                        if checkin_dt < arrival_dt:
                            warnings.append("⚠️  Warning: Check-in for next flight is before previous flight lands")
                            
                    elif next_event.type == 'flight_departure' and last_arrival:
                        departure_dt = datetime.strptime(f"{next_event.date} {next_event.time}", "%Y-%m-%d %H:%M")
                        arrival_dt = datetime.strptime(f"{last_arrival.date} {last_arrival.time}", "%Y-%m-%d %H:%M")
                        
                        time_diff = (departure_dt - arrival_dt).total_seconds() / 60
                        if time_diff < min_transfer_time:
                            location = last_arrival.description.split("arrives at ")[1]
                            warnings.append(f"⚠️  Warning: Only {int(time_diff)} minutes for transfer at {location}")
                        break  # Only check the next departure
        
        return warnings
    
    @classmethod
    def format_timeline(cls, flights: List[Flight], hotels: List[Hotel]) -> str:
        """Create a chronological timeline of all travel events."""
        events = []
        
        # Add flight events
        for flight in flights:
            events.extend(cls.create_flight_events(flight))
        
        # Add hotel events (deduplicated)
        seen_hotels = set()
        for hotel in hotels:
            hotel_key = (hotel.name, hotel.check_in_date, hotel.check_out_date)
            if hotel_key not in seen_hotels:
                events.extend(cls.create_hotel_events(hotel))
                seen_hotels.add(hotel_key)
        
        # Sort events chronologically
        events.sort()
        
        # Check for transfer time issues
        warnings = cls.check_transfer_times(events)
        
        # Format the timeline with warnings at the top
        timeline = []
        if warnings:
            timeline.extend(warnings)
            timeline.append("")  # Add spacing after warnings
        
        timeline.append("Chronological Timeline:")
        for event in events:
            timeline.append(f"- {event.date} {event.time}: {event.description}")
        
        return "\n".join(timeline)