#!/usr/bin/env python3
"""
Create a test PDF with realistic travel information
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor
from pathlib import Path

def create_test_trip_pdf():
    """Create a realistic test trip PDF"""
    
    # Ensure samples directory exists
    samples_dir = Path("data/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = samples_dir / "paris_trip_march2025.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#003366'),
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#006699'),
        spaceAfter=12,
    )
    
    # Build content
    content = []
    
    # Title
    content.append(Paragraph("Travel Itinerary - Paris Adventure", title_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Booking Reference
    content.append(Paragraph("Booking Confirmation", heading_style))
    content.append(Paragraph("Booking Reference: <b>TRP-2025-PAR-0315</b>", styles['Normal']))
    content.append(Paragraph("Booking Date: January 10, 2025", styles['Normal']))
    content.append(Paragraph("Travel Dates: <b>March 15-22, 2025</b>", styles['Normal']))
    content.append(Spacer(1, 0.3*inch))
    
    # Passengers
    content.append(Paragraph("Passenger Information", heading_style))
    content.append(Paragraph("Primary Passenger: <b>John Smith</b>", styles['Normal']))
    content.append(Paragraph("Email: john.smith@email.com", styles['Normal']))
    content.append(Paragraph("Phone: +44 7700 900123", styles['Normal']))
    content.append(Paragraph("Second Passenger: <b>Jane Smith</b>", styles['Normal']))
    content.append(Spacer(1, 0.3*inch))
    
    # Outbound Flight
    content.append(Paragraph("Outbound Flight Details", heading_style))
    content.append(Paragraph("<b>British Airways BA 2303</b>", styles['Normal']))
    content.append(Paragraph("Date: Saturday, March 15, 2025", styles['Normal']))
    content.append(Paragraph("From: London Heathrow (LHR) Terminal 5", styles['Normal']))
    content.append(Paragraph("To: Paris Charles de Gaulle (CDG) Terminal 2A", styles['Normal']))
    content.append(Paragraph("Departure: 10:30 AM GMT", styles['Normal']))
    content.append(Paragraph("Arrival: 12:45 PM CET (Local Time)", styles['Normal']))
    content.append(Paragraph("Seat Numbers: 12A, 12B (Economy Plus)", styles['Normal']))
    content.append(Paragraph("Baggage: 2 x 23kg checked, 2 x 10kg cabin", styles['Normal']))
    content.append(Spacer(1, 0.3*inch))
    
    # Hotel Information
    content.append(Paragraph("Accommodation Details", heading_style))
    content.append(Paragraph("<b>Hilton Paris Opera</b>", styles['Normal']))
    content.append(Paragraph("Address: 108 Rue Saint-Lazare, 75008 Paris, France", styles['Normal']))
    content.append(Paragraph("Phone: +33 1 40 08 44 44", styles['Normal']))
    content.append(Paragraph("Check-in: March 15, 2025 (3:00 PM)", styles['Normal']))
    content.append(Paragraph("Check-out: March 22, 2025 (11:00 AM)", styles['Normal']))
    content.append(Paragraph("Room Type: Deluxe Double Room with City View", styles['Normal']))
    content.append(Paragraph("Confirmation Number: HTL-PAR-456789", styles['Normal']))
    content.append(Paragraph("Breakfast: Continental breakfast included", styles['Normal']))
    content.append(Spacer(1, 0.3*inch))
    
    # Return Flight
    content.append(Paragraph("Return Flight Details", heading_style))
    content.append(Paragraph("<b>British Airways BA 2304</b>", styles['Normal']))
    content.append(Paragraph("Date: Saturday, March 22, 2025", styles['Normal']))
    content.append(Paragraph("From: Paris Charles de Gaulle (CDG) Terminal 2A", styles['Normal']))
    content.append(Paragraph("To: London Heathrow (LHR) Terminal 5", styles['Normal']))
    content.append(Paragraph("Departure: 2:30 PM CET", styles['Normal']))
    content.append(Paragraph("Arrival: 2:45 PM GMT (Local Time)", styles['Normal']))
    content.append(Paragraph("Seat Numbers: 14C, 14D (Economy Plus)", styles['Normal']))
    content.append(Spacer(1, 0.3*inch))
    
    # Additional Information
    content.append(Paragraph("Additional Services", heading_style))
    content.append(Paragraph("• Airport transfers pre-booked", styles['Normal']))
    content.append(Paragraph("• Travel insurance policy: TI-2025-00123", styles['Normal']))
    content.append(Paragraph("• Car rental: Not included", styles['Normal']))
    content.append(Paragraph("• Special requests: Vegetarian meals on flights", styles['Normal']))
    content.append(Spacer(1, 0.3*inch))
    
    # Important Notes
    content.append(Paragraph("Important Information", heading_style))
    content.append(Paragraph("• Passports must be valid for at least 6 months", styles['Normal']))
    content.append(Paragraph("• Check-in online 24 hours before departure", styles['Normal']))
    content.append(Paragraph("• Arrive at airport 2 hours before departure", styles['Normal']))
    content.append(Paragraph("• Hotel requires credit card for incidentals", styles['Normal']))
    
    # Build PDF
    doc.build(content)
    
    print(f"✅ Test PDF created: {pdf_path}")
    return str(pdf_path)

if __name__ == "__main__":
    create_test_trip_pdf()