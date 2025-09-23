"""
PDF Processing Service
Extracts text from PDF files with improved error handling and type safety
"""
import PyPDF2
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from ..utils.error_handling import (
    safe_execute, ProcessingError, log_and_return_error
)
from ..utils.validation import validate_pdf_file, validate_file_path
from ..interfaces.services import PDFProcessorInterface

logger = logging.getLogger(__name__)


class PDFProcessor(PDFProcessorInterface):
    """
    Service for processing PDF files and extracting text content
    """

    def __init__(self):
        """Initialize PDF processor"""
        self.logger = logger

    @safe_execute("PDF text extraction", logger=logger, default_return="")
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF file with improved error handling

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content

        Raises:
            ProcessingError: If PDF processing fails
            ValidationError: If file path is invalid
        """
        # Validate input using centralized validation
        file_path_obj = validate_pdf_file(file_path)

        text_content = []

        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            self.logger.info(
                f"Processing PDF with {num_pages} pages: {file_path}"
            )

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()

                if page_text.strip():  # Only add non-empty pages
                    text_content.append(page_text)
                    self.logger.debug(
                        f"Extracted {len(page_text)} characters from page "
                        f"{page_num + 1}"
                    )

        full_text = "\n".join(text_content)
        self.logger.info(
            f"Successfully extracted {len(full_text)} characters from PDF"
        )

        return full_text
    
    @safe_execute("PDF metadata extraction", logger=logger, default_return={})
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract PDF metadata with improved error handling

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary containing PDF metadata
        """
        if not file_path or not Path(file_path).exists():
            return {}

        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            metadata = {
                "pages": len(pdf_reader.pages),
                "file_size": Path(file_path).stat().st_size,
                "file_name": Path(file_path).name
            }

            # Extract PDF metadata if available
            if pdf_reader.metadata:
                pdf_meta = pdf_reader.metadata
                metadata.update({
                    "title": pdf_meta.get('/Title', '').strip(),
                    "author": pdf_meta.get('/Author', '').strip(),
                    "subject": pdf_meta.get('/Subject', '').strip(),
                    "creator": pdf_meta.get('/Creator', '').strip(),
                    "producer": pdf_meta.get('/Producer', '').strip(),
                    "creation_date": str(pdf_meta.get('/CreationDate', '')),
                    "modification_date": str(pdf_meta.get('/ModDate', ''))
                })

            self.logger.info(
                f"Extracted metadata for PDF: {metadata['pages']} pages, "
                f"{metadata['file_size']} bytes"
            )

        return metadata

    def validate_pdf(self, file_path: str) -> bool:
        """
        Validate if file is a readable PDF

        Args:
            file_path: Path to the file

        Returns:
            True if valid PDF, False otherwise
        """
        try:
            file_path_obj = Path(file_path)

            # Check file exists and has PDF extension
            if (not file_path_obj.exists() or 
                    file_path_obj.suffix.lower() != '.pdf'):
                return False

            # Try to read the PDF
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                # Try to access pages to ensure it's readable
                _ = len(pdf_reader.pages)

            return True

        except Exception as e:
            self.logger.warning(f"PDF validation failed for {file_path}: {e}")
            return False
