import pypdf
from pathlib import Path
from src.models.exceptions import PDFReadError

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    try:
        if not Path(file_path).is_file():
            raise PDFReadError(f"File not found: {file_path}")
            
        with open(file_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = pypdf.PdfReader(file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
    except Exception as e:
        raise PDFReadError(f"Error extracting text from PDF: {str(e)}")
