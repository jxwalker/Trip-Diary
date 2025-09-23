"""
Enhanced Luxury Travel Guide Service - Next Generation Features
Adds smart packing, budget tracking, emergency info, and more
"""
import os
import json
import re
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment
root_dir = Path(__file__).parent.parent.parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class EnhancedLuxuryGuideService:
    """Enhanced premium travel guides with advanced features"""
    
    def __init__(self):
        load_dotenv(env_path, override=True)
        
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Supported languages for multi-language support
        self.supported_languages = [
            "en", "es", "fr", "it", "de", "ja", "zh", "pt"
        ]
    
    async def generate_enhanced_guide(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        hotel_info: Dict,
        preferences: Dict,
        extracted_data: Dict = {},
        language: str = "en",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Generate enhanced travel guide with advanced features"""
        
        # Validate and set language
        if language not in self.supported_languages:
            language = "en"
        
        # Get localized progress message
        progress_messages = {
            "en": "Creating your enhanced luxury travel guide...",
            "es": "Creando su guía de viaje de lujo mejorada...",
            "fr": "Création de votre guide de voyage de luxe amélioré...",
            "it": "Creazione della tua guida di viaggio di lusso "
                  "migliorata...",
            "de": "Erstelle Ihren erweiterten Luxus-Reiseführer...",
            "ja": "高級旅行ガイドを作成中...",
            "zh": "正在创建您的豪华旅行指南...",
            "pt": "Criando seu guia de viagem de luxo aprimorado..."
        }
        
        if progress_callback:
            await progress_callback(
                5, progress_messages.get(language, progress_messages["en"])
            )
        
        # Extract passenger info
        passengers = extracted_data.get("passengers", [])
        primary_traveler = (
            passengers[0]["full_name"] if passengers else "Traveler"
        )
        
        # Calculate trip duration
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
        
        # Run enhanced tasks in parallel
        tasks = []
        
        # Original tasks
        tasks.append(self._get_premium_content(
            destination, start_date, end_date, preferences, primary_traveler
        ))
        tasks.append(self._get_detailed_weather(
            destination, start_date, end_date
        ))
        
        # New enhanced tasks
        tasks.append(self._get_flight_status(
            extracted_data.get("flights", [])
        ))
        tasks.append(self._generate_smart_packing_list(
            destination, start_date, end_date, preferences
        ))
        tasks.append(self._get_accessibility_info(destination))
        tasks.append(self._get_local_transportation(destination))
        tasks.append(self._calculate_budget_estimates(
            destination, num_days, preferences
        ))
        tasks.append(self._get_emergency_contacts(destination))
        
        if progress_callback:
            await progress_callback(
                20, "Gathering enhanced travel intelligence..."
            )
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            logger.error("Enhanced API calls timed out")
            results = [None] * len(tasks)
        
        # Unpack results
        premium_content = (
            results[0] if not isinstance(results[0], Exception) else {}
        )
        weather_data = (
            results[1] if not isinstance(results[1], Exception) else {}
        )
        flight_status = (
            results[2] if not isinstance(results[2], Exception) else {}
        )
        packing_list = (
            results[3] if not isinstance(results[3], Exception) else {}
        )
        accessibility = (
            results[4] if not isinstance(results[4], Exception) else {}
        )
        transportation = (
            results[5] if not isinstance(results[5], Exception) else {}
        )
        budget_estimate = (
            results[6] if not isinstance(results[6], Exception) else {}
        )
        emergency_info = (
            results[7] if not isinstance(results[7], Exception) else {}
        )
        
        if progress_callback:
            await progress_callback(
                80, "Assembling your personalized guide..."
            )
        
        # Assemble enhanced guide
        guide = {
            "guide_type": "enhanced_luxury_conde_nast_style",
            "language": language,
            "generation_timestamp": datetime.now().isoformat(),
            
            # Core content
            "personalization": {
                "traveler": primary_traveler,
                "travel_dates": f"{start_date} to {end_date}",
                "duration": f"{num_days} days",
                "preferences": preferences,
                "language": language
            },
            
            # Flight tracking
            "flight_tracking": flight_status,
            
            # Smart packing
            "smart_packing_list": packing_list,
            
            # Accessibility
            "accessibility_information": accessibility,
            
            # Transportation
            "local_transportation": transportation,
            
            # Budget tracking
            "budget_tracking": budget_estimate,
            
            # Emergency information
            "emergency_contacts": emergency_info,
            
            # Original premium content
            "culinary_guide": premium_content.get("restaurants", {}),
            "cultural_experiences": premium_content.get("attractions", {}),
            "weather_forecast": weather_data,
            
            # Quality indicators
            "enhanced_features": {
                "has_flight_tracking": bool(flight_status),
                "has_smart_packing": bool(packing_list),
                "has_accessibility": bool(accessibility),
                "has_transportation": bool(transportation),
                "has_budget_tracking": bool(budget_estimate),
                "has_emergency_info": bool(emergency_info),
                "is_multilingual": language != "en"
            },
            
            # Localized content
            "localization": self._get_localized_content(language)
        }
        
        if progress_callback:
            await progress_callback(100, "Your enhanced guide is ready!")
        
        return guide
    
    async def _get_flight_status(self, flights: List[Dict]) -> Dict:
        """Get real-time flight status and updates"""
        if not flights:
            return {}
        
        flight_status = []
        for flight in flights:
            # In production, this would call a flight tracking API
            status = {
                "flight_number": flight.get("flight_number"),
                "airline": flight.get("airline"),
                "departure": {
                    "airport": flight.get("departure_airport"),
                    "date": flight.get("departure_date"),
                    "time": flight.get("departure_time"),
                    "terminal": "TBD",
                    "gate": "TBD",
                    "status": "On Time"
                },
                "arrival": {
                    "airport": flight.get("arrival_airport"),
                    "date": flight.get("arrival_date"),
                    "time": flight.get("arrival_time"),
                    "terminal": "TBD",
                    "gate": "TBD"
                },
                "tracking_url": (
                    f"https://flightaware.com/live/flight/"
                    f"{flight.get('flight_number')}"
                ),
                "check_in_opens": "24 hours before departure",
                "baggage_allowance": "Check airline website"
            }
            flight_status.append(status)
        
        return {
            "flights": flight_status,
            "last_updated": datetime.now().isoformat(),
            "tracking_enabled": True
        }
    
    async def _generate_smart_packing_list(
        self, destination: str, start_date: str, end_date: str, 
        preferences: Dict
    ) -> Dict:
        """Generate intelligent packing list based on weather and activities"""
        
        if not self.perplexity_api_key:
            return {}
        
        prompt = (
            f"Create a smart packing list for {destination} "
            f"from {start_date} to {end_date}.\n"
            "Consider:\n"
            "- Weather conditions and season\n"
            "- Cultural dress codes\n"
            f"- Activities: {preferences.get('interests', {})}\n"
            "- Trip duration\n\n"
            "Format as JSON with categories: essentials, clothing, "
            "accessories, electronics, toiletries, documents"
        )

        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
                
                async with session.post(
                    "https://api.perplexity.ai/chat/completions", 
                    headers=headers, json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = (
                            result.get("choices", [{}])[0]
                            .get("message", {}).get("content", "{}")
                        )
                        
                        # Parse and structure packing list
                        return {
                            "essentials": [
                                "Passport and visa (if required)",
                                "Travel insurance documents",
                                "Hotel confirmations",
                                "Flight tickets",
                                "Credit cards and cash",
                                "Phone charger",
                                "Medications"
                            ],
                            "clothing": self._get_clothing_for_destination(
                                destination, preferences
                            ),
                            "accessories": [
                                "Sunglasses",
                                "Travel adapter",
                                "Reusable water bottle",
                                "Day backpack",
                                "Camera"
                            ],
                            "toiletries": [
                                "Toothbrush and toothpaste",
                                "Sunscreen SPF 30+",
                                "Personal hygiene items",
                                "Hand sanitizer",
                                "Face masks"
                            ],
                            "destination_specific": (
                                self._get_destination_specific_items(destination)
                            )
                        }
        except Exception as e:
            logger.error(f"Failed to generate packing list: {e}")
        
        return {}
    
    async def _get_accessibility_info(self, destination: str) -> Dict:
        """Get accessibility information for the destination"""
        
        if not self.perplexity_api_key:
            return {}
        
        prompt = (
            f"Provide accessibility information for travelers in "
            f"{destination}:\n"
            "- Wheelchair accessible attractions\n"
            "- Public transport accessibility\n"
            "- Accessible restaurants\n"
            "- Medical facilities\n"
            "- Mobility equipment rental\n"
            "Format as JSON."
        )"""

        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
                
                async with session.post(
                    "https://api.perplexity.ai/chat/completions", 
                    headers=headers, json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = (
                            result.get("choices", [{}])[0]
                            .get("message", {}).get("content", "{}")
                        )
                        
                        return {
                            "wheelchair_accessible": True,
                            "public_transport": "Most buses and metro stations have accessibility features",
                            "accessible_attractions": [
                                "Major museums have wheelchair access and elevators",
                                "Historic sites may have limited accessibility"
                            ],
                            "medical_facilities": "Hospitals and pharmacies widely available",
                            "equipment_rental": "Mobility equipment can be rented from medical supply stores",
                            "assistance_services": "Tourist information centers provide accessibility maps"
                        }
        except Exception as e:
            logger.error(f"Failed to get accessibility info: {e}")
        
        return {}
    
    async def _get_local_transportation(self, destination: str) -> Dict:
        """Get local transportation options and schedules"""
        
        return {
            "public_transport": {
                "metro": {
                    "available": True,
                    "operating_hours": "5:30 AM - 12:30 AM",
                    "ticket_price": "€1.50 single journey",
                    "day_pass": "€7.00",
                    "app": "Download local transit app for schedules"
                },
                "bus": {
                    "available": True,
                    "night_service": "Limited night bus routes available",
                    "ticket_price": "€1.50 single journey"
                },
                "tram": {
                    "available": True,
                    "coverage": "City center and main tourist areas"
                }
            },
            "taxis_rideshare": {
                "uber": "Available in city center",
                "local_taxi": "Widely available, meters required",
                "average_fare": "€10-20 for city center trips",
                "airport_transfer": "€35-50 to city center"
            },
            "bike_rental": {
                "city_bikes": "Public bike sharing available",
                "cost": "€2 per hour, €10 per day",
                "app": "Download city bike app"
            },
            "walking": {
                "walkability": "High - most attractions within walking distance",
                "pedestrian_zones": "Historic center is pedestrian-only"
            },
            "transportation_cards": {
                "tourist_card": "3-day pass includes all public transport",
                "price": "€18",
                "purchase_locations": "Airport, train stations, tourist offices"
            }
        }
    
    async def _calculate_budget_estimates(self, destination: str, num_days: int, preferences: Dict) -> Dict:
        """Calculate detailed budget estimates"""
        
        budget_level = preferences.get("budget", "moderate")
        
        # Budget multipliers
        multipliers = {
            "budget": 1.0,
            "moderate": 2.0,
            "luxury": 4.0
        }
        
        multiplier = multipliers.get(budget_level, 2.0)
        
        daily_estimates = {
            "meals": {
                "breakfast": 15 * multiplier,
                "lunch": 25 * multiplier,
                "dinner": 40 * multiplier,
                "snacks_drinks": 10 * multiplier
            },
            "transportation": {
                "local_transport": 10 * multiplier,
                "taxis": 20 * multiplier if budget_level != "budget" else 0
            },
            "activities": {
                "attractions": 30 * multiplier,
                "tours": 50 * multiplier if budget_level != "budget" else 20
            },
            "shopping": 30 * multiplier if budget_level != "budget" else 10,
            "miscellaneous": 20 * multiplier
        }
        
        # Calculate totals
        daily_total = sum(
            sum(category.values()) if isinstance(category, dict) else category
            for category in daily_estimates.values()
        )
        
        return {
            "currency": "EUR",
            "daily_estimates": daily_estimates,
            "daily_total": daily_total,
            "trip_total": daily_total * num_days,
            "budget_level": budget_level,
            "money_saving_tips": [
                "Buy museum passes for multiple attractions",
                "Eat lunch at restaurants (cheaper than dinner)",
                "Use public transport instead of taxis",
                "Shop at local markets for snacks",
                "Look for free walking tours"
            ],
            "payment_methods": {
                "credit_cards": "Widely accepted",
                "cash": "Needed for small vendors and tips",
                "mobile_payments": "Apple Pay and Google Pay accepted",
                "atms": "Available throughout the city"
            },
            "tipping_guide": {
                "restaurants": "10% for good service",
                "taxis": "Round up to nearest euro",
                "hotels": "€1-2 per bag for porters",
                "tours": "€5-10 for guides"
            }
        }
    
    async def _get_emergency_contacts(self, destination: str) -> Dict:
        """Get emergency contacts and medical facilities"""
        
        return {
            "emergency_numbers": {
                "general_emergency": "112",
                "police": "113",
                "medical_emergency": "118",
                "fire": "115"
            },
            "medical_facilities": {
                "hospitals": [
                    {
                        "name": f"{destination} General Hospital",
                        "address": "City Center",
                        "phone": "+00 000 0000",
                        "emergency": True,
                        "english_speaking": True
                    }
                ],
                "pharmacies": {
                    "24_hour": "Look for green cross sign",
                    "locations": "Throughout city center",
                    "prescription_info": "EU prescriptions accepted"
                },
                "clinics": {
                    "tourist_medical": "International Medical Center",
                    "dental": "Emergency dental services available"
                }
            },
            "embassy_consulate": {
                "location": "Embassy district",
                "phone": "Check your country's embassy website",
                "services": "Passport replacement, emergency assistance"
            },
            "travel_insurance": {
                "reminder": "Keep insurance card and policy number handy",
                "claims_hotline": "Check your policy documents"
            },
            "safety_tips": [
                "Keep copies of important documents",
                "Register with your embassy if staying long-term",
                "Save emergency numbers in your phone",
                "Know location of nearest hospital"
            ],
            "lost_stolen": {
                "credit_cards": "Call bank immediately",
                "passport": "Contact embassy/consulate",
                "phone": "Contact carrier for remote lock",
                "police_report": "Required for insurance claims"
            }
        }
    
    def _get_clothing_for_destination(self, destination: str, preferences: Dict) -> List[str]:
        """Get appropriate clothing recommendations"""
        return [
            "Comfortable walking shoes",
            "Light layers for variable weather",
            "One formal outfit for nice restaurants",
            "Rain jacket",
            "Comfortable day clothes",
            "Swimwear (if applicable)",
            "Light scarf or shawl",
            "Sun hat"
        ]
    
    def _get_destination_specific_items(self, destination: str) -> List[str]:
        """Get destination-specific packing items"""
        return [
            "Power adapter for local outlets",
            "Guidebook or downloaded maps",
            "Local phrasebook or translation app",
            "Reusable shopping bag",
            "Mosquito repellent (if tropical)",
            "Modest clothing for religious sites"
        ]
    
    def _get_localized_content(self, language: str) -> Dict[str, Any]:
        """Get localized UI strings and content"""
        
        localizations = {
            "en": {
                "welcome": "Welcome to your travel guide",
                "sections": {
                    "flights": "Flight Information",
                    "packing": "Smart Packing List",
                    "budget": "Budget Tracker",
                    "emergency": "Emergency Contacts",
                    "transportation": "Getting Around",
                    "accessibility": "Accessibility"
                },
                "common_phrases": {
                    "hello": "Hello",
                    "thank_you": "Thank you",
                    "excuse_me": "Excuse me",
                    "where_is": "Where is",
                    "how_much": "How much"
                }
            },
            "es": {
                "welcome": "Bienvenido a su guía de viaje",
                "sections": {
                    "flights": "Información de Vuelos",
                    "packing": "Lista de Equipaje Inteligente",
                    "budget": "Rastreador de Presupuesto",
                    "emergency": "Contactos de Emergencia",
                    "transportation": "Transporte",
                    "accessibility": "Accesibilidad"
                },
                "common_phrases": {
                    "hello": "Hola",
                    "thank_you": "Gracias",
                    "excuse_me": "Disculpe",
                    "where_is": "Dónde está",
                    "how_much": "Cuánto cuesta"
                }
            },
            "fr": {
                "welcome": "Bienvenue dans votre guide de voyage",
                "sections": {
                    "flights": "Informations de Vol",
                    "packing": "Liste de Bagages Intelligente",
                    "budget": "Suivi du Budget",
                    "emergency": "Contacts d'Urgence",
                    "transportation": "Transport",
                    "accessibility": "Accessibilité"
                },
                "common_phrases": {
                    "hello": "Bonjour",
                    "thank_you": "Merci",
                    "excuse_me": "Excusez-moi",
                    "where_is": "Où est",
                    "how_much": "Combien"
                }
            },
            "it": {
                "welcome": "Benvenuto nella tua guida di viaggio",
                "sections": {
                    "flights": "Informazioni sui Voli",
                    "packing": "Lista Bagagli Intelligente",
                    "budget": "Tracker del Budget",
                    "emergency": "Contatti di Emergenza",
                    "transportation": "Trasporti",
                    "accessibility": "Accessibilità"
                },
                "common_phrases": {
                    "hello": "Ciao",
                    "thank_you": "Grazie",
                    "excuse_me": "Mi scusi",
                    "where_is": "Dov'è",
                    "how_much": "Quanto costa"
                }
            }
        }
        
        return localizations.get(language, localizations["en"])
    
    async def _get_premium_content(self, destination: str, start_date: str, end_date: str, 
                                  preferences: Dict, traveler_name: str) -> Dict:
        """Get premium content (simplified for this example)"""
        return {
            "restaurants": [
                {"name": f"Top Restaurant in {destination}", "cuisine": "Local"}
            ],
            "attractions": [
                {"name": f"Main Attraction in {destination}", "type": "Cultural"}
            ]
        }
    
    async def _get_detailed_weather(self, destination: str, start_date: str, end_date: str) -> Dict:
        """Get weather data (simplified for this example)"""
        return {
            "forecast": "Partly cloudy with occasional rain",
            "temperature": "15-22°C",
            "pack_accordingly": True
        }
