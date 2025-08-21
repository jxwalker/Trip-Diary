"""
Enhanced Guide API routes for travel guide generation
"""
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, BackgroundTasks
from pydantic import BaseModel

from ..dependencies.services import (
    DatabaseServiceDep,
    EnhancedGuideServiceDep,
    FastGuideServiceDep,
    OptimizedGuideServiceDep,
    LuxuryGuideServiceDep
)
from ...utils.validation import validate_trip_id
from ...utils.error_handling import create_error_response, safe_execute
from ...services.enhanced_redis_cache import cache_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["enhanced-guide"])


class GenerateGuideRequest(BaseModel):
    """Request model for guide generation"""
    destination: str
    start_date: str
    end_date: str
    hotel_info: Dict[str, Any]
    preferences: Dict[str, Any]
    extracted_data: Optional[Dict[str, Any]] = {}
    use_fast_generation: bool = True
    use_optimized_service: bool = True  # Use new optimized service by default


@router.get("/enhanced-guide/{trip_id}")
async def get_enhanced_guide(
    trip_id: str,
    database_service: DatabaseServiceDep
) -> Dict[str, Any]:
    """
    Get existing enhanced guide for a trip with Redis caching
    
    Args:
        trip_id: Trip ID to get guide for
        database_service: Database service
        
    Returns:
        Enhanced guide data or error
    """
    try:
        validated_trip_id = validate_trip_id(trip_id)
        logger.info(f"Enhanced guide requested", extra={"trip_id": validated_trip_id})
        
        # Check Redis cache first
        cache_key_data = {"trip_id": validated_trip_id}
        cached_guide = await cache_manager.get("enhanced_guide", cache_key_data)
        if cached_guide:
            logger.info(f"Redis cache HIT for enhanced guide: {validated_trip_id}")
            return cached_guide
        
        # Get trip data from database
        trip_data = await database_service.get_trip_data(validated_trip_id)
        
        if not trip_data:
            raise HTTPException(
                status_code=404,
                detail=f"Trip not found: {validated_trip_id}"
            )
        
        # Check if enhanced guide exists
        if not trip_data.enhanced_guide:
            raise HTTPException(
                status_code=404,
                detail=f"Enhanced guide not found for trip: {validated_trip_id}"
            )
        
        result = {
            "trip_id": validated_trip_id,
            "status": "success",
            "guide": trip_data.enhanced_guide,
            "generated_at": trip_data.updated_at
        }
        
        # Cache the result
        await cache_manager.set("enhanced_guide", cache_key_data, result)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get enhanced guide for trip {trip_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "enhanced guide retrieval")
        )


