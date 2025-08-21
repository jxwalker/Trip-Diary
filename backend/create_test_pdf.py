#!/usr/bin/env python3
"""
Create Test PDF Documents for Workflow Testing
Generates realistic travel documents for comprehensive testing
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime, timedelta
import os


def create_flight_booking_pdf(filename: str = "test_flight_booking.pdf"):
    """Create a realistic flight booking PDF"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkblue
    )
    
    story.append(Paragraph("FLIGHT BOOKING CONFIRMATION", title_style))
    story.append(Spacer(1, 20))
    
    # Booking details
    booking_data = [
        ["Booking Reference:", "AF7X9K"],
        ["Passenger Name:", "WALKER/JAMES MR"],
        ["Booking Date:", datetime.now().strftime("%d %B %Y")],
        ["Total Amount:", "€1,247.50"]
    ]
    
    booking_table = Table(booking_data, colWidths=[2*inch, 3*inch])
    booking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(booking_table)
    story.append(Spacer(1, 30))
    
    # Flight details
    story.append(Paragraph("FLIGHT DETAILS", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Outbound flight
    outbound_date = datetime.now() + timedelta(days=30)
    return_date = outbound_date + timedelta(days=5)
    
    flight_data = [
        ["Flight", "Date", "Departure", "Arrival", "Duration"],
        [
            "AF 1234\nAir France",
            outbound_date.strftime("%d %b %Y"),
            "New York JFK\n20:30\nTerminal 1",
            "Paris CDG\n09:45+1\nTerminal 2E",
            "7h 15m"
        ],
        [
            "AF 1235\nAir France", 
            return_date.strftime("%d %b %Y"),
            "Paris CDG\n14:20\nTerminal 2E",
            "New York JFK\n17:05\nTerminal 1",
            "8h 45m"
        ]
    ]
    
    flight_table = Table(flight_data, colWidths=[1.5*inch, 1.2*inch, 1.8*inch, 1.8*inch, 1*inch])
    flight_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    
    story.append(flight_table)
    story.append(Spacer(1, 20))
    
    # Important information
    story.append(Paragraph("IMPORTANT INFORMATION", styles['Heading3']))
    story.append(Paragraph("• Check-in opens 24 hours before departure", styles['Normal']))
    story.append(Paragraph("• Arrive at airport 3 hours before international flights", styles['Normal']))
    story.append(Paragraph("• Baggage allowance: 1 x 23kg checked bag, 1 x 8kg carry-on", styles['Normal']))
    story.append(Paragraph("• Seat: 12A (Window) - Outbound, 15C (Aisle) - Return", styles['Normal']))
    
    story.append(Spacer(1, 30))
    
    # Contact information
    story.append(Paragraph("CONTACT INFORMATION", styles['Heading3']))
    story.append(Paragraph("Air France Customer Service: +1-800-237-2747", styles['Normal']))
    story.append(Paragraph("Email: customer.service@airfrance.com", styles['Normal']))
    
    doc.build(story)
    print(f"✅ Created flight booking PDF: {filename}")
    return filename


def create_hotel_booking_pdf(filename: str = "test_hotel_booking.pdf"):
    """Create a realistic hotel booking PDF"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.darkred
    )
    
    story.append(Paragraph("HOTEL RESERVATION CONFIRMATION", title_style))
    story.append(Spacer(1, 20))
    
    # Hotel information
    story.append(Paragraph("HOTEL PLAZA ATHÉNÉE", styles['Heading2']))
    story.append(Paragraph("25 Avenue Montaigne, 75008 Paris, France", styles['Normal']))
    story.append(Paragraph("Phone: +33 1 53 67 66 65", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Reservation details
    check_in = datetime.now() + timedelta(days=31)
    check_out = check_in + timedelta(days=4)
    
    reservation_data = [
        ["Confirmation Number:", "HTL789456"],
        ["Guest Name:", "James Walker"],
        ["Check-in Date:", check_in.strftime("%A, %d %B %Y")],
        ["Check-out Date:", check_out.strftime("%A, %d %B %Y")],
        ["Number of Nights:", "4"],
        ["Room Type:", "Deluxe Room with Eiffel Tower View"],
        ["Number of Guests:", "2 Adults"],
        ["Rate per Night:", "€850.00"],
        ["Total Amount:", "€3,400.00"]
    ]
    
    reservation_table = Table(reservation_data, colWidths=[2.5*inch, 3*inch])
    reservation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(reservation_table)
    story.append(Spacer(1, 30))
    
    # Room amenities
    story.append(Paragraph("ROOM AMENITIES", styles['Heading3']))
    amenities = [
        "• King-size bed with luxury linens",
        "• Marble bathroom with separate bathtub and shower",
        "• Complimentary WiFi",
        "• 24-hour room service",
        "• Minibar and Nespresso machine",
        "• Air conditioning and heating",
        "• Safe and work desk",
        "• Eiffel Tower view from private balcony"
    ]
    
    for amenity in amenities:
        story.append(Paragraph(amenity, styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Hotel services
    story.append(Paragraph("HOTEL SERVICES", styles['Heading3']))
    services = [
        "• Concierge service available 24/7",
        "• Michelin-starred restaurant Alain Ducasse au Plaza Athénée",
        "• Le Bar du Plaza for cocktails",
        "• Dior Institut spa",
        "• Fitness center",
        "• Business center",
        "• Valet parking available (€45/night)"
    ]
    
    for service in services:
        story.append(Paragraph(service, styles['Normal']))
    
    story.append(Spacer(1, 30))
    
    # Cancellation policy
    story.append(Paragraph("CANCELLATION POLICY", styles['Heading3']))
    story.append(Paragraph("Free cancellation until 48 hours before check-in. Late cancellation or no-show will result in a charge of one night's stay.", styles['Normal']))
    
    doc.build(story)
    print(f"✅ Created hotel booking PDF: {filename}")
    return filename


def create_comprehensive_itinerary_pdf(filename: str = "test_comprehensive_itinerary.pdf"):
    """Create a comprehensive travel itinerary PDF"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        textColor=colors.darkgreen
    )
    
    story.append(Paragraph("PARIS LUXURY GETAWAY ITINERARY", title_style))
    story.append(Spacer(1, 20))
    
    # Trip overview
    story.append(Paragraph("TRIP OVERVIEW", styles['Heading2']))
    
    trip_dates = datetime.now() + timedelta(days=31)
    
    overview_data = [
        ["Destination:", "Paris, France"],
        ["Travel Dates:", f"{trip_dates.strftime('%B %d')} - {(trip_dates + timedelta(days=4)).strftime('%B %d, %Y')}"],
        ["Duration:", "5 Days, 4 Nights"],
        ["Travelers:", "2 Adults"],
        ["Travel Style:", "Luxury Cultural Experience"],
        ["Budget Range:", "€5,000 - €7,000"]
    ]
    
    overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(overview_table)
    story.append(Spacer(1, 30))
    
    # Preferences
    story.append(Paragraph("TRAVEL PREFERENCES", styles['Heading2']))
    preferences = [
        "• Interests: Art, Architecture, Fine Dining, Wine, Shopping, Museums",
        "• Cuisine: French, Italian, International fine dining",
        "• Activity Level: Moderate walking, cultural experiences",
        "• Accommodation: 5-star luxury hotels with character",
        "• Transportation: Taxis, walking, occasional metro",
        "• Nightlife: Sophisticated bars, wine bars, cultural events"
    ]
    
    for pref in preferences:
        story.append(Paragraph(pref, styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Special requests
    story.append(Paragraph("SPECIAL REQUESTS", styles['Heading3']))
    story.append(Paragraph("• Restaurant reservations at Michelin-starred establishments", styles['Normal']))
    story.append(Paragraph("• Private museum tours if available", styles['Normal']))
    story.append(Paragraph("• Wine tasting experiences", styles['Normal']))
    story.append(Paragraph("• Shopping assistance for luxury boutiques", styles['Normal']))
    
    story.append(Spacer(1, 30))
    
    # Contact information
    story.append(Paragraph("EMERGENCY CONTACTS", styles['Heading2']))
    story.append(Paragraph("Primary Contact: James Walker", styles['Normal']))
    story.append(Paragraph("Phone: +1 (555) 123-4567", styles['Normal']))
    story.append(Paragraph("Email: james.walker@email.com", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Travel Insurance: Policy #TI789456123", styles['Normal']))
    story.append(Paragraph("Insurance Company: Global Travel Protection", styles['Normal']))
    story.append(Paragraph("Emergency Assistance: +1-800-555-0199", styles['Normal']))
    
    doc.build(story)
    print(f"✅ Created comprehensive itinerary PDF: {filename}")
    return filename


def main():
    """Create all test PDF documents"""
    
    print("🔧 Creating test PDF documents for workflow testing...")
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Create test PDFs
    flight_pdf = create_flight_booking_pdf("uploads/test_flight_booking.pdf")
    hotel_pdf = create_hotel_booking_pdf("uploads/test_hotel_booking.pdf")
    itinerary_pdf = create_comprehensive_itinerary_pdf("uploads/test_comprehensive_itinerary.pdf")
    
    print(f"\n✅ All test PDFs created successfully!")
    print(f"   Flight booking: {flight_pdf}")
    print(f"   Hotel booking: {hotel_pdf}")
    print(f"   Comprehensive itinerary: {itinerary_pdf}")
    print(f"\n💡 Use these files for testing the complete workflow")


if __name__ == "__main__":
    main()
