#!/usr/bin/env python3
"""
Create a realistic travel itinerary PDF for testing
Similar to what users would actually upload
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

def create_realistic_itinerary():
    filename = "realistic_itinerary.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2*cm, height - 2*cm, "E-TICKET ITINERARY")
    
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 2.7*cm, "Booking Reference: Z28XKT")
    c.drawString(2*cm, height - 3.2*cm, "Booking Date: 25 Jul 2025")
    
    # Passenger section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 4.5*cm, "PASSENGER INFORMATION")
    c.line(2*cm, height - 4.7*cm, width - 2*cm, height - 4.7*cm)
    
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, height - 5.3*cm, "MR PETER JAMES LLOYD WALKER")
    c.drawString(2*cm, height - 5.8*cm, "Frequent Flyer: BA47940415")
    
    # Flight section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 7*cm, "FLIGHT DETAILS")
    c.line(2*cm, height - 7.2*cm, width - 2*cm, height - 7.2*cm)
    
    # Outbound flight
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 8*cm, "OUTBOUND - 09 Aug 2025")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 8.5*cm, "BA115")
    c.drawString(4*cm, height - 8.5*cm, "British Airways")
    c.drawString(2*cm, height - 9*cm, "London Heathrow (LHR) Terminal 5 → New York JFK (JFK) Terminal 8")
    c.drawString(2*cm, height - 9.5*cm, "Departure: 14:40    Arrival: 17:35")
    c.drawString(2*cm, height - 10*cm, "Seat: 1A    Class: First    Aircraft: Boeing 777-300ER")
    
    # Return flight
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 11*cm, "RETURN - 14 Aug 2025")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 11.5*cm, "BA112")
    c.drawString(4*cm, height - 11.5*cm, "British Airways")
    c.drawString(2*cm, height - 12*cm, "New York JFK (JFK) Terminal 8 → London Heathrow (LHR) Terminal 5")
    c.drawString(2*cm, height - 12.5*cm, "Departure: 18:30    Arrival: 06:30+1")
    c.drawString(2*cm, height - 13*cm, "Seat: 1A    Class: First    Aircraft: Boeing 777-300ER")
    
    # Hotel section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 14.5*cm, "ACCOMMODATION")
    c.line(2*cm, height - 14.7*cm, width - 2*cm, height - 14.7*cm)
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 15.3*cm, "Luxury Collection Manhattan Midtown")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 15.8*cm, "151 West 54th Street, New York, NY 10019")
    c.drawString(2*cm, height - 16.3*cm, "Phone: +1 917 590 5400")
    c.drawString(2*cm, height - 16.8*cm, "Check-in: 09 Aug 2025 (15:00)")
    c.drawString(2*cm, height - 17.3*cm, "Check-out: 14 Aug 2025 (11:00)")
    c.drawString(2*cm, height - 17.8*cm, "Nights: 5")
    c.drawString(2*cm, height - 18.3*cm, "Confirmation: 83313860")
    c.drawString(2*cm, height - 18.8*cm, "Room Type: Suite, King Bed")
    c.drawString(2*cm, height - 19.3*cm, "Rate: USD 641.00 per night")
    
    # Total section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 21*cm, "TRIP SUMMARY")
    c.line(2*cm, height - 21.2*cm, width - 2*cm, height - 21.2*cm)
    
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 21.8*cm, "Total Trip Cost: GBP 3,865.92")
    c.drawString(2*cm, height - 22.3*cm, "Trip Locator: ONTRLU")
    
    # Save
    c.save()
    print(f"✅ Created realistic itinerary: {filename}")
    return filename

if __name__ == "__main__":
    create_realistic_itinerary()