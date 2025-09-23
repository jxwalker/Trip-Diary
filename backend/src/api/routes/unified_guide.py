"""
Unified Guide API Routes
Provides endpoints for the new unified guide service
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel

from ..dependencies.services import DatabaseServiceDep
from ...services.unified_guide_service import UnifiedGuideService
from ...services.magazine_pdf_service import MagazinePDFService
from ...utils.validation import validate_trip_id
from ...utils.error_handling import create_error_response, safe_execute

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/unified-guide", tags=["unified-guide"])

class GuideGenerationRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    preferences: Optional[Dict[str, Any]] = None
    hotel_address: Optional[str] = None
    persona: Optional[str] = None

class PDFGenerationRequest(BaseModel):
    guide_data: Dict[str, Any]
    destination: str

@router.post("/generate")
async def generate_unified_guide(
    request: GuideGenerationRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseServiceDep
):
    """Generate a unified travel guide using the new service"""
    try:
        unified_service = UnifiedGuideService()
        
        context = {
            "destination": request.destination,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "preferences": request.preferences or {},
            "hotel_address": request.hotel_address,
            "persona": request.persona
        }
        
        guide = await unified_service.generate_complete_guide(context)
        
        is_valid, errors, details = unified_service.validator.validate_guide(guide)
        
        if not is_valid:
            logger.warning(f"Generated guide failed validation: {errors}")
            return create_error_response(
                f"Guide validation failed: {', '.join(errors[:3])}",
                "guide_generation"
            )
        
        return {
            "success": True,
            "guide": guide,
            "validation": {
                "is_valid": is_valid,
                "details": details
            },
            "generated_with": "unified_guide_service"
        }
        
    except Exception as e:
        logger.error(f"Unified guide generation failed: {e}")
        return create_error_response(str(e), "unified_guide_generation")

@router.post("/generate-pdf")
async def generate_unified_pdf(
    request: PDFGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate magazine-quality PDF from unified guide data"""
    try:
        pdf_service = MagazinePDFService(destination=request.destination)
        
        pdf_bytes = pdf_service.create_magazine_pdf(request.guide_data)
        
        return {
            "success": True,
            "pdf_size": len(pdf_bytes),
            "message": "Magazine-quality PDF generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Unified PDF generation failed: {e}")
        return create_error_response(str(e), "unified_pdf_generation")

@router.get("/personas")
async def get_available_personas():
    """Get list of available travel personas"""
    return {
        "success": True,
        "personas": [
            {
                "id": "luxury_traveler",
                "name": "Luxury Traveler",
                "description": "High-end experiences, premium accommodations, fine dining"
            },
            {
                "id": "budget_explorer",
                "name": "Budget Explorer", 
                "description": "Cost-effective options, local experiences, budget accommodations"
            },
            {
                "id": "foodie",
                "name": "Foodie",
                "description": "Culinary experiences, local cuisine, food tours"
            },
            {
                "id": "adventure_seeker",
                "name": "Adventure Seeker",
                "description": "Outdoor activities, extreme sports, adventure tours"
            },
            {
                "id": "cultural_enthusiast",
                "name": "Cultural Enthusiast",
                "description": "Museums, historical sites, cultural experiences"
            },
            {
                "id": "family_friendly",
                "name": "Family Friendly",
                "description": "Kid-friendly activities, family accommodations, safe experiences"
            }
        ]
    }

@router.get("/health")
async def health_check():
    """Health check for unified guide service"""
    try:
        unified_service = UnifiedGuideService()
        return {
            "success": True,
            "service": "unified_guide_service",
            "status": "healthy",
            "features": [
                "llm_parsing",
                "weather_correlation", 
                "persona_detection",
                "real_time_events",
                "magazine_pdf"
            ]
        }
    except Exception as e:
        return create_error_response(str(e), "health_check")
