import pytest
from datetime import datetime
from src.models.events import Flight, Hotel

@pytest.fixture
def sample_flight():
    """Create a sample flight for testing."""
    return Flight(
        flight_number="BA2303",
        operator="Qatar Airways",
        booking_reference="MYH9XH",
        departure_location="Heathrow",
        departure_terminal="4",
        departure_date="2024-12-20",
        departure_time="16:00",
        arrival_location="Doha",
        arrival_terminal=None,
        arrival_date="2024-12-21",
        arrival_time="01:40",
        travel_class="Economy",
        checked_baggage="1 bag at 23kg (51lbs)",
        hand_baggage="1 handbag/laptop bag, plus 1 additional cabin bag"
    )

@pytest.fixture
def sample_hotel():
    """Create a sample hotel for testing."""
    return Hotel(
        name="Phuket Marriott Resort and Spa, Nai Yang Beach",
        city="Phuket",
        booking_reference="MYH9XH",
        check_in_date="2024-12-21",
        check_out_date="2024-12-27",
        room_details="Premium Pool Access, 1 King, Mini fridge"
    )

@pytest.fixture
def sample_itinerary(sample_flight, sample_hotel):
    """Create a sample itinerary dictionary."""
    return {
        "booking_reference": "MYH9XH",
        "flights": [vars(sample_flight)],
        "hotels": [vars(sample_hotel)],
        "source_file": "test_data/valid_ticket.pdf"
    }

@pytest.fixture
def mock_pdf_file(tmp_path):
    """Create a temporary PDF file for testing."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("%PDF-1.4\nTest PDF content")
    return str(pdf_path)