import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
from src.processors.pdf_processor import PDFProcessor
from src.models.events import Flight, Hotel
from src.formatters.summary_formatter import SummaryFormatter
from src.gpt_providers.gpt_selector import GPTSelector
from src.utils.timer import Timer

def parse_flight(flight_data: Dict[str, Any]) -> Flight:
    """Convert raw flight data to Flight object."""
    return Flight(
        flight_number=flight_data['flight_number'],
        operator=flight_data['operator'],
        booking_reference=flight_data.get('booking_reference', 'N/A'),
        departure_location=flight_data['departure']['location'],
        departure_terminal=flight_data['departure'].get('terminal'),
        departure_date=flight_data['departure']['date'],
        departure_time=flight_data['departure']['time'],
        arrival_location=flight_data['arrival']['location'],
        arrival_terminal=flight_data['arrival'].get('terminal'),
        arrival_date=flight_data['arrival']['date'],
        arrival_time=flight_data['arrival']['time'],
        travel_class=flight_data['class'],
        checked_baggage=flight_data.get('baggage_allowance', {}).get('checked_baggage', ''),
        hand_baggage=flight_data.get('baggage_allowance', {}).get('hand_baggage', '')
    )

def parse_hotel(hotel_data: Dict[str, Any]) -> Hotel:
    """Convert raw hotel data to Hotel object."""
    return Hotel(
        name=hotel_data['name'],
        city=hotel_data['city'],
        booking_reference=hotel_data.get('booking_reference', 'N/A'),
        check_in_date=hotel_data['check_in'],
        check_out_date=hotel_data['check_out'],
        room_details=hotel_data['room_details']
    )

def main():
    with Timer.track("Total Execution"):
        with Timer.track("Argument Parsing"):
            parser = argparse.ArgumentParser(description='Consolidate multiple travel itineraries')
            parser.add_argument('--input', required=True, nargs='+', help='Paths to PDF files')
            parser.add_argument('--output', help='Path to save consolidated JSON output')
            parser.add_argument('--gpt-provider', default='openai', 
                              choices=['openai', 'claude', 'xai', 'sambanova'],
                              help='Choose GPT provider for text generation')
            args = parser.parse_args()
        
        try:
            with Timer.track("GPT Interface Creation"):
                gpt_selector = GPTSelector()
                gpt_provider = gpt_selector.get_provider(args.gpt_provider)
            
            with Timer.track("PDF Processing"):
                itineraries, errors = PDFProcessor.process_files(args.input, gpt_provider)
            
            if errors:
                print("\nErrors encountered:")
                for error in errors:
                    print(f"- {error}")
                if not itineraries:
                    return
            
            if not itineraries:
                print("\nNo valid itineraries found!")
                return
            
            with Timer.track("Data Parsing"):
                # Convert raw data to objects
                flights = []
                hotels = []
                
                # Process each itinerary
                for itinerary in itineraries:
                    # Add flights from this itinerary
                    for flight in itinerary.get('flights', []):
                        try:
                            flight['booking_reference'] = itinerary.get('booking_reference', 'N/A')
                            flights.append(parse_flight(flight))
                        except Exception as e:
                            print(f"Error parsing flight: {e}")
                    
                    # Add hotels from this itinerary
                    for hotel in itinerary.get('hotels', []):
                        try:
                            hotels.append(parse_hotel(hotel))
                        except Exception as e:
                            print(f"Error parsing hotel: {e}")
                
                # Sort chronologically
                flights.sort(key=lambda x: (x.departure_date, x.departure_time))
                hotels.sort(key=lambda x: x.check_in_date)
            
            with Timer.track("Output Generation"):
                # Create consolidated output
                if args.output:
                    consolidated = {
                        "flights": [vars(f) for f in flights],
                        "hotels": [vars(h) for h in hotels]
                    }
                    try:
                        with open(args.output, 'w') as f:
                            json.dump(consolidated, f, indent=2)
                        print(f"\nSaved consolidated JSON to: {args.output}")
                    except Exception as e:
                        print(f"\nError saving JSON output: {str(e)}")
                
                # Print human-readable summary
                print("\nConsolidated Itinerary Summary:")
                print(SummaryFormatter.format_summary(flights, hotels))
            
        except Exception as e:
            print(f"\nFatal error: {type(e).__name__}: {str(e)}")
            raise

if __name__ == "__main__":
    main()