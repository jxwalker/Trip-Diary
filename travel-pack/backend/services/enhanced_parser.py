"""
Enhanced parser for structured Perplexity responses
Handles detailed restaurant, attraction, and event data
"""
import re
from typing import List, Dict, Optional

def parse_restaurants_enhanced(response: str) -> List[Dict]:
    """
    Parse restaurant data with all details including reviews, contact, distance
    """
    restaurants = []
    sections = response.split('**')
    
    for i in range(1, len(sections), 2):  # Names are in odd indices after split
        if i >= len(sections):
            break
            
        name = sections[i].strip()
        if not name or len(name) > 100:  # Skip if not a valid name
            continue
            
        # Get the content after the name
        content = sections[i + 1] if i + 1 < len(sections) else ""
        
        restaurant = {
            'name': name,
            'address': '',
            'cuisine': '',
            'price': '',
            'distance': '',
            'phone': '',
            'website': '',
            'reservation_link': '',
            'hours': '',
            'why_recommended': '',
            'signature_dishes': [],
            'review': '',
            'description': ''
        }
        
        # Parse the structured content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Address:'):
                restaurant['address'] = line.replace('Address:', '').strip()
            elif line.startswith('Cuisine:'):
                restaurant['cuisine'] = line.replace('Cuisine:', '').strip()
            elif line.startswith('Price:'):
                restaurant['price'] = line.replace('Price:', '').strip()
            elif line.startswith('Distance'):
                restaurant['distance'] = line.replace('Distance from hotel:', '').strip()
            elif line.startswith('Phone:'):
                restaurant['phone'] = line.replace('Phone:', '').strip()
            elif line.startswith('Website:'):
                restaurant['website'] = line.replace('Website:', '').strip()
            elif line.startswith('Reservation link:'):
                restaurant['reservation_link'] = line.replace('Reservation link:', '').strip()
            elif line.startswith('Hours:'):
                restaurant['hours'] = line.replace('Hours:', '').strip()
            elif line.startswith('Why recommended:'):
                restaurant['why_recommended'] = line.replace('Why recommended:', '').strip()
            elif line.startswith('Signature dishes:'):
                dishes = line.replace('Signature dishes:', '').strip()
                restaurant['signature_dishes'] = [d.strip() for d in dishes.split(',')]
            elif line.startswith('Review:'):
                restaurant['review'] = line.replace('Review:', '').strip()
            elif line.startswith('Reservation:'):
                restaurant['reservation'] = line.replace('Reservation:', '').strip()
            elif len(line) > 20 and not any(line.startswith(k + ':') for k in 
                ['Address', 'Cuisine', 'Price', 'Distance', 'Phone', 'Hours', 
                 'Why', 'Signature', 'Review', 'Reservation']):
                # This might be a description
                if not restaurant['description']:
                    restaurant['description'] = line
        
        # Only add if we have at least name and address or description
        if restaurant['name'] and (restaurant['address'] or restaurant['description']):
            restaurants.append(restaurant)
    
    return restaurants

