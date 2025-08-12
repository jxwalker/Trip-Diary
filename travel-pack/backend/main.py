from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import asyncio
from datetime import datetime
import uuid
import aiofiles
from pathlib import Path

# Import our modules
from services.pdf_processor import PDFProcessor
from services.llm_extractor import LLMExtractor
from services.llm_multimodal_extractor import MultimodalLLMExtractor
from services.itinerary_generator import ItineraryGenerator
from services.pdf_generator import TravelPackGenerator
from services.maps_service import MapsService
from services.recommendations import RecommendationsService
from services.weather_service import WeatherService
from services.places_service import PlacesService
from services.events_service import EventsService
from services.enhanced_guide_service import EnhancedGuideService
from services.immediate_guide_generator import ImmediateGuideGenerator
from database import TripDatabase

app = FastAPI(title="TripCraft AI API", version="1.0.0")

# Initialize database
db = TripDatabase()

# Configure CORS - allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Models
class TripDetails(BaseModel):
    destination: str
    start_date: str
    end_date: str
    travelers: int = 1
    flights: Optional[Dict[str, str]] = None
    hotels: Optional[List[Dict[str, str]]] = None

class ProcessingResponse(BaseModel):
    trip_id: str
    status: str
    message: str
    progress: int
    extracted_data: Optional[Dict] = None

class ItineraryResponse(BaseModel):
    trip_id: str
    itinerary: Dict
    recommendations: Dict
    pdf_url: Optional[str] = None

# In-memory storage (for MVP - should use database in production)
processing_status = {}
trip_data = {}

@app.get("/")
async def root():
    return {"message": "TripCraft AI API is running", "version": "1.0.0"}

@app.post("/api/test-multimodal")
async def test_multimodal(file: UploadFile = File(...)):
    """
    Test multimodal extraction on a single file
    """
    try:
        # Save file temporarily
        temp_path = UPLOAD_DIR / f"test_{file.filename}"
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Use multimodal extractor
        from services.llm_multimodal_extractor import MultimodalLLMExtractor
        extractor = MultimodalLLMExtractor()
        result = await extractor.extract_from_image(file_path=str(temp_path))
        
        # Clean up
        temp_path.unlink()
        
        return result
        
    except Exception as e:
        return {"error": str(e), "flights": [], "hotels": [], "passengers": []}

