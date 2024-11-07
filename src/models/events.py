from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

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
class Passenger:
    title: str
    first_name: str
    last_name: str
    frequent_flyer: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.title} {self.first_name} {self.last_name}"
        
    def __eq__(self, other):
        if not isinstance(other, Passenger):
            return NotImplemented
        return (self.first_name.lower(), self.last_name.lower()) == (other.first_name.lower(), other.last_name.lower())
        
    def __hash__(self):
        return hash((self.first_name.lower(), self.last_name.lower()))

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
    checked_baggage: Optional[str]
    hand_baggage: Optional[str]
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None

    def __str__(self) -> str:
        terminal = f" Terminal {self.departure_terminal}" if self.departure_terminal else ""
        return f"{self.flight_number} ({self.operator}): {self.departure_location}{terminal} → {self.arrival_location}"

@dataclass
class Hotel:
    name: str
    city: str
    check_in_date: str
    check_out_date: str
    room_type: str
    room_features: str
    booking_reference: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'Hotel':
        """Create a Hotel instance from a dictionary."""
        stay = data.get('stay', '').split(' to ')
        room_info = data.get('room', '').split(',', 1)
        
        return cls(
            name=data['name'],
            city=data.get('location', data.get('city', 'Unknown')),
            check_in_date=stay[0] if len(stay) > 0 else data.get('check_in_date', 'Unknown'),
            check_out_date=stay[1] if len(stay) > 1 else data.get('check_out_date', 'Unknown'),
            room_type=room_info[0].strip() if room_info else 'Standard Room',
            room_features=room_info[1].strip() if len(room_info) > 1 else '',
            booking_reference=data.get('booking_reference')
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.check_in_date} to {self.check_out_date})"