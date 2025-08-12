#!/usr/bin/env python3
"""Fix missing Path imports in all services"""
import os
import re

services_dir = "/home/james/code/trip-diary/travel-pack/backend/services"

for filename in os.listdir(services_dir):
    if filename.endswith(".py"):
        filepath = os.path.join(services_dir, filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check if it uses Path but doesn't import it
        if "root_dir = Path" in content and "from pathlib import Path" not in content:
            # Add the import after dotenv import
            content = content.replace(
                "from dotenv import load_dotenv",
                "from dotenv import load_dotenv\nfrom pathlib import Path"
            )
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"Fixed: {filename}")

print("Done!")