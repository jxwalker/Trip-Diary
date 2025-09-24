"""
Generation API routes for itinerary creation and status tracking
"""
import logging
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json

from ..dependencies.services import (
    DatabaseServiceDep,
    EnhancedGuideServiceDep,
    OptimizedGuideServiceDep
)
from ...models.database_models import ProcessingStatus
from ...utils.error_handling import safe_execute, create_error_response
from ...utils.trip_data_extractor import extract_trip_info, extract_hotel_info
from ...services.enhanced_redis_cache import cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["generation"])


@router.get("/generation-status/{trip_id}")
async def get_generation_status(
    trip_id: str,
    database_service: DatabaseServiceDep
):
    """
    Get the current status of itinerary generation
    
    Args:
        trip_id: The trip identifier
        database_service: Database service dependency
        
    Returns:
        Generation status information
    """
    logger.info(f"Checking generation status for trip {trip_id}")
    
    try:
        # Get trip data to check if guide exists
        trip_data = await database_service.get_trip_data(trip_id)
        
        if not trip_data:
            logger.warning(f"Trip not found: {trip_id}")
            return {
                "status": "not_found",
                "message": f"Trip {trip_id} not found"
            }
        
        # Get processing state
        processing_state = await database_service.get_processing_state(trip_id)
        
        # Check if guide is already generated
        if trip_data.enhanced_guide:
            return {
                "status": "completed",
                "message": "Itinerary generation complete",
                "progress": 100,
                "has_guide": True
            }
        
        # Check processing state
        if processing_state:
            status_value = processing_state.status
            if hasattr(status_value, 'value'):
                status_value = status_value.value
                
            return {
                "status": status_value,
                "message": processing_state.message or "Processing...",
                "progress": processing_state.progress or 0,
                "has_guide": False
            }
        
        # No generation started yet
        return {
            "status": "pending",
            "message": "Generation not started",
            "progress": 0,
            "has_guide": False
        }
        
    except Exception as e:
        logger.error(
            f"Failed to get generation status for trip {trip_id}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "generation status check")
        )


# SSE streaming route removed to prevent screen refresh issues


@router.post("/generate-guide/{trip_id}")
async def generate_guide(
    trip_id: str,
    database_service: DatabaseServiceDep,
    guide_service: OptimizedGuideServiceDep
):
    """
    Trigger guide generation for a trip (non-streaming)
    
    Args:
        trip_id: The trip identifier
        database_service: Database service dependency
        guide_service: Guide generation service
        
    Returns:
        Success response with guide data
    """
    logger.info(f"Generating guide for trip {trip_id}")
    
    try:
        # Get trip data
        trip_data = await database_service.get_trip_data(trip_id)
        
        if not trip_data:
            raise HTTPException(
                status_code=404,
                detail=f"Trip {trip_id} not found"
            )
        
        if not trip_data.itinerary:
            raise HTTPException(
                status_code=400,
                detail="No itinerary data found for this trip"
            )
        
        # Update status
        await database_service.update_processing_state(
            trip_id,
            status=ProcessingStatus.PROCESSING,
            progress=10,
            message="Starting guide generation..."
        )
        
        # Extract required data from itinerary using intelligent extraction
        itinerary = trip_data.itinerary
        destination, start_date, end_date = extract_trip_info(itinerary)
        
        # Get hotel info with smart defaults
        hotel_info = extract_hotel_info(itinerary, destination)
        
        # Generate the guide
        enhanced_guide = await guide_service.generate_optimized_guide(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            hotel_info=hotel_info,
            preferences=trip_data.preferences or {},
            extracted_data=itinerary
        )
        
        # Save the guide
        trip_data.enhanced_guide = enhanced_guide
        await database_service.save_trip_data(trip_data)
        
        # Invalidate Redis cache for this trip
        cache_key_data = {"trip_id": trip_id}
        await cache_manager.delete("enhanced_guide", cache_key_data)
        logger.info(f"Invalidated Redis cache for trip {trip_id}")
        
        # Update status to completed
        await database_service.update_processing_state(
            trip_id,
            status=ProcessingStatus.COMPLETED,
            progress=100,
            message="Guide generation complete"
        )
        
        logger.info(f"Guide generated successfully for trip {trip_id}")
        
        return {
            "status": "success",
            "trip_id": trip_id,
            "message": "Guide generated successfully",
            "has_guide": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate guide for trip {trip_id}: {e}")
        
        # Update status to error
        await database_service.update_processing_state(
            trip_id,
            status=ProcessingStatus.ERROR,
            message=f"Generation failed: {str(e)}",
            error_details=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "guide generation")
        )
