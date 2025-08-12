"""
PDF Processing Service
Extracts text from PDF files
"""
import PyPDF2
from pathlib import Path
from typing import List, Dict, Any

class PDFProcessor:
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF file
        """
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                    
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
        
        return text
    
    def extract_metadata(self, file_path: str) -> Dict:
        """
        Extract PDF metadata
        """
        metadata = {}
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if pdf_reader.metadata:
                    metadata = {
                        "title": pdf_reader.metadata.get('/Title', ''),
                        "author": pdf_reader.metadata.get('/Author', ''),
                        "subject": pdf_reader.metadata.get('/Subject', ''),
                        "creator": pdf_reader.metadata.get('/Creator', ''),
                        "pages": len(pdf_reader.pages)
                    }
        except Exception as e:
            print(f"Error extracting metadata: {e}")
        
        return metadata