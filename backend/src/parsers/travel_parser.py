# src/parsers/travel_parser.py
from typing import Dict, Optional, Any, Tuple, Set
from src.models.events import (
    Flight, Hotel, Passenger, Location, BaggageAllowance
)
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class TravelDataParser:
    """Parser for travel-related data."""
    
    @staticmethod
    def parse_flight(flight_data: Dict) -> Optional[Flight]:
        """Parse flight data into Flight object."""
        try:
            # Clean flight data
            flight_data = flight_data.copy()
            
            # Ensure required nested structures exist
            if 'departure' not in flight_data or 'arrival' not in flight_data:
                logger.error("Missing departure or arrival data")
                return None

            # Parse baggage allowance if present
            if 'baggage_allowance' in flight_data:
                flight_data['baggage_allowance'] = BaggageAllowance(
                    **flight_data['baggage_allowance']
                )

            # Create Flight object
            return Flight(**flight_data)
        except Exception as e:
            logger.error(f"Error parsing flight: {str(e)}")
            return None

    @staticmethod
    def parse_passenger(passenger_data: Dict) -> Optional[Passenger]:
        """Parse passenger data into Passenger object."""
        try:
            # If already a Passenger object, return as-is
            if isinstance(passenger_data, Passenger):
                return passenger_data
            
            # Clean up names
            title = passenger_data.get('title', '').upper().strip()
            first_name = passenger_data.get('first_name', '').strip()
            last_name = passenger_data.get('last_name', '').upper().strip()
            
            return Passenger(
                title=title,
                first_name=first_name,
                last_name=last_name,
                frequent_flyer=passenger_data.get('frequent_flyer')
            )
                
        except Exception as e:
            logger.error(f"Error parsing passenger data: {str(e)}")
            return None

    @staticmethod
    def parse_hotel(hotel_data: Dict) -> Optional[Hotel]:
        """Parse hotel data into Hotel object."""
        try:
            # Skip invalid hotels
            if hotel_data.get('name') in ['Not provided', None, ''] or \
               hotel_data.get('city') in ['Not provided', None, '']:
                return None

            # Use the Hotel.parse() method
            return Hotel.parse(hotel_data)
        except Exception as e:
            logger.error(f"Error parsing hotel: {str(e)}")
            return None

    @classmethod
    def parse_itinerary(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse itinerary data into structured format."""
        result = {
            'flights': [],
            'hotels': [],
            'passengers': [],
            'errors': []
        }
        
        try:
            # Process flights with deduplication
            seen_flights = set()
            for flight_data in data.get('flights', []):
                flight = cls.parse_flight(flight_data)
                if flight and flight not in seen_flights:
                    result['flights'].append(flight)
                    seen_flights.add(flight)

            # Process hotels with deduplication
            seen_hotels = set()
            for hotel_data in data.get('hotels', []):
                hotel = cls.parse_hotel(hotel_data)
                if hotel and hotel not in seen_hotels:
                    result['hotels'].append(hotel)
                    seen_hotels.add(hotel)

            # Process passengers with improved deduplication
            seen_passengers = {}
            for passenger_data in data.get('passengers', []):
                passenger = cls.parse_passenger(passenger_data)
                if passenger:
                    # Create deduplication key using normalized names
                    # Use the first part of first name and full last name
                    # for matching
                    first_name_parts = passenger.first_name.split()
                    first_name_key = (
                        first_name_parts[0].upper() 
                        if first_name_parts else ""
                    )
                    dedup_key = (
                        passenger.title.upper(), 
                        first_name_key, 
                        passenger.last_name.upper()
                    )
                    
                    # If we already have this passenger, keep the version
                    # with the longer first name
                    if dedup_key in seen_passengers:
                        existing = seen_passengers[dedup_key]
                        if (len(passenger.first_name) > 
                            len(existing.first_name)):
                            seen_passengers[dedup_key] = passenger
                    else:
                        seen_passengers[dedup_key] = passenger

            # Sort passengers by last name, first name
            result['passengers'] = sorted(
                seen_passengers.values(),
                key=lambda x: (x.last_name.upper(), x.first_name.upper())
            )

            if not any([
                result['flights'], result['hotels'], result['passengers']
            ]):
                result['errors'].append("No valid data found in itinerary")

        except Exception as e:
            result['errors'].append(f"Error parsing itinerary: {str(e)}")
            logger.error(f"Error parsing itinerary: {str(e)}", exc_info=True)

        return result

    @staticmethod
    def validate_itinerary(itinerary: Dict) -> Dict[str, Any]:
        """Validate parsed itinerary data."""
        errors = []
        
        # Check for required data
        if not itinerary.get('passengers'):
            errors.append("No valid passenger information found")
        
        if not itinerary.get('flights') and not itinerary.get('hotels'):
            errors.append("No valid flight or hotel information found")
            
        # Return validation results
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
