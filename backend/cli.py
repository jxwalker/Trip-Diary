import argparse
import time
import sys
from pathlib import Path
from typing import List, Dict

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.processors.pdf_processor import PDFProcessor
from src.formatters.summary_formatter import SummaryFormatter
from src.gpt_providers.gpt_selector import GPTSelector
from src.parsers import TravelDataParser
from src.utils.logging_config import setup_logging
import logging

# Set up logging for CLI
setup_logging("logs", debug=False)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Trip Diary Processing...")
    
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
            logger.warning("Errors encountered during PDF processing:")
            for error in errors:
                logger.warning(f"- {error}")
            if not itineraries:
                return

        if not itineraries:
            logger.error("No valid itineraries found!")
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

        logger.info("Consolidated Itinerary Summary:")
        print(SummaryFormatter.format_summary(flights, hotels, passengers))

        # Log processing summary
        logger.info("Processing Summary:")
        logger.info(f"PDF Processing Time: {processing_time:.2f} seconds")
        logger.info(f"Total Execution Time: {total_time:.2f} seconds")
        logger.info(f"Files Processed: {len(args.input)}")
        logger.info(f"Flights Found: {len(flights)}")
        logger.info(f"Hotels Found: {len(hotels)}")
        logger.info(f"Passengers Found: {len(passengers)}")

        if errors:
            logger.warning(f"PDF Processing Errors: {len(errors)}")
        if parse_errors:
            logger.warning(f"Data Parsing Errors: {len(parse_errors)}")
            logger.warning("Parsing Errors encountered:")
            for error in parse_errors:
                logger.warning(f"- {error}")
            
    except Exception as e:
        logger.error(f"Fatal error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()