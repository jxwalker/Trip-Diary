"""
Parser for Perplexity API responses
Handles the actual format that Perplexity returns
"""
import re
from typing import List, Dict

class PerplexityResponseParser:
    """Parse real Perplexity responses into structured data"""
    
    @staticmethod
    def parse_restaurants(response: str) -> List[Dict]:
        """
        Parse restaurant recommendations from Perplexity response
        
        Handles multiple formats:
        1. **Restaurant Name** - Address. Description
        2. **Restaurant Name**
           - **Address:** 123 Street
        """
        restaurants = []
        current_restaurant = None
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for numbered restaurant with inline format: 
            # "1. **Name** - Address"
            inline_match = re.match(
                r'^(\d+)\.\s+\*\*(.+?)\*\*\s*[-–]\s*(.+)', line
            )
            if inline_match:
                # Save previous restaurant if exists
                if current_restaurant:
                    restaurants.append(current_restaurant)
                
                # Extract name and rest of line
                name = inline_match.group(2).strip()
                rest = inline_match.group(3).strip()
                
                # The rest often contains address followed by description
                # Try to extract address (usually ends with ZIP code)
                address_match = re.match(
                    r'^([^.]+(?:NY|New York)\s+\d{5})', rest
                )
                if address_match:
                    address = address_match.group(1).strip()
                    description = rest[address_match.end():].strip('. ')
                else:
                    # If no clear address pattern, take everything before first
                    parts = rest.split('. ', 1)
                    address = parts[0] if parts else rest
                    description = parts[1] if len(parts) > 1 else ''
                
                current_restaurant = {
                    'name': name,
                    'address': address,
                    'description': description,
                    'raw_text': [line]
                }
                continue
            
            # Check for numbered restaurant without inline
            # (e.g., "1. **Restaurant Name**")
            numbered_match = re.match(r'^(\d+)\.\s+\*\*(.+?)\*\*', line)
            if numbered_match:
                # Save previous restaurant if exists
                if current_restaurant:
                    restaurants.append(current_restaurant)
                
                # Start new restaurant
                current_restaurant = {
                    'name': numbered_match.group(2).strip(),
                    'raw_text': []
                }
                continue
            
            # If we're in a restaurant section, parse details
            if current_restaurant:
                # Check for address
                if '**Address:**' in line or '**address:**' in line:
                    address = re.sub(r'\*\*[Aa]ddress:\*\*\s*', '', line)
                    address = address.strip('- ').strip()
                    current_restaurant['address'] = address
                
                # Check for why it's great / description
                elif '**Why it' in line or '**why it' in line:
                    desc = (line.split(':', 1)[1].strip() 
                           if ':' in line else line)
                    desc = re.sub(r'\*\*.*?\*\*\s*', '', desc).strip('- ')
                    current_restaurant['description'] = desc
                
                # Check for price
                elif '**Price' in line or '**price' in line:
                    price = (line.split(':', 1)[1].strip() 
                            if ':' in line else line)
                    price = re.sub(r'\*\*.*?\*\*\s*', '', price).strip('- ')
                    # Extract just the $ symbols if present
                    if '$' in price:
                        dollar_match = re.search(r'(\$+)', price)
                        if dollar_match:
                            current_restaurant['price'] = dollar_match.group(1)
                        else:
                            current_restaurant['price'] = price
                    else:
                        current_restaurant['price'] = price
                
                # Check for cuisine type
                elif '**Cuisine' in line or '**cuisine' in line:
                    cuisine = (line.split(':', 1)[1].strip() 
                              if ':' in line else line)
                    cuisine = re.sub(r'\*\*.*?\*\*\s*', '', cuisine).strip(
                        '- ')
                    current_restaurant['cuisine'] = cuisine
                
                # Check for hours
                elif '**Hours' in line or '**Open' in line:
                    hours = (line.split(':', 1)[1].strip() 
                            if ':' in line else line)
                    hours = re.sub(r'\*\*.*?\*\*\s*', '', hours).strip('- ')
                    current_restaurant['hours'] = hours
                
                # Store raw text for reference
                current_restaurant['raw_text'].append(line)
        
        # Don't forget the last restaurant
        if current_restaurant:
            restaurants.append(current_restaurant)
        
        # Clean up the results
        for restaurant in restaurants:
            # Join raw text for any missing description
            if 'description' not in restaurant and restaurant.get('raw_text'):
                # Look for descriptive text that's not a labeled field
                desc_lines = []
                for line in restaurant['raw_text']:
                    if (not line.startswith('-') and '**' not in line 
                        and len(line) > 20):
                        desc_lines.append(line)
                if desc_lines:
                    restaurant['description'] = ' '.join(desc_lines)
            
            # Remove raw_text from final output
            restaurant.pop('raw_text', None)
        
        return restaurants
    
    @staticmethod
    def parse_attractions(response: str) -> List[Dict]:
        """Parse attractions from Perplexity response"""
        attractions = []
        current_attraction = None
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for numbered attraction
            numbered_match = re.match(r'^(\d+)\.\s+\*\*(.+?)\*\*', line)
            if numbered_match:
                if current_attraction:
                    attractions.append(current_attraction)
                
                current_attraction = {
                    'name': numbered_match.group(2).strip(),
                    'details': []
                }
                continue
            
            if current_attraction:
                # Parse address
                if '**Address:**' in line or 'Address:' in line:
                    address = re.sub(
                        r'(\*\*)?[Aa]ddress:(\*\*)?\s*', '', line
                    ).strip('- ')
                    current_attraction['address'] = address
                
                # Parse hours
                elif 'Hours:' in line or 'Open:' in line:
                    hours = (line.split(':', 1)[1].strip() 
                            if ':' in line else '')
                    current_attraction['hours'] = hours.strip('- ')
                
                # Parse price/admission
                elif any(word in line.lower() 
                        for word in ['price:', 'admission:', 'tickets:', 'cost:']):
                    price = (line.split(':', 1)[1].strip() 
                            if ':' in line else line)
                    current_attraction['price'] = re.sub(
                        r'\*\*.*?\*\*\s*', '', price).strip('- ')
                
                # Parse why it's recommended
                elif 'Why' in line or 'Description:' in line:
                    desc = (line.split(':', 1)[1].strip() 
                           if ':' in line else line)
                    current_attraction['description'] = re.sub(
                        r'\*\*.*?\*\*\s*', '', desc).strip('- ')
                
                # Collect other details
                elif line.startswith('-'):
                    current_attraction['details'].append(line.strip('- '))
        
        if current_attraction:
            attractions.append(current_attraction)
        
        return attractions
    
    @staticmethod
    def parse_daily_itinerary(response: str) -> Dict:
        """Parse a daily itinerary from Perplexity response"""
        itinerary = {
            "morning": [],
            "lunch": [],
            "afternoon": [],
            "evening": [],
            "tips": []
        }
        
        current_section = None
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            line_lower = line.lower()
            if 'morning' in line_lower or '8:00' in line or '9:00' in line:
                current_section = 'morning'
            elif 'lunch' in line_lower or '12:00' in line or '1:00' in line:
                current_section = 'lunch'
            elif 'afternoon' in line_lower or '2:00' in line or '3:00' in line:
                current_section = 'afternoon'
            elif ('evening' in line_lower or 'dinner' in line_lower 
                  or '6:00' in line or '7:00' in line):
                current_section = 'evening'
            elif 'tip' in line_lower or 'note' in line_lower:
                current_section = 'tips'
            elif current_section:
                # Clean up the line
                cleaned = re.sub(r'\*\*.*?\*\*:', '', line)
                cleaned = cleaned.strip('- ').strip()
                
                # Only add substantial content
                if (len(cleaned) > 10 and not cleaned.lower().startswith(
                    ('morning', 'afternoon', 'evening', 'lunch'))):
                    itinerary[current_section].append(cleaned)
        
        return itinerary
    
    @staticmethod
    def parse_events(response: str) -> List[Dict]:
        """Parse events from Perplexity response"""
        events = []
        current_event = None
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Look for numbered events or bold titles
            if re.match(r'^\d+\.', line) or '**' in line:
                if current_event and current_event.get('name'):
                    events.append(current_event)
                
                # Extract event name
                name = re.sub(r'^\d+\.\s*', '', line)
                name = re.sub(r'\*\*', '', name).strip()
                
                current_event = {
                    'name': name,
                    'details': []
                }
            elif current_event:
                # Parse event details
                if any(word in line.lower() 
                       for word in ['date:', 'when:', 'dates:']):
                    date = (line.split(':', 1)[1].strip() 
                           if ':' in line else line)
                    current_event['date'] = date
                elif any(word in line.lower() 
                        for word in ['venue:', 'location:', 'where:']):
                    venue = (line.split(':', 1)[1].strip() 
                            if ':' in line else line)
                    current_event['venue'] = venue
                elif any(word in line.lower() 
                        for word in ['price:', 'tickets:', 'cost:']):
                    price = (line.split(':', 1)[1].strip() 
                            if ':' in line else line)
                    current_event['price'] = price
                elif line.startswith('-'):
                    current_event['details'].append(line.strip('- '))
                elif len(line) > 20:
                    if 'description' not in current_event:
                        current_event['description'] = line
        
        if current_event and current_event.get('name'):
            events.append(current_event)
        
        return events
    
    @staticmethod
    def parse_local_insights(response: str) -> Dict:
        """Parse local insights and tips from Perplexity response"""
        insights = {
            "weather": [],
            "transportation": [],
            "money": [],
            "cultural": [],
            "safety": [],
            "tips": []
        }
        
        current_section = 'tips'
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            line_lower = line.lower()
            if 'weather' in line_lower or 'climate' in line_lower:
                current_section = 'weather'
            elif 'transport' in line_lower or 'getting around' in line_lower:
                current_section = 'transportation'
            elif ('money' in line_lower or 'currency' in line_lower 
                  or 'cost' in line_lower):
                current_section = 'money'
            elif ('cultur' in line_lower or 'custom' in line_lower 
                  or 'etiquette' in line_lower):
                current_section = 'cultural'
            elif 'safety' in line_lower or 'security' in line_lower:
                current_section = 'safety'
            else:
                # Add content to current section
                cleaned = re.sub(r'\*\*.*?\*\*:', '', line)
                cleaned = cleaned.strip('- •').strip()
                
                if (len(cleaned) > 10 and not any(
                    cleaned.lower().startswith(word) for word in 
                    ['weather', 'transport', 'money', 'cultur', 'safety'])):
                    insights[current_section].append(cleaned)
        
        return insights
