"""
Status API routes for trip processing status
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Path

from ..dependencies.services import DatabaseServiceDep
from ...utils.validation import validate_trip_id
from ...utils.error_handling import create_error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status/{trip_id}")
async def get_processing_status(
    database_service: DatabaseServiceDep,
    trip_id: str = Path(..., description="Trip ID to check status for")
) -> Dict[str, Any]:
    """
    Get processing status for a trip

    Args:
        trip_id: Trip ID to check
        database_service: Database service

    Returns:
        Processing status information
    """
    try:
        # Validate trip ID format
        validated_trip_id = validate_trip_id(trip_id)

        logger.info(f"Status check requested", extra={"trip_id": validated_trip_id})

        # Get processing state
        processing_state = await database_service.get_processing_state(validated_trip_id)

        if not processing_state:
            raise HTTPException(
                status_code=404,
                detail=f"Trip not found: {validated_trip_id}"
            )

        # Get trip data if available
        trip_data = await database_service.get_trip_data(validated_trip_id)

        # Handle status as either enum or string
        status_value = processing_state.status
        if hasattr(status_value, 'value'):
            status_value = status_value.value
        
        response = {
            "trip_id": validated_trip_id,
            "status": status_value,
            "message": processing_state.message,
            "progress": processing_state.progress,
            "created_at": processing_state.created_at,
            "updated_at": processing_state.updated_at,
            "has_data": trip_data is not None
        }

        # Add data summary if available
        if trip_data:
            response["data_summary"] = {
                "has_extracted_data": bool(trip_data.extracted_data),
                "has_itinerary": bool(trip_data.itinerary),
                "has_recommendations": bool(trip_data.recommendations),
                "has_enhanced_guide": bool(trip_data.enhanced_guide)
            }

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Status check failed for trip {trip_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "status check")
        )
