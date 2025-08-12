#!/usr/bin/env python3
"""
Create a sample travel ticket PDF for testing
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime, timedelta

def create_test_ticket():
    # Create PDF
    filename = "sample_ticket.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Colors
    primary_color = HexColor('#1e40af')  # Blue
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(primary_color)
    c.drawString(2*cm, height - 2*cm, "BOARDING PASS")
    
    # Airline
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 3*cm, "British Airways")
    
    # Passenger info
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor('#111827'))
    c.drawString(2*cm, height - 4.5*cm, "PASSENGER NAME")
    c.setFont("Helvetica", 14)
    c.drawString(2*cm, height - 5.2*cm, "MR JOHN SMITH")
    
    # Flight info - Left column
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 7*cm, "FLIGHT")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(HexColor('#111827'))
    c.drawString(2*cm, height - 7.8*cm, "BA283")
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 9.5*cm, "FROM")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor('#111827'))
    c.drawString(2*cm, height - 10.3*cm, "LHR")
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, height - 10.9*cm, "London Heathrow")
    c.drawString(2*cm, height - 11.4*cm, "Terminal 5")
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 13*cm, "DATE")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor('#111827'))
    c.drawString(2*cm, height - 13.7*cm, "15 MAR 2025")
    
    # Flight info - Middle column
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(8*cm, height - 7*cm, "SEAT")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(HexColor('#111827'))
    c.drawString(8*cm, height - 7.8*cm, "12A")
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(8*cm, height - 9.5*cm, "TO")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor('#111827'))
    c.drawString(8*cm, height - 10.3*cm, "LAX")
    c.setFont("Helvetica", 11)
    c.drawString(8*cm, height - 10.9*cm, "Los Angeles")
    c.drawString(8*cm, height - 11.4*cm, "Terminal B")
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(8*cm, height - 13*cm, "DEPARTURE")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor('#111827'))
    c.drawString(8*cm, height - 13.7*cm, "10:30")
    
    # Flight info - Right column
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(14*cm, height - 7*cm, "GATE")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(HexColor('#111827'))
    c.drawString(14*cm, height - 7.8*cm, "A23")
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(14*cm, height - 9.5*cm, "CLASS")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor('#111827'))
    c.drawString(14*cm, height - 10.3*cm, "ECONOMY")
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(14*cm, height - 13*cm, "ARRIVAL")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor('#111827'))
    c.drawString(14*cm, height - 13.7*cm, "13:45")
    
    # Booking reference
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 15.5*cm, "BOOKING REFERENCE")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(primary_color)
    c.drawString(2*cm, height - 16.3*cm, "ABC123")
    
    # Frequent flyer
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(8*cm, height - 15.5*cm, "FREQUENT FLYER")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor('#111827'))
    c.drawString(8*cm, height - 16.3*cm, "BA1234567")
    
    # Barcode placeholder
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 18.5*cm, "|||||| |||| | |||| |||| | |||| |||||| |||| |||||")
    
    # Footer
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor('#9ca3af'))
    c.drawString(2*cm, 2*cm, "Please arrive at the gate at least 30 minutes before departure")
    
    # Save
    c.save()
    print(f"✅ Created test ticket: {filename}")
    
    return filename

def create_hotel_booking():
    """Create a sample hotel booking PDF"""
    filename = "sample_hotel.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(HexColor('#7c3aed'))  # Purple
    c.drawString(2*cm, height - 2*cm, "HOTEL CONFIRMATION")
    
    # Hotel name
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HexColor('#111827'))
    c.drawString(2*cm, height - 3.5*cm, "The Grand Hotel Los Angeles")
    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 4.2*cm, "123 Sunset Boulevard, Los Angeles, CA 90028")
    c.drawString(2*cm, height - 4.8*cm, "Tel: +1 (310) 555-0100")
    
    # Confirmation details
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 6.5*cm, "CONFIRMATION NUMBER")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(HexColor('#7c3aed'))
    c.drawString(2*cm, height - 7.2*cm, "HTL789456")
    
    # Guest info
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 9*cm, "GUEST NAME")
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor('#111827'))
    c.drawString(2*cm, height - 9.7*cm, "Mr. John Smith")
    
    # Stay details
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 11.5*cm, "CHECK-IN")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor('#111827'))
    c.drawString(2*cm, height - 12.2*cm, "15 March 2025")
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, height - 12.8*cm, "After 3:00 PM")
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(8*cm, height - 11.5*cm, "CHECK-OUT")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor('#111827'))
    c.drawString(8*cm, height - 12.2*cm, "20 March 2025")
    c.setFont("Helvetica", 11)
    c.drawString(8*cm, height - 12.8*cm, "Before 11:00 AM")
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(14*cm, height - 11.5*cm, "NIGHTS")
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(HexColor('#111827'))
    c.drawString(14*cm, height - 12.2*cm, "5")
    
    # Room details
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 14.5*cm, "ROOM TYPE")
    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor('#111827'))
    c.drawString(2*cm, height - 15.2*cm, "Deluxe King Suite")
    c.drawString(2*cm, height - 15.8*cm, "1 King Bed, City View")
    
    # Rate
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawString(2*cm, height - 17.5*cm, "RATE")
    c.setFont("Helvetica", 12)
    c.setFillColor(HexColor('#111827'))
    c.drawString(2*cm, height - 18.2*cm, "USD 250.00 per night")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 18.8*cm, "Total: USD 1,250.00")
    
    # Save
    c.save()
    print(f"✅ Created hotel booking: {filename}")
    
    return filename

if __name__ == "__main__":
    try:
        from reportlab.lib.pagesizes import A4
        print("Creating sample travel documents for testing...\n")
        create_test_ticket()
        create_hotel_booking()
        print("\n✅ Test documents created successfully!")
        print("\nYou can now test with:")
        print("  python test_multimodal.py")
    except ImportError:
        print("❌ reportlab not installed")
        print("\nInstall it with:")
        print("  pip install reportlab")
        print("\nOr test with any existing PDF/image files")