from typing import List
from src.models.events import Flight, Hotel
from src.formatters.timeline_formatter import TimelineFormatter
from src.utils.timer import Timer

class SummaryFormatter:
    @staticmethod
    def format_summary(flights: List[Flight], hotels: List[Hotel]) -> str:
        with Timer.track("Summary Formatting"):
            timeline = TimelineFormatter.format_timeline(flights, hotels)
            details = SummaryFormatter.format_details(flights, hotels)
            
            # Add timing information at the end
            performance = Timer.format_timings()
            
            return f"{timeline}\n\n{details}\n\n{performance}"
    
    @staticmethod
    def format_details(flights: List[Flight], hotels: List[Hotel]) -> str:
        # Get trip duration from flights only
        flight_dates = []
        for flight in flights:
            flight_dates.extend([flight.departure_date, flight.arrival_date])
        
        start_date = min(flight_dates)
        end_date = max(flight_dates)
        
        details = [f"Detailed Information\n"]
        details.append(f"Trip Duration: {start_date} to {end_date}\n")
        
        # Add flight details
        if flights:
            details.append("Flight Details:")
            for flight in flights:
                details.append(SummaryFormatter.format_flight_details(flight))
        
        # Add hotel details
        if hotels:
            details.append("\nHotel Details:")
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
        # Clean up any double spaces and fix common typos
        room_details = (hotel.room_details
                       .replace("  ", " ")  # Remove double spaces
                       .replace("interne t", "internet")
                       .replace("inter net", "internet")
                       .replace("sitt ing", "sitting")
                       .replace("Cof fee", "Coffee")
                       .replace("sqm /", "sqm/")
                       .replace("sq ft", "sqft")
                       .replace("com plimentary", "complimentary"))
        
        details = [
            f"  {hotel.name} [Booking: {hotel.booking_reference}]",
            f"  {hotel.city}: {hotel.check_in_date} to {hotel.check_out_date}",
            f"  Room: {room_details}"
        ]
        return "\n".join(details)