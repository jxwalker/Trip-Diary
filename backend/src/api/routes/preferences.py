"""
Preferences API routes for customizing trip details
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from ..dependencies.services import DatabaseServiceDep
from ...models.database_models import TripData
from ...utils.error_handling import safe_execute, create_error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["preferences"])


@router.post("/preferences/{trip_id}")
async def save_preferences(
    trip_id: str,
    preferences: Dict[str, Any],
    database_service: DatabaseServiceDep
):
    """
    Save user preferences for a trip
    
    Args:
        trip_id: The trip identifier
        preferences: User preferences dictionary
        database_service: Database service dependency
        
    Returns:
        Success response with saved preferences
    """
    logger.info(f"Saving preferences for trip {trip_id}")
    
    try:
        # Get existing trip data
        trip_data = await database_service.get_trip_data(trip_id)
        
        if not trip_data:
            # Create new trip data if it doesn't exist
            trip_data = TripData(
                trip_id=trip_id,
                user_id="default",
                itinerary={},
                preferences=preferences,
                enhanced_guide=None
            )
        else:
            # Update preferences
            trip_data.preferences = preferences
        
        # Save to database
        await database_service.save_trip_data(trip_data)
        
        logger.info(f"Preferences saved for trip {trip_id}")
        
        return {
            "status": "success",
            "trip_id": trip_id,
            "preferences": preferences,
            "message": "Preferences saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to save preferences for trip {trip_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "preferences saving")
        )


@router.get("/preferences/{trip_id}")
async def get_preferences(
    trip_id: str,
    database_service: DatabaseServiceDep
):
    """
    Get user preferences for a trip
    
    Args:
        trip_id: The trip identifier
        database_service: Database service dependency
        
    Returns:
        Trip preferences
    """
    logger.info(f"Getting preferences for trip {trip_id}")
    
    try:
        trip_data = await database_service.get_trip_data(trip_id)
        
        if not trip_data:
            logger.warning(f"Trip not found: {trip_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Trip {trip_id} not found"
            )
        
        return {
            "status": "success",
            "trip_id": trip_id,
            "preferences": trip_data.preferences or {},
            "has_itinerary": bool(trip_data.itinerary),
            "has_guide": bool(trip_data.enhanced_guide)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get preferences for trip {trip_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "preferences retrieval")
        )