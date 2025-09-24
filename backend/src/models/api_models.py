"""
API Models - Request and Response schemas for FastAPI endpoints
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ProcessingStatusEnum(str, Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class TripDetailsRequest(BaseModel):
    """Request model for trip details"""
    destination: str = Field(..., description="Trip destination")
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Trip end date (YYYY-MM-DD)")
    travelers: int = Field(
        default=1, ge=1, le=20, description="Number of travelers"
    )
    flights: Optional[Dict[str, str]] = Field(None, description="Flight information")
    hotels: Optional[List[Dict[str, str]]] = Field(
        None, description="Hotel information"
    )

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')


class ProcessingResponse(BaseModel):
    """Response model for processing status"""
    trip_id: str = Field(..., description="Unique trip identifier")
    status: ProcessingStatusEnum = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    extracted_data: Optional[Dict[str, Any]] = Field(
        None, description="Extracted trip data"
    )
    error_details: Optional[str] = Field(
        None, description="Error details if status is error"
    )


class ItineraryResponse(BaseModel):
    """Response model for trip itinerary"""
    trip_id: str = Field(..., description="Unique trip identifier")
    itinerary: Dict[str, Any] = Field(..., description="Generated itinerary")
    recommendations: Dict[str, Any] = Field(default_factory=dict, description="Travel recommendations")
    pdf_url: Optional[str] = Field(
        None, description="URL to download PDF travel pack"
    )


class PreferencesRequest(BaseModel):
    """Request model for user preferences"""
    dining: Optional[Dict[str, Any]] = Field(None, description="Dining preferences")
    interests: Optional[Dict[str, Any]] = Field(None, description="Interest categories")
    travel_style: Optional[Dict[str, Any]] = Field(None, description="Travel style preferences")
    budget: Optional[Dict[str, Any]] = Field(None, description="Budget preferences")
    accessibility: Optional[Dict[str, Any]] = Field(
        None, description="Accessibility requirements"
    )


class ProfileRequest(BaseModel):
    """Request model for user profile"""
    profile_id: Optional[str] = Field(None, description="Profile identifier")
    profile_name: str = Field(..., description="Profile name")
    user_email: Optional[str] = Field(None, description="User email")
    dining: Optional[Dict[str, Any]] = Field(None, description="Dining preferences")
    interests: Optional[Dict[str, Any]] = Field(None, description="Interest categories")
    travel_style: Optional[Dict[str, Any]] = Field(None, description="Travel style preferences")


class ProfileResponse(BaseModel):
    """Response model for user profile"""
    status: str = Field(..., description="Operation status")
    profile_id: str = Field(..., description="Profile identifier")
    profile_name: str = Field(..., description="Profile name")
    message: Optional[str] = Field(None, description="Response message")


class ProfileListResponse(BaseModel):
    """Response model for profile list"""
    profiles: List[Dict[str, Any]] = Field(..., description="List of profiles")
    count: int = Field(..., description="Number of profiles")


class GenerationStatusResponse(BaseModel):
    """Response model for generation status"""
    status: ProcessingStatusEnum = Field(..., description="Generation status")
    message: str = Field(..., description="Status message")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")


class EnhancedGuideResponse(BaseModel):
    """Response model for enhanced travel guide"""
    trip_id: str = Field(..., description="Unique trip identifier")
    itinerary: Dict[str, Any] = Field(..., description="Trip itinerary")
    enhanced_guide: Dict[str, Any] = Field(
        ..., description="Enhanced travel guide"
    )
    recommendations: Dict[str, Any] = Field(default_factory=dict, description="Travel recommendations")


class TripSaveResponse(BaseModel):
    """Response model for trip save operation"""
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message")
    trip_id: str = Field(..., description="Trip identifier")


class TripListResponse(BaseModel):
    """Response model for trip list"""
    trips: List[Dict[str, Any]] = Field(..., description="List of trips")
    count: int = Field(..., description="Number of trips")


class TripSearchResponse(BaseModel):
    """Response model for trip search"""
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results")


class CleanupResponse(BaseModel):
    """Response model for cleanup operation"""
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message")
    stats: Optional[Dict[str, Any]] = Field(
        None, description="Cleanup statistics"
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Check timestamp"
    )
    version: str = Field(default="1.0.0", description="API version")
    services: Dict[str, str] = Field(
        default_factory=dict, description="Service statuses"
    )


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    correlation_id: Optional[str] = Field(
        None, description="Request correlation ID"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )
