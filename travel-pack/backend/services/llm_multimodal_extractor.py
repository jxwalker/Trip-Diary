"""
Multimodal LLM Extractor Service
Uses vision-capable models to extract travel information directly from images/PDFs
"""
import os
import json
import base64
from typing import Dict, Any, Optional, List, Union
from openai import AsyncOpenAI
import anthropic
from dotenv import load_dotenv
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import io

# Load .env from backend directory
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(env_path)

class MultimodalLLMExtractor:
    def __init__(self):
        self.openai_client = None
        self.claude_client = None
        
        if os.getenv("OPENAI_API_KEY"):
            self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if os.getenv("ANTHROPIC_API_KEY"):
            self.claude_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def pdf_to_images_base64(self, pdf_path: str, max_pages: int = 10) -> List[str]:
        """Convert PDF pages to base64 encoded images."""
        images = []
        try:
            pdf_document = fitz.open(pdf_path)
            for page_num in range(min(len(pdf_document), max_pages)):
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale
                img_data = pix.pil_tobytes(format="PNG")
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                images.append(img_base64)
            pdf_document.close()
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
        return images
    
    def image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    async def extract_from_image(self, 
                                 file_path: Optional[str] = None,
                                 image_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Extract travel information using multimodal vision capabilities.
        """
        
        system_prompt = """You are an expert travel document analyzer with perfect OCR capabilities.
        Extract ALL travel information from the document image(s) with 100% accuracy.
        
        CRITICAL REQUIREMENTS:
        - Extract ALL flights (both outbound AND return flights)
        - Parse dates EXACTLY - "09 Aug 25" means August 9, 2025
        - Extract passenger names EXACTLY as shown (e.g., "MR PETER JAMES LLOYD WALKER")
        - For hotel dates, find actual check-in and check-out dates
        - Identify the destination city from the travel documents
        - Return dates in YYYY-MM-DD format (2025-08-09 not 2024-08-09)
        - Include booking references, PNRs, confirmation numbers
        - If year is abbreviated (25), it means 2025
        - Extract seat numbers, flight classes, terminals
        """
        
        user_prompt = """Extract ALL travel information from this document.
        
        CRITICAL INSTRUCTIONS:
        1. Extract EXACT dates as shown in document (e.g., "09 Aug 25" becomes "2025-08-09")
        2. Extract FULL passenger names exactly as written
        3. For dates, if you see "09 Aug" assume current or next year (2025)
        4. Include ALL flight segments (outbound AND return)
        5. Extract actual check-in/check-out dates for hotels
        
        Return a JSON object with this EXACT structure:
        {
            "flights": [
                {
                    "flight_number": "XX123",
                    "airline": "Example Airlines",
                    "departure_airport": "ABC",
                    "departure_city": "City1",
                    "arrival_airport": "XYZ",
                    "arrival_city": "City2",
                    "departure_date": "YYYY-MM-DD",
                    "departure_time": "HH:MM",
                    "arrival_date": "YYYY-MM-DD",
                    "arrival_time": "HH:MM",
                    "seat": "1A",
                    "class": "Economy/Business/First",
                    "terminal": "1",
                    "gate": "A1",
                    "booking_reference": "ABC123",
                    "passenger_name": "MR/MS FIRSTNAME LASTNAME",
                    "confidence": 1.0
                }
            ],
            "hotels": [
                {
                    "name": "Hotel Name",
                    "address": "123 Street",
                    "city": "New York",
                    "check_in_date": "2025-08-09",
                    "check_out_date": "2025-08-14",
                    "confirmation_number": "83313860",
                    "room_type": "Suite",
                    "nights": 5,
                    "confidence": 1.0
                }
            ],
            "passengers": [
                {
                    "title": "MR",
                    "first_name": "Peter",
                    "last_name": "Walker",
                    "full_name": "Peter Walker",
                    "frequent_flyer": "BA47940415",
                    "confidence": 1.0
                }
            ],
            "dates": {
                "start_date": "2025-08-09",
                "end_date": "2025-08-14"
            },
            "destination": "New York",
            "other": []
        }
        
        Include confidence scores (0-1) for each extracted item.
        Return ONLY the JSON, no markdown or explanations."""
        
        try:
            # Prepare image data
            image_data_list = []
            
            if file_path:
                file_ext = Path(file_path).suffix.lower()
                
                if file_ext == '.pdf':
                    # Convert PDF to images
                    images = self.pdf_to_images_base64(file_path)
                    image_data_list = [{"base64": img, "type": "image/png"} for img in images]
                elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    # Direct image
                    img_base64 = self.image_to_base64(file_path)
                    image_data_list = [{"base64": img_base64, "type": f"image/{file_ext[1:]}"}]
            elif image_bytes:
                # Raw bytes
                img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                image_data_list = [{"base64": img_base64, "type": "image/png"}]
            
            if not image_data_list:
                return self._empty_result("No valid image data")
            
            # Use OpenAI GPT-4 Vision
            if self.openai_client:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt}
                        ]
                    }
                ]
                
                # Add images to the message
                for img_data in image_data_list:
                    messages[1]["content"].append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{img_data['type']};base64,{img_data['base64']}",
                            "detail": "high"  # High detail for better OCR
                        }
                    })
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",  # or "gpt-4-vision-preview"
                    messages=messages,
                    max_tokens=4096,
                    temperature=0.1
                )
                
                result_text = response.choices[0].message.content
                
                # Clean up response
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0]
                
                result = json.loads(result_text.strip())
                
                # Add metadata
                result['_metadata'] = {
                    'extraction_method': 'multimodal_vision',
                    'model': 'gpt-4o',
                    'pages_processed': len(image_data_list)
                }
                
                return result
            
            # Use Claude Vision if available
            elif self.claude_client:
                # Claude 3 models with vision
                message_content = [
                    {"type": "text", "text": user_prompt}
                ]
                
                for img_data in image_data_list:
                    message_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": img_data['type'],
                            "data": img_data['base64']
                        }
                    })
                
                response = await self.claude_client.messages.create(
                    model="claude-3-sonnet-20240229",  # or claude-3-opus-20240229
                    max_tokens=4096,
                    temperature=0.1,
                    messages=[
                        {"role": "user", "content": message_content}
                    ]
                )
                
                result_text = response.content[0].text
                
                # Extract JSON
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result['_metadata'] = {
                        'extraction_method': 'multimodal_vision',
                        'model': 'claude-3-sonnet',
                        'pages_processed': len(image_data_list)
                    }
                    return result
            
            return self._empty_result("No vision-capable LLM available")
            
        except Exception as e:
            print(f"Multimodal extraction error: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_result(str(e))
    
    def _empty_result(self, error_msg: str = "") -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "flights": [],
            "hotels": [],
            "passengers": [],
            "other": [],
            "_metadata": {
                "extraction_method": "multimodal_vision",
                "error": error_msg
            }
        }
    
    async def extract_from_multiple_files(self, file_paths: List[str], progress_callback=None) -> Dict[str, Any]:
        """Process multiple files and merge results."""
        all_results = {
            "flights": [],
            "hotels": [],
            "passengers": [],
            "other": []
        }
        
        total_files = len(file_paths)
        for idx, file_path in enumerate(file_paths):
            # Update progress if callback provided
            if progress_callback:
                progress = 30 + (20 * (idx + 1) // total_files)  # Progress from 30-50%
                await progress_callback(progress, f"Analyzing document {idx+1} of {total_files}...")
            
            result = await self.extract_from_image(file_path=file_path)
            if result and not result.get("_metadata", {}).get("error"):
                all_results["flights"].extend(result.get("flights", []))
                all_results["hotels"].extend(result.get("hotels", []))
                all_results["passengers"].extend(result.get("passengers", []))
                all_results["other"].extend(result.get("other", []))
        
        # Deduplicate
        all_results = self._deduplicate_results(all_results)
        
        return all_results
    
    def _deduplicate_results(self, results: Dict) -> Dict:
        """Remove duplicate entries."""
        # Deduplicate flights by flight number + date
        seen_flights = set()
        unique_flights = []
        for flight in results["flights"]:
            key = f"{flight.get('flight_number', '')}{flight.get('departure_date', '')}"
            if key not in seen_flights:
                seen_flights.add(key)
                unique_flights.append(flight)
        results["flights"] = unique_flights
        
        # Deduplicate hotels by name + check-in date
        seen_hotels = set()
        unique_hotels = []
        for hotel in results["hotels"]:
            key = f"{hotel.get('name', '')}{hotel.get('check_in_date', '')}"
            if key not in seen_hotels:
                seen_hotels.add(key)
                unique_hotels.append(hotel)
        results["hotels"] = unique_hotels
        
        # Deduplicate passengers by name
        seen_passengers = set()
        unique_passengers = []
        for passenger in results["passengers"]:
            key = f"{passenger.get('first_name', '')}{passenger.get('last_name', '')}"
            if key not in seen_passengers:
                seen_passengers.add(key)
                unique_passengers.append(passenger)
        results["passengers"] = unique_passengers
        
        return results