import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
from src.processors.pdf_processor import PDFProcessor
from src.models.events import Flight, Hotel, Passenger
from src.formatters.summary_formatter import SummaryFormatter
from src.gpt_providers.gpt_selector import GPTSelector
from src.utils.timer import Timer
import time

def parse_flight(flight_data: Dict) -> Flight:
    """Parse flight data into Flight object."""
    departure = flight_data['departure']
    arrival = flight_data['arrival']
    baggage = flight_data.get('baggage_allowance', {})
    
    return Flight(
        flight_number=flight_data['flight_number'],
        operator=flight_data['operator'],
        booking_reference=flight_data.get('booking_reference', 'N/A'),
        departure_location=departure['location'],
        departure_terminal=departure.get('terminal'),
        departure_date=departure['date'],
        departure_time=departure['time'],
        departure_city=departure.get('city'),
        arrival_location=arrival['location'],
        arrival_terminal=arrival.get('terminal'),
        arrival_date=arrival['date'],
        arrival_time=arrival['time'],
        arrival_city=arrival.get('city'),
        travel_class=flight_data.get('class', 'Economy'),
        checked_baggage=baggage.get('checked_baggage'),
        hand_baggage=baggage.get('hand_baggage')
    )

def parse_hotel(hotel_data: Dict) -> Hotel:
    """Parse hotel data into Hotel object."""
    try:
        return Hotel(
            name=hotel_data['name'],
            city=hotel_data['city'],
            check_in_date=hotel_data['check_in_date'],
            check_out_date=hotel_data['check_out_date'],
            room_type=hotel_data['room_type'],
            room_features=hotel_data.get('room_features', ''),
            booking_reference=hotel_data.get('booking_reference')
        )
    except Exception as e:
        print(f"Error parsing hotel: {str(e)}")
        print(f"Hotel data: {hotel_data}")
        return None

def parse_passenger(passenger_data: Dict) -> Passenger:
    """Parse passenger data into Passenger object."""
    return Passenger(
        title=passenger_data['title'],
        first_name=passenger_data['first_name'],
        last_name=passenger_data['last_name'],
        frequent_flyer=passenger_data.get('frequent_flyer')
    )

def main():
    print("Starting Trip Diary Processing...\n")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Consolidate multiple travel itineraries')
    parser.add_argument('--input', required=True, nargs='+', help='Paths to PDF files')
    parser.add_argument('--output', help='Path to save consolidated JSON output')
    parser.add_argument('--gpt-provider', default='openai', 
                      choices=['openai', 'claude', 'xai', 'sambanova'],
                      help='Choose GPT provider for text generation')
    args = parser.parse_args()
    
    try:
        start_time = time.perf_counter()
        
        # Create GPT provider
        gpt_selector = GPTSelector()
        gpt_provider = gpt_selector.get_provider(args.gpt_provider)
        
        # Process PDFs
        itineraries, errors, processing_time = PDFProcessor.process_files(args.input, gpt_provider)
        
        if errors:
            print("\nErrors encountered:")
            for error in errors:
                print(f"- {error}")
            if not itineraries:
                return
        
        if not itineraries:
            print("\nNo valid itineraries found!")
            return
        
        # Parse data
        flights = []
        hotels = []
        passengers = []
        
        # Process each itinerary
        for itinerary in itineraries:
            # Add passengers
            for passenger in itinerary.get('passengers', []):
                try:
                    passengers.append(parse_passenger(passenger))
                except Exception as e:
                    print(f"Error parsing passenger: {e}")
            
            # Add flights
            for flight in itinerary.get('flights', []):
                try:
                    flight['booking_reference'] = itinerary.get('booking_reference', 'N/A')
                    flights.append(parse_flight(flight))
                except Exception as e:
                    print(f"Error parsing flight: {e}")
            
            # Add hotels
            for hotel in itinerary.get('hotels', []):
                try:
                    hotels.append(parse_hotel(hotel))
                except Exception as e:
                    print(f"Error parsing hotel: {e}")
        
        # Sort chronologically
        flights.sort(key=lambda x: (x.departure_date, x.departure_time))
        hotels.sort(key=lambda x: x.check_in_date)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        print("\nConsolidated Itinerary Summary:\n")
        print(SummaryFormatter.format_summary(flights, hotels, passengers))
        
        print("\nProcessing Summary:")
        print(f"PDF Processing Time: {processing_time:.2f} seconds")
        print(f"Total Execution Time: {total_time:.2f} seconds")
        print(f"Files Processed: {len(args.input)}")
        print(f"Flights Found: {len(flights)}")
        print(f"Hotels Found: {len(hotels)}")
        print(f"Passengers Found: {len(passengers)}")
        
        if errors:
            print(f"Errors Encountered: {len(errors)}")
            
    except Exception as e:
        print(f"\nFatal error: {type(e).__name__}: {str(e)}")
        raise

if __name__ == "__main__":
    main()