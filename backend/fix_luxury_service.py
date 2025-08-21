#!/usr/bin/env python
"""
Fix the luxury guide service indentation and API calls
"""
import os

# Read the file
with open('/home/james/code/trip-diary/backend/src/services/luxury_guide_service.py', 'r') as f:
    lines = f.readlines()

# Find and fix the _get_premium_content method
in_method = False
indent_level = 0
fixed_lines = []

for i, line in enumerate(lines):
    if 'async def _get_premium_content' in line:
        in_method = True
        fixed_lines.append(line)
    elif in_method and line.strip().startswith('async def'):
        in_method = False
        fixed_lines.append(line)
    elif in_method:
        # Fix specific indentation issues
        if 'headers = {' in line and not line.startswith('                    headers'):
            line = '                    headers = {\n'
        elif '"Authorization":' in line and not line.startswith('                        '):
            line = '                        "Authorization": f"Bearer {self.perplexity_api_key}",\n'
        elif '"Content-Type":' in line and not line.startswith('                        '):
            line = '                        "Content-Type": "application/json"\n'
        elif line.strip() == '}' and 'headers' in lines[i-1]:
            line = '                    }\n'
        elif 'payload = {' in line and not line.startswith('                    '):
            line = '                    payload = {\n'
        elif 'async with session.post(' in line and not line.startswith('                    '):
            line = '                    async with session.post(\n'
            
        fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write back
with open('/home/james/code/trip-diary/backend/src/services/luxury_guide_service.py', 'w') as f:
    f.writelines(fixed_lines)
    
print("Fixed indentation issues")