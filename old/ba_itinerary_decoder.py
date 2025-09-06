import argparse
import json
from modules.pdf_extractor import extract_text_from_pdf
from modules.claude_processor import extract_itinerary_with_claude, format_itinerary_summary

def main():
    parser = argparse.ArgumentParser(description='Decode airline itinerary PDF')
    parser.add_argument('--input', required=True, help='Path to PDF file')
    parser.add_argument('--home_address', required=True, help='Home address')
    parser.add_argument('--airport', required=True, help='Home airport code')
    
    args = parser.parse_args()
    
    print("\n1. Extracting text from PDF:", args.input)
    text = extract_text_from_pdf(args.input)
    print(f"Extracted {len(text)} characters of text")
    
    print("\n2. Parsing itinerary with Claude...")
    itinerary = extract_itinerary_with_claude(text)
    
    if itinerary:
        print("\nParsed JSON data:")
        print(json.dumps(itinerary, indent=2))
        
        print("\nItinerary Summary:")
        print(format_itinerary_summary(itinerary))
    else:
        print("\nFailed to parse itinerary")

if __name__ == "__main__":
    main()