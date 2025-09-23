"""
Magazine-Quality PDF Generation Service
Creates stunning, magazine-style travel guides with beautiful layouts and
photographs
"""
import os
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white, HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                      Image, Table, TableStyle, PageBreak)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


class MagazinePDFService:
    """
    Creates magazine-quality PDF travel guides with:
    - Beautiful typography and layouts
    - High-quality photographs from Unsplash
    - Professional color schemes
    - Interactive elements and QR codes
    - Magazine-style sections and layouts
    """

    def __init__(self, destination: str = None):
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.unsplash_secret_key = os.getenv("UNSPLASH_SECRET_KEY")
        self.destination = destination

        self.color_palette = self._generate_destination_colors(destination)
        self.colors = {
            "primary": self.color_palette.get('primary', HexColor("#1a365d")),
            "secondary": self.color_palette.get('secondary',
                                                   HexColor("#2d3748")),
            "accent": self.color_palette.get('accent', HexColor("#e53e3e")),
            "gold": self.color_palette.get('gold', HexColor("#d69e2e")),
            "light_gray": self.color_palette.get('light', HexColor("#f7fafc")),
            "text": self.color_palette.get('text', HexColor("#2d3748")),
            "muted": self.color_palette.get('muted', HexColor("#718096"))
        }

        # Typography styles
        self.styles = self._create_styles()

        self.photo_style = self._determine_photo_aesthetic(destination)

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create magazine-quality typography styles"""
        styles = getSampleStyleSheet()

        # Title style
        title_style = ParagraphStyle(
            'MagazineTitle',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=self.colors["primary"],
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Subtitle style
        subtitle_style = ParagraphStyle(
            'MagazineSubtitle',
            parent=styles['Heading2'],
            fontSize=24,
            textColor=self.colors["secondary"],
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )

        # Section header
        section_style = ParagraphStyle(
            'MagazineSection',
            parent=styles['Heading2'],
            fontSize=20,
            textColor=self.colors["primary"],
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )

        # Body text
        body_style = ParagraphStyle(
            'MagazineBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.colors["text"],
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            leading=14
        )

        # Caption style
        caption_style = ParagraphStyle(
            'MagazineCaption',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.colors["muted"],
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )

        # Quote style
        quote_style = ParagraphStyle(
            'MagazineQuote',
            parent=styles['Normal'],
            fontSize=14,
            textColor=self.colors["accent"],
            spaceAfter=15,
            spaceBefore=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique',
            leftIndent=20,
            rightIndent=20
        )

        return {
            'title': title_style,
            'subtitle': subtitle_style,
            'section': section_style,
            'body': body_style,
            'caption': caption_style,
            'quote': quote_style
        }

    async def generate_magazine_pdf(
        self,
        guide_data: Dict[str, Any],
        output_path: str,
        trip_id: str
    ) -> Dict[str, Any]:
        """
        Generate a magazine-quality PDF travel guide

        Args:
            guide_data: Complete guide data from the guide service
            output_path: Path to save the PDF
            trip_id: Trip ID for caching and tracking

        Returns:
            Dict with success status and metadata
        """
        try:
            logger.info(f"Generating magazine PDF for trip {trip_id}")

            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build story (content)
            story = []

            # Cover page
            await self._add_cover_page(story, guide_data)
            story.append(PageBreak())

            # Table of contents
            await self._add_table_of_contents(story, guide_data)
            story.append(PageBreak())

            # Weather section
            await self._add_weather_section(story, guide_data)
            story.append(PageBreak())

            # Daily itinerary
            await self._add_daily_itinerary(story, guide_data)

            # Restaurants section
            await self._add_restaurants_section(story, guide_data)
            story.append(PageBreak())

            # Attractions section
            await self._add_attractions_section(story, guide_data)
            story.append(PageBreak())

            # Practical information
            await self._add_practical_section(story, guide_data)
            story.append(PageBreak())

            # Transportation
            await self._add_transportation_section(story, guide_data)
            story.append(PageBreak())

            # Accessibility
            await self._add_accessibility_section(story, guide_data)
            story.append(PageBreak())

            # Emergency contacts
            await self._add_emergency_section(story, guide_data)

            # Build PDF
            doc.build(story)

            logger.info(f"Magazine PDF generated successfully: {output_path}")

            return {
                "success": True,
                "file_path": output_path,
                "file_size": os.path.getsize(output_path),
                "pages": len([item for item in story
                             if isinstance(item, PageBreak)]) + 1,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to generate magazine PDF: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

    async def _add_cover_page(self, story: List,
                              guide_data: Dict[str, Any]) -> None:
        """Add a stunning cover page"""
        destination = guide_data.get("destination", "Your Destination")
        summary = guide_data.get("summary", "Your Personalized Travel Guide")

        # Hero image
        hero_image = await self._get_hero_image(destination)
        if hero_image:
            story.append(Image(hero_image, width=6*inch, height=4*inch))
            story.append(Spacer(1, 20))

        # Title
        story.append(Paragraph(f"<b>{destination}</b>", self.styles['title']))
        story.append(Spacer(1, 20))

        # Subtitle
        story.append(Paragraph("Your Personalized Travel Guide", 
                               self.styles['subtitle']))
        story.append(Spacer(1, 30))

        # Quote
        quote = f"<i>\"{summary}\"</i>"
        story.append(Paragraph(quote, self.styles['quote']))
        story.append(Spacer(1, 40))

        # Generated date
        date_str = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"Generated on {date_str}", 
                               self.styles['caption']))
    
    async def _add_table_of_contents(self, story: List, 
                                     guide_data: Dict[str, Any]) -> None:
        """Add table of contents"""
        story.append(Paragraph("Table of Contents", self.styles['section']))
        story.append(Spacer(1, 20))
        
        contents = [
            "Weather Forecast",
            "Daily Itinerary", 
            "Restaurants & Dining",
            "Attractions & Activities",
            "Practical Information",
            "Transportation",
            "Accessibility",
            "Emergency Contacts"
        ]
        
        for i, item in enumerate(contents, 1):
            story.append(Paragraph(f"{i}. {item}", self.styles['body']))
            story.append(Spacer(1, 8))
    
    async def _add_weather_section(self, story: List, 
                                   guide_data: Dict[str, Any]) -> None:
        """Add weather forecast section with beautiful layout"""
        story.append(Paragraph("Weather Forecast", self.styles['section']))
        story.append(Spacer(1, 15))
        
        weather_data = guide_data.get("weather", [])
        if not weather_data:
            story.append(Paragraph(
                "Weather information will be available closer to your "
                "travel date.", 
                self.styles['body']))
            return
        
        # Create weather table
        weather_table_data = [["Date", "Conditions", "High", "Low", 
                               "Description"]]
        
        for day in weather_data[:5]:  # Show 5 days
            date = day.get("date", "")
            conditions = day.get("conditions", "")
            high = day.get("temperature", {}).get("high", "--")
            low = day.get("temperature", {}).get("low", "--")
            description = day.get("description", "")
            
            weather_table_data.append([date, conditions, high, low, 
                                       description])
        
        weather_table = Table(
            weather_table_data, 
            colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 2.7*inch]
        )
        weather_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors["primary"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.colors["light_gray"]),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        story.append(weather_table)
        story.append(Spacer(1, 20))
    
    async def _add_daily_itinerary(
        self, story: List, guide_data: Dict[str, Any]
    ) -> None:
        """Add daily itinerary with photos and beautiful layout"""
        story.append(Paragraph("Daily Itinerary", self.styles['section']))
        story.append(Spacer(1, 15))
        
        daily_itinerary = guide_data.get("daily_itinerary", [])
        
        for day_data in daily_itinerary:
            day_num = day_data.get("day", 1)
            date = day_data.get("date", "")
            day_of_week = day_data.get("day_of_week", "")
            
            # Day header
            story.append(Paragraph(
                f"Day {day_num} - {day_of_week}, {date}", 
                self.styles['section']
            ))
            story.append(Spacer(1, 10))
            
            # Morning activities
            morning = day_data.get("morning", [])
            if morning:
                story.append(Paragraph("<b>Morning</b>", self.styles['body']))
                for activity in morning:
                    if activity.strip():
                        story.append(Paragraph(
                            f"• {activity}", self.styles['body']
                        ))
                story.append(Spacer(1, 10))
            
            # Afternoon activities
            afternoon = day_data.get("afternoon", [])
            if afternoon:
                story.append(Paragraph(
                    "<b>Afternoon</b>", self.styles['body']
                ))
                for activity in afternoon:
                    if activity.strip():
                        story.append(Paragraph(
                            f"• {activity}", self.styles['body']
                        ))
                story.append(Spacer(1, 10))
            
            # Evening activities
            evening = day_data.get("evening", [])
            if evening:
                story.append(Paragraph("<b>Evening</b>", self.styles['body']))
                for activity in evening:
                    if activity.strip():
                        story.append(Paragraph(
                            f"• {activity}", self.styles['body']
                        ))
                story.append(Spacer(1, 15))
            
            # Add day separator
            if day_num < len(daily_itinerary):
                story.append(HRFlowable(
                    width="100%", thickness=1, lineCap='round', 
                    color=self.colors["muted"]
                ))
                story.append(Spacer(1, 15))
    
    async def _add_restaurants_section(
        self, story: List, guide_data: Dict[str, Any]
    ) -> None:
        """Add restaurants section with photos and details"""
        story.append(Paragraph("Restaurants & Dining", self.styles['section']))
        story.append(Spacer(1, 15))
        
        restaurants = guide_data.get("restaurants", [])
        
        for i, restaurant in enumerate(restaurants[:10]):  # Top 10 restaurants
            name = restaurant.get("name", "")
            cuisine = restaurant.get("cuisine", "")
            price_range = restaurant.get("price_range", "")
            address = restaurant.get("address", "")
            description = restaurant.get("description", "")
            
            # Restaurant photo
            photo = await self._get_restaurant_photo(name, cuisine)
            if photo:
                story.append(Image(photo, width=2*inch, height=1.5*inch))
                story.append(Spacer(1, 10))
            
            # Restaurant details
            story.append(Paragraph(f"<b>{name}</b>", self.styles['body']))
            story.append(Paragraph(
                f"{cuisine} • {price_range}", self.styles['caption']
            ))
            story.append(Paragraph(f"📍 {address}", self.styles['body']))
            story.append(Paragraph(description, self.styles['body']))
            story.append(Spacer(1, 15))
    
    async def _add_attractions_section(
        self, story: List, guide_data: Dict[str, Any]
    ) -> None:
        """Add attractions section with photos and details"""
        story.append(Paragraph("Attractions & Activities", self.styles['section']))
        story.append(Spacer(1, 15))
        
        attractions = guide_data.get("attractions", [])
        
        for attraction in attractions[:8]:  # Top 8 attractions
            name = attraction.get("name", "")
            attraction_type = attraction.get("type", "")
            address = attraction.get("address", "")
            description = attraction.get("description", "")
            hours = attraction.get("hours", "")
            price = attraction.get("price", "")
            
            # Attraction photo
            photo = await self._get_attraction_photo(name, attraction_type)
            if photo:
                story.append(Image(photo, width=2*inch, height=1.5*inch))
                story.append(Spacer(1, 10))
            
            # Attraction details
            story.append(Paragraph(f"<b>{name}</b>", self.styles['body']))
            story.append(Paragraph(
                f"{attraction_type}", self.styles['caption']
            ))
            story.append(Paragraph(f"📍 {address}", self.styles['body']))
            if hours:
                story.append(Paragraph(f"🕒 {hours}", self.styles['body']))
            if price:
                story.append(Paragraph(f"💰 {price}", self.styles['body']))
            story.append(Paragraph(description, self.styles['body']))
            story.append(Spacer(1, 15))
    
    async def _add_practical_section(
        self, story: List, guide_data: Dict[str, Any]
    ) -> None:
        """Add practical information section"""
        story.append(Paragraph("Practical Information", self.styles['section']))
        story.append(Spacer(1, 15))
        
        practical_info = guide_data.get("practical_info", {})
        
        # Budget information
        budget_info = practical_info.get("budget_info", {})
        if budget_info:
            story.append(Paragraph(
                "<b>Budget Information</b>", self.styles['body']
            ))
            for key, value in budget_info.items():
                story.append(Paragraph(f"• {key}: {value}", self.styles['body']))
            story.append(Spacer(1, 10))
        
        # Cultural etiquette
        cultural = practical_info.get("cultural_etiquette", {})
        if cultural:
            story.append(Paragraph(
                "<b>Cultural Etiquette</b>", self.styles['body']
            ))
            for key, value in cultural.items():
                story.append(Paragraph(f"• {key}: {value}", self.styles['body']))
            story.append(Spacer(1, 10))
        
        # Safety information
        safety = practical_info.get("safety_info", {})
        if safety:
            story.append(Paragraph(
                "<b>Safety Information</b>", self.styles['body']
            ))
            for key, value in safety.items():
                story.append(Paragraph(f"• {key}: {value}", self.styles['body']))
    
    async def _add_transportation_section(
        self, story: List, guide_data: Dict[str, Any]
    ) -> None:
        """Add transportation section"""
        story.append(Paragraph("Transportation", self.styles['section']))
        story.append(Spacer(1, 15))
        
        transportation = guide_data.get("transportation", {})
        
        if transportation and not transportation.get("error"):
            for transport_type, details in transportation.items():
                if details and not isinstance(details, str):
                    story.append(Paragraph(
                        f"<b>{transport_type.replace('_', ' ').title()}</b>", 
                        self.styles['body']
                    ))
                    if isinstance(details, dict):
                        for key, value in details.items():
                            story.append(Paragraph(f"• {key}: {value}", self.styles['body']))
                    story.append(Spacer(1, 10))
        else:
            story.append(Paragraph(
                "Transportation information will be available in the full guide.", 
                self.styles['body']
            ))
    
    async def _add_accessibility_section(
        self, story: List, guide_data: Dict[str, Any]
    ) -> None:
        """Add accessibility section"""
        story.append(Paragraph("Accessibility", self.styles['section']))
        story.append(Spacer(1, 15))
        
        accessibility = guide_data.get("accessibility", {})
        
        if accessibility and not accessibility.get("error"):
            for access_type, details in accessibility.items():
                if details and not isinstance(details, str):
                    story.append(Paragraph(f"<b>{access_type.replace('_', ' ').title()}</b>", self.styles['body']))
                    if isinstance(details, dict):
                        for key, value in details.items():
                            story.append(Paragraph(f"• {key}: {value}", self.styles['body']))
                    story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("Accessibility information will be available in the full guide.", self.styles['body']))
    
    async def _add_emergency_section(self, story: List, guide_data: Dict[str, Any]) -> None:
        """Add emergency contacts section"""
        story.append(Paragraph("Emergency Contacts", self.styles['section']))
        story.append(Spacer(1, 15))
        
        practical_info = guide_data.get("practical_info", {})
        emergency_contacts = practical_info.get("emergency_contacts", {})
        
        if emergency_contacts:
            for contact_type, details in emergency_contacts.items():
                story.append(Paragraph(f"<b>{contact_type.replace('_', ' ').title()}</b>", self.styles['body']))
                if isinstance(details, dict):
                    for key, value in details.items():
                        story.append(Paragraph(f"• {key}: {value}", self.styles['body']))
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("Emergency contact information will be available in the full guide.", self.styles['body']))
    
    async def _get_hero_image(self, destination: str) -> Optional[str]:
        """Get hero image for the destination"""
        try:
            if not self.unsplash_access_key:
                return None
            
            async with aiohttp.ClientSession() as session:
                url = "https://api.unsplash.com/search/photos"
                params = {
                    "query": destination,
                    "orientation": "landscape",
                    "per_page": 1,
                    "client_id": self.unsplash_access_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("results"):
                            image_url = data["results"][0]["urls"]["regular"]
                            return await self._download_image(image_url)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get hero image: {e}")
            return None
    
    async def _get_restaurant_photo(self, name: str, cuisine: str) -> Optional[str]:
        """Get photo for restaurant"""
        try:
            if not self.unsplash_access_key:
                return None
            
            query = f"{cuisine} restaurant {name}"
            
            async with aiohttp.ClientSession() as session:
                url = "https://api.unsplash.com/search/photos"
                params = {
                    "query": query,
                    "orientation": "landscape",
                    "per_page": 1,
                    "client_id": self.unsplash_access_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("results"):
                            image_url = data["results"][0]["urls"]["small"]
                            return await self._download_image(image_url)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get restaurant photo: {e}")
            return None
    
    async def _get_attraction_photo(self, name: str, attraction_type: str) -> Optional[str]:
        """Get photo for attraction"""
        try:
            if not self.unsplash_access_key:
                return None
            
            query = f"{name} {attraction_type}"
            
            async with aiohttp.ClientSession() as session:
                url = "https://api.unsplash.com/search/photos"
                params = {
                    "query": query,
                    "orientation": "landscape",
                    "per_page": 1,
                    "client_id": self.unsplash_access_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("results"):
                            image_url = data["results"][0]["urls"]["small"]
                            return await self._download_image(image_url)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get attraction photo: {e}")
            return None
    
    async def _download_image(self, image_url: str) -> Optional[str]:
        """Download image and return local path"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Create temporary file
                        temp_path = f"/tmp/temp_image_{hash(image_url)}.jpg"
                        with open(temp_path, 'wb') as f:
                            f.write(image_data)
                        
                        return temp_path
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None
    
    def _generate_destination_colors(self, destination: str) -> Dict[str, Any]:
        """Generate destination-specific color palette"""
        if not destination:
            return {
                'primary': HexColor('#1a365d'),
                'secondary': HexColor('#2d3748'),
                'accent': HexColor('#e53e3e'),
                'gold': HexColor('#d69e2e'),
                'light': HexColor('#f7fafc'),
                'text': HexColor('#2d3748'),
                'muted': HexColor('#718096')
            }
        
        destination_lower = destination.lower()
        
        if any(place in destination_lower for place in ['paris', 'france']):
            return {
                'primary': HexColor('#8B4513'),  # Warm brown
                'secondary': HexColor('#2F4F4F'), # Dark slate gray
                'accent': HexColor('#DAA520'),   # Golden
                'gold': HexColor('#FFD700'),     # Gold
                'light': HexColor('#F5F5DC'),    # Beige
                'text': HexColor('#2F4F4F'),     # Dark slate gray
                'muted': HexColor('#696969')     # Dim gray
            }
        elif any(place in destination_lower for place in ['tokyo', 'japan']):
            return {
                'primary': HexColor('#DC143C'),  # Crimson
                'secondary': HexColor('#2F2F2F'), # Dark gray
                'accent': HexColor('#FFB6C1'),   # Light pink
                'gold': HexColor('#FF69B4'),     # Hot pink
                'light': HexColor('#F8F8FF'),    # Ghost white
                'text': HexColor('#2F2F2F'),     # Dark gray
                'muted': HexColor('#808080')     # Gray
            }
        elif any(place in destination_lower for place in ['bali', 'indonesia']):
            return {
                'primary': HexColor('#228B22'),  # Forest green
                'secondary': HexColor('#8B4513'), # Saddle brown
                'accent': HexColor('#FF6347'),   # Tomato
                'gold': HexColor('#FFA500'),     # Orange
                'light': HexColor('#F0FFF0'),    # Honeydew
                'text': HexColor('#8B4513'),     # Saddle brown
                'muted': HexColor('#A0522D')     # Sienna
            }
        elif any(place in destination_lower for place in ['santorini', 'greece']):
            return {
                'primary': HexColor('#4169E1'),  # Royal blue
                'secondary': HexColor('#191970'), # Midnight blue
                'accent': HexColor('#FFFFFF'),   # White
                'gold': HexColor('#87CEEB'),     # Sky blue
                'light': HexColor('#F0F8FF'),    # Alice blue
                'text': HexColor('#191970'),     # Midnight blue
                'muted': HexColor('#6495ED')     # Cornflower blue
            }
        else:
            return {
                'primary': HexColor('#1a365d'),
                'secondary': HexColor('#2d3748'),
                'accent': HexColor('#e53e3e'),
                'gold': HexColor('#d69e2e'),
                'light': HexColor('#f7fafc'),
                'text': HexColor('#2d3748'),
                'muted': HexColor('#718096')
            }
    
    def _determine_photo_aesthetic(self, destination: str) -> Dict[str, str]:
        """Determine photo aesthetic based on destination"""
        if not destination:
            return {'style': 'modern', 'filter': 'none'}
        
        destination_lower = destination.lower()
        
        if any(place in destination_lower for place in ['paris', 'rome', 'london']):
            return {'style': 'classic', 'filter': 'warm'}
        elif any(place in destination_lower for place in ['tokyo', 'seoul', 'singapore']):
            return {'style': 'modern', 'filter': 'vibrant'}
        elif any(place in destination_lower for place in ['bali', 'thailand', 'maldives']):
            return {'style': 'tropical', 'filter': 'bright'}
        else:
            return {'style': 'contemporary', 'filter': 'natural'}
    
    def create_magazine_pdf(self, guide_data: Dict[str, Any]) -> bytes:
        """Create magazine-quality PDF with enhanced design"""
        return self.generate_magazine_pdf(guide_data)