@app.post("/api/upload", response_model=ProcessingResponse)
async def upload_files(
    files: List[UploadFile] = File([]),
    trip_details: Optional[str] = Form(None),
    free_text: Optional[str] = Form(None),
    use_vision: Optional[bool] = Form(True)  # Default to vision mode
):
    """
    Upload travel documents and/or manual trip details
    """
    trip_id = str(uuid.uuid4())
    
    # Debug logging
    print(f"[DEBUG] Upload endpoint called with {len(files) if files else 0} files")
    if files:
        for f in files:
            print(f"[DEBUG] File: {f.filename}, type: {f.content_type}")
    
    # Initialize processing status
    processing_status[trip_id] = {
        "status": "processing",
        "progress": 10,
        "message": "Starting processing..."
    }
    
    # Parse trip details if provided
    details = None
    if trip_details:
        try:
            details = json.loads(trip_details)
        except:
            details = None
    
    # Save uploaded files
    uploaded_files = []
    if files and len(files) > 0:
        for file in files:
            if file.filename:
                file_path = UPLOAD_DIR / f"{trip_id}_{file.filename}"
                print(f"[DEBUG] Saving file: {file_path}")
                async with aiofiles.open(file_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                uploaded_files.append(str(file_path))
                print(f"[DEBUG] File saved: {file_path}, size: {len(content)} bytes")
    
    # Start async processing
    asyncio.create_task(process_trip_data(
        trip_id, 
        uploaded_files, 
        details, 
        free_text,
        use_vision
    ))
    
    return ProcessingResponse(
        trip_id=trip_id,
        status="processing",
        message="Your documents are being processed",
        progress=10
    )

@app.post("/api/upload-single", response_model=ProcessingResponse)
async def upload_single_file(
    file: UploadFile = File(...),
    trip_details: Optional[str] = Form(None),
    free_text: Optional[str] = Form(None),
    use_vision: Optional[bool] = Form(False)  # Default to text mode for single files
):
    """
    Upload a single travel document
    """
    trip_id = str(uuid.uuid4())
    
    print(f"[DEBUG] Single file upload: {file.filename}, type: {file.content_type}")
    
    # Initialize processing status
    processing_status[trip_id] = {
        "status": "processing",
        "progress": 10,
        "message": "Starting processing..."
    }
    
    # Save uploaded file
    uploaded_files = []
    if file and file.filename:
        file_path = UPLOAD_DIR / f"{trip_id}_{file.filename}"
        print(f"[DEBUG] Saving single file: {file_path}")
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        uploaded_files.append(str(file_path))
        print(f"[DEBUG] Single file saved: {file_path}, size: {len(content)} bytes")
    
    # Parse trip details if provided
    details = None
    if trip_details:
        try:
            details = json.loads(trip_details)
        except:
            details = None
    
    # Start async processing
    asyncio.create_task(process_trip_data(
        trip_id, 
        uploaded_files, 
        details, 
        free_text,
        use_vision
    ))
    
    return ProcessingResponse(
        trip_id=trip_id,
        status="processing",
        message="Your document is being processed",
        progress=10
    )

async def process_trip_data(
    trip_id: str, 
    files: List[str], 
    trip_details: Optional[Dict], 
    free_text: Optional[str],
    use_vision: bool = True
):
    """
    Async processing of trip data
    """
    print(f"[DEBUG] Starting process_trip_data for {trip_id}")
    print(f"[DEBUG] Files to process: {files}")
    print(f"[DEBUG] Use vision: {use_vision}")
    
    try:
        # Update status
        processing_status[trip_id]["progress"] = 20
        processing_status[trip_id]["message"] = "Extracting data from documents..."
        
        # Extract data from documents
        extracted_data = {}
        if files:
            # Check if we should use vision mode
            if use_vision:
                # Use multimodal vision extraction
                multimodal_extractor = MultimodalLLMExtractor()
                processing_status[trip_id]["progress"] = 30
                processing_status[trip_id]["message"] = "AI is visually analyzing your documents..."
                
                # Small delay to ensure status update is seen
                await asyncio.sleep(0.5)
                
                # Define progress callback
                async def update_progress(progress: int, message: str):
                    processing_status[trip_id]["progress"] = progress
                    processing_status[trip_id]["message"] = message
                    await asyncio.sleep(0.1)  # Small delay to ensure update is propagated
                
                # Process all files with vision
                vision_result = await multimodal_extractor.extract_from_multiple_files(
                    files, 
                    progress_callback=update_progress
                )
                extracted_data["vision_extraction"] = vision_result
                
                # Update progress after extraction
                processing_status[trip_id]["progress"] = 50
                processing_status[trip_id]["message"] = "Documents analyzed successfully..."
            else:
                # Fallback to text extraction
                pdf_processor = PDFProcessor()
                llm_extractor = LLMExtractor()
                
                total_files = len(files)
                for idx, file_path in enumerate(files):
                    # Update progress for each file
                    file_progress = 30 + (20 * idx // total_files)
                    processing_status[trip_id]["progress"] = file_progress
                    processing_status[trip_id]["message"] = f"Processing file {idx+1} of {total_files}..."
                    
                    print(f"[DEBUG] Processing file: {file_path}")
                    print(f"[DEBUG] File extension check: pdf={file_path.endswith('.pdf')}, txt={file_path.endswith('.txt')}")
                    
                    if file_path.endswith('.pdf'):
                        # Extract text from PDF
                        text = pdf_processor.extract_text(file_path)
                        
                        # Use LLM to extract structured data
                        processing_status[trip_id]["message"] = f"AI is analyzing document {idx+1}..."
                        
                        file_data = await llm_extractor.extract_travel_info(text)
                        extracted_data[os.path.basename(file_path)] = file_data
                    elif file_path.endswith('.txt'):
                        # Read text file directly
                        with open(file_path, 'r') as f:
                            text = f.read()
                        
                        # Use LLM to extract structured data
                        processing_status[trip_id]["message"] = f"AI is analyzing document {idx+1}..."
                        
                        file_data = await llm_extractor.extract_travel_info(text)
                        extracted_data[os.path.basename(file_path)] = file_data
                    elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                        # For images, use multimodal even if text mode selected
                        multimodal_extractor = MultimodalLLMExtractor()
                        img_data = await multimodal_extractor.extract_from_image(file_path=file_path)
                        extracted_data[os.path.basename(file_path)] = img_data
        
        # Combine with manual details
        if trip_details:
            extracted_data["manual_input"] = trip_details
        
        if free_text:
            processing_status[trip_id]["progress"] = 55
            processing_status[trip_id]["message"] = "Processing additional text input..."
            text_data = await LLMExtractor().extract_travel_info(free_text)
            extracted_data["free_text"] = text_data
        
        # Debug extracted data
        print(f"[DEBUG] Extracted data keys: {list(extracted_data.keys())}")
        for key, value in extracted_data.items():
            if isinstance(value, dict):
                print(f"[DEBUG] {key}: flights={len(value.get('flights', []))}, hotels={len(value.get('hotels', []))}")
        
        # Generate itinerary
        processing_status[trip_id]["progress"] = 65
        processing_status[trip_id]["message"] = "Creating your personalized itinerary..."
        await asyncio.sleep(0.5)  # Small delay to show progress
        
        generator = ItineraryGenerator()
        itinerary = await generator.create_itinerary(extracted_data)
        
        # IMMEDIATELY enhance with real content from Perplexity
        processing_status[trip_id]["progress"] = 65
        processing_status[trip_id]["message"] = "Searching for real restaurants and attractions..."
        
        # Debug logging
        print(f"[DEBUG] Trip {trip_id} - Destination: {itinerary.get('trip_summary', {}).get('destination')}")
        print(f"[DEBUG] Trip {trip_id} - Start Date: {itinerary.get('trip_summary', {}).get('start_date')}")
        print(f"[DEBUG] Trip {trip_id} - End Date: {itinerary.get('trip_summary', {}).get('end_date')}")
        
        try:
            immediate_generator = ImmediateGuideGenerator()
            itinerary = await immediate_generator.enhance_itinerary_immediately(itinerary)
            print(f"[DEBUG] Trip {trip_id} - Enhanced with {len(itinerary.get('restaurants', []))} restaurants")
            print(f"[DEBUG] Trip {trip_id} - Enhanced with {len(itinerary.get('attractions', []))} attractions")
        except Exception as e:
            print(f"[ERROR] Trip {trip_id} - Error enhancing: {e}")
            import traceback
            traceback.print_exc()
        
        # Store intermediate results for real-time display
        trip_data[trip_id] = {"itinerary": itinerary}
        
        # Update progress after itinerary
        processing_status[trip_id]["progress"] = 75
        processing_status[trip_id]["message"] = "Itinerary created! Finding recommendations..."
        
        # Get recommendations
        processing_status[trip_id]["progress"] = 85
        processing_status[trip_id]["message"] = "Finding the best restaurants and activities..."
        await asyncio.sleep(0.5)  # Small delay to show progress
        
        recommender = RecommendationsService()
        recommendations = await recommender.get_recommendations(itinerary)
        
        # Store trip data
        trip_data[trip_id] = {
            "extracted_data": extracted_data,
            "itinerary": itinerary,
            "recommendations": recommendations,
            "created_at": datetime.now().isoformat()
        }
        
        # Final processing steps
        processing_status[trip_id]["progress"] = 95
        processing_status[trip_id]["message"] = "Finalizing your travel package..."
        await asyncio.sleep(0.5)
        
        # Update final status
        processing_status[trip_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Processing complete! Your travel package is ready.",
            "extracted_data": extracted_data
        }
        
        # Auto-save the trip
        try:
            await db.save_trip(trip_id, trip_data[trip_id], "default")
            print(f"[DEBUG] Trip {trip_id} auto-saved to database")
        except Exception as e:
            print(f"[DEBUG] Failed to auto-save trip {trip_id}: {e}")
        
    except Exception as e:
        processing_status[trip_id] = {
            "status": "error",
            "progress": 0,
            "message": f"Error processing: {str(e)}"
        }

@app.get("/api/status/{trip_id}", response_model=ProcessingResponse)
async def get_processing_status(trip_id: str):
    """
    Get processing status for a trip
    """
    if trip_id not in processing_status:
        raise HTTPException(status_code=404, detail="Trip ID not found")
    
    status = processing_status[trip_id].copy()
    
    # Include partial extracted data if available
    if trip_id in trip_data and "itinerary" in trip_data[trip_id]:
        itinerary = trip_data[trip_id]["itinerary"]
        status["extracted_data"] = {
            "destination": itinerary.get("trip_summary", {}).get("destination"),
            "dates": {
                "start_date": itinerary.get("trip_summary", {}).get("start_date"),
                "end_date": itinerary.get("trip_summary", {}).get("end_date")
            },
            "flights": itinerary.get("flights", []),
            "hotels": itinerary.get("accommodations", [])
        }
    
    return ProcessingResponse(
        trip_id=trip_id,
        status=status["status"],
        message=status["message"],
        progress=status["progress"],
        extracted_data=status.get("extracted_data")
    )

@app.get("/api/itinerary/{trip_id}", response_model=ItineraryResponse)
async def get_itinerary(trip_id: str):
    """
    Get generated itinerary and recommendations
    """
    if trip_id not in trip_data:
        raise HTTPException(status_code=404, detail="Trip data not found")
    
    data = trip_data[trip_id]
    return ItineraryResponse(
        trip_id=trip_id,
        itinerary=data["itinerary"],
        recommendations=data["recommendations"]
    )

@app.post("/api/generate-pdf/{trip_id}")
async def generate_pdf(trip_id: str):
    """
    Generate PDF travel pack with enhanced guide
    """
    if trip_id not in trip_data:
        raise HTTPException(status_code=404, detail="Trip data not found")
    
    try:
        data = trip_data[trip_id]
        
        # Generate PDF with enhanced guide if available
        pdf_generator = TravelPackGenerator()
        pdf_path = await pdf_generator.generate(
            trip_id,
            data.get("itinerary", {}),
            data.get("recommendations", {}),
            data.get("enhanced_guide", None)  # Pass enhanced guide if it exists
        )
        
        # Store PDF path
        trip_data[trip_id]["pdf_path"] = pdf_path
        
        return {
            "status": "success",
            "pdf_url": f"/api/download/{trip_id}"
        }
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{trip_id}")
async def download_pdf(trip_id: str):
    """
    Download generated PDF
    """
    if trip_id not in trip_data or "pdf_path" not in trip_data[trip_id]:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    pdf_path = trip_data[trip_id]["pdf_path"]
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"travel_pack_{trip_id}.pdf"
    )

@app.post("/api/preferences/{trip_id}")
async def update_preferences(trip_id: str, preferences: Dict):
    """
    Update user preferences and generate enhanced travel guide
    """
    if trip_id not in trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Store preferences
    trip_data[trip_id]["preferences"] = preferences
    
    # Get trip details
    itinerary = trip_data[trip_id].get("itinerary", {})
    destination = itinerary.get("trip_summary", {}).get("destination", "")
    start_date = itinerary.get("trip_summary", {}).get("start_date", "")
    end_date = itinerary.get("trip_summary", {}).get("end_date", "")
    hotels = itinerary.get("accommodations", [])
    hotel_info = hotels[0] if hotels else {}
    
    # Initialize enhanced guide service
    guide_service = EnhancedGuideService()
    
    # Generate comprehensive enhanced guide using advanced prompting
    enhanced_guide = await guide_service.generate_enhanced_guide(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        hotel_info=hotel_info,
        preferences=preferences,
        extracted_data=trip_data[trip_id].get("extracted_data", {})
    )
    
    # Store enhanced guide
    trip_data[trip_id]["enhanced_guide"] = enhanced_guide
    
    # Update recommendations
    recommender = RecommendationsService()
    updated_recs = await recommender.update_with_preferences(
        trip_data[trip_id]["recommendations"],
        preferences
    )
    trip_data[trip_id]["recommendations"] = updated_recs
    
    return {
        "status": "success",
        "message": "Travel guide enhanced with personalized recommendations",
        "guide_preview": {
            "has_summary": bool(enhanced_guide.get("summary")),
            "itinerary_days": len(enhanced_guide.get("daily_itinerary", [])),
            "restaurants_found": len(enhanced_guide.get("restaurants", [])),
            "attractions_found": len(enhanced_guide.get("attractions", [])),
            "events_found": len(enhanced_guide.get("events", [])),
            "hidden_gems": len(enhanced_guide.get("hidden_gems", []))
        }
    }

@app.get("/api/generation-status/{trip_id}")
async def get_generation_status(trip_id: str):
    """
    Get the status of itinerary generation
    """
    if trip_id not in trip_data:
        return {"status": "not_found", "message": "Trip not found"}
    
    # Check if enhanced guide exists
    if "enhanced_guide" in trip_data[trip_id] and trip_data[trip_id]["enhanced_guide"]:
        return {
            "status": "completed",
            "message": "Your personalized guide is ready!",
            "progress": 100
        }
    
    # Check if preferences are being processed
    if "preference_progress" in trip_data[trip_id]:
        return trip_data[trip_id]["preference_progress"]
    
    # Default status
    return {
        "status": "pending",
        "message": "Waiting to start generation",
        "progress": 0
    }

@app.post("/api/trips/{trip_id}/save")
async def save_trip(trip_id: str, user_id: str = "default"):
    """
    Save a trip to persistent storage
    """
    if trip_id not in trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Save the trip
    success = await db.save_trip(trip_id, trip_data[trip_id], user_id)
    
    if success:
        return {"status": "success", "message": "Trip saved successfully", "trip_id": trip_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to save trip")

@app.get("/api/trips/saved")
async def list_saved_trips(user_id: str = "default"):
    """
    List all saved trips for a user
    """
    trips = await db.list_trips(user_id)
    return {"trips": trips, "count": len(trips)}

@app.get("/api/trips/{trip_id}/load")
async def load_saved_trip(trip_id: str):
    """
    Load a saved trip
    """
    # First check if it's already in memory
    if trip_id in trip_data:
        return {
            "trip_id": trip_id,
            "itinerary": trip_data[trip_id].get("itinerary", {}),
            "recommendations": trip_data[trip_id].get("recommendations", {}),
            "source": "memory"
        }
    
    # Try to load from database
    saved_trip = await db.load_trip(trip_id)
    if saved_trip:
        # Load it into memory for quick access
        trip_data[trip_id] = saved_trip
        return {
            "trip_id": trip_id,
            "itinerary": saved_trip.get("itinerary", {}),
            "recommendations": saved_trip.get("recommendations", {}),
            "source": "database"
        }
    
    raise HTTPException(status_code=404, detail="Trip not found")

@app.delete("/api/trips/{trip_id}")
async def delete_trip(trip_id: str):
    """
    Delete a saved trip
    """
    success = await db.delete_trip(trip_id)
    
    # Also remove from memory if present
    if trip_id in trip_data:
        del trip_data[trip_id]
    
    if success:
        return {"status": "success", "message": "Trip deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Trip not found")

@app.get("/api/trips/search")
async def search_trips(q: str, user_id: str = "default"):
    """
    Search saved trips by destination or date
    """
    results = await db.search_trips(q, user_id)
    return {"results": results, "count": len(results)}

@app.get("/api/enhanced-guide/{trip_id}")
async def get_enhanced_guide(trip_id: str):
    """
    Get the enhanced travel guide with all recommendations
    """
    if trip_id not in trip_data:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if "enhanced_guide" not in trip_data[trip_id]:
        raise HTTPException(status_code=404, detail="Enhanced guide not yet generated. Please set preferences first.")
    
    return {
        "trip_id": trip_id,
        "itinerary": trip_data[trip_id]["itinerary"],
        "enhanced_guide": trip_data[trip_id]["enhanced_guide"],
        "recommendations": trip_data[trip_id]["recommendations"]
    }

@app.get("/api/prompts")
async def get_prompts():
    """
    Get the current prompts configuration
    """
    try:
        prompts_path = Path("prompts.json")
        if not prompts_path.exists():
            raise HTTPException(status_code=404, detail="Prompts file not found")
        
        with open(prompts_path, 'r') as f:
            prompts = json.load(f)
        
        return prompts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompts")
async def update_prompts(prompts: Dict):
    """
    Update the prompts configuration
    """
    try:
        prompts_path = Path("prompts.json")
        
        # Create backup
        if prompts_path.exists():
            backup_path = Path(f"prompts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(prompts_path, 'r') as f:
                backup_data = json.load(f)
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
        
        # Save new prompts
        with open(prompts_path, 'w') as f:
            json.dump(prompts, f, indent=2)
        
        return {"status": "success", "message": "Prompts updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)