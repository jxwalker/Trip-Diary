#!/usr/bin/env python3
"""
Test script for multimodal travel document extraction
"""
import asyncio
import sys
from pathlib import Path
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from src.gpt_providers.openai_multimodal import OpenAIMultimodal

async def test_multimodal():
    print("Testing Multimodal Travel Document Extraction\n")
    print("=" * 50)
    
    # Check for test files
    test_files = []
    
    # Look for any PDF or image files in current directory
    for pattern in ['*.pdf', '*.jpg', '*.jpeg', '*.png']:
        files = list(Path('.').glob(pattern))
        test_files.extend(files)
    
    if not test_files:
        print("\n❌ No test files found!")
        print("\nPlease add one of the following to test:")
        print("  - A PDF travel document (boarding pass, hotel booking, etc.)")
        print("  - A screenshot or photo of a ticket")
        print("  - Any travel itinerary document")
        print("\nExample: python test_multimodal.py")
        return
    
    print(f"\n✅ Found {len(test_files)} test file(s):")
    for f in test_files:
        print(f"  - {f}")
    
    # Test with first file
    test_file = str(test_files[0])
    print(f"\n📄 Testing with: {test_file}")
    print("-" * 50)
    
    try:
        # Initialize multimodal extractor
        print("\n🤖 Initializing OpenAI Multimodal...")
        extractor = OpenAIMultimodal()
        
        # Process document
        print(f"👁️ Processing document with vision AI...")
        result = extractor.process_document(document_path=test_file)
        
        if result and 'error' not in result:
            print("\n✅ Extraction successful!")
            
            # Display results
            print("\n📊 Extracted Data:")
            print("-" * 50)
            
            # Flights
            if result.get('flights'):
                print(f"\n✈️ Flights ({len(result['flights'])} found):")
                for i, flight in enumerate(result['flights'], 1):
                    print(f"\n  Flight {i}:")
                    print(f"    • Number: {flight.get('flight_number', 'N/A')}")
                    print(f"    • Route: {flight.get('departure', {}).get('location', 'N/A')} → {flight.get('arrival', {}).get('location', 'N/A')}")
                    print(f"    • Date: {flight.get('departure', {}).get('date', 'N/A')}")
                    print(f"    • Time: {flight.get('departure', {}).get('time', 'N/A')} - {flight.get('arrival', {}).get('time', 'N/A')}")
                    if flight.get('seat'):
                        print(f"    • Seat: {flight['seat']}")
                    if flight.get('confidence'):
                        print(f"    • Confidence: {flight['confidence']:.0%}")
            
            # Hotels
            if result.get('hotels'):
                print(f"\n🏨 Hotels ({len(result['hotels'])} found):")
                for i, hotel in enumerate(result['hotels'], 1):
                    print(f"\n  Hotel {i}:")
                    print(f"    • Name: {hotel.get('name', 'N/A')}")
                    print(f"    • City: {hotel.get('city', 'N/A')}")
                    print(f"    • Check-in: {hotel.get('check_in_date', 'N/A')}")
                    print(f"    • Check-out: {hotel.get('check_out_date', 'N/A')}")
                    if hotel.get('confirmation_number'):
                        print(f"    • Confirmation: {hotel['confirmation_number']}")
                    if hotel.get('confidence'):
                        print(f"    • Confidence: {hotel['confidence']:.0%}")
            
            # Passengers
            if result.get('passengers'):
                print(f"\n👥 Passengers ({len(result['passengers'])} found):")
                for i, passenger in enumerate(result['passengers'], 1):
                    print(f"\n  Passenger {i}:")
                    print(f"    • Name: {passenger.get('first_name', '')} {passenger.get('last_name', '')}")
                    if passenger.get('frequent_flyer'):
                        print(f"    • Frequent Flyer: {passenger['frequent_flyer']}")
                    if passenger.get('confidence'):
                        print(f"    • Confidence: {passenger['confidence']:.0%}")
            
            # Other items
            if result.get('other'):
                print(f"\n📋 Other Items ({len(result['other'])} found):")
                for item in result['other']:
                    print(f"  • {item.get('type', 'Unknown')}: {item.get('description', '')}")
            
            # Metadata
            if result.get('_metadata'):
                print(f"\n📊 Processing Info:")
                print(f"  • Method: {result['_metadata'].get('processing_type', 'N/A')}")
                print(f"  • Model: {result['_metadata'].get('model', 'N/A')}")
                print(f"  • Document Type: {result['_metadata'].get('document_type', 'N/A')}")
            
            # Save full result
            output_file = f"extracted_{Path(test_file).stem}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Full results saved to: {output_file}")
            
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'No result'
            print(f"\n❌ Extraction failed: {error_msg}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Test complete!")

def main():
    # Check for API key
    import os
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not set")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Run async test
    asyncio.run(test_multimodal())

if __name__ == "__main__":
    main()