from datetime import datetime, timedelta

def calculate_checkin_time(departure_time: str) -> str:
    """Calculate airport check-in time (2 hours before departure)."""
    try:
        # Parse the time string
        dep_time = datetime.strptime(departure_time, '%H:%M')
        # Subtract 2 hours
        checkin_time = dep_time - timedelta(hours=2)
        # Return formatted time
        return checkin_time.strftime('%H:%M')
    except ValueError as e:
        print(f"Warning: Could not calculate check-in time from {departure_time}: {str(e)}")
        return "Unknown"

def format_event_timeline(flights: List[Dict[str, Any]], hotels: List[Dict[str, Any]]) -> str:
    """Create a chronological timeline of all travel events."""
    events = []
    
    # Add flights as check-in, departure and arrival events
    for f in flights:
        # Add check-in time
        checkin_time = calculate_checkin_time(f['departure']['time'])
        events.append({
            'date': f['departure']['date'],
            'time': checkin_time,
            'type': 'flight_checkin',
            'description': f"Check in for flight {f['flight_number']} at {f['departure']['location']}"
        })
        
        # Add departure
        events.append({
            'date': f['departure']['date'],
            'time': f['departure']['time'],
            'type': 'flight_departure',
            'description': f"Flight {f['flight_number']} departs {f['departure']['location']} → {f['arrival']['location']}"
        })
        
        # Add arrival
        events.append({
            'date': f['arrival']['date'],
            'time': f['arrival']['time'],
            'type': 'flight_arrival',
            'description': f"Flight {f['flight_number']} arrives at {f['arrival']['location']}"
        })
    
    # Add hotel check-in and check-out events (deduplicated by property)
    seen_hotels = set()
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