@router.post("/generate-enhanced-guide")
async def generate_enhanced_guide(
    request: GenerateGuideRequest,
    background_tasks: BackgroundTasks,
    database_service: DatabaseServiceDep,
    enhanced_guide_service: EnhancedGuideServiceDep,
    fast_guide_service: FastGuideServiceDep,
    optimized_guide_service: OptimizedGuideServiceDep
) -> Dict[str, Any]:
    """
    Generate enhanced travel guide
    
    Args:
        request: Guide generation request
        background_tasks: Background task manager
        database_service: Database service
        enhanced_guide_service: Enhanced guide service
        fast_guide_service: Fast guide service
        
    Returns:
        Generated guide or processing status
    """
    trip_id = str(uuid.uuid4())
    
    logger.info(f"Enhanced guide generation requested", extra={
        "trip_id": trip_id,
        "destination": request.destination,
        "dates": f"{request.start_date} to {request.end_date}",
        "use_fast": request.use_fast_generation
    })
    
    try:
        # Initialize processing state
        await database_service.create_processing_state(
            trip_id, "Starting enhanced guide generation..."
        )
        
        # Choose service based on request
        if request.use_optimized_service:
            # Optimized generation with concurrent processing (15-25 seconds)
            guide = await optimized_guide_service.generate_optimized_guide(
                destination=request.destination,
                start_date=request.start_date,
                end_date=request.end_date,
                hotel_info=request.hotel_info,
                preferences=request.preferences,
                extracted_data=request.extracted_data,
                progress_callback=lambda progress, message:
                    database_service.update_processing_state(trip_id, message, progress)
            )
        elif request.use_fast_generation:
            # Fast generation (10-20 seconds)
            guide = await fast_guide_service.generate_fast_guide(
                destination=request.destination,
                start_date=request.start_date,
                end_date=request.end_date,
                hotel_info=request.hotel_info,
                preferences=request.preferences,
                progress_callback=lambda progress, message:
                    database_service.update_processing_state(trip_id, message, progress),
                timeout=45
            )
        else:
            # Full enhanced generation (30-60 seconds)
            guide = await enhanced_guide_service.generate_enhanced_guide(
                destination=request.destination,
                start_date=request.start_date,
                end_date=request.end_date,
                hotel_info=request.hotel_info,
                preferences=request.preferences,
                extracted_data=request.extracted_data,
                progress_callback=lambda progress, message:
                    database_service.update_processing_state(trip_id, message, progress),
                single_pass=True
            )
        
        # Check for errors
        if guide.get("error"):
            await database_service.update_processing_state(
                trip_id, f"Generation failed: {guide['error']}"
            )
            return {
                "trip_id": trip_id,
                "status": "error",
                "error": guide["error"],
                "message": guide.get("message", "Guide generation failed")
            }
        
        # Save guide
        await database_service.save_enhanced_guide(trip_id, guide)
        await database_service.update_processing_state(trip_id, "Guide generation complete", 100)
        
        return {
            "trip_id": trip_id,
            "status": "success",
            "message": "Enhanced guide generated successfully",
            "guide": guide,
            "generation_time": guide.get("generation_time"),
            "validation_passed": guide.get("validation_passed", False)
        }
        
    except Exception as e:
        logger.error(f"Enhanced guide generation failed for trip {trip_id}: {e}")
        await database_service.update_processing_state(
            trip_id, f"Generation failed: {str(e)}"
        )
        
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "enhanced guide generation")
        )


@router.post("/generate-enhanced-guide/{trip_id}")
async def regenerate_enhanced_guide(
    trip_id: str,
    background_tasks: BackgroundTasks,
    database_service: DatabaseServiceDep,
    enhanced_guide_service: EnhancedGuideServiceDep,
    fast_guide_service: FastGuideServiceDep,
    use_fast: bool = True
) -> Dict[str, Any]:
    """
    Regenerate enhanced guide for existing trip
    
    Args:
        trip_id: Trip ID to regenerate guide for
        background_tasks: Background task manager
        database_service: Database service
        enhanced_guide_service: Enhanced guide service
        fast_guide_service: Fast guide service
        use_fast: Whether to use fast generation
        
    Returns:
        Regenerated guide or processing status
    """
    try:
        validated_trip_id = validate_trip_id(trip_id)
        logger.info(f"Guide regeneration requested", extra={"trip_id": validated_trip_id})
        
        # Get existing trip data
        trip_data = await database_service.get_trip_data(validated_trip_id)
        
        if not trip_data:
            raise HTTPException(
                status_code=404,
                detail=f"Trip not found: {validated_trip_id}"
            )
        
        # Extract required data from existing trip
        extracted_data = trip_data.itinerary or {}
        
        # Try to extract destination and dates from existing data
        destination = extracted_data.get("destination") if isinstance(extracted_data, dict) else "Paris"
        
        # Get dates from flights if available
        if isinstance(extracted_data, dict) and extracted_data.get("flights"):
            start_date = extracted_data["flights"][0].get("departure_date", "2025-03-15")
            end_date = extracted_data["flights"][-1].get("arrival_date", "2025-03-22")
        else:
            start_date = "2025-03-15"
            end_date = "2025-03-22"
            
        # Get hotel info if available
        if isinstance(extracted_data, dict) and extracted_data.get("hotels"):
            hotel_info = extracted_data["hotels"][0]
            if not destination and hotel_info.get("city"):
                destination = hotel_info["city"]
        else:
            hotel_info = {"name": "Hotel", "address": ""}
            
        preferences = trip_data.preferences or {}
        
        # Update processing state
        await database_service.update_processing_state(
            validated_trip_id, "Regenerating enhanced guide..."
        )
        
        # Generate new guide
        if use_fast:
            guide = await fast_guide_service.generate_fast_guide(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                hotel_info=hotel_info,
                preferences=preferences,
                progress_callback=lambda progress, message: 
                    database_service.update_processing_state(validated_trip_id, message, progress),
                timeout=45
            )
        else:
            guide = await enhanced_guide_service.generate_enhanced_guide(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                hotel_info=hotel_info,
                preferences=preferences,
                extracted_data=extracted_data,
                progress_callback=lambda progress, message: 
                    database_service.update_processing_state(validated_trip_id, message, progress),
                single_pass=True
            )
        
        # Check for errors
        if guide.get("error"):
            await database_service.update_processing_state(
                validated_trip_id, f"Regeneration failed: {guide['error']}"
            )
            return {
                "trip_id": validated_trip_id,
                "status": "error",
                "error": guide["error"],
                "message": guide.get("message", "Guide regeneration failed")
            }
        
        # Save updated guide
        await database_service.save_enhanced_guide(validated_trip_id, guide)
        await database_service.update_processing_state(validated_trip_id, "Guide regeneration complete", 100)
        
        return {
            "trip_id": validated_trip_id,
            "status": "success",
            "message": "Enhanced guide regenerated successfully",
            "guide": guide,
            "generation_time": guide.get("generation_time"),
            "validation_passed": guide.get("validation_passed", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced guide regeneration failed for trip {trip_id}: {e}")
        await database_service.update_processing_state(
            trip_id, f"Regeneration failed: {str(e)}"
        )
        
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "enhanced guide regeneration")
        )


