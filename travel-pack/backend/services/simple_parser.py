"""
Simple robust parser for Perplexity responses
Handles the actual formats Perplexity returns
"""
import re
from typing import List, Dict

def parse_restaurants_simple(response: str) -> List[Dict]:
    """
    Simple parser that handles real Perplexity formats:
    1. **Name** - Address
    2. **Name**
       Address on next line
    3. **Name**
       - Address: ...
    """
    restaurants = []
    lines = response.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for restaurant name in bold
        if '**' in line:
            # Extract name
            name_match = re.search(r'\*\*(.+?)\*\*', line)
            if name_match:
                name = name_match.group(1).strip()
                
                # Check if address is on same line after dash
                rest_of_line = line[name_match.end():].strip()
                if rest_of_line.startswith(('-', '–', '—')):
                    # Address is inline
                    address = rest_of_line.strip('-–— ').strip()
                    # Remove trailing description if present
                    if '. ' in address:
                        address = address.split('. ', 1)[0]
                    
                    restaurant = {'name': name, 'address': address}
                    
                    # Look for description on next line
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not next_line.startswith(('**', '-', '1.', '2.', '3.')):
                            restaurant['description'] = next_line
                            i += 1
                else:
                    # Address might be on next line
                    restaurant = {'name': name}
                    
                    # Check next few lines for address
                    for j in range(1, 4):
                        if i + j < len(lines):
                            next_line = lines[i + j].strip()
                            
                            # Skip empty lines
                            if not next_line:
                                continue
                            
                            # Stop if we hit another restaurant
                            if '**' in next_line or re.match(r'^\d+\.', next_line):
                                break
                            
                            # Check if this looks like an address
                            if any(marker in next_line for marker in 
                                   ['Street', 'St', 'Ave', 'Avenue', 'Road', 'NY', 'New York']):
                                restaurant['address'] = next_line.strip('- ')
                                # Description might be after address
                                if i + j + 1 < len(lines):
                                    desc_line = lines[i + j + 1].strip()
                                    if desc_line and not desc_line.startswith(('**', '-', '1.', '2.')):
                                        restaurant['description'] = desc_line
                                i = i + j
                                break
                            # Check for labeled address
                            elif 'Address:' in next_line:
                                restaurant['address'] = next_line.split(':', 1)[1].strip()
                                i = i + j
                                break
                            # If no address markers, might be description
                            elif not restaurant.get('description'):
                                restaurant['description'] = next_line
                
                restaurants.append(restaurant)
        
        i += 1
    
    return restaurants

def parse_attractions_simple(response: str) -> List[Dict]:
    """Simple parser for attractions"""
    # Similar logic to restaurants
    attractions = []
    lines = response.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for attraction name in bold
        if '**' in line and not any(skip in line.lower() for skip in ['address:', 'price:', 'hours:']):
            name_match = re.search(r'\*\*(.+?)\*\*', line)
            if name_match:
                name = name_match.group(1).strip()
                attraction = {'name': name}
                
                # Look for details in next few lines
                for j in range(1, 6):
                    if i + j < len(lines):
                        detail_line = lines[i + j].strip()
                        
                        if not detail_line:
                            continue
                        
                        if '**' in detail_line or re.match(r'^\d+\.', detail_line):
                            break
                        
                        # Parse different types of information
                        if any(marker in detail_line for marker in ['Street', 'St', 'Ave', 'Avenue', 'NY']):
                            if 'address' not in attraction:
                                attraction['address'] = detail_line.strip('- ')
                        elif 'Price:' in detail_line or 'Admission:' in detail_line:
                            attraction['price'] = detail_line.split(':', 1)[1].strip()
                        elif 'Hours:' in detail_line or 'Open:' in detail_line:
                            attraction['hours'] = detail_line.split(':', 1)[1].strip()
                        elif not attraction.get('description') and len(detail_line) > 20:
                            attraction['description'] = detail_line
                
                if attraction.get('name'):
                    attractions.append(attraction)
        
        i += 1
    
    return attractions