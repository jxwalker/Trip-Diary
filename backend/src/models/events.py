from datetime import datetime
from typing import Optional, List, Any, Dict, Union
from pydantic import BaseModel, Field, validator

# --- Base Models ---

class Location(BaseModel):
    """Location information for flights."""
    location: str
    terminal: Optional[str] = None
    date: str
    time: str

    @validator('date')
    def validate_date(cls, v):
        """Convert date to YYYY-MM-DD format if needed."""
        try:
            # First try the expected format
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            try:
                # Try parsing DD MMM YYYY format
                parsed_date = datetime.strptime(v, '%d %b %Y')
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    # Try parsing with full month name
                    parsed_date = datetime.strptime(v, '%d %B %Y')
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    raise ValueError(
                        f"Invalid date format: {v}. Expected YYYY-MM-DD or DD MMM YYYY"
                    )

class BaggageAllowance(BaseModel):
    """Baggage allowance information."""
    checked_baggage: Optional[str] = None
    hand_baggage: Optional[str] = None

    def __str__(self) -> str:
        parts = []
        if self.checked_baggage:
            parts.append(f"Checked: {self.checked_baggage}")
        if self.hand_baggage:
            parts.append(f"Hand: {self.hand_baggage}")
        return ", ".join(parts) if parts else "No baggage information"

class RoomDetails(BaseModel):
    """Details for a specific room."""
    room_type: str
    bed_type: Optional[str] = None
    size: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    meal_plan: Optional[str] = None
    occupancy: Optional[str] = None

    @classmethod
    def parse(cls, data: Union[Dict, 'RoomDetails', Any]) -> Optional['RoomDetails']:
        """Safely parse room details from various input types."""
        try:
            if isinstance(data, cls):
                return data
            if isinstance(data, dict):
                # Clean up room type if it's being used as bed type
                if ('room_type' in data and 
                    any(bed in data['room_type'].lower() 
                        for bed in ['king', 'queen', 'double', 'twin'])):
                    data['bed_type'] = data['room_type']
                    data['room_type'] = 'Standard Room'
                return cls(**data)
            return None
        except Exception as e:
            logger.error(f"Error parsing room details: {str(e)}")
            return None

# --- Complex Models ---

class Flight(BaseModel):
    """Flight information."""
    flight_number: str
    operator: str
    departure: Location
    arrival: Location
    travel_class: Optional[str] = "Economy"
    baggage_allowance: Optional[BaggageAllowance] = None
    passengers: List['Passenger'] = Field(default_factory=list)

    @classmethod
    def parse(cls, data: Dict[str, Any]) -> Optional['Flight']:
        """Safely parse flight data with validation."""
        try:
            # Skip incomplete flight entries
            if not data.get('flight_number') or not data.get('operator'):
                return None
                
            # Ensure required nested objects
            if 'departure' in data and isinstance(data['departure'], dict):
                data['departure'] = Location.parse(data['departure'])
            if 'arrival' in data and isinstance(data['arrival'], dict):
                data['arrival'] = Location.parse(data['arrival'])
            
            # Parse passengers if present
            if 'passengers' in data and isinstance(data['passengers'], list):
                passengers = []
                for passenger_data in data['passengers']:
                    if isinstance(passenger_data, dict):
                        passenger = Passenger.parse(passenger_data)
                        if passenger:
                            passengers.append(passenger)
                data['passengers'] = passengers
            else:
                data['passengers'] = []
                
            return cls(**data)
        except ValidationError as e:
            logger.error(f"Validation error parsing flight: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing flight: {str(e)}")
            return None

    def __eq__(self, other):
        """Compare flights based on core attributes."""
        if not isinstance(other, Flight):
            return False
        return (self.flight_number == other.flight_number and 
                self.departure.date == other.departure.date and
                self.departure.time == other.departure.time)

    def __hash__(self):
        """Hash based on core attributes."""
        return hash((
            self.flight_number, self.departure.date, self.departure.time
        ))

