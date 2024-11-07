from typing import List
from src.models.events import Flight, Hotel, Passenger
from src.formatters.timeline_formatter import TimelineFormatter
from src.utils.timer import Timer
from datetime import datetime, timedelta

class SummaryFormatter:
    @staticmethod
    def format_summary(flights: List[Flight], hotels: List[Hotel], passengers: List[Passenger]) -> str:
        """Format the complete itinerary summary."""
        summary = []
        
        # Deduplicate passengers
        unique_passengers = list(set(passengers))
        unique_passengers.sort(key=lambda p: (p.last_name.lower(), p.first_name.lower()))
        
        # Add passenger information
        if unique_passengers:
            summary.append("Passengers:")
            for passenger in unique_passengers:
                summary.append(SummaryFormatter.format_passenger_details(passenger))
            summary.append("")
        
        # Add timeline
        summary.append("Timeline:")
        summary.append(SummaryFormatter.format_timeline(flights, hotels))
        summary.append("")
        
        # Add detailed itinerary
        summary.append("Detailed Itinerary:")
        summary.append("")
        
        # Add date range
        if flights:
            first_date = min(datetime.strptime(f.departure_date, '%Y-%m-%d') for f in flights)
            last_date = max(datetime.strptime(f.arrival_date, '%Y-%m-%d') for f in flights)
            summary.append(f"Date Range: {first_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')}")
            summary.append("")
        
        # Add flights
        if flights:
            summary.append("Flights:")
            for flight in flights:
                summary.append(SummaryFormatter.format_flight_details(flight))
            summary.append("")
        
        # Add hotels (deduplicated by room type)
        if hotels:
            summary.append("Hotels:")
            seen_rooms = set()
            for hotel in hotels:
                room_key = f"{hotel.name}_{hotel.room_type}"
                if room_key not in seen_rooms:
                    summary.append(SummaryFormatter.format_hotel_details(hotel))
                    summary.append("")  # Add blank line between hotels
                    seen_rooms.add(room_key)
        
        return "\n".join(summary)

    @staticmethod
    def format_timeline(flights: List[Flight], hotels: List[Hotel]) -> str:
        """Format a chronological timeline of events."""
        events = []
        seen_hotel_events = set()  # Track unique hotel events
        
        # Add flight events
        for flight in flights:
            events.append({
                'date': datetime.strptime(flight.departure_date, '%Y-%m-%d'),
                'time': flight.departure_time,
                'type': 'DEPARTURE',
                'details': f"Flight {flight.flight_number} from {flight.departure_location}"
            })
            events.append({
                'date': datetime.strptime(flight.arrival_date, '%Y-%m-%d'),
                'time': flight.arrival_time,
                'type': 'ARRIVAL',
                'details': f"Flight {flight.flight_number} to {flight.arrival_location}"
            })
        
        # Add hotel events (deduplicated)
        for hotel in hotels:
            # Create unique identifiers for check-in/out events
            checkin_key = f"{hotel.name}_{hotel.check_in_date}_IN"
            checkout_key = f"{hotel.name}_{hotel.check_out_date}_OUT"
            
            # Only add check-in if we haven't seen it
            if checkin_key not in seen_hotel_events:
                events.append({
                    'date': datetime.strptime(hotel.check_in_date, '%Y-%m-%d'),
                    'time': '12:00',  # Default check-in time
                    'type': 'CHECK-IN',
                    'details': f"Check in at {hotel.name}, {hotel.city}"
                })
                seen_hotel_events.add(checkin_key)
            
            # Only add check-out if we haven't seen it
            if checkout_key not in seen_hotel_events:
                events.append({
                    'date': datetime.strptime(hotel.check_out_date, '%Y-%m-%d'),
                    'time': '11:00',  # Default check-out time
                    'type': 'CHECK-OUT',
                    'details': f"Check out from {hotel.name}, {hotel.city}"
                })
                seen_hotel_events.add(checkout_key)
        
        # Sort events chronologically
        events.sort(key=lambda x: (x['date'], x['time']))
        
        # Format timeline
        timeline = []
        current_date = None
        
        for event in events:
            if current_date != event['date'].date():
                current_date = event['date'].date()
                timeline.append(f"\n  {current_date.strftime('%Y-%m-%d')}:")
            
            timeline.append(f"    {event['time']} - {event['type']}: {event['details']}")
        
        return "\n".join(timeline)

    @staticmethod
    def format_passenger_details(passenger: Passenger) -> str:
        """Format passenger details."""
        details = [f"  {passenger.full_name}"]
        if passenger.frequent_flyer:
            details.append(f"    Frequent Flyer: {passenger.frequent_flyer}")
        return "\n".join(details)

    @staticmethod
    def format_details(flights: List[Flight], hotels: List[Hotel]) -> str:
        """Format the detailed itinerary section."""
        details = []
        
        # Handle empty flights list
        if not flights:
            details.append("No flights found in itinerary.")
            flight_dates = []
        else:
            flight_dates = [
                datetime.strptime(flight.departure_date, '%Y-%m-%d')
                for flight in flights
            ]
        
        # Handle empty hotels list
        if not hotels:
            details.append("No hotels found in itinerary.")
            hotel_dates = []
        else:
            hotel_dates = [
                datetime.strptime(hotel.check_in_date, '%Y-%m-%d')
                for hotel in hotels
            ]
        
        # Get date range if any dates exist
        all_dates = flight_dates + hotel_dates
        if all_dates:
            start_date = min(all_dates)
            end_date = max(all_dates)
            details.append(f"\nDate Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        else:
            details.append("\nNo dates found in itinerary.")
        
        if flights:
            details.append("\nFlights:")
            for flight in flights:
                details.append(SummaryFormatter.format_flight_details(flight))
        
        if hotels:
            details.append("\nHotels:")
            for hotel in hotels:
                details.append(SummaryFormatter.format_hotel_details(hotel))
        
        return "\n".join(details)

    @staticmethod
    def format_flight_details(flight: Flight) -> str:
        details = [
            f"  {flight.flight_number} ({flight.operator})",
            f"  {flight.departure_location} Terminal {flight.departure_terminal or 'N/A'} → {flight.arrival_location} Terminal {flight.arrival_terminal or 'N/A'}",
            f"  Departure: {flight.departure_date} {flight.departure_time}",
            f"  Arrival: {flight.arrival_date} {flight.arrival_time}",
            f"  Class: {flight.travel_class}",
            f"  Baggage: {flight.checked_baggage}, Hand: {flight.hand_baggage or 'N/A'}"
        ]
        return "\n".join(details)

    @staticmethod
    def format_hotel_details(hotel: Hotel) -> str:
        """Format hotel details in a cleaner way."""
        # Clean up the room features
        features = hotel.room_features.replace(',', ', ')  # Add spaces after commas
        features = ' '.join(features.split())  # Remove extra whitespace
        
        # Split amenities into bullet points
        amenities = [a.strip() for a in features.split('-') if a.strip()]
        
        details = [
            f"  {hotel.name} [Booking: {hotel.booking_reference or 'None'}]",
            f"  {hotel.city}: {hotel.check_in_date} to {hotel.check_out_date}",
            f"  Room Type: {hotel.room_type}",
            "  Room Features:"
        ]
        
        # Add amenities as bullet points
        for amenity in amenities:
            details.append(f"    • {amenity}")
        
        return "\n".join(details)