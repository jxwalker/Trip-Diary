# src/formatters/summary_formatter.py
from typing import List
from datetime import datetime
from ..models.events import Flight, Hotel, Passenger
from .timeline_formatter import TimelineFormatter
import re
from collections import defaultdict

class SummaryFormatter:
    """Formats travel information into readable summaries."""
    
    @staticmethod
    def format_summary(flights: List[Flight], hotels: List[Hotel], passengers: List[Passenger]) -> str:
        """Format the complete itinerary summary."""
        summary = []
        
        # Deduplicate passengers using a dictionary
        unique_passengers = {
            f"{p.title}_{p.first_name}_{p.last_name}": p 
            for p in passengers
        }.values()
        
        # Add passenger information
        if unique_passengers:
            summary.append("Passengers:")
            for passenger in sorted(unique_passengers, key=lambda p: (p.last_name, p.first_name)):
                summary.append(f"  {passenger.title} {passenger.first_name} {passenger.last_name}")
                if passenger.frequent_flyer:
                    summary.append(f"    Frequent Flyer: {passenger.frequent_flyer}")
            summary.append("")
        
        # Add timeline
        summary.append("Timeline:")
        summary.append(TimelineFormatter.format_timeline(flights, hotels))
        summary.append("")
        
        # Add detailed itinerary section
        summary.append("Detailed Itinerary:")
        summary.append("")
        
        # Add date range if we have events
        all_dates = []
        if flights:
            all_dates.extend([datetime.strptime(f.departure.date, '%Y-%m-%d') for f in flights])
            all_dates.extend([datetime.strptime(f.arrival.date, '%Y-%m-%d') for f in flights])
        if hotels:
            all_dates.extend([datetime.strptime(h.check_in_date, '%Y-%m-%d') for h in hotels])
            all_dates.extend([datetime.strptime(h.check_out_date, '%Y-%m-%d') for h in hotels])
            
        if all_dates:
            summary.append(f"Date Range: {min(all_dates).strftime('%Y-%m-%d')} to {max(all_dates).strftime('%Y-%m-%d')}")
            summary.append("")
        
        # Add flights
        if flights:
            summary.append("Flights:")
            sorted_flights = sorted(flights, key=lambda f: (f.departure.date, f.departure.time))
            for flight in sorted_flights:
                summary.append(SummaryFormatter.format_flight_details(flight))
            summary.append("")
        
        # Add hotels
        if hotels:
            summary.append("Hotels:")
            sorted_hotels = sorted(hotels, key=lambda h: h.check_in_date)
            for hotel in sorted_hotels:
                summary.append(SummaryFormatter.format_hotel_details(hotel))
                summary.append("")
        
        return "\n".join(summary)

    @staticmethod
    def format_passenger_details(passenger: Passenger) -> str:
        """Format passenger details."""
        details = [f"  {passenger.title} {passenger.first_name} {passenger.last_name}"]
        if passenger.frequent_flyer:
            details.append(f"    Frequent Flyer: {passenger.frequent_flyer}")
        return "\n".join(details)

    @staticmethod
    def format_flight_details(flight: Flight) -> str:
        """Format flight details."""
        # Use TimelineFormatter for consistent location formatting
        dep_location = TimelineFormatter.format_location(flight.departure.location, flight.departure.terminal)
        arr_location = TimelineFormatter.format_location(flight.arrival.location, flight.arrival.terminal)
        
        details = [
            f"  {flight.flight_number} ({flight.operator})",
            f"  {dep_location} → {arr_location}",
            f"  Departure: {flight.departure.date} {flight.departure.time}",
            f"  Arrival: {flight.arrival.date} {flight.arrival.time}",
            f"  Class: {flight.travel_class}"
        ]
        
        if flight.baggage_allowance:
            baggage = []
            if flight.baggage_allowance.checked_baggage:
                baggage.append(f"Baggage: {flight.baggage_allowance.checked_baggage}")
            if flight.baggage_allowance.hand_baggage:
                baggage.append(f"Hand: {flight.baggage_allowance.hand_baggage}")
            if baggage:
                details.append("  " + ", ".join(baggage))
        
        # Add passengers for this flight
        if flight.passengers:
            details.append("  Passengers:")
            for passenger in sorted(flight.passengers, key=lambda p: (p.last_name, p.first_name)):
                details.append(f"    {passenger.title} {passenger.first_name} {passenger.last_name}")
        
        return "\n".join(details)

    @staticmethod
    def format_hotel_details(hotel: Hotel) -> str:
        """Format hotel details including numbered rooms."""
        lines = []
        lines.append(f"\n{hotel.name} [{hotel.city}] [Booking: {hotel.booking_reference}]")
        lines.append(f"{hotel.check_in_date} to {hotel.check_out_date}\n")

        # Format each room with a room number
        for i, room in enumerate(hotel.rooms, 1):
            lines.append(f"Room {i}:")
            lines.append(f"  {room.room_type}")
            if room.bed_type:
                lines.append(f"  Bed Configuration: {room.bed_type}")
            if room.size:
                lines.append(f"  Size: {room.size}")
            
            if room.features:
                lines.append("  Room Features:")
                for feature in sorted(room.features):
                    lines.append(f"    • {feature}")
            
            if room.meal_plan:
                lines.append(f"  Meal Plan: {room.meal_plan}")
            if room.occupancy:
                lines.append(f"  Occupancy: {room.occupancy}")
            lines.append("")  # Add blank line between rooms

        return "\n".join(lines)