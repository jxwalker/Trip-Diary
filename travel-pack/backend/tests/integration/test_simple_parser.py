#!/usr/bin/env python3
"""Test simple parser"""
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.simple_parser import parse_restaurants_simple

# Test with actual Perplexity response we got
response = """Here are three Italian restaurants in New York City with their addresses:

1. **L'Artusi**  
   314 Bleecker St, New York, NY 10014  
   Known for dishes like orecchiette with fennel-braised pork and fettuccine with tomato sauce and Calabrian chili.

2. **I Sodi**  
   113 Greenwich Ave, New York, NY 10014  
   Famous for Tuscan food, including pappardelle al limone and 21-layer lasagna.

3. **Tony's Di Napoli**  
   147 West 43rd Street, New York, NY 10036  
   Family-style Italian dining"""

print("Testing simple parser...")
restaurants = parse_restaurants_simple(response)

print(f"\n✅ Found {len(restaurants)} restaurants:")
for r in restaurants:
    print(f"\n- {r.get('name')}")
    print(f"  Address: {r.get('address', 'NONE')}")
    if r.get('description'):
        print(f"  Desc: {r['description'][:60]}...")