class Hotel(BaseModel):
    """Hotel booking information."""
    name: str
    city: str
    check_in_date: str
    check_out_date: str
    rooms: List[RoomDetails] = Field(default_factory=list)
    booking_reference: Optional[str] = None
    address: Optional[str] = None

    @validator('check_in_date', 'check_out_date')
    def validate_dates(cls, v):
        """Convert dates to YYYY-MM-DD format if needed."""
        try:
            # First try the expected format
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            try:
                # Try parsing DD MMM YYYY format
                parsed_date = datetime.strptime(v, '%d %b %Y')
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    # Try parsing with full month name
                    parsed_date = datetime.strptime(v, '%d %B %Y')
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    raise ValueError(
                        f"Invalid date format: {v}. Expected YYYY-MM-DD or DD MMM YYYY"
                    )

    @validator('name')
    def clean_hotel_name(cls, v):
        """Clean up hotel name by removing city suffixes."""
        if ',' in v:
            name_parts = v.split(',')
            return name_parts[0].strip()
        return v

    @classmethod
    def parse(cls, data: Dict[str, Any]) -> 'Hotel':
        """Parse hotel data with proper room handling."""
        # Ensure we have a rooms list
        if "rooms" not in data:
            data["rooms"] = []
        elif isinstance(data["rooms"], dict):
            data["rooms"] = [data["rooms"]]  # Convert single room dict to list
        
        # Parse each room
        if isinstance(data["rooms"], list):
            rooms = []
            for room_data in data["rooms"]:
                room = RoomDetails.parse(room_data)
                if room:
                    rooms.append(room)
            data["rooms"] = rooms
        
        return cls(**data)

    def __eq__(self, other):
        """Compare hotels based on core attributes."""
        if not isinstance(other, Hotel):
            return False
        return (self.name == other.name and 
                self.city == other.city and 
                self.check_in_date == other.check_in_date and 
                self.check_out_date == other.check_out_date)

    def __hash__(self):
        """Hash based on core attributes."""
        return hash((
            self.name, self.city, self.check_in_date, self.check_out_date
        ))

# --- Person Model ---

class Passenger(BaseModel):
    """Passenger information."""
    title: str
    first_name: str
    last_name: str
    frequent_flyer: Optional[str] = None

    @classmethod
    def parse(cls, data: Dict[str, Any]) -> Optional['Passenger']:
        """Safely parse passenger data with validation."""
        try:
            if not data.get('first_name') or not data.get('last_name'):
                return None
                
            return cls(
                title=data.get('title', '').upper().strip(),
                first_name=data.get('first_name', '').strip(),
                last_name=data.get('last_name', '').upper().strip(),
                frequent_flyer=data.get('frequent_flyer')
            )
        except Exception as e:
            logger.error(f"Error parsing passenger: {str(e)}")
            return None

    def __hash__(self) -> int:
        return hash((
            self.title.upper(), self.first_name.upper(), self.last_name.upper()
        ))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Passenger):
            return NotImplemented
        return (self.title.upper() == other.title.upper() and
                self.first_name.upper() == other.first_name.upper() and
                self.last_name.upper() == other.last_name.upper())

# --- Event Model ---

class TravelEvent(BaseModel):
    """Base class for travel events like flights and hotel stays."""
    event_type: str
    start_date: str  # Format: "YYYY-MM-DD HH:MM"
    end_date: Optional[str] = None
    description: str

    def __lt__(self, other: 'TravelEvent') -> bool:
        if not isinstance(other, TravelEvent):
            return NotImplemented
        if self.start_date != other.start_date:
            return self.start_date < other.start_date
        type_priority = {
            'flight_checkin': 0,
            'flight_departure': 1,
            'flight_arrival': 2,
            'hotel_checkin': 3,
            'hotel_checkout': 4
        }
        return (type_priority.get(self.event_type, 999) < 
                type_priority.get(other.event_type, 999))