def parse_attractions_enhanced(response: str) -> List[Dict]:
    """
    Parse attraction data with full visitor information
    """
    attractions = []
    sections = response.split('**')
    
    for i in range(1, len(sections), 2):  # Names are in odd indices
        if i >= len(sections):
            break
            
        name_part = sections[i].strip()
        if not name_part or len(name_part) > 150:
            continue
            
        # Extract name and type
        type_match = re.search(r'\((type:|[A-Za-z/]+)\)', name_part)
        if type_match:
            name = name_part[:type_match.start()].strip()
            attraction_type = type_match.group(1).replace('type:', '').strip()
        else:
            name = name_part
            attraction_type = ''
        
        content = sections[i + 1] if i + 1 < len(sections) else ""
        
        attraction = {
            'name': name,
            'type': attraction_type,
            'address': '',
            'hours': 'Check website',
            'price': 'Varies',
            'duration': '',
            'distance': '',
            'why_visit': '',
            'highlights': [],
            'tips': '',
            'special': '',
            'nearby': [],
            'description': ''
        }
        
        # Parse structured content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('Address:'):
                attraction['address'] = line.replace('Address:', '').strip()
            elif line.startswith('Hours:'):
                attraction['hours'] = line.replace('Hours:', '').strip()
            elif line.startswith('Price:'):
                attraction['price'] = line.replace('Price:', '').strip()
            elif line.startswith('Duration:'):
                attraction['duration'] = line.replace('Duration:', '').strip()
            elif line.startswith('Distance'):
                attraction['distance'] = line.replace('Distance from hotel:', '').strip()
            elif line.startswith('Why visit:'):
                attraction['why_visit'] = line.replace('Why visit:', '').strip()
            elif line.startswith('Highlights:'):
                highlights = line.replace('Highlights:', '').strip()
                attraction['highlights'] = [h.strip() for h in highlights.split(',')]
            elif line.startswith('Tips:'):
                attraction['tips'] = line.replace('Tips:', '').strip()
            elif line.startswith('Special:'):
                attraction['special'] = line.replace('Special:', '').strip()
            elif line.startswith('Nearby:'):
                nearby = line.replace('Nearby:', '').strip()
                attraction['nearby'] = [n.strip() for n in nearby.split(',')]
            elif len(line) > 20 and not any(line.startswith(k + ':') for k in 
                ['Address', 'Hours', 'Price', 'Duration', 'Distance', 
                 'Why', 'Highlights', 'Tips', 'Special', 'Nearby']):
                if not attraction['description']:
                    attraction['description'] = line
        
        if attraction['name']:
            attractions.append(attraction)
    
    return attractions

def parse_events_structured(response: str) -> List[Dict]:
    """
    Parse events into structured format instead of wall of text
    """
    events = []
    
    # Look for event patterns
    sections = response.split('**')
    
    for i in range(1, len(sections), 2):
        if i >= len(sections):
            break
            
        name = sections[i].strip()
        if not name or len(name) > 150:
            continue
            
        # Skip section headers
        if any(header in name.lower() for header in 
               ['concerts', 'theater', 'museum', 'festival', 'sports', 'cultural']):
            continue
        
        content = sections[i + 1] if i + 1 < len(sections) else ""
        
        event = {
            'name': name,
            'date': '',
            'time': '',
            'venue': '',
            'address': '',
            'price': '',
            'booking_link': '',
            'website': '',
            'description': '',
            'why_attend': '',
            'category': ''
        }
        
        # Determine category from context
        content_lower = content.lower()
        if 'concert' in content_lower or 'music' in content_lower:
            event['category'] = 'Music'
        elif 'theater' in content_lower or 'performance' in content_lower:
            event['category'] = 'Theater'
        elif 'museum' in content_lower or 'exhibition' in content_lower:
            event['category'] = 'Exhibition'
        elif 'festival' in content_lower:
            event['category'] = 'Festival'
        elif 'sport' in content_lower:
            event['category'] = 'Sports'
        else:
            event['category'] = 'Event'
        
        # Parse structured data
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for date patterns
            date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', line)
            if date_match and not event['date']:
                event['date'] = date_match.group()
            
            # Look for time patterns
            time_match = re.search(r'\d{1,2}:\d{2}\s*(AM|PM|am|pm)', line)
            if time_match and not event['time']:
                event['time'] = time_match.group()
            
            # Parse labeled fields
            if line.startswith('Date'):
                date_part = line.split(':', 1)[1] if ':' in line else line.replace('Date', '')
                event['date'] = date_part.strip()
            elif line.startswith('Time'):
                time_part = line.split(':', 1)[1] if ':' in line else line.replace('Time', '')
                event['time'] = time_part.strip()
            elif line.startswith('Venue:'):
                event['venue'] = line.replace('Venue:', '').strip()
            elif line.startswith('Booking link:'):
                event['booking_link'] = line.replace('Booking link:', '').strip()
            elif line.startswith('Website:'):
                event['website'] = line.replace('Website:', '').strip()
            elif line.startswith('Price:'):
                event['price'] = line.replace('Price:', '').strip()
            elif line.startswith('Why'):
                event['why_attend'] = line.split(':', 1)[1].strip() if ':' in line else line
            elif 'starting at $' in line.lower():
                price_match = re.search(r'\$[\d,]+', line)
                if price_match and not event['price']:
                    event['price'] = price_match.group()
            elif len(line) > 30 and not event['description']:
                event['description'] = line
        
        if event['name'] and (event['date'] or event['description']):
            events.append(event)
    
    return events