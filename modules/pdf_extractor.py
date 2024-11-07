import PyPDF2

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    try:
        print(f"Opening PDF file: {file_path}")
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"PDF has {len(reader.pages)} pages")
            text = ''
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += page_text + '\n'
                print(f"Extracted {len(page_text)} characters from page {i+1}")
        return text
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")