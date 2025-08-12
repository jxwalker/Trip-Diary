import argparse
import time
from pathlib import Path
from typing import List, Dict
from src.processors.pdf_processor import PDFProcessor
from src.processors.multimodal_processor import MultimodalProcessor
from src.formatters.summary_formatter import SummaryFormatter
from src.gpt_providers.gpt_selector import GPTSelector
from src.gpt_providers.openai_multimodal import OpenAIMultimodal
from src.parsers import TravelDataParser
import logging

logger = logging.getLogger(__name__)

def main():
    print("Starting Trip Diary Processing...\n")
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Consolidate multiple travel itineraries')
    parser.add_argument('--input', required=True, nargs='+', help='Paths to PDF/image files')
    parser.add_argument('--output', help='Path to save consolidated JSON output')
    parser.add_argument('--gpt-provider', default='openai', 
                      choices=['openai', 'claude', 'xai', 'sambanova'],
                      help='Choose GPT provider for text generation')
    parser.add_argument('--multimodal', action='store_true',
                      help='Use multimodal processing (vision) for documents')
    args = parser.parse_args()
    
    try:
        start_time = time.perf_counter()
        
        if args.multimodal:
            print("Using multimodal (vision) processing...")
            # Use multimodal provider
            if args.gpt_provider == 'openai':
                provider = OpenAIMultimodal()
                # Process files with multimodal
                itineraries, errors, processing_time = MultimodalProcessor.process_files(
                    args.input, provider
                )
            else:
                print(f"Multimodal not yet implemented for {args.gpt_provider}, falling back to text extraction")
                args.multimodal = False
        
        if not args.multimodal:
            print("Using traditional text extraction...")
            # Create GPT provider
            gpt_selector = GPTSelector()
            gpt_provider = gpt_selector.get_provider(args.gpt_provider)
            
            # Process PDFs with text extraction
            itineraries, errors, processing_time = PDFProcessor.process_files(
                args.input, gpt_provider
            )
        
        if errors:
            print("\nErrors encountered during processing:")
            for error in errors:
                print(f"- {error}")
            if not itineraries:
                return
        
        if not itineraries:
            print("\nNo valid itineraries found!")
            return
        
        # Parse all itineraries
        flights = []
        hotels = []
        passengers = []
        other_items = []
        parse_errors = []
        
        for itinerary in itineraries:
            if args.multimodal:
                # Multimodal returns data directly
                flights.extend(itinerary.get('flights', []))
                hotels.extend(itinerary.get('hotels', []))
                passengers.extend(itinerary.get('passengers', []))
                other_items.extend(itinerary.get('other', []))
            else:
                # Traditional parsing
                parsed_data = TravelDataParser.parse_itinerary(itinerary)
                flights.extend(parsed_data['flights'])
                hotels.extend(parsed_data['hotels'])
                passengers.extend(parsed_data['passengers'])
                if parsed_data['errors']:
                    parse_errors.extend(parsed_data['errors'])
        
        # Convert multimodal results to proper objects if needed
        if args.multimodal and flights:
            # The multimodal data is in dict format, need to convert to objects
            from src.parsers import TravelDataParser
            converted_flights = []
            for f in flights:
                try:
                    # Create a proper Flight object from the dict
                    flight_dict = {'flights': [f], 'hotels': [], 'passengers': []}
                    parsed = TravelDataParser.parse_itinerary(flight_dict)
                    converted_flights.extend(parsed['flights'])
                except:
                    pass
            flights = converted_flights
            
            # Similar for hotels
            converted_hotels = []
            for h in hotels:
                try:
                    hotel_dict = {'flights': [], 'hotels': [h], 'passengers': []}
                    parsed = TravelDataParser.parse_itinerary(hotel_dict)
                    converted_hotels.extend(parsed['hotels'])
                except:
                    pass
            hotels = converted_hotels
            
            # And passengers
            converted_passengers = []
            for p in passengers:
                try:
                    pass_dict = {'flights': [], 'hotels': [], 'passengers': [p]}
                    parsed = TravelDataParser.parse_itinerary(pass_dict)
                    converted_passengers.extend(parsed['passengers'])
                except:
                    pass
            passengers = converted_passengers
        
        # Sort chronologically
        if flights:
            flights = sorted(flights, key=lambda x: (x.departure.date, x.departure.time))
        if hotels:
            hotels = sorted(hotels, key=lambda x: x.check_in_date)
        if passengers:
            passengers = sorted(list(set(passengers)), key=lambda x: (x.last_name, x.first_name))
        
        # Generate and print summary
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        print("\nConsolidated Itinerary Summary:\n")
        print(SummaryFormatter.format_summary(flights, hotels, passengers))
        
        if args.multimodal and other_items:
            print("\nOther Travel Items:")
            for item in other_items:
                print(f"- {item.get('type', 'Unknown')}: {item.get('description', '')}")
                if item.get('date'):
                    print(f"  Date: {item['date']}")
                if item.get('confirmation'):
                    print(f"  Confirmation: {item['confirmation']}")
        
        # Print processing summary
        print("\nProcessing Summary:")
        print(f"Processing Mode: {'Multimodal (Vision)' if args.multimodal else 'Text Extraction'}")
        print(f"Processing Time: {processing_time:.2f} seconds")
        print(f"Total Execution Time: {total_time:.2f} seconds")
        print(f"Files Processed: {len(args.input)}")
        print(f"Flights Found: {len(flights)}")
        print(f"Hotels Found: {len(hotels)}")
        print(f"Passengers Found: {len(passengers)}")
        if args.multimodal:
            print(f"Other Items Found: {len(other_items)}")
        
        if parse_errors:
            print("\nParsing Warnings:")
            for error in parse_errors:
                print(f"- {error}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()