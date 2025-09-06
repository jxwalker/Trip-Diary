"""
PDF generation routes
Generate a magazine-style travel pack PDF for a trip using the enhanced guide
"""
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse

from ..dependencies.services import (
    DatabaseServiceDep,
    OptimizedGuideServiceDep
)
from ...services.pdf_generator import TravelPackGenerator
from ...utils.error_handling import create_error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["pdf"])


@router.post("/generate-pdf/{trip_id}")
async def generate_pdf_for_trip(
    trip_id: str = Path(..., description="Trip ID to generate PDF for"),
    database_service: DatabaseServiceDep = None,
    guide_service: OptimizedGuideServiceDep = None,
) -> Any:
    """
    Generate a PDF for a trip. If an enhanced guide doesn't exist yet,
    it will be generated using the optimized guide service.
    """
    try:
        # Fetch trip data
        trip_data = await database_service.get_trip_data(trip_id)
        if not trip_data:
            raise HTTPException(status_code=404, detail=f"Trip not found: {trip_id}")

        # If no enhanced guide, generate it now
        if not trip_data.enhanced_guide:
            itinerary = trip_data.itinerary or {}
            destination = itinerary.get("trip_summary", {}).get("destination") or itinerary.get("destination") or ""
            start_date = itinerary.get("trip_summary", {}).get("start_date") or itinerary.get("start_date") or ""
            end_date = itinerary.get("trip_summary", {}).get("end_date") or itinerary.get("end_date") or ""

            if not (destination and start_date and end_date):
                raise HTTPException(status_code=400, detail="Trip is missing destination or dates required to generate guide")

            hotel_info = {}
            hotels = itinerary.get("accommodations") or itinerary.get("hotels") or []
            if hotels:
                h = hotels[0]
                hotel_info = {
                    "name": h.get("name") or h.get("hotel") or "",
                    "address": h.get("address") or ""
                }

            enhanced = await guide_service.generate_optimized_guide(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                hotel_info=hotel_info,
                preferences=trip_data.preferences or {},
                extracted_data=itinerary
            )
            trip_data.enhanced_guide = enhanced
            await database_service.save_trip_data(trip_data)

        # Build minimal itinerary shell if missing
        itinerary = trip_data.itinerary or {}
        if not itinerary.get("trip_summary"):
            # Construct a basic summary from the guide context
            destination = itinerary.get("destination") or (trip_data.enhanced_guide.get("summary", "").split(" ")[3] if trip_data.enhanced_guide else "Your Trip")
            itinerary = {
                **itinerary,
                "trip_summary": {
                    "destination": destination,
                    "start_date": itinerary.get("start_date", ""),
                    "end_date": itinerary.get("end_date", ""),
                    "duration": itinerary.get("duration", ""),
                    "total_passengers": itinerary.get("total_passengers", 1)
                }
            }

        # Prepare recommendations fallback (legacy)
        recommendations: Dict[str, Any] = trip_data.recommendations or {}

        # Generate PDF (ReportLab engine). For HTML-based engine use /api/generate-pdf-html
        generator = TravelPackGenerator()
        pdf_path = await generator.generate(
            trip_id=trip_id,
            itinerary=itinerary,
            recommendations=recommendations,
            enhanced_guide=trip_data.enhanced_guide or {}
        )

        filename = f"travel_pack_{trip_id}.pdf"
        return FileResponse(
            path=pdf_path,
            filename=filename,
            media_type="application/pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate PDF for trip {trip_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "PDF generation")
        )
