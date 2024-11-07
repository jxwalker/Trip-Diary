import pytest
from unittest.mock import Mock, patch
from src.processors.pdf_processor import PDFProcessor
from src.models.exceptions import PDFReadError, NoTravelContentError
from src.gpt_interfaces.gpt_interface import GPTInterface
import json
import io
from pypdf import PdfWriter

# Mock GPTInterface for testing
class MockGPTProvider(GPTInterface):
    def generate_text(self, prompt: str, system_prompt: str) -> str:
        # Return a mock JSON response
        return json.dumps({
            "booking_reference": "TEST123",
            "flights": [{
                "flight_number": "AB123",
                "operator": "Airline",
                "class": "Economy",
                "departure": {
                    "date": "2024-12-20",
                    "time": "16:00",
                    "location": "LHR",
                    "terminal": "5"
                },
                "arrival": {
                    "date": "2024-12-20",
                    "time": "20:00",
                    "location": "JFK",
                    "terminal": "4"
                },
                "baggage_allowance": {
                    "hand_baggage": "7kg",
                    "checked_baggage": "23kg"
                }
            }],
            "hotels": []
        })

@pytest.fixture
def mock_gpt_provider():
    return MockGPTProvider()

def create_mock_pdf():
    """Create a simple PDF file in memory."""
    pdf_writer = PdfWriter()
    pdf_writer.add_blank_page(width=72, height=72)
    pdf_bytes = io.BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes

def test_process_file_success(mock_gpt_provider):
    """Test successful processing of a PDF file."""
    mock_pdf = create_mock_pdf()
    
    with patch('src.utils.pdf_utils.extract_text_from_pdf', return_value="Sample text"):
        with patch('pathlib.Path.is_file', return_value=True):
            with patch('builtins.open', return_value=mock_pdf):
                result = PDFProcessor.process_file("sample.pdf", mock_gpt_provider)
                assert result['booking_reference'] == "TEST123"
                assert len(result['flights']) == 1

def test_process_file_pdf_read_error(mock_gpt_provider):
    """Test PDFReadError handling in process_file."""
    with patch('src.utils.pdf_utils.extract_text_from_pdf', side_effect=PDFReadError("Error")):
        with patch('pathlib.Path.is_file', return_value=True):
            with pytest.raises(PDFReadError):
                PDFProcessor.process_file("sample.pdf", mock_gpt_provider)

def test_process_file_no_travel_content_error(mock_gpt_provider):
    """Test NoTravelContentError handling in process_file."""
    with patch('src.utils.pdf_utils.extract_text_from_pdf', return_value=""):
        with patch('pathlib.Path.is_file', return_value=True):
            with pytest.raises(PDFReadError):
                PDFProcessor.process_file("sample.pdf", mock_gpt_provider)

def test_extract_itinerary_with_gpt_success(mock_gpt_provider):
    """Test successful itinerary extraction with GPT."""
    text = "Sample text"
    result = PDFProcessor.extract_itinerary_with_gpt(text, mock_gpt_provider)
    assert result['booking_reference'] == "TEST123"
    assert len(result['flights']) == 1

def test_extract_itinerary_with_gpt_invalid_json(mock_gpt_provider):
    """Test handling of invalid JSON response from GPT."""
    mock_gpt_provider.generate_text = Mock(return_value="Invalid JSON")
    result = PDFProcessor.extract_itinerary_with_gpt("Sample text", mock_gpt_provider)
    assert result is None

def test_extract_itinerary_with_gpt_missing_fields(mock_gpt_provider):
    """Test handling of missing fields in GPT response."""
    mock_gpt_provider.generate_text = Mock(return_value=json.dumps({}))
    result = PDFProcessor.extract_itinerary_with_gpt("Sample text", mock_gpt_provider)
    assert result is None