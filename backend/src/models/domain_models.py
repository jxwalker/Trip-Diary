"""
Domain Models - Core business entities and value objects
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class TripStatus(str, Enum):
    """Trip status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AccommodationType(str, Enum):
    """Accommodation type enumeration"""
    HOTEL = "hotel"
    RESORT = "resort"
    APARTMENT = "apartment"
    HOSTEL = "hostel"
    BNB = "bnb"
    OTHER = "other"


class TransportationType(str, Enum):
    """Transportation type enumeration"""
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    CAR = "car"
    TAXI = "taxi"
    WALKING = "walking"
    OTHER = "other"


@dataclass
class Location:
    """Geographic location"""
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    
    def __str__(self) -> str:
        parts = [self.name]
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


@dataclass
class Passenger:
    """Trip passenger information"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    passport_number: Optional[str] = None
    special_requirements: List[str] = field(default_factory=list)


@dataclass
class Flight:
    """Flight information"""
    flight_number: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    departure_city: Optional[str] = None
    arrival_city: Optional[str] = None
    seat: Optional[str] = None
    confirmation_code: Optional[str] = None
    gate: Optional[str] = None
    terminal: Optional[str] = None


@dataclass
class Accommodation:
    """Accommodation information"""
    name: str
    type: AccommodationType
    location: Location
    check_in: date
    check_out: date
    confirmation_code: Optional[str] = None
    room_type: Optional[str] = None
    amenities: List[str] = field(default_factory=list)
    contact_info: Optional[Dict[str, str]] = None
    rating: Optional[float] = None
    price_per_night: Optional[float] = None


@dataclass
class Transportation:
    """Transportation information"""
    type: TransportationType
    provider: Optional[str] = None
    departure_location: Optional[Location] = None
    arrival_location: Optional[Location] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    confirmation_code: Optional[str] = None
    seat: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Activity:
    """Travel activity or event"""
    name: str
    description: Optional[str] = None
    location: Optional[Location] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    category: Optional[str] = None
    price: Optional[float] = None
    booking_required: bool = False
    confirmation_code: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None


@dataclass
class DayItinerary:
    """Single day itinerary"""
    date: date
    activities: List[Activity] = field(default_factory=list)
    transportation: List[Transportation] = field(default_factory=list)
    meals: List[Dict[str, Any]] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class Itinerary:
    """Complete trip itinerary"""
    trip_id: str
    destination: str
    start_date: date
    end_date: date
    passengers: List[Passenger] = field(default_factory=list)
    flights: List[Flight] = field(default_factory=list)
    accommodations: List[Accommodation] = field(default_factory=list)
    daily_itineraries: List[DayItinerary] = field(default_factory=list)
    transportation: List[Transportation] = field(default_factory=list)
    emergency_contacts: List[Dict[str, str]] = field(default_factory=list)
    
    @property
    def duration_days(self) -> int:
        """Calculate trip duration in days"""
        return (self.end_date - self.start_date).days + 1


@dataclass
class TravelPreferences:
    """User travel preferences"""
    dining: Dict[str, Any] = field(default_factory=dict)
    interests: Dict[str, Any] = field(default_factory=dict)
    travel_style: Dict[str, Any] = field(default_factory=dict)
    budget: Dict[str, Any] = field(default_factory=dict)
    accessibility: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'dining': self.dining,
            'interests': self.interests,
            'travel_style': self.travel_style,
            'budget': self.budget,
            'accessibility': self.accessibility
        }


@dataclass
class UserProfile:
    """User profile with preferences"""
    profile_id: str
    profile_name: str
    user_email: Optional[str] = None
    preferences: Optional[TravelPreferences] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = TravelPreferences()
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Trip:
    """Complete trip entity"""
    trip_id: str
    user_id: str
    status: TripStatus
    itinerary: Itinerary
    preferences: Optional[TravelPreferences] = None
    enhanced_guide: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def destination(self) -> str:
        """Get trip destination"""
        return self.itinerary.destination
    
    @property
    def start_date(self) -> date:
        """Get trip start date"""
        return self.itinerary.start_date
    
    @property
    def end_date(self) -> date:
        """Get trip end date"""
        return self.itinerary.end_date


@dataclass
class TravelGuide:
    """Enhanced travel guide"""
    trip_id: str
    destination: str
    sections: Dict[str, Any] = field(default_factory=dict)
    recommendations: Dict[str, Any] = field(default_factory=dict)
    local_info: Dict[str, Any] = field(default_factory=dict)
    emergency_info: Dict[str, Any] = field(default_factory=dict)
    generated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()
