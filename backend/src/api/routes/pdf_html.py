"""
HTML PDF routes: generate an HTML-rendered magazine PDF using Playwright
"""
import logging
from typing import Any, Dict
from pathlib import Path

from fastapi import APIRouter, HTTPException, Path as FPath
from fastapi.responses import FileResponse

from ..dependencies.services import (
    DatabaseServiceDep,
    OptimizedGuideServiceDep
)
from ...services.html_pdf_renderer import HTMLPDFRenderer
from ...utils.error_handling import create_error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["pdf-html"]) 


@router.post("/generate-pdf-html/{trip_id}")
async def generate_pdf_html(
    trip_id: str = FPath(..., description="Trip ID to generate HTML-based PDF for"),
    database_service: DatabaseServiceDep = None,
    guide_service: OptimizedGuideServiceDep = None,
) -> Any:
    try:
        trip_data = await database_service.get_trip_data(trip_id)
        if not trip_data:
            raise HTTPException(status_code=404, detail=f"Trip not found: {trip_id}")

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

        # Ensure itinerary summary exists
        itinerary = trip_data.itinerary or {}
        if not itinerary.get("trip_summary"):
            itinerary = {
                **itinerary,
                "trip_summary": {
                    "destination": itinerary.get("destination", "Your Trip"),
                    "start_date": itinerary.get("start_date", ""),
                    "end_date": itinerary.get("end_date", ""),
                }
            }

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        pdf_path = output_dir / f"travel_pack_{trip_id}_magazine.pdf"

        renderer = HTMLPDFRenderer()
        try:
            out = renderer.render_magazine_pdf(guide=trip_data.enhanced_guide, itinerary=itinerary, output_path=pdf_path)
        except RuntimeError as e:
            # Playwright not installed
            raise HTTPException(status_code=500, detail=str(e))

        return FileResponse(path=str(out), filename=out.name, media_type="application/pdf")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate HTML PDF for trip {trip_id}: {e}")
        raise HTTPException(status_code=500, detail=create_error_response(e, "HTML PDF generation"))

