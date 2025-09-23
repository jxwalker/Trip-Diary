"""
Database Models - Data persistence and storage entities
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json


class ProcessingStatus(str, Enum):
    """Processing status for database operations"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ProcessingState:
    """Processing state for trip operations"""
    trip_id: str
    status: ProcessingStatus
    progress: int
    message: str
    created_at: datetime
    updated_at: datetime
    extracted_data: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value

        # Handle datetime fields safely
        if isinstance(self.created_at, datetime):
            data['created_at'] = self.created_at.isoformat()
        else:
            data['created_at'] = str(self.created_at)

        if isinstance(self.updated_at, datetime):
            data['updated_at'] = self.updated_at.isoformat()
        else:
            data['updated_at'] = str(self.updated_at)

        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingState':
        """Create from dictionary"""
        return cls(
            trip_id=data['trip_id'],
            status=ProcessingStatus(data['status']),
            progress=data['progress'],
            message=data['message'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            extracted_data=data.get('extracted_data'),
            error_details=data.get('error_details')
        )


@dataclass
class TripData:
    """Complete trip data for database storage"""
    trip_id: str
    user_id: str = "default"
    extracted_data: Optional[Dict[str, Any]] = None
    itinerary: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    enhanced_guide: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    preferences_raw: Optional[Dict[str, Any]] = None
    preference_progress: Optional[Dict[str, Any]] = None
    pdf_path: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamps if not provided"""
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        self.updated_at = now
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TripData':
        """Create from dictionary"""
        return cls(**data)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now().isoformat()


@dataclass
class TripMetadata:
    """Trip metadata for quick listing and searching"""
    trip_id: str
    user_id: str
    title: str
    destination: str
    start_date: str
    end_date: str
    duration: str
    passengers: int
    flights: int
    hotels: int
    status: str
    created_at: str
    updated_at: str
    tags: List[str] = None
    
    def __post_init__(self):
        """Initialize tags if not provided"""
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TripMetadata':
        """Create from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_trip_data(cls, trip_data: TripData) -> 'TripMetadata':
        """Create metadata from trip data"""
        itinerary = trip_data.itinerary or {}
        trip_summary = itinerary.get('trip_summary', {})
        
        return cls(
            trip_id=trip_data.trip_id,
            user_id=trip_data.user_id,
            title=(f"{trip_summary.get('destination', 'Trip')} - "
                   f"{trip_summary.get('start_date', '')}"),
            destination=trip_summary.get('destination', 'Unknown'),
            start_date=trip_summary.get('start_date', ''),
            end_date=trip_summary.get('end_date', ''),
            duration=trip_summary.get('duration', ''),
            passengers=len(itinerary.get('passengers', [])),
            flights=len(itinerary.get('flights', [])),
            hotels=len(itinerary.get('accommodations', [])),
            status='active',
            created_at=trip_data.created_at or datetime.now().isoformat(),
            updated_at=trip_data.updated_at or datetime.now().isoformat()
        )


@dataclass
class UserProfileData:
    """User profile data for database storage"""
    profile_id: str
    user_email: Optional[str]
    profile_name: str
    dining: Dict[str, Any]
    interests: Dict[str, Any]
    travel_style: Dict[str, Any]
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfileData':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class DatabaseIndex:
    """Database index for efficient querying"""
    trips_by_user: Dict[str, List[str]]
    trips_by_destination: Dict[str, List[str]]
    trips_by_date: Dict[str, List[str]]
    profiles_by_user: Dict[str, List[str]]
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseIndex':
        """Create from dictionary"""
        return cls(**data)
    
    @classmethod
    def empty(cls) -> 'DatabaseIndex':
        """Create empty index"""
        return cls(
            trips_by_user={},
            trips_by_destination={},
            trips_by_date={},
            profiles_by_user={},
            last_updated=datetime.now().isoformat()
        )


@dataclass
class BackupMetadata:
    """Backup metadata for database backups"""
    backup_id: str
    created_at: str
    file_path: str
    size_bytes: int
    trip_count: int
    profile_count: int
    checksum: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupMetadata':
        """Create from dictionary"""
        return cls(**data)


class DatabaseError(Exception):
    """Database operation error"""
    pass


class ValidationError(Exception):
    """Data validation error"""
    pass


class NotFoundError(Exception):
    """Resource not found error"""
    pass
