"""
Models package for TripCraft AI
Contains all data models, schemas, and domain objects
"""

from .api_models import *
from .domain_models import *
from .database_models import *

__all__ = [
    # API Models
    'TripDetailsRequest',
    'ProcessingResponse',
    'ItineraryResponse',
    'PreferencesRequest',
    'ProfileRequest',

    # Domain Models
    'Trip',
    'Itinerary',
    'TravelPreferences',
    'UserProfile',
    'TravelGuide',

    # Database Models
    'TripData',
    'ProcessingState',
    'TripMetadata',
]