"""
Processing Service Interface
Standardized interface for file and data processing services
"""
from abc import abstractmethod
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import mimetypes

from .base import BaseService, ServiceConfig


class ProcessingType(str, Enum):
    """Types of processing services"""
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    MULTIMODAL = "multimodal"


class FileType(str, Enum):
    """Supported file types"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    WEBP = "webp"


@dataclass
class ProcessingRequest:
    """Processing request"""
    file_path: Union[str, Path]
    processing_type: ProcessingType
    options: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        self.file_path = Path(self.file_path)
        if self.options is None:
            self.options = {}
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def file_size(self) -> int:
        """Get file size in bytes"""
        return self.file_path.stat().st_size if self.file_path.exists() else 0
    
    @property
    def file_extension(self) -> str:
        """Get file extension"""
        return self.file_path.suffix.lower().lstrip('.')
    
    @property
    def mime_type(self) -> Optional[str]:
        """Get MIME type"""
        return mimetypes.guess_type(str(self.file_path))[0]


@dataclass
class ProcessingResult:
    """Processing result"""
    success: bool
    extracted_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_ms: Optional[float] = None
    
    @classmethod
    def success_result(
        cls,
        extracted_text: Optional[str] = None,
        extracted_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        processing_time_ms: Optional[float] = None
    ):
        return cls(
            success=True,
            extracted_text=extracted_text,
            extracted_data=extracted_data,
            metadata=metadata,
            processing_time_ms=processing_time_ms
        )
    
    @classmethod
    def error_result(cls, error: str, metadata: Optional[Dict[str, Any]] = None):
        return cls(success=False, error=error, metadata=metadata)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "extracted_text": self.extracted_text,
            "extracted_data": self.extracted_data,
            "metadata": self.metadata,
            "error": self.error,
            "processing_time_ms": self.processing_time_ms
        }


class ProcessingServiceInterface(BaseService):
    """Interface for processing services"""
    
    @property
    @abstractmethod
    def processing_type(self) -> ProcessingType:
        """Get the processing type"""
        pass
    
    @property
    @abstractmethod
    def supported_file_types(self) -> List[FileType]:
        """Get supported file types"""
        pass
    
    @property
    @abstractmethod
    def max_file_size_mb(self) -> int:
        """Get maximum file size in MB"""
        pass
    
    @abstractmethod
    async def process_file(self, request: ProcessingRequest) -> ProcessingResult:
        """Process a file"""
        pass
    
    @abstractmethod
    async def validate_file(self, file_path: Union[str, Path]) -> bool:
        """Validate if file can be processed"""
        pass
    
    async def process_file_with_progress(
        self,
        request: ProcessingRequest,
        progress_callback: Optional[Callable[[int, str], Awaitable[None]]] = None
    ) -> ProcessingResult:
        """Process file with progress updates"""
        if progress_callback:
            await progress_callback(0, "Starting file processing...")
        
        # Validate file
        if not await self.validate_file(request.file_path):
            return ProcessingResult.error_result("File validation failed")
        
        if progress_callback:
            await progress_callback(20, "File validated, processing...")
        
        # Process file
        result = await self.process_file(request)
        
        if progress_callback:
            progress = 100 if result.success else 0
            message = "Processing complete" if result.success else f"Processing failed: {result.error}"
            await progress_callback(progress, message)
        
        return result
    
    def supports_file_type(self, file_type: Union[FileType, str]) -> bool:
        """Check if file type is supported"""
        if isinstance(file_type, str):
            try:
                file_type = FileType(file_type.lower())
            except ValueError:
                return False
        return file_type in self.supported_file_types
    
    def get_file_type(self, file_path: Union[str, Path]) -> Optional[FileType]:
        """Get file type from path"""
        path = Path(file_path)
        extension = path.suffix.lower().lstrip('.')
        try:
            return FileType(extension)
        except ValueError:
            return None
    
    async def validate_file_size(self, file_path: Union[str, Path]) -> bool:
        """Validate file size"""
        path = Path(file_path)
        if not path.exists():
            return False
        
        size_mb = path.stat().st_size / (1024 * 1024)
        return size_mb <= self.max_file_size_mb
    
    async def validate_file_type(self, file_path: Union[str, Path]) -> bool:
        """Validate file type"""
        file_type = self.get_file_type(file_path)
        return file_type is not None and self.supports_file_type(file_type)


class PDFProcessorInterface(ProcessingServiceInterface):
    """Interface for PDF processing services"""
    
    @property
    def processing_type(self) -> ProcessingType:
        return ProcessingType.PDF
    
    @property
    def supported_file_types(self) -> List[FileType]:
        return [FileType.PDF]
    
    @abstractmethod
    async def extract_text(self, file_path: Union[str, Path]) -> str:
        """Extract text from PDF"""
        pass
    
    @abstractmethod
    async def extract_metadata(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        pass
    
    @abstractmethod
    async def extract_images(self, file_path: Union[str, Path]) -> List[bytes]:
        """Extract images from PDF"""
        pass
    
    async def get_page_count(self, file_path: Union[str, Path]) -> int:
        """Get number of pages in PDF"""
        metadata = await self.extract_metadata(file_path)
        return metadata.get("page_count", 0)


class ImageProcessorInterface(ProcessingServiceInterface):
    """Interface for image processing services"""
    
    @property
    def processing_type(self) -> ProcessingType:
        return ProcessingType.IMAGE
    
    @property
    def supported_file_types(self) -> List[FileType]:
        return [FileType.JPG, FileType.JPEG, FileType.PNG, FileType.GIF, FileType.BMP, FileType.WEBP]
    
    @abstractmethod
    async def extract_text_ocr(self, file_path: Union[str, Path]) -> str:
        """Extract text from image using OCR"""
        pass
    
    @abstractmethod
    async def get_image_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get image information (dimensions, format, etc.)"""
        pass
    
    @abstractmethod
    async def resize_image(
        self,
        file_path: Union[str, Path],
        width: int,
        height: int,
        output_path: Union[str, Path]
    ) -> bool:
        """Resize image"""
        pass


class MultimodalProcessorInterface(ProcessingServiceInterface):
    """Interface for multimodal processing services (vision + text)"""
    
    @property
    def processing_type(self) -> ProcessingType:
        return ProcessingType.MULTIMODAL
    
    @property
    def supported_file_types(self) -> List[FileType]:
        return [FileType.PDF, FileType.JPG, FileType.JPEG, FileType.PNG]
    
    @abstractmethod
    async def extract_with_vision(
        self,
        file_path: Union[str, Path],
        prompt: str
    ) -> Dict[str, Any]:
        """Extract information using vision models"""
        pass
    
    @abstractmethod
    async def analyze_document_structure(
        self,
        file_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """Analyze document structure and layout"""
        pass


class TextProcessorInterface(ProcessingServiceInterface):
    """Interface for text processing services"""
    
    @property
    def processing_type(self) -> ProcessingType:
        return ProcessingType.TEXT
    
    @property
    def supported_file_types(self) -> List[FileType]:
        return [FileType.TXT, FileType.DOCX]
    
    @abstractmethod
    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        pass
    
    @abstractmethod
    async def summarize_text(self, text: str, max_length: int = 500) -> str:
        """Summarize text"""
        pass
    
    @abstractmethod
    async def classify_text(self, text: str, categories: List[str]) -> Dict[str, float]:
        """Classify text into categories"""
        pass
