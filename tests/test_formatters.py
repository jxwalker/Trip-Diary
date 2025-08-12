import pytest
from src.formatters.timeline_formatter import TimelineFormatter
from src.formatters.summary_formatter import SummaryFormatter
from src.models.events import Flight, Hotel, Passenger

def test_timeline_formatter(sample_flight, sample_hotel):
    """Test timeline formatting."""
    timeline = TimelineFormatter.format_timeline([sample_flight], [sample_hotel])
    
    # Check check-in time (2 hours before flight)
    assert "2024-12-20 14:00: Check in for flight BA2303" in timeline
    # Check departure
    assert "2024-12-20 16:00: Flight BA2303 departs Heathrow → Doha" in timeline
    # Check arrival
    assert "2024-12-21 01:40: Flight BA2303 arrives at Doha" in timeline
    # Check hotel check-in
    assert "Check in to Phuket Marriott Resort" in timeline

def test_summary_formatter(sample_flight, sample_hotel):
    """Test summary formatting."""
    sample_passenger = Passenger(
        title="MR",
        first_name="Test",
        last_name="User"
    )
    summary = SummaryFormatter.format_summary(
        [sample_flight], 
        [sample_hotel],
        [sample_passenger]
    )
    assert "Phuket Marriott Resort" in summary

def test_flight_details_formatting(sample_flight):
    """Test flight details formatting."""
    details = SummaryFormatter.format_flight_details(sample_flight)
    
    assert "BA2303 (Qatar Airways)" in details
    assert "Terminal 4" in details
    assert "Economy" in details
    assert "23kg" in details

def test_hotel_details_formatting(sample_hotel):
    """Test hotel details formatting."""
    details = SummaryFormatter.format_hotel_details(sample_hotel)
    
    assert "Phuket Marriott Resort" in details
    assert "2024-12-21 to 2024-12-27" in details
    assert "Premium Pool Access" in details

def test_timeline_multiple_flights(sample_flight):
    """Test timeline with multiple flights."""
    second_flight = Flight(
        flight_number="BA2304",
        operator="Qatar Airways",
        booking_reference="MYH9XH",
        departure_location="Doha",
        departure_terminal="1",
        departure_date="2024-12-21",
        departure_time="03:40",
        arrival_location="Phuket",
        arrival_terminal=None,
        arrival_date="2024-12-21",
        arrival_time="14:20",
        travel_class="Economy",
        checked_baggage="1 bag at 23kg (51lbs)",
        hand_baggage="1 handbag/laptop bag"
    )
    
    timeline = TimelineFormatter.format_timeline([sample_flight, second_flight], [])
    assert "2024-12-20 14:00: Check in for flight BA2303" in timeline
    assert "2024-12-21 01:40: Flight BA2303 arrives at Doha" in timeline
    assert "2024-12-21 03:40: Flight BA2304 departs Doha → Phuket" in timeline

def test_short_transfer_warning():
    """Test warning for short transfer times between flights."""
    first_flight = Flight(
        flight_number="BA2303",
        operator="Qatar Airways",
        booking_reference="MYH9XH",
        departure_location="London",
        departure_terminal="4",
        departure_date="2024-12-20",
        departure_time="16:00",
        arrival_location="Doha",
        arrival_terminal=None,
        arrival_date="2024-12-21",
        arrival_time="01:40",
        travel_class="Economy",
        checked_baggage="23kg",
        hand_baggage="7kg"
    )
    
    second_flight = Flight(
        flight_number="BA7000",
        operator="Qatar Airways",
        booking_reference="MYH9XH",
        departure_location="Doha",
        departure_terminal=None,
        departure_date="2024-12-21",
        departure_time="02:30",
        arrival_location="Bangkok",
        arrival_terminal=None,
        arrival_date="2024-12-21",
        arrival_time="12:55",
        travel_class="Economy",
        checked_baggage="23kg",
        hand_baggage="7kg"
    )
    
    timeline = TimelineFormatter.format_timeline([first_flight, second_flight], [])
    assert "⚠️  Warning: Only 50 minutes for transfer at Doha" in timeline

def test_transfer_time_warnings():
    """Test warnings for short transfer times between flights."""
    first_flight = Flight(
        flight_number="BA2303",
        operator="Qatar Airways",
        booking_reference="MYH9XH",
        departure_location="LHR",
        departure_terminal="4",
        departure_date="2024-12-20",
        departure_time="16:00",
        arrival_location="DOH",
        arrival_terminal=None,
        arrival_date="2024-12-21",
        arrival_time="01:40",
        travel_class="Economy",
        checked_baggage="23kg",
        hand_baggage="7kg"
    )
    
    second_flight = Flight(
        flight_number="BA7000",
        operator="Qatar Airways",
        booking_reference="MYH9XH",
        departure_location="DOH",
        departure_terminal=None,
        departure_date="2024-12-21",
        departure_time="02:30",
        arrival_location="HKT",
        arrival_terminal="I",
        arrival_date="2024-12-21",
        arrival_time="12:55",
        travel_class="Economy",
        checked_baggage="23kg",
        hand_baggage="7kg"
    )
    
    timeline = TimelineFormatter.format_timeline([first_flight, second_flight], [])
    assert "⚠️  Warning: Only" in timeline
    assert "minutes for transfer at DOH" in timeline