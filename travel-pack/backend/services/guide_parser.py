"""
Advanced parser for travel guide content from LLMs
Handles various formats and extracts structured data
"""
import re
from typing import Dict, List, Any

class GuideParser:
    """Parse unstructured travel guide text into structured data"""
    
    def parse_comprehensive_guide(self, content: str) -> Dict:
        """Parse a complete travel guide from text"""
        
        guide = {
            "summary": self._extract_summary(content),
            "destination_insights": self._extract_insights(content),
            "weather": self._extract_weather(content),
            "daily_itinerary": self._extract_itinerary(content),
            "restaurants": self._extract_restaurants(content),
            "attractions": self._extract_attractions(content),
            "events": self._extract_events(content),
            "hotels": self._extract_hotels(content),
            "practical_info": self._extract_practical_info(content),
            "hidden_gems": self._extract_hidden_gems(content),
            "raw_content": content
        }
        
        return guide
    
    def _extract_summary(self, content: str) -> str:
        """Extract executive summary or overview"""
        # Look for summary section
        patterns = [
            r"(?:Executive Summary|Overview|Summary)[:\n]+(.*?)(?:\n\n|\n##|\n\*\*)",
            r"^(.*?)(?:\n\n|\n##|\n\*\*)",  # First paragraph
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                if len(summary) > 100:  # Ensure it's meaningful
                    return summary
        
        # Fallback: get first substantial paragraph
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para) > 100 and not para.startswith('#'):
                return para.strip()
        
        return ""
    
    def _extract_weather(self, content: str) -> Dict:
        """Extract weather information"""
        weather = {}
        
        # Look for weather section
        weather_pattern = r"(?:Weather|Forecast|Climate).*?\n(.*?)(?:\n\n|\n##|\n\*\*|$)"
        match = re.search(weather_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            weather_text = match.group(1)
            
            # Extract temperature
            temp_pattern = r"(\d+)°?[FC]"
            temps = re.findall(temp_pattern, weather_text)
            if temps:
                weather["temperature_range"] = f"{min(temps)}-{max(temps)}°"
            
            # Extract conditions
            if "snow" in weather_text.lower():
                weather["conditions"] = "Snow possible"
            elif "rain" in weather_text.lower():
                weather["conditions"] = "Rain possible"
            elif "sunny" in weather_text.lower() or "clear" in weather_text.lower():
                weather["conditions"] = "Clear/Sunny"
            else:
                weather["conditions"] = "Variable"
            
            weather["details"] = weather_text.strip()
        
        return weather
    
    def _extract_itinerary(self, content: str) -> List[Dict]:
        """Extract daily itinerary with activities"""
        days = []
        
        # Pattern for day headers
        day_patterns = [
            r"\*\*Day (\d+)[^*\n]*\*\*([^\n]*)\n(.*?)(?=\*\*Day \d+|\n---|\Z)",
            r"### Day (\d+)[^\n]*\n(.*?)(?=### Day \d+|\n---|\Z)",
            r"Day (\d+)[^:\n]*[:\n]+(.*?)(?=Day \d+|\n---|\Z)"
        ]
        
        for pattern in day_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                for match in matches:
                    if len(match) >= 2:
                        day_num = match[0]
                        day_content = match[-1] if len(match) > 2 else match[1]
                        
                        # Extract activities with times
                        activities = []
                        time_pattern = r"(\d{1,2}:\d{2}\s*[AP]M|\d{1,2}\s*[AP]M)[^\n]*"
                        time_activities = re.findall(time_pattern, day_content)
                        
                        if time_activities:
                            activities = time_activities
                        else:
                            # Split by lines and bullets
                            for line in day_content.split('\n'):
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    activities.append(line.strip('- •*').strip())
                        
                        days.append({
                            "day": int(day_num) if day_num.isdigit() else len(days) + 1,
                            "title": f"Day {day_num}",
                            "activities": activities[:15]  # Limit activities
                        })
                break
        
        return days
    
    def _extract_restaurants(self, content: str) -> List[Dict]:
        """Extract restaurant recommendations"""
        restaurants = []
        
        # Look for restaurant section
        rest_section = re.search(
            r"(?:Restaurant|Dining|Fine Dining|Where to Eat).*?\n(.*?)(?:\n##|\n\*\*\*|\n---|\Z)",
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if rest_section:
            rest_text = rest_section.group(1)
            
            # First check for markdown table format (what Perplexity returns)
            # Look for table with headers like | Restaurant | Cuisine | etc
            table_pattern = r"\| *Restaurant[^\n]*\|.*?\n\|[-\s|]+\n((?:\|[^\n]+\n)+)"
            table_match = re.search(table_pattern, rest_text, re.DOTALL | re.MULTILINE)
            
            if table_match:
                # Parse table rows
                table_body = table_match.group(1)
                rows = table_body.strip().split('\n')
                
                for row in rows[:10]:  # Limit to 10 restaurants
                    # Split by | and clean up
                    cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                    if len(cells) >= 2:  # At least name and cuisine
                        name = cells[0].strip('*')
                        cuisine = cells[1] if len(cells) > 1 else ""
                        ambiance = cells[2] if len(cells) > 2 else ""
                        must_try = cells[3] if len(cells) > 3 else ""
                        
                        restaurants.append({
                            "name": name,
                            "cuisine": cuisine,
                            "ambiance": ambiance,
                            "must_try": must_try,
                            "description": f"{cuisine} - {ambiance}",
                            "type": self._guess_cuisine_type(cuisine)
                        })
            else:
                # Fallback to other patterns
                patterns = [
                    r"\*\*([^*]+)\*\*\s*[–-]\s*([^\n]+)",  # **Name** - Description
                    r"(\d+\.\s*\*\*[^*]+\*\*[^\n]+)",  # 1. **Name** description
                    r"(?:^|\n)([A-Z][^:\n]{3,50}):\s*([^\n]+)",  # Name: Description
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, rest_text)
                    if matches:
                        for match in matches[:10]:  # Limit to 10 restaurants
                            if isinstance(match, tuple):
                                name = match[0].strip('*#. \t')
                                desc = match[1].strip() if len(match) > 1 else ""
                            else:
                                parts = match.split('–', 1) if '–' in match else match.split('-', 1)
                                name = parts[0].strip('*#. \t')
                                desc = parts[1].strip() if len(parts) > 1 else ""
                            
                            if name and len(name) < 100:  # Reasonable name length
                                restaurants.append({
                                    "name": name,
                                    "description": desc,
                                    "type": self._guess_cuisine_type(name + " " + desc)
                                })
                        break
        
        return restaurants
    
    def _extract_attractions(self, content: str) -> List[Dict]:
        """Extract attractions and museums"""
        attractions = []
        
        # Keywords for attractions
        keywords = ["museum", "gallery", "park", "monument", "landmark", "observatory", "memorial"]
        
        # Find lines mentioning attractions
        for line in content.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                # Clean up the line
                name = line.strip('- •*#\t ').split('–')[0].split('-')[0].strip()
                if 5 < len(name) < 100:  # Reasonable length
                    attractions.append({
                        "name": name,
                        "type": self._guess_attraction_type(line_lower),
                        "description": line
                    })
        
        # Deduplicate by name
        seen = set()
        unique_attractions = []
        for attr in attractions:
            if attr["name"] not in seen:
                seen.add(attr["name"])
                unique_attractions.append(attr)
        
        return unique_attractions[:15]  # Limit to 15
    
    def _extract_events(self, content: str) -> List[Dict]:
        """Extract events and shows"""
        events = []
        
        # Look for Broadway/theater mentions
        show_pattern = r"(?:Broadway|show|theater|theatre|performance|concert|exhibition).*?([A-Z][^\n]{5,100})"
        matches = re.findall(show_pattern, content, re.IGNORECASE)
        
        for match in matches[:10]:
            if not match.startswith('http'):
                events.append({
                    "name": match.strip('- •*'),
                    "type": "Performance/Show",
                    "description": match
                })
        
        return events
    
    def _extract_hotels(self, content: str) -> Dict:
        """Extract hotel information"""
        hotel_info = {}
        
        # Look for Plaza Hotel mentions
        if "Plaza Hotel" in content:
            plaza_mentions = re.findall(r"[^\n]*Plaza Hotel[^\n]*", content)
            if plaza_mentions:
                hotel_info["name"] = "The Plaza Hotel"
                hotel_info["mentions"] = plaza_mentions[:3]
                hotel_info["location"] = "768 5th Ave, New York, NY 10019"
        
        return hotel_info
    
    def _extract_practical_info(self, content: str) -> Dict:
        """Extract practical travel information"""
        info = {}
        
        # Transportation
        if "subway" in content.lower() or "metro" in content.lower():
            transport_lines = [line for line in content.split('\n') if 'subway' in line.lower() or 'metro' in line.lower()]
            if transport_lines:
                info["transportation"] = transport_lines[0]
        
        # Tipping
        tip_pattern = r"(?:tip|tipping|gratuity).*?(\d+%)"
        tip_match = re.search(tip_pattern, content, re.IGNORECASE)
        if tip_match:
            info["tipping"] = tip_match.group(0)
        
        return info
    
    def _extract_hidden_gems(self, content: str) -> List[str]:
        """Extract hidden gems and local secrets"""
        gems = []
        
        # Look for hidden/secret/local mentions
        gem_pattern = r"(?:hidden gem|secret|local favorite|off.*beaten|lesser.known).*?([^\n]{20,200})"
        matches = re.findall(gem_pattern, content, re.IGNORECASE)
        
        for match in matches[:5]:
            gems.append(match.strip())
        
        return gems
    
    def _extract_insights(self, content: str) -> str:
        """Extract destination insights"""
        # Look for culture/insight sections
        insight_pattern = r"(?:Culture|Insight|About|Essence).*?\n(.*?)(?:\n\n|\n##|\Z)"
        match = re.search(insight_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _guess_cuisine_type(self, text: str) -> str:
        """Guess cuisine type from text"""
        cuisines = {
            "french": "French",
            "italian": "Italian",
            "japanese": "Japanese",
            "chinese": "Chinese",
            "american": "American",
            "seafood": "Seafood",
            "steakhouse": "Steakhouse",
            "mexican": "Mexican",
            "thai": "Thai",
            "indian": "Indian"
        }
        
        text_lower = text.lower()
        for key, value in cuisines.items():
            if key in text_lower:
                return value
        
        return "International"
    
    def _guess_attraction_type(self, text: str) -> str:
        """Guess attraction type from text"""
        if "museum" in text:
            return "Museum"
        elif "gallery" in text:
            return "Gallery"
        elif "park" in text:
            return "Park"
        elif "monument" in text or "memorial" in text:
            return "Monument"
        elif "observatory" in text or "view" in text:
            return "Viewpoint"
        else:
            return "Attraction"