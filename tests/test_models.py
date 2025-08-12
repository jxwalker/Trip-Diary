import pytest
from datetime import datetime
from src.models.events import TravelEvent, Flight, Hotel

def test_travel_event_sorting():
    """Test that TravelEvent objects can be sorted correctly."""
    events = [
        TravelEvent("2024-12-20", "16:00", "flight_departure", "Flight 1"),
        TravelEvent("2024-12-20", "14:00", "flight_checkin", "Check in"),
        TravelEvent("2024-12-21", "01:40", "flight_arrival", "Arrival")
    ]
    
    sorted_events = sorted(events)
    assert sorted_events[0].time == "14:00"  # Check-in should be first
    assert sorted_events[-1].date == "2024-12-21"  # Arrival should be last

def test_flight_creation(sample_flight):
    """Test Flight object creation and attributes."""
    assert sample_flight.flight_number == "BA2303"
    assert sample_flight.operator == "Qatar Airways"
    assert sample_flight.departure_time == "16:00"
    assert sample_flight.arrival_terminal is None

def test_hotel_creation(sample_hotel):
    """Test hotel creation with valid data."""
    assert sample_hotel.name == "Phuket Marriott Resort and Spa, Nai Yang Beach"
    assert sample_hotel.check_in_date == "2024-12-21"
    assert sample_hotel.room_features == "WiFi, TV, Pool Access"

def test_flight_string_representation(sample_flight):
    """Test Flight string representation."""
    flight_str = str(sample_flight)
    assert "BA2303" in flight_str
    assert "Heathrow Terminal 4 → Doha" in flight_str

def test_hotel_string_representation(sample_hotel):
    """Test Hotel string representation."""
    hotel_str = str(sample_hotel)
    assert "Phuket Marriott Resort" in hotel_str
    assert "2024-12-21 to 2024-12-27" in hotel_str

def test_travel_event_comparison():
    """Test TravelEvent comparison logic."""
    event1 = TravelEvent("2024-12-20", "14:00", "type1", "Event 1")
    event2 = TravelEvent("2024-12-20", "14:00", "type2", "Event 2")
    event3 = TravelEvent("2024-12-20", "15:00", "type3", "Event 3")
    event4 = TravelEvent("2024-12-21", "14:00", "type4", "Event 4")
    
    assert event1 <= event2  # Same date and time
    assert event1 < event3   # Same date, different time
    assert event1 < event4   # Different date
    assert event4 > event1   # Different date reverse comparison