"""
PDF Generator Service
Creates beautiful PDF travel packs with enhanced guide content
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from pathlib import Path
from typing import Dict, List, Any
import os
from datetime import datetime
import html

class TravelPackGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0ea5e9'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
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
    
    async def generate(self, trip_id: str, itinerary: Dict, recommendations: Dict, enhanced_guide: Dict = None) -> str:
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
        
        # Cover page
        story.extend(self._create_cover_page(itinerary))
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
            story.extend(self._create_accommodation_section(itinerary["accommodations"]))
            story.append(PageBreak())
        
        # Daily Itinerary (from enhanced guide or basic schedule)
        if enhanced_guide and enhanced_guide.get("daily_itinerary"):
            story.extend(self._create_enhanced_itinerary(enhanced_guide["daily_itinerary"]))
            story.append(PageBreak())
        elif itinerary.get("daily_schedule"):
            story.extend(self._create_daily_schedule(itinerary["daily_schedule"]))
            story.append(PageBreak())
        
        # Restaurant Recommendations (from enhanced guide)
        if enhanced_guide and enhanced_guide.get("restaurants"):
            story.extend(self._create_restaurant_section(enhanced_guide["restaurants"]))
            story.append(PageBreak())
        
        # Attractions (from enhanced guide)
        if enhanced_guide and enhanced_guide.get("attractions"):
            story.extend(self._create_attractions_section(enhanced_guide["attractions"]))
            story.append(PageBreak())
        
        # Basic Recommendations (fallback)
        if recommendations:
            story.extend(self._create_recommendations_section(recommendations))
            story.append(PageBreak())
        
        # Practical Information
        if enhanced_guide and enhanced_guide.get("practical_info"):
            story.extend(self._create_practical_info(enhanced_guide["practical_info"]))
            story.append(PageBreak())
        
        # Important information
        if itinerary.get("important_info"):
            story.extend(self._create_important_info(itinerary["important_info"]))
        
        # Build PDF
        try:
            doc.build(story)
            return str(pdf_path)
        except Exception as e:
            print(f"Error generating PDF: {e}")
            # Return a simple PDF even if there's an error
            story = [
                Paragraph("Travel Pack", self.styles['CustomTitle']),
                Spacer(1, 0.5*inch),
                Paragraph(f"Trip ID: {trip_id}", self.styles['InfoText']),
                Paragraph("Your travel pack is being prepared. Please try again later.", self.styles['InfoText'])
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
        text_str = ''.join(char for char in text_str if ord(char) >= 32 or char == '\n')
        return text_str
    
    def _create_cover_page(self, itinerary: Dict) -> List:
        """Create cover page"""
        trip_summary = itinerary.get("trip_summary", {})
        destination = trip_summary.get("destination", "Your Trip")
        
        return [
            Spacer(1, 2*inch),
            Paragraph("TRAVEL PACK", self.styles['CustomTitle']),
            Spacer(1, 0.5*inch),
            Paragraph(f"<b>{destination}</b>", self.styles['CustomTitle']),
            Spacer(1, 0.3*inch),
            Paragraph(
                f"{trip_summary.get('start_date', '')} - {trip_summary.get('end_date', '')}",
                self.styles['InfoText']
            ),
            Spacer(1, 2*inch),
            Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", self.styles['SmallText'])
        ]
    
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
    
    def _create_enhanced_itinerary(self, daily_itinerary: List[Dict]) -> List:
        """Create enhanced daily itinerary section"""
        story = []
        story.append(Paragraph("Daily Itinerary", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for day in daily_itinerary:
            # Day header
            day_title = self._safe_text(day.get("title", f"Day {day.get('day', '')}"))
            story.append(Paragraph(f"<b>{day_title}</b>", self.styles['SubHeader']))
            
            # Activities
            if day.get("activities"):
                for activity in day["activities"]:
                    story.append(Paragraph(f"• {self._safe_text(activity)}", self.styles['InfoText']))
            
            story.append(Spacer(1, 0.2*inch))
        
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
        """Create restaurant recommendations section"""
        story = []
        story.append(Paragraph("Recommended Restaurants", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for restaurant in restaurants[:10]:  # Limit to 10 for PDF size
            name = self._safe_text(restaurant.get("name", "Restaurant"))
            story.append(Paragraph(f"<b>{name}</b>", self.styles['SubHeader']))
            
            if restaurant.get("description"):
                story.append(Paragraph(self._safe_text(restaurant["description"]), self.styles['InfoText']))
            
            # Details
            if restaurant.get("details"):
                for detail in restaurant["details"][:5]:  # Limit details
                    story.append(Paragraph(f"• {self._safe_text(detail)}", self.styles['SmallText']))
            
            story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _create_attractions_section(self, attractions: List[Dict]) -> List:
        """Create attractions section"""
        story = []
        story.append(Paragraph("Must-See Attractions", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        for attraction in attractions[:10]:  # Limit to 10 for PDF size
            name = self._safe_text(attraction.get("name", "Attraction"))
            story.append(Paragraph(f"<b>{name}</b>", self.styles['SubHeader']))
            
            if attraction.get("type"):
                story.append(Paragraph(f"Type: {self._safe_text(attraction['type'])}", self.styles['SmallText']))
            
            if attraction.get("description"):
                story.append(Paragraph(self._safe_text(attraction["description"]), self.styles['InfoText']))
            
            story.append(Spacer(1, 0.15*inch))
        
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