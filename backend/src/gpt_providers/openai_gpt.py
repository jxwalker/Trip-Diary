import os
from openai import OpenAI
from typing import Dict, Any
import json

class OpenAIGPT:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("PRIMARY_MODEL", "xai/grok-4-fast-free")

    def generate_text(self, prompt: str, system: str | None = None) -> Dict[str, Any]:
        """Generate structured travel data from text."""
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            
            messages.append({
                "role": "system",
                "content": """You are a travel itinerary parser. Extract all flight, hotel, and passenger information.
                
                For flights, include:
                - All flight details (number, operator, departure, arrival, class, baggage)
                - Passengers on each specific flight (who is traveling on which flight)
                
                For hotels, always include detailed room information including:
                - Room type
                - Bed configuration
                - Room size
                - Room features
                - Meal plan
                - Occupancy
                
                For passengers, include:
                - All passengers mentioned in the document
                - Assign passengers to the specific flights they are on
                
                Format the response as a JSON object with 'flights', 'hotels', and 'passengers' arrays."""
            })

            messages.append({"role": "user", "content": prompt})

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
                                    "departure": {
                                        "type": "object",
                                        "properties": {
                                            "location": {"type": "string"},
                                            "terminal": {"type": "string", "nullable": True},
                                            "date": {"type": "string", "format": "date"},
                                            "time": {"type": "string", "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"}
                                        },
                                        "required": ["location", "date", "time"]
                                    },
                                    "arrival": {
                                        "type": "object",
                                        "properties": {
                                            "location": {"type": "string"},
                                            "terminal": {"type": "string", "nullable": True},
                                            "date": {"type": "string", "format": "date"},
                                            "time": {"type": "string", "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"}
                                        },
                                        "required": ["location", "date", "time"]
                                    },
                                    "travel_class": {"type": "string", "default": "Economy"},
                                    "baggage_allowance": {
                                        "type": "object",
                                        "properties": {
                                            "checked_baggage": {"type": "string", "nullable": True},
                                            "hand_baggage": {"type": "string", "nullable": True}
                                        }
                                    },
                                    "passengers": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string", "enum": ["MR", "MRS", "MS", "MISS"]},
                                                "first_name": {"type": "string"},
                                                "last_name": {"type": "string"},
                                                "frequent_flyer": {"type": "string", "nullable": True}
                                            },
                                            "required": ["title", "first_name", "last_name"]
                                        }
                                    }
                                },
                                "required": ["flight_number", "operator", "departure", "arrival"]
                            }
                        },
                        "hotels": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "city": {"type": "string"},
                                    "check_in_date": {"type": "string"},
                                    "check_out_date": {"type": "string"},
                                    "rooms": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "room_type": {"type": "string"},
                                                "bed_type": {"type": "string"},
                                                "size": {"type": "string"},
                                                "features": {
                                                    "type": "array",
                                                    "items": {"type": "string"}
                                                },
                                                "meal_plan": {"type": "string"},
                                                "occupancy": {"type": "string"}
                                            },
                                            "required": ["room_type"]
                                        }
                                    }
                                },
                                "required": ["name", "city", "check_in_date", "check_out_date"]
                            }
                        },
                        "passengers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "enum": ["MR", "MRS", "MS", "MISS"]},
                                    "first_name": {"type": "string"},
                                    "last_name": {"type": "string"},
                                    "frequent_flyer": {"type": "string", "nullable": True}
                                },
                                "required": ["title", "first_name", "last_name"]
                            }
                        }
                    }
                }
            }

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=[function_schema],
                function_call={"name": "parse_travel_details"}
            )

            return json.loads(response.choices[0].message.function_call.arguments)
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return None
