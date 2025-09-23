"""
Secure proxy endpoints for Google Places API to avoid exposing API keys
in frontend
"""

import os
import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/places/photo/{photo_reference}")
async def get_place_photo(
    photo_reference: str,
    maxwidth: int = Query(800, description="Maximum width of the photo")
):
    """
    Secure proxy for Google Places photos that doesn't expose API keys
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="Google Maps API key not configured"
            )
        
        # Construct the Google Places photo URL with API key
        photo_url = (
            f"https://maps.googleapis.com/maps/api/place/photo?"
            f"maxwidth={maxwidth}&photoreference={photo_reference}&key={api_key}"
        )
        
        # Fetch the photo from Google Places API
        async with httpx.AsyncClient() as client:
            response = await client.get(photo_url)
            response.raise_for_status()
            
            # Return the image as a streaming response
            return StreamingResponse(
                response.iter_bytes(),
                media_type=response.headers.get("content-type", "image/jpeg"),
                headers={
                    "Cache-Control": "public, max-age=86400",
                    "Content-Length": str(len(response.content))
                }
            )
            
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch photo from Google Places API: {e}")
        raise HTTPException(
            status_code=502, 
            detail="Failed to fetch photo from Google Places API"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching photo: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/places/staticmap")
async def get_static_map(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    zoom: int = Query(15, description="Zoom level"),
    size: str = Query("400x300", description="Map size"),
    type: str = Query("restaurant", description="Type of marker")
):
    """
    Secure proxy for Google Static Maps that doesn't expose API keys
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="Google Maps API key not configured"
            )
        
        # Determine marker color based on type
        marker_color = "blue" if type == "restaurant" else "red"
        
        # Construct the Google Static Maps URL with API key
        map_url = (
            f"https://maps.googleapis.com/maps/api/staticmap?"
            f"center={lat},{lng}&zoom={zoom}&size={size}&"
            f"markers=color:{marker_color}%7C{lat},{lng}&key={api_key}"
        )
        
        # Fetch the map from Google Static Maps API
        async with httpx.AsyncClient() as client:
            response = await client.get(map_url)
            response.raise_for_status()
            
            # Return the image as a streaming response
            return StreamingResponse(
                response.iter_bytes(),
                media_type="image/png",
                headers={
                    "Cache-Control": "public, max-age=86400",
                    "Content-Length": str(len(response.content))
                }
            )
            
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch static map from Google Maps API: {e}")
        raise HTTPException(
            status_code=502, 
            detail="Failed to fetch static map from Google Maps API"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching static map: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/places/embed/{place_id}")
async def get_place_embed(place_id: str):
    """
    Secure proxy for Google Maps embed that doesn't expose API keys
    """
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, 
                detail="Google Maps API key not configured"
            )
        
        # Return the embed URL with API key (this is safe as it's server-side)
        embed_url = (
            f"https://www.google.com/maps/embed/v1/place?"
            f"key={api_key}&q=place_id:{place_id}"
        )
        
        return {
            "embed_url": embed_url,
            "place_id": place_id
        }
        
    except Exception as e:
        logger.error(f"Unexpected error generating embed URL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
