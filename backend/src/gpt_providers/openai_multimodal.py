import os
import base64
from openai import OpenAI
from typing import Dict, Any, List, Union
import json
from pathlib import Path
import logging
from PIL import Image
import io
import fitz  # PyMuPDF for PDF to image conversion

logger = logging.getLogger(__name__)

class OpenAIMultimodal:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # GPT-4 with vision capabilities
        
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def pdf_to_images(self, pdf_path: str, max_pages: int = 10) -> List[str]:
        """Convert PDF pages to base64 encoded images."""
        images = []
        try:
            pdf_document = fitz.open(pdf_path)
            for page_num in range(min(len(pdf_document), max_pages)):
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.pil_tobytes(format="PNG")
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                images.append(img_base64)
            pdf_document.close()
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
        return images
    
    def process_document(self, 
                        document_path: str = None,
                        image_data: bytes = None,
                        text_prompt: str = None) -> Dict[str, Any]:
        """Process document using multimodal capabilities."""
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert travel document parser. Analyze the provided image(s) and extract ALL travel information including:
                
                1. FLIGHTS: flight numbers, airlines, departure/arrival times, dates, airports, terminals, gates, seat numbers, booking references, baggage allowance
                2. HOTELS: hotel names, addresses, check-in/out dates, room types, confirmation numbers, amenities, meal plans
                3. PASSENGERS: names (with titles), frequent flyer numbers, passport details if visible
                4. OTHER: car rentals, tours, activities, transfers, travel insurance
                
                Extract information from ALL visible elements including:
                - Main text content
                - Headers and footers
                - Tables and structured data
                - QR codes and barcodes (describe what they likely contain)
                - Logos and airline/hotel branding
                - Handwritten notes if any
                
                Return a JSON object with 'flights', 'hotels', 'passengers' and 'other' arrays.
                Include confidence scores (0-1) for extracted data when uncertain."""
            }
        ]
        
        user_content = []
        
        # Add text prompt if provided
        if text_prompt:
            user_content.append({
                "type": "text",
                "text": (f"Additional context: {text_prompt}\n\n"
                         "Please extract all travel information from the document(s):")
            })
        else:
            user_content.append({
                "type": "text", 
                "text": ("Please extract all travel information from the "
                         "following document(s):")
            })
        
        # Process based on input type
        if document_path:
            file_ext = Path(document_path).suffix.lower()
            
            if file_ext == '.pdf':
                # Convert PDF to images
                images = self.pdf_to_images(document_path)
                for img_base64 in images:
                    user_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}",
                            "detail": "high"  # Use high detail for better OCR
                        }
                    })
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                # Direct image processing
                img_base64 = self.encode_image(document_path)
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": (f"data:image/{file_ext[1:]};"
                                f"base64,{img_base64}"),
                        "detail": "high"
                    }
                })
        elif image_data:
            # Process raw image bytes
            img_base64 = base64.b64encode(image_data).decode('utf-8')
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}",
                    "detail": "high"
                }
            })
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        # Define the expected response structure
        function_schema = {
            "name": "parse_travel_details",
            "parameters": {
                "type": "object",
                "properties": {
                    "flights": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "flight_number": {"type": "string"},
                                "operator": {"type": "string"},
                                "booking_reference": {
                                    "type": "string", "nullable": True
                                },
                                "departure": {
                                    "type": "object",
                                    "properties": {
                                        "location": {"type": "string"},
                                        "airport_code": {
                                            "type": "string", "nullable": True
                                        },
                                        "terminal": {
                                            "type": "string", "nullable": True
                                        },
                                        "gate": {
                                            "type": "string", "nullable": True
                                        },
                                        "date": {"type": "string"},
                                        "time": {"type": "string"}
                                    }
                                },
                                "arrival": {
                                    "type": "object",
                                    "properties": {
                                        "location": {"type": "string"},
                                        "airport_code": {
                                            "type": "string", "nullable": True
                                        },
                                        "terminal": {
                                            "type": "string", "nullable": True
                                        },
                                        "gate": {
                                            "type": "string", "nullable": True
                                        },
                                        "date": {"type": "string"},
                                        "time": {"type": "string"}
                                    }
                                },
                                "seat": {"type": "string", "nullable": True},
                                "travel_class": {"type": "string"},
                                "baggage_allowance": {
                                    "type": "object", "nullable": True
                                },
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                            }
                        }
                    },
                    "hotels": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "address": {
                                    "type": "string", "nullable": True
                                },
                                "city": {"type": "string"},
                                "confirmation_number": {
                                    "type": "string", "nullable": True
                                },
                                "check_in_date": {"type": "string"},
                                "check_out_date": {"type": "string"},
                                "room_type": {
                                    "type": "string", "nullable": True
                                },
                                "meal_plan": {
                                    "type": "string", "nullable": True
                                },
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                            }
                        }
                    },
                    "passengers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "nullable": True},
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                                "frequent_flyer": {
                                    "type": "string", "nullable": True
                                },
                                "passport_number": {
                                    "type": "string", "nullable": True
                                },
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                            }
                        }
                    },
                    "other": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "description": {"type": "string"},
                                "date": {"type": "string", "nullable": True},
                                "confirmation": {
                                    "type": "string", "nullable": True
                                },
                                "details": {"type": "object", "nullable": True}
                            }
                        }
                    }
                }
            }
        }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=[function_schema],
                function_call={"name": "parse_travel_details"},
                max_tokens=4096
            )
            
            result = json.loads(response.choices[0].message.function_call.arguments)
            
            # Add metadata about processing
            result['_metadata'] = {
                'model': self.model,
                'processing_type': 'multimodal',
                'document_type': (Path(document_path).suffix 
                                 if document_path else 'image')
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing document with multimodal: {str(e)}")
            return {
                'error': str(e),
                'flights': [],
                'hotels': [],
                'passengers': [],
                'other': []
            }
    
    def process_multiple_documents(self, document_paths: List[str]) -> Dict[str, Any]:
        """Process multiple documents and merge results."""
        all_results = {
            'flights': [],
            'hotels': [],
            'passengers': [],
            'other': []
        }
        
        for path in document_paths:
            result = self.process_document(path)
            if 'error' not in result:
                all_results['flights'].extend(result.get('flights', []))
                all_results['hotels'].extend(result.get('hotels', []))
                all_results['passengers'].extend(result.get('passengers', []))
                all_results['other'].extend(result.get('other', []))
        
        # Deduplicate passengers
        seen_passengers = set()
        unique_passengers = []
        for p in all_results['passengers']:
            key = f"{p.get('first_name', '')}{p.get('last_name', '')}"
            if key not in seen_passengers:
                seen_passengers.add(key)
                unique_passengers.append(p)
        all_results['passengers'] = unique_passengers
        
        return all_results
