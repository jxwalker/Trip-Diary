"""
Unified Guide API Routes
Provides endpoints for the new unified guide service
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from ..dependencies.services import DatabaseServiceDep
from ...services.unified_guide_service import UnifiedGuideService
from ...services.magazine_pdf_service import MagazinePDFService
from ...utils.error_handling import create_error_response

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
        context = {
            "destination": request.destination,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "preferences": request.preferences or {},
            "hotel_address": request.hotel_address,
            "persona": request.persona
        }

        unified_service = UnifiedGuideService()
        guide = await unified_service.generate_complete_guide(
            destination=context["destination"],
            start_date=context["start_date"],
            end_date=context["end_date"],
            hotel_info=context.get("hotel_address"),
            preferences=context.get("preferences", {}),
            budget=context.get("budget"),
            group_size=context.get("group_size", 1)
        )

        from ...services.guide_validator import GuideValidator
        is_valid, errors = GuideValidator.validate_guide(guide)

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
                "errors": errors
            },
            "generated_with": "unified_guide_service"
        }

    except Exception as e:
        logger.exception(f"Unified guide generation failed: {e}")
        return create_error_response(str(e), "unified_guide_generation")


@router.post("/generate-pdf")
async def generate_unified_pdf(
    request: PDFGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate magazine-quality PDF from unified guide data"""
    try:
        pdf_service = MagazinePDFService(destination=request.destination)

        pdf_result = pdf_service.create_magazine_pdf(request.guide_data)

        if hasattr(pdf_result, '__await__'):
            pdf_result = await pdf_result

        if isinstance(pdf_result, bytes):
            pdf_bytes = pdf_result
        elif isinstance(pdf_result, dict):
            if "pdf_bytes" in pdf_result:
                pdf_bytes = pdf_result["pdf_bytes"]
            elif "output_path" in pdf_result:
                with open(pdf_result["output_path"], "rb") as f:
                    pdf_bytes = f.read()
            else:
                logger.exception("PDF service returned unexpected dict format")
                return create_error_response(
                    "PDF generation failed - unexpected format",
                    "unified_pdf_generation"
                )
        else:
            logger.exception(
                f"PDF service returned unexpected type: {type(pdf_result)}"
            )
            return create_error_response(
                "PDF generation failed - unexpected return type",
                "unified_pdf_generation"
            )

        if not pdf_bytes:
            logger.error("Failed to generate PDF")
            return create_error_response(
                "PDF generation failed",
                "unified_pdf_generation"
            )

        return {
            "success": True,
            "pdf_size": len(pdf_bytes),
            "message": "Magazine-quality PDF generated successfully"
        }

    except Exception as e:
        logger.exception(f"Unified PDF generation failed: {e}")
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
                "description": ("High-end experiences, premium "
                                "accommodations, fine dining")
            },
            {
                "id": "budget_explorer",
                "name": "Budget Explorer",
                "description": ("Cost-effective options, local "
                                "experiences, budget accommodations")
            },
            {
                "id": "foodie",
                "name": "Foodie",
                "description": (
                    "Culinary experiences, local cuisine, food tours"
                )
            },
            {
                "id": "adventure_seeker",
                "name": "Adventure Seeker",
                "description": (
                    "Outdoor activities, extreme sports, adventure tours"
                )
            },
            {
                "id": "cultural_enthusiast",
                "name": "Cultural Enthusiast",
                "description": (
                    "Museums, historical sites, cultural experiences"
                )
            },
            {
                "id": "family_friendly",
                "name": "Family Friendly",
                "description": ("Kid-friendly activities, family "
                                "accommodations, safe experiences")
            }
        ]
    }


@router.get("/health")
async def health_check():
    """Health check for unified guide service"""
    try:
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
