from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TravelEvent:
    date: str
    time: str
    type: str
    description: str
    
    def __lt__(self, other):
        if not isinstance(other, TravelEvent):
            return NotImplemented
        return (self.date, self.time) < (other.date, other.time)
    
    def __le__(self, other):
        if not isinstance(other, TravelEvent):
            return NotImplemented
        return (self.date, self.time) <= (other.date, other.time)

@dataclass
class Flight:
    flight_number: str
    operator: str
    booking_reference: str
    departure_location: str
    departure_terminal: Optional[str]
    departure_date: str
    departure_time: str
    arrival_location: str
    arrival_terminal: Optional[str]
    arrival_date: str
    arrival_time: str
    travel_class: str
    checked_baggage: str
    hand_baggage: str

    def __str__(self) -> str:
        terminal = f" Terminal {self.departure_terminal}" if self.departure_terminal else ""
        return f"{self.flight_number} ({self.operator}): {self.departure_location}{terminal} → {self.arrival_location}"

@dataclass
class Hotel:
    name: str
    city: str
    booking_reference: str
    check_in_date: str
    check_out_date: str
    room_details: str

    def __str__(self) -> str:
        return f"{self.name} ({self.check_in_date} to {self.check_out_date})"