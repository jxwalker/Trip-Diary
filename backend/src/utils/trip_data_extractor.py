"""
Trip Data Extractor
Intelligently extracts trip information from incomplete data
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def extract_trip_info(itinerary: Dict) -> Tuple[str, str, str]:
    """
    Extract destination, start_date, and end_date from potentially incomplete 
    trip data.
    Only the destination (city) is truly required.
    
    Args:
        itinerary: Trip itinerary data
        
    Returns:
        Tuple of (destination, start_date, end_date)
    """
    
    # Try to get from trip_details first
    trip_details = itinerary.get('trip_details', {})
    destination = trip_details.get('destination', '')
    start_date = trip_details.get('start_date', '')
    end_date = trip_details.get('end_date', '')
    
    # If no destination, try to infer from flights
    if not destination:
        flights = itinerary.get('flights', [])
        if flights:
            first_flight = flights[0]

            # Try arrival city from structured data
            if first_flight.get('arrival_city'):
                destination = first_flight['arrival_city']
                logger.info(
                    f"Got destination from arrival_city: {destination}"
                )
    
    # If still no destination, try hotels
    if not destination:
        hotels = itinerary.get('hotels', [])
        if hotels:
            first_hotel = hotels[0]

            # Use hotel city if available
            if first_hotel.get('city'):
                destination = first_hotel['city']
                logger.info(f"Got destination from hotel city: {destination}")
    
    # Extract dates if not provided
    if not start_date or not end_date:
        flights = itinerary.get('flights', [])
        
        # Get start date from first flight
        if flights and not start_date:
            first_flight = flights[0]
            if first_flight.get('departure_date'):
                start_date = first_flight['departure_date']
                logger.info(f"Using first flight date as start: {start_date}")
            elif first_flight.get('arrival_date'):
                start_date = first_flight['arrival_date']
                logger.info(
                    f"Using first flight arrival as start: {start_date}"
                )
        
        # Get end date from last flight
        if flights and not end_date:
            last_flight = flights[-1]
            if last_flight.get('departure_date'):
                end_date = last_flight['departure_date']
                logger.info(f"Using last flight date as end: {end_date}")
        
        # Try hotel dates
        if not start_date or not end_date:
            hotels = itinerary.get('hotels', [])
            if hotels:
                first_hotel = hotels[0]
                if not start_date and first_hotel.get('check_in_date'):
                    start_date = first_hotel['check_in_date']
                    logger.info(f"Using hotel check-in as start: {start_date}")
                if not end_date and first_hotel.get('check_out_date'):
                    end_date = first_hotel['check_out_date']
                    logger.info(f"Using hotel check-out as end: {end_date}")
    
    # If we have flights but no clear dates, use the flight dates
    if not start_date and not end_date:
        flights = itinerary.get('flights', [])
        dates = []
        for flight in flights:
            if flight.get('departure_date'):
                dates.append(flight['departure_date'])
            if flight.get('arrival_date'):
                dates.append(flight['arrival_date'])
        
        if dates:
            dates.sort()
            start_date = dates[0]
            end_date = dates[-1]
            logger.info(f"Using flight date range: {start_date} to {end_date}")
    
    # Default dates if still missing (7-day trip starting tomorrow)
    if not start_date:
        tomorrow = (datetime.now() + timedelta(days=1))
        start_date = tomorrow.strftime('%Y-%m-%d')
        logger.info(f"Using default start date: {start_date}")
    
    if not end_date:
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = start + timedelta(days=7)
                end_date = end.strftime('%Y-%m-%d')
                logger.info(f"Using default 7-day duration, end: {end_date}")
            except:
                # Fallback to a week from tomorrow
                week_later = (datetime.now() + timedelta(days=8))
                end_date = week_later.strftime('%Y-%m-%d')
                logger.info(f"Using default end date: {end_date}")
    
    # Final validation
    if not destination:
        destination = "Unknown Destination"
        logger.warning("Could not determine destination from trip data")
    
    return destination, start_date, end_date


def extract_hotel_info(itinerary: Dict, destination: str) -> Dict:
    """
    Extract hotel information with smart defaults
    """
    # Try trip_details first
    trip_details = itinerary.get('trip_details', {})
    hotel_name = trip_details.get('hotel', '')

    if hotel_name:
        # Create hotel info from trip_details
        city = (destination.split(',')[0].strip() 
                if destination != "Unknown Destination" else "City")
        return {
            'name': hotel_name,
            'city': city,
            'address': f'{city}',  # Basic address
            'description': f'Your accommodation in {city}',
            'source': 'trip_details'
        }

    # Fallback to hotels array
    hotels = itinerary.get('hotels', [])

    if hotels:
        hotel = hotels[0]

        # Fill in missing city from destination
        if not hotel.get('city') and destination != "Unknown Destination":
            city = destination.split(',')[0].strip()
            hotel['city'] = city

        return hotel
    else:
        # Create default hotel info
        city = (destination.split(',')[0].strip() 
                if destination != "Unknown Destination" else "City")
        return {
            'name': f'Hotel in {city}',
            'city': city,
            'address': '',
            'description': f'Accommodation in {city}',
            'source': 'default'
        }
