#!/usr/bin/env python3
"""Test parser with the actual Perplexity response"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.perplexity_search_service import PerplexitySearchService

# Read the actual response we just got
with open("test/perplexity_output.txt", "r") as f:
    response = f.read()

print("Testing parser with real Perplexity response...")
print("=" * 60)

service = PerplexitySearchService()
parsed = service._parse_restaurant_response(response)

print(f"Parser found: {len(parsed)} restaurants")

if len(parsed) == 0:
    print("\n❌ PARSER FAILED TO EXTRACT ANY RESTAURANTS!")
    print("\nLet's look at what the parser is trying to match...")
    print("\nThe response contains:")
    print("- '**' bold markers:", "**" in response)
    print("- 'Address:' labels:", "Address:" in response)
    print("- Numbered items:", any(f"{i}." in response for i in range(1, 10)))
    
    # Let's try a different parsing approach
    print("\n🔧 Let me write a better parser...")
    
    restaurants = []
    current = None
    
    for line in response.split('\n'):
        line = line.strip()
        
        # Look for restaurant names in bold
        if '**' in line and not line.startswith('-'):
            # Start of a new restaurant
            if current:
                restaurants.append(current)
            
            # Extract name between ** markers
            import re
            match = re.search(r'\*\*(.+?)\*\*', line)
            if match:
                current = {'name': match.group(1).strip()}
        elif current and line.startswith('- **Address:**'):
            # Extract address
            address = line.replace('- **Address:**', '').strip()
            current['address'] = address
        elif current and line.startswith('- **Why'):
            # Extract description
            desc = line.split(':', 1)[1].strip() if ':' in line else ''
            current['description'] = desc
        elif current and line.startswith('- **Price'):
            # Extract price
            price = line.split(':', 1)[1].strip() if ':' in line else ''
            current['price'] = price
    
    if current:
        restaurants.append(current)
    
    print(f"\n✅ Better parser found: {len(restaurants)} restaurants")
    for i, r in enumerate(restaurants, 1):
        print(f"\n{i}. {r.get('name', 'Unknown')}")
        if 'address' in r:
            print(f"   📍 {r['address']}")
        if 'price' in r:
            print(f"   💰 {r['price']}")
else:
    print("\n✅ Parser worked! Found restaurants:")
    for i, r in enumerate(parsed, 1):
        print(f"\n{i}. {r.get('name', 'Unknown')}")
        for key, value in r.items():
            if key != 'name' and key != 'details':
                print(f"   {key}: {value}")
            elif key == 'details' and value:
                print(f"   Details: {', '.join(value[:2])}...")