import argparse
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from modules.pdf_extractor import extract_text_from_pdf
from modules.claude_processor import extract_itinerary_with_claude

def load_itineraries(file_paths: List[str]) -> List[Dict[str, Any]]:
    """Process multiple PDF files and return list of parsed itineraries."""
    itineraries = []
    
    for file_path in file_paths:
        print(f"\nProcessing: {file_path}")
        text = extract_text_from_pdf(file_path)
        print(f"Extracted {len(text)} characters of text")
        
        itinerary = extract_itinerary_with_claude(text)
        if itinerary:
            itinerary['source_file'] = file_path  # Add source file for reference
            itineraries.append(itinerary)
        else:
            print(f"Failed to parse itinerary from {file_path}")
    
    return itineraries

def consolidate_flights(itineraries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract and sort all flights from multiple itineraries."""
    all_flights = []
    
    for itinerary in itineraries:
        for flight in itinerary.get('flights', []):
            flight['booking_reference'] = itinerary['booking_reference']
            flight['source_file'] = itinerary['source_file']
            all_flights.append(flight)
    
    # Sort flights by departure date and time
    return sorted(all_flights, key=lambda x: (
        x['departure']['date'],
        x['departure']['time']
    ))

def consolidate_hotels(itineraries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract and sort all hotel stays from multiple itineraries."""
    all_hotels = []
    
    for itinerary in itineraries:
        for hotel in itinerary.get('hotels', []):
            hotel['booking_reference'] = itinerary['booking_reference']
            hotel['source_file'] = itinerary['source_file']
            all_hotels.append(hotel)
    
    # Sort hotels by check-in date
    return sorted(all_hotels, key=lambda x: x['check_in'])

def format_event_timeline(flights: List[Dict[str, Any]], hotels: List[Dict[str, Any]]) -> str:
    """Create a chronological timeline of all travel events."""
    events = []
    
    # Add flights as departure and arrival events
    for f in flights:
        events.append({
            'date': f['departure']['date'],
            'time': f['departure']['time'],
            'type': 'flight_departure',
            'description': f"Flight {f['flight_number']} departs {f['departure']['location']} → {f['arrival']['location']}"
        })
        events.append({
            'date': f['arrival']['date'],
            'time': f['arrival']['time'],
            'type': 'flight_arrival',
            'description': f"Flight {f['flight_number']} arrives at {f['arrival']['location']}"
        })
    
    # Add hotel check-in and check-out events (deduplicated by property)
    seen_hotels = set()  # Track unique hotel/date combinations
    for h in hotels:
        hotel_key = (h['name'], h['check_in'], h['check_out'])
        if hotel_key not in seen_hotels:
            events.append({
                'date': h['check_in'],
                'time': '15:00',  # Standard check-in time
                'type': 'hotel_checkin',
                'description': f"Check in to {h['name']}, {h['city']}"
            })
            events.append({
                'date': h['check_out'],
                'time': '12:00',  # Standard check-out time
                'type': 'hotel_checkout',
                'description': f"Check out from {h['name']}, {h['city']}"
            })
            seen_hotels.add(hotel_key)
    
    # Sort all events chronologically
    events.sort(key=lambda x: (x['date'], x['time']))
    
    # Format the timeline
    timeline = ["Chronological Timeline:"]
    for e in events:
        timeline.append(f"- {e['date']} {e['time']}: {e['description']}")
    
    return "\n".join(timeline)

def format_consolidated_summary(flights: List[Dict[str, Any]], hotels: List[Dict[str, Any]]) -> str:
    """Create a human-readable summary of all flights and hotels in date order."""
    summary = []
    
    # Trip duration
    if flights:
        first_departure = flights[0]['departure']['date']
        last_arrival = flights[-1]['arrival']['date']
        summary.append(f"Trip Duration: {first_departure} to {last_arrival}\n")
    
    # Add chronological timeline
    summary.append(format_event_timeline(flights, hotels))
    summary.append("\n")
    
    # Add detailed itinerary header
    summary.append("Detailed Itinerary:")
    summary.append("-" * 20)
    summary.append("")
    
    # Flights
    if flights:
        summary.append("Flights (in chronological order):")
        for f in flights:
            dep = f['departure']
            arr = f['arrival']
            baggage = f.get('baggage_allowance', {})
            
            # Format terminals
            dep_terminal = f" Terminal {dep.get('terminal', '').replace('Terminal ', '')}" if dep.get('terminal') else ""
            arr_terminal = f" Terminal {arr.get('terminal', '').replace('Terminal ', '')}" if arr.get('terminal') else ""
            
            # Format baggage info
            checked_baggage = baggage.get('checked_baggage', 'N/A')
            hand_baggage = baggage.get('hand_baggage', 'N/A')
            
            # Clean up Air Asia baggage format
            if 'Checked baggage' in checked_baggage:
                checked_baggage = checked_baggage.replace('Checked baggage ', '')
            
            # Set correct hand baggage for BA/Qatar flights
            if f['flight_number'].startswith('BA'):
                if f['operator'] in ['Qatar Airways', 'British Airways']:
                    hand_baggage = "1 handbag/laptop bag, plus 1 additional cabin bag"
            
            baggage_info = []
            if checked_baggage != 'N/A':
                baggage_info.append(f"Checked: {checked_baggage}")
            if hand_baggage != 'N/A':
                baggage_info.append(f"Hand: {hand_baggage}")
            baggage_str = " | ".join(baggage_info) if baggage_info else "N/A"
            
            summary.append(
                f"- {f['flight_number']} ({f['operator']}) [Booking: {f['booking_reference']}]\n"
                f"  {dep['location']}{dep_terminal} → {arr['location']}{arr_terminal}\n"
                f"  {dep['date']} {dep['time']} → {arr['date']} {arr['time']}\n"
                f"  Class: {f['class']}\n"
                f"  Baggage: {baggage_str}"
            )
        summary.append("")
    
    # Hotels
    if hotels:
        summary.append("Hotels (in chronological order):")
        for h in hotels:
            summary.append(
                f"- {h['name']} [Booking: {h['booking_reference']}]\n"
                f"  {h['city']}: {h['check_in']} to {h['check_out']}\n"
                f"  {h['room_details']}"
            )
        summary.append("")
    
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description='Consolidate multiple travel itineraries')
    parser.add_argument('--input', required=True, nargs='+', help='Paths to PDF files')
    parser.add_argument('--output', help='Path to save consolidated JSON output')
    
    args = parser.parse_args()
    
    # Process all itineraries
    itineraries = load_itineraries(args.input)
    
    if not itineraries:
        print("\nNo valid itineraries found!")
        return
    
    # Consolidate and sort flights and hotels
    all_flights = consolidate_flights(itineraries)
    all_hotels = consolidate_hotels(itineraries)
    
    # Create consolidated output
    consolidated = {
        "flights": all_flights,
        "hotels": all_hotels
    }
    
    # Save JSON output if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(consolidated, f, indent=2)
        print(f"\nSaved consolidated JSON to: {args.output}")
    
    # Print human-readable summary
    print("\nConsolidated Itinerary Summary:")
    print(format_consolidated_summary(all_flights, all_hotels))

if __name__ == "__main__":
    main()