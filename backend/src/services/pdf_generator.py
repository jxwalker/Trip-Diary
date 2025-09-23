"""
PDF Generator Service
Creates beautiful PDF travel packs with enhanced guide content
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, 
    Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from pathlib import Path
from typing import Dict, List, Any, Optional
import os
from datetime import datetime
import html
import tempfile
import urllib.request
import hashlib

from .maps_service import MapsService

class TravelPackGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._image_cache: Dict[str, str] = {}
        self.theme = {
            "primary": colors.HexColor('#0ea5e9'),
            "secondary": colors.HexColor('#0284c7'),
            "accent": colors.HexColor('#0369a1')
        }
        self._register_fonts()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        title_font = 'Helvetica-Bold'
        body_font = 'Helvetica'
        if 'PlayfairDisplay' in pdfmetrics.getRegisteredFontNames():
            title_font = 'PlayfairDisplay'
        if 'Inter' in pdfmetrics.getRegisteredFontNames():
            body_font = 'Inter'

        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            leading=32,
            textColor=self.theme['primary'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=title_font
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=self.theme['secondary'],
            spaceAfter=12,
            spaceBefore=20,
            fontName=title_font
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=self.theme['accent'],
            spaceAfter=8,
            spaceBefore=12,
            fontName=title_font
        ))
        
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName=body_font
        ))
        
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['BodyText'],
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=4,
            textColor=colors.HexColor('#666666'),
            fontName=body_font
        ))
        
        self.styles.add(ParagraphStyle(
            name='Caption',
            parent=self.styles['BodyText'],
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_LEFT,
            spaceAfter=4,
            fontName=body_font
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#0284c7'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#0369a1'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['BodyText'],
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=4,
            textColor=colors.HexColor('#666666')
        ))
    
    async def generate(self, trip_id: str, itinerary: Dict, 
                      recommendations: Dict, enhanced_guide: Dict = None) -> str:
        """
        Generate PDF travel pack with enhanced guide content
        """
        # Create output path
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        pdf_path = output_dir / f"travel_pack_{trip_id}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Build content
        story = []
        
        # Cover page (use hero image if available)
        story.extend(await self._create_cover_page(itinerary, enhanced_guide))
        story.append(PageBreak())
        
        # Trip overview
        story.extend(self._create_trip_overview(itinerary))
        story.append(PageBreak())
        
        # Enhanced Guide Summary (if available)
        if enhanced_guide and enhanced_guide.get("summary"):
            story.extend(self._create_guide_summary(enhanced_guide))
            story.append(PageBreak())
        
        # Flight information
        if itinerary.get("flights"):
            story.extend(self._create_flight_section(itinerary["flights"]))
            story.append(PageBreak())
        
        # Accommodation information
        if itinerary.get("accommodations"):
            story.extend(
                self._create_accommodation_section(itinerary["accommodations"])
            )
            story.append(PageBreak())
        
        # Weather (from enhanced guide if available)
        if enhanced_guide and enhanced_guide.get("weather"):
            story.extend(
                self._create_weather_section(enhanced_guide["weather"])
            )
            story.append(PageBreak())

        # Static Map (hotel + key POIs) if Maps API configured
        static_map = await self._maybe_create_static_map(
            itinerary, enhanced_guide
        )
        if static_map:
            story.extend(static_map)
            story.append(PageBreak())

        # Daily Itinerary (from enhanced guide or basic schedule)
        if enhanced_guide and enhanced_guide.get("daily_itinerary"):
            story.extend(await self._create_enhanced_itinerary(
                enhanced_guide["daily_itinerary"], enhanced_guide
            ))
            story.append(PageBreak())
        elif itinerary.get("daily_schedule"):
            story.extend(
                self._create_daily_schedule(itinerary["daily_schedule"])
            )
            story.append(PageBreak())
        
        # Restaurant Recommendations (from enhanced guide)
        if enhanced_guide and enhanced_guide.get("restaurants"):
            story.extend(
                self._create_restaurant_section(enhanced_guide["restaurants"])
            )
            story.append(PageBreak())
        
        # Attractions (from enhanced guide)
        if enhanced_guide and enhanced_guide.get("attractions"):
            story.extend(
                self._create_attractions_section(enhanced_guide["attractions"])
            )
            story.append(PageBreak())
        
        # Basic Recommendations (fallback)
        if recommendations:
            story.extend(self._create_recommendations_section(recommendations))
            story.append(PageBreak())
        
        # Practical Information
        if enhanced_guide and enhanced_guide.get("practical_info"):
            story.extend(
                self._create_practical_info(enhanced_guide["practical_info"])
            )
            story.append(PageBreak())
        
        # Important information
        if itinerary.get("important_info"):
            story.extend(
                self._create_important_info(itinerary["important_info"])
            )
        
        # Build PDF
        try:
            doc.build(story)
            return str(pdf_path)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating PDF: {e}")
            # Return a simple PDF even if there's an error
            story = [
                Paragraph("Travel Pack", self.styles['CustomTitle']),
                Spacer(1, 0.5*inch),
                Paragraph(f"Trip ID: {trip_id}", self.styles['InfoText']),
                Paragraph(
                    "Your travel pack is being prepared. Please try again later.", 
                    self.styles['InfoText']
                )
            ]
            doc.build(story)
            return str(pdf_path)
    
    def _safe_text(self, text: Any) -> str:
        """Safely convert text for PDF inclusion"""
        if text is None:
            return ""
        text_str = str(text)
        # Escape HTML entities
        text_str = html.escape(text_str)
        # Remove any control characters
        text_str = ''.join(
            char for char in text_str if ord(char) >= 32 or char == '\n'
        )
        return text_str
    
    async def _create_cover_page(self, itinerary: Dict, enhanced_guide: Optional[Dict]) -> List:
        """Create cover page with optional hero image and persona."""
        story: List[Any] = []
        trip_summary = itinerary.get("trip_summary", {})
        destination = trip_summary.get("destination", "Your Trip")
        persona = (enhanced_guide or {}).get("persona") or "Personalized Guide"

        # Choose hero image
        hero_url = self._choose_hero_image(enhanced_guide)
        if hero_url:
            hero_path = await self._download_image(hero_url)
            if hero_path:
                img = Image(hero_path, width=6.5*inch, height=3.8*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))

        story.extend([
            Paragraph("TRAVEL PACK", self.styles['CustomTitle']),
            Spacer(1, 0.15*inch),
            Paragraph(f"<b>{destination}</b>", self.styles['CustomTitle']),
            Spacer(1, 0.15*inch),
            Paragraph(
                f"{trip_summary.get('start_date', '')} - {trip_summary.get('end_date', '')}",
                self.styles['InfoText']
            ),
            Paragraph(f"{persona}", self.styles['SmallText']),
            Spacer(1, 0.6*inch),
            Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", self.styles['SmallText'])
        ])
        return story
    
    def _create_trip_overview(self, itinerary: Dict) -> List:
        """Create trip overview section"""
        story = []
        trip_summary = itinerary.get("trip_summary", {})
        
        story.append(Paragraph("Trip Overview", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Create overview table
        data = []
        if trip_summary.get("destination"):
            data.append(["Destination:", self._safe_text(trip_summary.get("destination"))])
        if trip_summary.get("duration"):
            data.append(["Duration:", self._safe_text(trip_summary.get("duration"))])
        if trip_summary.get("start_date"):
            data.append(["Start Date:", self._safe_text(trip_summary.get("start_date"))])
        if trip_summary.get("end_date"):
            data.append(["End Date:", self._safe_text(trip_summary.get("end_date"))])
        if trip_summary.get("total_passengers"):
            data.append(["Travelers:", self._safe_text(trip_summary.get("total_passengers"))])
        
        if data:
            table = Table(data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(table)
        
        return story
    
    def _create_guide_summary(self, enhanced_guide: Dict) -> List:
        """Create enhanced guide summary section"""
        story = []
        story.append(Paragraph("Your Personalized Travel Guide", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        if enhanced_guide.get("summary"):
            # Split summary into paragraphs for better formatting
            summary_text = self._safe_text(enhanced_guide["summary"])
            for para in summary_text.split('\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['InfoText']))
                    story.append(Spacer(1, 0.1*inch))
        
        if enhanced_guide.get("destination_insights"):
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Destination Insights", self.styles['SubHeader']))
            insights_text = self._safe_text(enhanced_guide["destination_insights"])
            for para in insights_text.split('\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['InfoText']))
                    story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_flight_section(self, flights: List[Dict]) -> List:
        """Create flight information section"""
        story = []
        story.append(Paragraph("Flight Information", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for i, flight in enumerate(flights):
            if i > 0:
                story.append(Spacer(1, 0.3*inch))
            
            # Flight header
            flight_num = self._safe_text(flight.get("flight_number", f"Flight {i+1}"))
            airline = self._safe_text(flight.get("airline", ""))
            story.append(Paragraph(f"<b>{flight_num}</b> - {airline}", self.styles['SubHeader']))
            
            # Flight details table
            data = []
            
            # Departure
            if flight.get("departure"):
                dep = flight["departure"]
                data.append([
                    "Departure:",
                    f"{self._safe_text(dep.get('airport', ''))}",
                    f"{self._safe_text(dep.get('date', ''))} at {self._safe_text(dep.get('time', ''))}"
                ])
            
            # Arrival
            if flight.get("arrival"):
                arr = flight["arrival"]
                data.append([
                    "Arrival:",
                    f"{self._safe_text(arr.get('airport', ''))}",
                    f"{self._safe_text(arr.get('date', ''))} at {self._safe_text(arr.get('time', ''))}"
                ])
            
            # Other details
            if flight.get("seat"):
                data.append(["Seat:", self._safe_text(flight.get("seat")), ""])
            if flight.get("class"):
                data.append(["Class:", self._safe_text(flight.get("class")), ""])
            
            if data:
                table = Table(data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(table)
        
        return story
    
    def _create_accommodation_section(self, accommodations: List[Dict]) -> List:
        """Create accommodation information section"""
        story = []
        story.append(Paragraph("Accommodation", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for hotel in accommodations:
            story.append(Paragraph(f"<b>{self._safe_text(hotel.get('name', 'Hotel'))}</b>", self.styles['SubHeader']))
            
            data = []
            if hotel.get("address"):
                data.append(["Address:", self._safe_text(hotel.get("address"))])
            if hotel.get("check_in"):
                data.append(["Check-in:", self._safe_text(hotel.get("check_in"))])
            if hotel.get("check_out"):
                data.append(["Check-out:", self._safe_text(hotel.get("check_out"))])
            if hotel.get("confirmation"):
                data.append(["Confirmation:", self._safe_text(hotel.get("confirmation"))])
            if hotel.get("phone"):
                data.append(["Phone:", self._safe_text(hotel.get("phone"))])
            
            if data:
                table = Table(data, colWidths=[1.5*inch, 4.5*inch])
                table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(table)
                story.append(Spacer(1, 0.2*inch))
        
        return story
    
    async def _create_enhanced_itinerary(self, daily_itinerary: List[Dict], enhanced_guide: Dict) -> List:
        """Create enhanced daily itinerary section with hero images and collages"""
        story: List[Any] = []
        story.append(Paragraph("Daily Itinerary", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))

        used_photos: set[str] = set()
        all_images: List[str] = []
        for section in ("attractions", "restaurants"):
            for item in enhanced_guide.get(section, []) or []:
                photo = item.get("photo") or (item.get("photos") or [None])[0]
                if photo:
                    all_images.append(photo)

        for idx, day in enumerate(daily_itinerary):
            # Day header
            day_title = self._safe_text(day.get("title", f"Day {day.get('day', idx+1)}"))
            story.append(Paragraph(f"<b>{day_title}</b>", self.styles['SubHeader']))

            # Hero for day
            day_images = self._pick_day_images(all_images, used_photos, max_count=3)
            if day_images:
                # First image as hero
                hero_path = await self._download_image(day_images[0])
                if hero_path:
                    story.append(Image(hero_path, width=6*inch, height=3.2*inch))
                    story.append(Spacer(1, 0.1*inch))
                # Remaining as collage
                if len(day_images) > 1:
                    row_imgs: List[Image] = []
                    for url in day_images[1:3]:
                        img_path = await self._download_image(url)
                        if img_path:
                            row_imgs.append(Image(img_path, width=2.9*inch, height=1.9*inch))
                    if row_imgs:
                        # Place images vertically with small gap
                        for img in row_imgs:
                            story.append(img)
                            story.append(Spacer(1, 0.05*inch))

            # Activities block
            # Support either activities array (simple) or morning/afternoon/evening keys
            if day.get("activities"):
                for activity in day["activities"]:
                    story.append(Paragraph(f"• {self._safe_text(activity)}", self.styles['InfoText']))
            else:
                for part in ("morning", "afternoon", "evening"):
                    if day.get(part):
                        story.append(Paragraph(part.title(), self.styles['SmallText']))
                        for act in day[part]:
                            story.append(Paragraph(f"• {self._safe_text(act)}", self.styles['InfoText']))

            story.append(Spacer(1, 0.25*inch))
        
        return story
    
    def _create_daily_schedule(self, schedule: List[Dict]) -> List:
        """Create basic daily schedule section"""
        story = []
        story.append(Paragraph("Daily Schedule", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for day in schedule:
            story.append(Paragraph(f"<b>Day {day.get('day', '')} - {self._safe_text(day.get('date', ''))}</b>", self.styles['SubHeader']))
            
            if day.get("activities"):
                for activity in day["activities"]:
                    time = self._safe_text(activity.get("time", ""))
                    desc = self._safe_text(activity.get("description", ""))
                    if time:
                        story.append(Paragraph(f"<b>{time}:</b> {desc}", self.styles['InfoText']))
                    else:
                        story.append(Paragraph(f"• {desc}", self.styles['InfoText']))
            
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_restaurant_section(self, restaurants: List[Dict]) -> List:
        """Create restaurant recommendations section with photos and QR codes"""
        story = []
        story.append(Paragraph("Recommended Restaurants", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for restaurant in restaurants[:10]:  # Limit to 10 for PDF size
            name = self._safe_text(restaurant.get("name", "Restaurant"))
            story.append(Paragraph(f"<b>{name}</b>", self.styles['SubHeader']))

            # Photo if available
            photo = restaurant.get("photo") or (restaurant.get("photos") or [None])[0]
            if photo:
                try:
                    # Use synchronous helper to avoid complicating flow
                    img_path = self._image_cache.get(photo)
                    if not img_path:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                            urllib.request.urlretrieve(photo, tmp.name)
                            img_path = tmp.name
                            self._image_cache[photo] = img_path
                    story.append(Image(img_path, width=3.5*inch, height=2.3*inch))
                    story.append(Spacer(1, 0.1*inch))
                except Exception:
                    pass
            
            if restaurant.get("description"):
                story.append(Paragraph(self._safe_text(restaurant["description"]), self.styles['InfoText']))
            
            # Details
            if restaurant.get("details"):
                for detail in restaurant["details"][:5]:  # Limit details
                    story.append(Paragraph(f"• {self._safe_text(detail)}", self.styles['SmallText']))

            # Booking QR
            booking = (
                restaurant.get("booking_url")
                or (restaurant.get("booking_urls") or {}).get("opentable")
                or restaurant.get("website")
            )
            if booking:
                story.append(Spacer(1, 0.05*inch))
                story.append(Paragraph("Reserve / View Menu:", self.styles['SmallText']))
                story.append(self._qr_flowable(booking))
            
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_attractions_section(self, attractions: List[Dict]) -> List:
        """Create attractions section with photos and QR codes"""
        story = []
        story.append(Paragraph("Must-See Attractions", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for attraction in attractions[:10]:  # Limit to 10 for PDF size
            name = self._safe_text(attraction.get("name", "Attraction"))
            story.append(Paragraph(f"<b>{name}</b>", self.styles['SubHeader']))

            photo = attraction.get("photo") or (attraction.get("photos") or [None])[0]
            if photo:
                try:
                    img_path = self._image_cache.get(photo)
                    if not img_path:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                            urllib.request.urlretrieve(photo, tmp.name)
                            img_path = tmp.name
                            self._image_cache[photo] = img_path
                    story.append(Image(img_path, width=3.5*inch, height=2.3*inch))
                    story.append(Spacer(1, 0.1*inch))
                except Exception:
                    pass
            
            if attraction.get("type"):
                story.append(Paragraph(f"Type: {self._safe_text(attraction['type'])}", self.styles['SmallText']))
            
            if attraction.get("description"):
                story.append(Paragraph(self._safe_text(attraction["description"]), self.styles['InfoText']))

            # Map QR
            map_url = attraction.get("google_maps_url") or attraction.get("website")
            if map_url:
                story.append(Spacer(1, 0.05*inch))
                story.append(Paragraph("Open in Maps:", self.styles['SmallText']))
                story.append(self._qr_flowable(map_url))
            
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_recommendations_section(self, recommendations: Dict) -> List:
        """Create basic recommendations section"""
        story = []
        story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Restaurants
        if recommendations.get("restaurants"):
            story.append(Paragraph("Restaurants", self.styles['SubHeader']))
            for rest in recommendations["restaurants"][:5]:
                story.append(Paragraph(f"• <b>{self._safe_text(rest.get('name', ''))}</b> - {self._safe_text(rest.get('type', ''))}", self.styles['InfoText']))
            story.append(Spacer(1, 0.2*inch))
        
        # Activities
        if recommendations.get("activities"):
            story.append(Paragraph("Activities", self.styles['SubHeader']))
            for activity in recommendations["activities"][:5]:
                story.append(Paragraph(f"• {self._safe_text(activity.get('name', ''))}", self.styles['InfoText']))
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_practical_info(self, practical_info: Dict) -> List:
        """Create practical information section"""
        story = []
        story.append(Paragraph("Practical Information", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for category, items in practical_info.items():
            story.append(Paragraph(self._safe_text(category).title(), self.styles['SubHeader']))
            
            if isinstance(items, list):
                for item in items[:5]:  # Limit items
                    story.append(Paragraph(f"• {self._safe_text(item)}", self.styles['InfoText']))
            else:
                story.append(Paragraph(self._safe_text(items), self.styles['InfoText']))
            
            story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _create_important_info(self, info: Dict) -> List:
        """Create important information section"""
        story = []
        story.append(Paragraph("Important Information", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        data = []
        for key, value in info.items():
            label = key.replace("_", " ").title()
            data.append([f"{label}:", self._safe_text(value)])
        
        if data:
            table = Table(data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(table)
        
        return story

    def _create_weather_section(self, weather_data: Any) -> List:
        """Create a weather section if structured data is available."""
        story = []
        story.append(Paragraph("Weather Forecast", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))

        # Accept either list of dicts or simple strings
        if isinstance(weather_data, list) and weather_data and isinstance(weather_data[0], dict):
            # Tabular daily forecast
            data = [["Date", "High", "Low", "Condition"]]
            for day in weather_data[:10]:
                data.append([
                    self._safe_text(day.get("date", "")),
                    self._safe_text(day.get("temp_high", "")),
                    self._safe_text(day.get("temp_low", "")),
                    self._safe_text(day.get("condition", "")),
                ])
            table = Table(data, colWidths=[1.5*inch, 1*inch, 1*inch, 2.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0,0), (-1,-1), 0.25, colors.HexColor('#cbd5e1')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(table)
        else:
            # Fallback to plain paragraphs (still real content, not mocks)
            if isinstance(weather_data, list):
                for line in weather_data[:10]:
                    story.append(Paragraph(self._safe_text(str(line)), self.styles['InfoText']))
            elif isinstance(weather_data, dict):
                for k, v in weather_data.items():
                    story.append(Paragraph(f"<b>{self._safe_text(str(k)).title()}:</b> {self._safe_text(str(v))}", self.styles['InfoText']))
        return story

    async def _maybe_create_static_map(self, itinerary: Dict, enhanced_guide: Dict | None) -> List:
        """Insert a static map if we can build a URL with an API key and markers."""
        try:
            maps = MapsService()
            locations: List[Dict[str, Any]] = []

            # Hotel marker
            hotels = itinerary.get("accommodations", [])
            if hotels:
                address = hotels[0].get("address")
                if address:
                    locations.append({"address": address})

            # Top restaurants
            if enhanced_guide and enhanced_guide.get("restaurants"):
                for r in enhanced_guide["restaurants"][:5]:
                    addr = r.get("address") or r.get("location")
                    if addr:
                        locations.append({"address": addr})

            # Top attractions
            if enhanced_guide and enhanced_guide.get("attractions"):
                for a in enhanced_guide["attractions"][:5]:
                    addr = a.get("address")
                    if addr:
                        locations.append({"address": addr})

            if not locations:
                return []

            url = maps.get_static_map_url(locations)
            if not url:
                return []

            # Download to temp file for ReportLab Image
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                urllib.request.urlretrieve(url, tmp.name)
                tmp_path = tmp.name

            img = Image(tmp_path, width=6*inch, height=4*inch)
            return [Paragraph("Map Overview", self.styles['SectionHeader']), Spacer(1, 0.1*inch), img]
        except Exception as e:
            print(f"Static map generation failed: {e}")
            return []

    def _register_fonts(self) -> None:
        """Attempt to register custom fonts if available (PlayfairDisplay, Inter)."""
        try:
            base = Path(__file__).parent.parent.parent / "assets" / "fonts"
            playfair = base / "PlayfairDisplay-Regular.ttf"
            inter = base / "Inter-Regular.ttf"
            if playfair.exists():
                pdfmetrics.registerFont(TTFont('PlayfairDisplay', str(playfair)))
            if inter.exists():
                pdfmetrics.registerFont(TTFont('Inter', str(inter)))
        except Exception:
            pass

    async def _download_image(self, url: str) -> Optional[str]:
        """Download and cache image, return local path."""
        if not url:
            return None
        if url in self._image_cache:
            return self._image_cache[url]
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                urllib.request.urlretrieve(url, tmp.name)
                self._image_cache[url] = tmp.name
                return tmp.name
        except Exception:
            return None

    def _qr_flowable(self, url: str) -> Drawing:
        """Create a QR code flowable for a URL."""
        code = qr.QrCodeWidget(url)
        bounds = code.getBounds()
        size = 72  # 1 inch square
        w = bounds[2] - bounds[0]
        h = bounds[3] - bounds[1]
        d = Drawing(size, size, transform=[size/w, 0, 0, size/h, 0, 0])
        d.add(code)
        return d

    def _choose_hero_image(self, enhanced_guide: Optional[Dict]) -> Optional[str]:
        """Pick a hero image from attractions or restaurants."""
        if not enhanced_guide:
            return None
        for section in ("attractions", "restaurants"):
            items = enhanced_guide.get(section) or []
            for it in items:
                photo = it.get("photo") or (it.get("photos") or [None])[0]
                if photo:
                    return photo
        return None

    def _pick_day_images(self, all_images: List[str], used: set, max_count: int = 3) -> List[str]:
        picks: List[str] = []
        for url in all_images:
            if url in used:
                continue
            picks.append(url)
            used.add(url)
            if len(picks) >= max_count:
                break
        return picks
