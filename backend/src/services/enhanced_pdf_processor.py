"""
Enhanced PDF Processing Service
Advanced PDF processing with multimodal capabilities
"""
import asyncio
import io
import base64
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable
import logging

from .interfaces import (
    PDFProcessorInterface,
    ProcessingRequest,
    ProcessingResult,
    ProcessingType,
    FileType,
    ServiceConfig
)
from ..core.exceptions import ProcessingError, ValidationError, FileError
from ..config import get_settings
from .enhanced_redis_cache import cache_manager

logger = logging.getLogger(__name__)


class EnhancedPDFProcessor(PDFProcessorInterface):
    """Enhanced PDF processor with multimodal capabilities"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        if config is None:
            settings = get_settings()
            config = ServiceConfig(
                enabled=settings.services.pdf_enabled,
                timeout_seconds=settings.services.pdf_timeout,
                retry_attempts=2,
                cache_enabled=True,
                cache_ttl_seconds=3600  # 1 hour cache for PDF processing
            )
        
        super().__init__(config, logger)
        
        self.settings = get_settings()
        self._cache: Dict[str, ProcessingResult] = {}
        self._pdf_libraries_available = self._check_pdf_libraries()
    
    @property
    def max_file_size_mb(self) -> int:
        """Get maximum file size in MB"""
        return self.settings.services.file_max_size_mb
    
    async def initialize(self) -> None:
        """Initialize the PDF processor"""
        try:
            if not self._pdf_libraries_available:
                raise ProcessingError(
                    "Required PDF processing libraries not available"
                )
            
            logger.info("Enhanced PDF processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PDF processor: {e}")
            raise ProcessingError(f"PDF processor initialization failed: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check PDF processor health"""
        try:
            return {
                "status": "healthy",
                "processing_type": self.processing_type.value,
                "supported_file_types": [
                    ft.value for ft in self.supported_file_types
                ],
                "max_file_size_mb": self.max_file_size_mb,
                "libraries_available": self._pdf_libraries_available,
                "cache_enabled": self.config.cache_enabled,
                "cache_size": len(self._cache),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self) -> None:
        """Cleanup PDF processor resources"""
        self._cache.clear()
        logger.info("Enhanced PDF processor cleanup completed")
    
    async def process_file(
        self, request: ProcessingRequest
    ) -> ProcessingResult:
        """Process a PDF file with Redis caching"""
        try:
            start_time = datetime.now()
            
            # Validate file
            if not await self.validate_file(request.file_path):
                return ProcessingResult.error_result("File validation failed")
            
            # Generate cache key based on file content hash and options
            file_path = Path(request.file_path)
            file_hash = (
                hashlib.md5(file_path.read_bytes()).hexdigest()
                if file_path.exists() else ""
            )
            
            cache_key_data = {
                "file_hash": file_hash,
                "file_name": file_path.name,
                "options": str(request.options)
            }
            
            # Check Redis cache first
            if self.config.cache_enabled:
                cached_result = await cache_manager.get(
                    "pdf_extraction", cache_key_data
                )
                if cached_result:
                    logger.info(
                        f"Redis cache HIT for PDF: {request.file_path}"
                    )
                    # Convert dict back to ProcessingResult
                    return ProcessingResult(**cached_result)
            
            # Check local memory cache as fallback
            local_cache_key = (
                f"{request.file_path}_{hash(str(request.options))}"
            )
            if self.config.cache_enabled and local_cache_key in self._cache:
                cached_result = self._cache[local_cache_key]
                logger.debug(
                    f"Memory cache HIT for PDF: {request.file_path}"
                )
                # Also store in Redis for next time
                await cache_manager.set(
                    "pdf_extraction", cache_key_data, cached_result.__dict__
                )
                return cached_result
            
            # Extract text and metadata
            extracted_text = await self.extract_text(request.file_path)
            metadata = await self.extract_metadata(request.file_path)
            
            # Extract structured data if requested
            extracted_data = None
            if request.options.get("extract_structured_data", False):
                extracted_data = await self._extract_structured_data(
                    extracted_text, 
                    request.options.get("extraction_type", "travel")
                )
            
            # Extract images if requested
            images = []
            if request.options.get("extract_images", False):
                images = await self.extract_images(request.file_path)
            
            processing_time = (
                (datetime.now() - start_time).total_seconds() * 1000
            )
            
            result = ProcessingResult.success_result(
                extracted_text=extracted_text,
                extracted_data=extracted_data,
                metadata={
                    **metadata,
                    "images_count": len(images),
                    "has_images": len(images) > 0,
                    "processing_options": request.options
                },
                processing_time_ms=processing_time
            )
            
            # Cache result in both Redis and memory
            if self.config.cache_enabled:
                # Store in Redis
                await cache_manager.set(
                    "pdf_extraction", cache_key_data, result.__dict__
                )
                # Store in memory cache
                self._cache[local_cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process PDF {request.file_path}: {e}")
            return ProcessingResult.error_result(f"PDF processing failed: {e}")
    
    async def extract_text(self, file_path: Union[str, Path]) -> str:
        """Extract text from PDF"""
        try:
            file_path = Path(file_path)
            
            # Try multiple extraction methods
            text = await self._extract_text_pypdf2(file_path)
            
            if not text.strip():
                # Fallback to OCR if no text found
                text = await self._extract_text_ocr(file_path)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {e}")
            raise ProcessingError(f"Text extraction failed: {e}")
    
    async def extract_metadata(
        self, file_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        try:
            file_path = Path(file_path)
            
            # Basic file metadata
            stat = file_path.stat()
            metadata = {
                "file_size": stat.st_size,
                "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_time": datetime.fromtimestamp(
                    stat.st_ctime
                ).isoformat(),
                "modified_time": datetime.fromtimestamp(
                    stat.st_mtime
                ).isoformat()
            }
            
            # PDF-specific metadata
            try:
                import PyPDF2
                
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    metadata.update({
                        "page_count": len(pdf_reader.pages),
                        "is_encrypted": pdf_reader.is_encrypted,
                        "pdf_version": getattr(
                            pdf_reader, 'pdf_version', 'Unknown'
                        )
                    })
                    
                    # Document info
                    if pdf_reader.metadata:
                        doc_info = pdf_reader.metadata
                        metadata.update({
                            "title": doc_info.get("/Title", ""),
                            "author": doc_info.get("/Author", ""),
                            "subject": doc_info.get("/Subject", ""),
                            "creator": doc_info.get("/Creator", ""),
                            "producer": doc_info.get("/Producer", ""),
                            "creation_date": str(
                                doc_info.get("/CreationDate", "")
                            ),
                            "modification_date": str(
                                doc_info.get("/ModDate", "")
                            )
                        })
                        
            except Exception as e:
                logger.warning(f"Failed to extract PDF metadata: {e}")
                metadata["pdf_metadata_error"] = str(e)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            return {"error": f"Metadata extraction failed: {e}"}
    
    async def extract_images(self, file_path: Union[str, Path]) -> List[bytes]:
        """Extract images from PDF"""
        try:
            file_path = Path(file_path)
            images = []
            
            try:
                import PyPDF2
                import PIL.Image
                
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        if '/XObject' in page['/Resources']:
                            xObject = page['/Resources'][
                                '/XObject'
                            ].get_object()
                            
                            for obj in xObject:
                                if xObject[obj]['/Subtype'] == '/Image':
                                    try:
                                        size = (
                                            xObject[obj]['/Width'], 
                                            xObject[obj]['/Height']
                                        )
                                        data = xObject[obj].get_data()
                                        
                                        if (xObject[obj]['/ColorSpace'] == 
                                            '/DeviceRGB'):
                                            mode = "RGB"
                                        else:
                                            mode = "P"
                                        
                                        # Convert to PIL Image and bytes
                                        img = PIL.Image.frombytes(
                                            mode, size, data
                                        )
                                        img_bytes = io.BytesIO()
                                        img.save(img_bytes, format='PNG')
                                        images.append(img_bytes.getvalue())
                                        
                                    except Exception as img_error:
                                        logger.warning(
                                            f"Failed to extract image from "
                                            f"page {page_num}: {img_error}"
                                        )
                                        continue
                                        
            except Exception as e:
                logger.warning(f"Failed to extract images using PyPDF2: {e}")
            
            return images
            
        except Exception as e:
            logger.error(f"Failed to extract images from {file_path}: {e}")
            return []
    
    async def _extract_text_pypdf2(self, file_path: Path) -> str:
        """Extract text using PyPDF2"""
        try:
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    try:
                        page_text = page.extract_text()
                        text += page_text + "\n"
                    except Exception as e:
                        logger.warning(
                            f"Failed to extract text from page: {e}"
                        )
                        continue
            
            return text
            
        except ImportError:
            raise ProcessingError("PyPDF2 library not available")
        except Exception as e:
            raise ProcessingError(f"PyPDF2 text extraction failed: {e}")
    
    async def _extract_text_ocr(self, file_path: Path) -> str:
        """Extract text using OCR (fallback method)"""
        try:
            # This would require additional OCR libraries like pytesseract
            # For now, return a placeholder
            logger.warning(
                "OCR text extraction not implemented - would require pytesseract"
            )
            return ""
            
        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            return ""
    
    async def _extract_structured_data(
        self, text: str, extraction_type: str
    ) -> Dict[str, Any]:
        """Extract structured data from text using LLM"""
        try:
            # Import LLM service
            from .service_factory import get_llm_service
            from .interfaces import LLMProvider
            
            # Get LLM service
            llm_service = await get_llm_service(LLMProvider.OPENAI)
            
            # Create extraction prompt based on type
            if extraction_type == "travel":
                prompt = f"""
                Extract travel information from the following text and 
                return as JSON:
                
                Text: {text[:4000]}  # Limit text length
                
                Extract:
                - flights (flight numbers, airlines, dates, times, airports)
                - hotels (names, addresses, check-in/out dates, confirmation codes)
                - passengers (names, contact information)
                - activities (tours, reservations, dates, times)
                - transportation (car rentals, trains, buses)
                
                Return valid JSON only.
                """
            else:
                prompt = f"""
                Extract structured information from the following text and return as JSON:
                
                Text: {text[:4000]}
                
                Extract key information including dates, names, locations, and important details.
                Return valid JSON only.
                """
            
            # Generate response
            response = await llm_service.generate_response(prompt)
            
            if response.is_success:
                # Parse JSON response
                import json
                try:
                    return json.loads(response.content)
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    import re
                    json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    return {"error": "Failed to parse LLM response"}
            else:
                return {"error": f"LLM extraction failed: {response.error}"}
                
        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")
            return {"error": f"Structured extraction failed: {e}"}
    
    def _check_pdf_libraries(self) -> bool:
        """Check if required PDF libraries are available"""
        try:
            import PyPDF2
            return True
        except ImportError:
            logger.warning("PyPDF2 library not available")
            return False
    
    async def validate_file(self, file_path: Union[str, Path]) -> bool:
        """Validate if file can be processed"""
        try:
            file_path = Path(file_path)
            
            # Check if file exists
            if not file_path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            # Check file type
            if not self.supports_file_type(self.get_file_type(file_path)):
                logger.error(f"Unsupported file type: {file_path.suffix}")
                return False
            
            # Check file size
            if not await self.validate_file_size(file_path):
                logger.error(f"File too large: {file_path}")
                return False
            
            # Try to open the PDF
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    # Check if PDF is readable
                    if pdf_reader.is_encrypted:
                        logger.warning(f"PDF is encrypted: {file_path}")
                        # Could still be processed if password is provided
                    
                    # Check if PDF has pages
                    if len(pdf_reader.pages) == 0:
                        logger.error(f"PDF has no pages: {file_path}")
                        return False
                        
            except Exception as e:
                logger.error(f"Failed to validate PDF structure: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File validation failed: {e}")
            return False
    
    async def process_with_vision(
        self,
        file_path: Union[str, Path],
        prompt: str = "Extract all text and information from this document"
    ) -> ProcessingResult:
        """Process PDF using vision models (for complex layouts)"""
        try:
            # Convert PDF pages to images
            images = await self._convert_pdf_to_images(file_path)
            
            if not images:
                return ProcessingResult.error_result("Failed to convert PDF to images")
            
            # Process with vision LLM
            from .service_factory import get_llm_service
            from .interfaces import LLMProvider, LLMRequest
            
            llm_service = await get_llm_service(LLMProvider.OPENAI)
            
            if not llm_service.supports_vision():
                return ProcessingResult.error_result("Vision processing not supported")
            
            # Process first few pages with vision
            all_content = []
            for i, image_bytes in enumerate(images[:5]):  # Limit to first 5 pages
                # Convert to base64
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                vision_request = LLMRequest(
                    prompt=f"{prompt} (Page {i+1})",
                    images=[image_b64]
                )
                
                response = await llm_service.generate_response(vision_request)
                if response.is_success:
                    all_content.append(f"Page {i+1}:\n{response.content}")
            
            combined_content = "\n\n".join(all_content)
            
            return ProcessingResult.success_result(
                extracted_text=combined_content,
                metadata={
                    "processing_method": "vision",
                    "pages_processed": len(all_content),
                    "total_pages": len(images)
                }
            )
            
        except Exception as e:
            logger.error(f"Vision processing failed: {e}")
            return ProcessingResult.error_result(f"Vision processing failed: {e}")
    
    async def _convert_pdf_to_images(self, file_path: Union[str, Path]) -> List[bytes]:
        """Convert PDF pages to images"""
        try:
            # This would require pdf2image library
            # For now, return empty list
            logger.warning("PDF to image conversion not implemented - would require pdf2image")
            return []
            
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            return []