# Fallback guide endpoint removed - no fallback/mock content allowed per requirements


@router.post("/generate-luxury-guide/{trip_id}")
async def generate_luxury_guide(
    trip_id: str,
    database_service: DatabaseServiceDep,
    luxury_guide_service: LuxuryGuideServiceDep
) -> Dict[str, Any]:
    """
    Generate a luxury Condé Nast style travel guide
    
    Args:
        trip_id: Trip ID to generate guide for
        database_service: Database service
        luxury_guide_service: Luxury guide service
        
    Returns:
        Premium travel guide with rich content
    """
    try:
        validated_trip_id = validate_trip_id(trip_id)
        logger.info(f"Luxury guide generation requested", extra={"trip_id": validated_trip_id})
        
        # Get trip data
        trip_data = await database_service.get_trip_data(validated_trip_id)
        
        if not trip_data:
            raise HTTPException(
                status_code=404,
                detail=f"Trip not found: {validated_trip_id}"
            )
        
        # Extract required data
        extracted_data = trip_data.itinerary or {}
        
        # Get destination and dates
        destination = extracted_data.get("destination", "Paris")
        
        if isinstance(extracted_data, dict) and extracted_data.get("flights"):
            start_date = extracted_data["flights"][0].get("departure_date", "2025-03-15")
            end_date = extracted_data["flights"][-1].get("arrival_date", "2025-03-22")
        else:
            start_date = "2025-03-15"
            end_date = "2025-03-22"
        
        # Get hotel info
        if isinstance(extracted_data, dict) and extracted_data.get("hotels"):
            hotel_info = extracted_data["hotels"][0]
            if not destination and hotel_info.get("city"):
                destination = hotel_info["city"]
        else:
            hotel_info = {"name": "Luxury Hotel", "address": "City Center"}
        
        preferences = trip_data.preferences or {}
        
        # Update processing state
        await database_service.update_processing_state(
            validated_trip_id, "Creating your luxury travel experience..."
        )
        
        # Generate luxury guide
        guide = await luxury_guide_service.generate_luxury_guide(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            hotel_info=hotel_info,
            preferences=preferences,
            extracted_data=extracted_data,
            progress_callback=lambda progress, message: 
                database_service.update_processing_state(validated_trip_id, message, progress)
        )
        
        # Save guide
        await database_service.save_enhanced_guide(validated_trip_id, guide)
        await database_service.update_processing_state(validated_trip_id, "Luxury guide complete", 100)
        
        return {
            "trip_id": validated_trip_id,
            "status": "success",
            "message": "Luxury travel guide generated successfully",
            "guide": guide,
            "guide_type": "luxury_conde_nast_style"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Luxury guide generation failed for trip {trip_id}: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "luxury guide generation")
        )
