"""
Upload API routes for file processing
"""
import uuid
import logging
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import aiofiles

from ..dependencies.services import (
    PDFProcessorDep,
    LLMExtractorDep,
    DatabaseServiceDep,
    ImmediateGuideGeneratorDep
)
from ...utils.validation import validate_required_field
from ...utils.error_handling import safe_execute, ProcessingError, create_error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])

# Constants
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_files(
    pdf_processor: PDFProcessorDep,
    llm_extractor: LLMExtractorDep,
    database_service: DatabaseServiceDep,
    immediate_guide: ImmediateGuideGeneratorDep,
    file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = File(None),
    trip_details: Optional[str] = Form(None),
    free_text: Optional[str] = Form(None),
    use_vision: Optional[bool] = Form(True)
):
    """
    Upload travel documents and/or manual trip details

    Args:
        files: List of uploaded files
        trip_details: Manual trip details (JSON string)
        free_text: Free text description
        use_vision: Whether to use vision mode for processing
        pdf_processor: PDF processing service
        llm_extractor: LLM extraction service
        database_service: Database service
        immediate_guide: Immediate guide generator

    Returns:
        Processing response with trip ID and status
    """
    trip_id = str(uuid.uuid4())

    logger.info(f"Upload request received", extra={
        "trip_id": trip_id,
        "file_count": len(files) if files else 0,
        "has_trip_details": bool(trip_details),
        "has_free_text": bool(free_text),
        "use_vision": use_vision
    })

    try:
        # Initialize processing state
        await database_service.create_processing_state(trip_id, "Starting processing...")

        # Process uploaded files
        extracted_data = {}
        
        # Handle single file or multiple files
        files_to_process = []
        if file:
            files_to_process = [file]
        elif files:
            files_to_process = files
            
        logger.info(f"Files to process: {len(files_to_process)}")
        
        if files_to_process:
            file_results = await _process_uploaded_files(
                files_to_process, trip_id, pdf_processor, llm_extractor, use_vision
            )
            # Flatten the extracted data if it's wrapped in filename keys
            if file_results and isinstance(file_results, dict):
                # Get the first file's data (assuming single file upload)
                for filename, data in file_results.items():
                    extracted_data = data
                    break

        # Process manual trip details
        if trip_details:
            logger.info(f"Processing manual trip details: {trip_details[:200]}...")
            manual_data = await _process_manual_details(trip_details, llm_extractor)
            logger.info(f"Manual data extracted: {manual_data}")
            extracted_data.update(manual_data)

        # Process free text
        if free_text:
            text_data = await _process_free_text(free_text, llm_extractor)
            extracted_data.update(text_data)

        # Save extracted data
        await database_service.update_processing_state(
            trip_id, 
            progress=50,
            message="Extraction complete, saving data..."
        )

        # Generate immediate guide (commented out for now)
        # if extracted_data:
        #     immediate_guide_data = await immediate_guide.enhance_itinerary_immediately(extracted_data)
        #     await database_service.save_immediate_guide(trip_id, immediate_guide_data)

        # Mark processing as complete with proper status
        from ...models.database_models import ProcessingStatus
        await database_service.update_processing_state(
            trip_id,
            status=ProcessingStatus.COMPLETED,
            progress=100,
            message="Processing complete"
        )

        # Save the trip data to database for future guide generation
        if extracted_data:
            from ...models.database_models import TripData
            trip_data = TripData(
                trip_id=trip_id,
                user_id="default",  # Default user for now
                extracted_data=extracted_data,
                itinerary=extracted_data,
                preferences={},
                enhanced_guide=None
            )
            await database_service.save_trip_data(trip_data)

            # Clear any cached data for this trip to ensure fresh extraction
            await database_service.clear_trip_cache(trip_id)

            logger.info(f"Saved trip data for {trip_id}")

        return {
            "trip_id": trip_id,
            "status": "success",
            "message": "Files processed successfully",
            "extracted_data": extracted_data
        }

    except Exception as e:
        logger.error(f"Upload processing failed for trip {trip_id}: {e}")
        from ...models.database_models import ProcessingStatus
        await database_service.update_processing_state(
            trip_id,
            status=ProcessingStatus.ERROR,
            message=f"Processing failed: {str(e)}",
            error_details=str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=create_error_response(e, "file upload processing")
        )


async def _process_uploaded_files(
    files: List[UploadFile],
    trip_id: str,
    pdf_processor: PDFProcessorDep,
    llm_extractor: LLMExtractorDep,
    use_vision: bool
) -> dict:
    """Process uploaded files and extract travel data"""
    logger.info(f"Processing {len(files)} files for trip {trip_id}")
    extracted_data = {}

    for file in files:
        if not file.filename:
            continue

        # Save file temporarily
        file_path = UPLOAD_DIR / f"{trip_id}_{file.filename}"

        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        logger.info(f"Processing file: {file.filename}", extra={
            "trip_id": trip_id,
            "file_size": len(content),
            "use_vision": use_vision
        })

        # Extract text from files
        if file.filename.lower().endswith('.pdf'):
            text = pdf_processor.extract_text(str(file_path))
            logger.info(f"Extracted {len(text) if text else 0} characters from PDF")
            if text:
                # Extract structured data using LLM
                file_data = await llm_extractor.extract_travel_info(text)
                logger.info(f"LLM extraction result: {file_data is not None}")
                extracted_data[file.filename] = file_data
            else:
                logger.warning(f"No text extracted from PDF: {file.filename}")
        elif file.filename.lower().endswith('.txt'):
            # Handle text files
            async with aiofiles.open(file_path, 'r') as f:
                text = await f.read()
            logger.info(f"Read {len(text) if text else 0} characters from text file")
            if text:
                # Extract structured data using LLM
                logger.info(f"Sending text to LLM for extraction: {text[:200]}...")
                file_data = await llm_extractor.extract_travel_info(text)
                logger.info(f"LLM extraction result: {file_data}")
                if file_data:
                    extracted_data[file.filename] = file_data
                else:
                    logger.warning(f"LLM extraction returned None for file: {file.filename}")
            else:
                logger.warning(f"Empty text file: {file.filename}")

    return extracted_data


@safe_execute("manual details processing", logger=logger, default_return={})
async def _process_manual_details(
    trip_details: str,
    llm_extractor: LLMExtractorDep
) -> dict:
    """Process manual trip details"""
    import json

    try:
        # Try to parse as JSON first
        manual_data = json.loads(trip_details)
        # Return the data directly if it has the expected structure
        if isinstance(manual_data, dict) and any(key in manual_data for key in ['flights', 'hotels', 'trip_details']):
            return manual_data
        return {"manual_details": manual_data}
    except json.JSONDecodeError:
        # Treat as free text and extract with LLM
        extracted = await llm_extractor.extract_travel_info(trip_details)
        return extracted if extracted else {}


@safe_execute("free text processing", logger=logger, default_return={})
async def _process_free_text(
    free_text: str,
    llm_extractor: LLMExtractorDep
) -> dict:
    """Process free text description"""
    extracted = await llm_extractor.extract_travel_data(free_text)
    return {"free_text": extracted}
