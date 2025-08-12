import argparse
import time
from pathlib import Path
from typing import List, Dict
from src.processors.pdf_processor import PDFProcessor
from src.formatters.summary_formatter import SummaryFormatter
from src.gpt_providers.gpt_selector import GPTSelector
from src.parsers import TravelDataParser
import logging

logger = logging.getLogger(__name__)

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
            print("\nErrors encountered during PDF processing:")
            for error in errors:
                print(f"- {error}")
            if not itineraries:
                return
        
        if not itineraries:
            print("\nNo valid itineraries found!")
            return
        
        # Parse all itineraries using the new parser
        flights = []
        hotels = []
        passengers = []
        parse_errors = []
        
        for itinerary in itineraries:
            parsed_data = TravelDataParser.parse_itinerary(itinerary)
            
            flights.extend(parsed_data['flights'])
            hotels.extend(parsed_data['hotels'])
            passengers.extend(parsed_data['passengers'])
            
            if parsed_data['errors']:
                parse_errors.extend(parsed_data['errors'])
        
        # Sort chronologically
        flights = sorted(flights, key=lambda x: (x.departure.date, x.departure.time))
        hotels = sorted(hotels, key=lambda x: x.check_in_date)
        passengers = sorted(list(passengers), key=lambda x: (x.last_name, x.first_name))
        
        # Generate and print summary
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        print("\nConsolidated Itinerary Summary:\n")
        print(SummaryFormatter.format_summary(flights, hotels, passengers))
        
        # Print processing summary
        print("\nProcessing Summary:")
        print(f"PDF Processing Time: {processing_time:.2f} seconds")
        print(f"Total Execution Time: {total_time:.2f} seconds")
        print(f"Files Processed: {len(args.input)}")
        print(f"Flights Found: {len(flights)}")
        print(f"Hotels Found: {len(hotels)}")
        print(f"Passengers Found: {len(passengers)}")
        
        if errors:
            print(f"PDF Processing Errors: {len(errors)}")
        if parse_errors:
            print(f"Data Parsing Errors: {len(parse_errors)}")
            print("\nParsing Errors encountered:")
            for error in parse_errors:
                print(f"- {error}")
            
    except Exception as e:
        logger.error(f"Fatal error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()