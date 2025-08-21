"""
Consolidated Test Fixtures and Dummy Data
Combines all existing test data into a centralized location
"""

import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import json

class TestFixtures:
    """Centralized test fixtures and dummy data"""
    
    @staticmethod
    def get_sample_flight():
        """Sample flight data"""
        return {
            "flight_number": "BA2303",
            "operator": "Qatar Airways",
            "booking_reference": "MYH9XH",
            "departure_location": "Heathrow",
            "departure_terminal": "4",
            "departure_date": "2024-12-20",
            "departure_time": "16:00",
            "arrival_location": "Doha",
            "arrival_terminal": None,
            "arrival_date": "2024-12-21",
            "arrival_time": "01:40",
            "travel_class": "Economy",
            "checked_baggage": "1 bag at 23kg (51lbs)",
            "hand_baggage": "1 handbag/laptop bag, plus 1 additional cabin bag"
        }
    
    @staticmethod
    def get_sample_hotel():
        """Sample hotel data"""
        return {
            "name": "Phuket Marriott Resort and Spa, Nai Yang Beach",
            "city": "Phuket",
            "check_in_date": "2024-12-21",
            "check_out_date": "2024-12-27",
            "room_type": "Premium Pool Access",
            "room_features": "WiFi, TV, Pool Access",
            "booking_reference": "TEST123"
        }
    
    @staticmethod
    def get_comprehensive_trip_data():
        """Comprehensive trip data for testing"""
        return {
            "destination": "Paris, France",
            "start_date": "2025-01-15",
            "end_date": "2025-01-18",
            "travelers": 2,
            "hotel_info": {
                "name": "Hotel Plaza Athénée",
                "address": "25 Avenue Montaigne, 75008 Paris",
                "latitude": 48.8656,
                "longitude": 2.3048,
                "rating": 4.8,
                "amenities": ["WiFi", "Spa", "Restaurant", "Concierge"],
                "check_in": "2025-01-15",
                "check_out": "2025-01-18"
            },
            "flights": [
                {
                    "flight_number": "AF123",
                    "airline": "Air France",
                    "departure": {"airport": "JFK", "date": "2025-01-15", "time": "20:00"},
                    "arrival": {"airport": "CDG", "date": "2025-01-16", "time": "09:30"},
                    "booking_reference": "AF123456"
                },
                {
                    "flight_number": "AF456",
                    "airline": "Air France",
                    "departure": {"airport": "CDG", "date": "2025-01-18", "time": "14:00"},
                    "arrival": {"airport": "JFK", "date": "2025-01-18", "time": "17:30"},
                    "booking_reference": "AF123456"
                }
            ],
            "preferences": {
                "interests": {
                    "museums": True,
                    "food": True,
                    "shopping": True,
                    "nightlife": False,
                    "outdoor": True,
                    "history": True,
                    "art": True
                },
                "budget": "luxury",
                "pace": "relaxed",
                "specialInterests": ["art", "history", "cuisine", "architecture"],
                "mobility": "full",
                "dietary": ["vegetarian"],
                "group_type": "couple",
                "accommodation_type": "hotel"
            },
            "extracted_data": {
                "flights": [
                    {
                        "flight_number": "AF123",
                        "departure": {"airport": "JFK", "date": "2025-01-15", "time": "20:00"},
                        "arrival": {"airport": "CDG", "date": "2025-01-16", "time": "09:30"}
                    }
                ],
                "travelers": [{"name": "John Doe", "type": "adult"}, {"name": "Jane Doe", "type": "adult"}],
                "confirmation_numbers": ["AF123456", "HTL123456"]
            }
        }
    
    @staticmethod
    def get_sample_itinerary():
        """Sample itinerary structure"""
        return {
            "trip_summary": {
                "destination": "Paris, France",
                "start_date": "2025-01-15",
                "end_date": "2025-01-18",
                "duration": "3 days",
                "travelers": 2
            },
            "flights": [
                {
                    "flight_number": "AF123",
                    "airline": "Air France",
                    "departure": {"airport": "JFK", "date": "2025-01-15", "time": "20:00"},
                    "arrival": {"airport": "CDG", "date": "2025-01-16", "time": "09:30"},
                    "seat": "12A",
                    "booking_reference": "AF123456"
                }
            ],
            "accommodations": [
                {
                    "name": "Hotel Plaza Athénée",
                    "address": "25 Avenue Montaigne, 75008 Paris",
                    "check_in": "2025-01-16",
                    "check_out": "2025-01-18",
                    "room_type": "Deluxe Room",
                    "booking_reference": "HTL123456"
                }
            ],
            "daily_schedule": [
                {
                    "date": "2025-01-16",
                    "activities": [
                        "Arrive at CDG Airport",
                        "Check into Hotel Plaza Athénée",
                        "Lunch at hotel restaurant",
                        "Visit Louvre Museum",
                        "Dinner at L'Ambroisie"
                    ]
                },
                {
                    "date": "2025-01-17",
                    "activities": [
                        "Breakfast at hotel",
                        "Visit Eiffel Tower",
                        "Lunch at Café de Flore",
                        "Shopping on Champs-Élysées",
                        "Seine River cruise"
                    ]
                }
            ]
        }
    
    @staticmethod
    def get_sample_recommendations():
        """Sample recommendations structure"""
        return {
            "restaurants": [
                {
                    "name": "L'Ambroisie",
                    "cuisine": "French Fine Dining",
                    "address": "9 Place des Vosges, 75004 Paris",
                    "rating": 4.9,
                    "price_range": "€€€€",
                    "specialties": ["Foie gras", "Lobster", "Soufflé"],
                    "vegetarian_options": True,
                    "distance_from_hotel": "1.2 km",
                    "reservation_required": True
                },
                {
                    "name": "Café de Flore",
                    "cuisine": "French Bistro",
                    "address": "172 Boulevard Saint-Germain, 75006 Paris",
                    "rating": 4.2,
                    "price_range": "€€",
                    "specialties": ["Coffee", "Croissants", "French Onion Soup"],
                    "vegetarian_options": True,
                    "distance_from_hotel": "0.8 km",
                    "reservation_required": False
                }
            ],
            "attractions": [
                {
                    "name": "Louvre Museum",
                    "type": "Museum",
                    "address": "Rue de Rivoli, 75001 Paris",
                    "rating": 4.7,
                    "hours": "9:00 AM - 6:00 PM",
                    "price": "€17",
                    "highlights": ["Mona Lisa", "Venus de Milo", "Egyptian Antiquities"],
                    "time_needed": "3-4 hours",
                    "distance_from_hotel": "1.5 km"
                },
                {
                    "name": "Eiffel Tower",
                    "type": "Landmark",
                    "address": "Champ de Mars, 75007 Paris",
                    "rating": 4.6,
                    "hours": "9:30 AM - 11:45 PM",
                    "price": "€29.40",
                    "highlights": ["City views", "Iron architecture", "Light show"],
                    "time_needed": "2-3 hours",
                    "distance_from_hotel": "2.1 km"
                }
            ],
            "events": [
                {
                    "name": "Winter Art Exhibition",
                    "venue": "Grand Palais",
                    "date": "2025-01-16",
                    "time": "10:00 AM - 8:00 PM",
                    "price": "€15",
                    "description": "Contemporary art exhibition featuring local and international artists"
                }
            ]
        }
    
    @staticmethod
    def get_sample_enhanced_guide():
        """Sample enhanced guide structure"""
        return {
            "summary": "Your personalized 3-day guide to Paris, France, tailored for art and cuisine enthusiasts",
            "destination_insights": "Paris in January offers fewer crowds and cozy indoor experiences perfect for museum visits and fine dining",
            "weather": {
                "daily_forecasts": [
                    {"date": "2025-01-16", "temp_high": 8, "temp_low": 3, "condition": "Clouds", "icon": "☁️", "precipitation": "10%"},
                    {"date": "2025-01-17", "temp_high": 10, "temp_low": 4, "condition": "Clear", "icon": "☀️", "precipitation": "0%"},
                    {"date": "2025-01-18", "temp_high": 7, "temp_low": 2, "condition": "Rain", "icon": "🌧️", "precipitation": "80%"}
                ],
                "summary": {
                    "avg_high": 8,
                    "avg_low": 3,
                    "predominant_condition": "Mixed",
                    "packing_suggestions": ["warm jacket", "umbrella", "comfortable walking shoes", "layers"]
                }
            },
            "daily_itinerary": [
                {
                    "date": "2025-01-16",
                    "theme": "Arrival and Art",
                    "activities": [
                        "9:30 AM - Arrive at CDG Airport",
                        "11:00 AM - Transfer to Hotel Plaza Athénée",
                        "12:30 PM - Check-in and lunch at hotel",
                        "2:30 PM - Visit Louvre Museum",
                        "6:00 PM - Return to hotel to rest",
                        "8:00 PM - Dinner at L'Ambroisie"
                    ],
                    "meals": {
                        "breakfast": "In-flight meal",
                        "lunch": "Hotel Plaza Athénée Restaurant",
                        "dinner": "L'Ambroisie (Michelin 3-star)"
                    },
                    "transportation": ["Airport shuttle", "Walking", "Metro Line 1"]
                }
            ],
            "restaurants": TestFixtures.get_sample_recommendations()["restaurants"],
            "attractions": TestFixtures.get_sample_recommendations()["attractions"],
            "events": TestFixtures.get_sample_recommendations()["events"],
            "neighborhoods": [
                {
                    "name": "Le Marais",
                    "description": "Historic district with Jewish quarter, trendy boutiques, and art galleries",
                    "highlights": ["Place des Vosges", "Jewish quarter", "Vintage shops"],
                    "best_for": ["Shopping", "History", "Food"]
                }
            ],
            "practical_info": {
                "transportation": [
                    "Metro day pass costs €7.50 and covers all zones",
                    "Taxis are readily available but expensive",
                    "Walking is pleasant in central Paris"
                ],
                "money": [
                    "Credit cards widely accepted",
                    "ATMs available throughout the city",
                    "Tipping 10% is standard in restaurants"
                ],
                "cultural": [
                    "Dress code for fine dining restaurants",
                    "Museums often closed on Mondays",
                    "French greeting customs important"
                ],
                "tips": [
                    "Book restaurant reservations well in advance",
                    "Avoid tourist traps near major landmarks",
                    "Learn basic French phrases"
                ]
            },
            "hidden_gems": [
                {
                    "name": "Musée Rodin Secret Garden",
                    "description": "Peaceful sculpture garden behind the famous museum",
                    "why_special": "Less crowded than main museum, beautiful sculptures in natural setting"
                }
            ],
            "citations": [
                "Perplexity AI search results for Paris restaurants January 2025",
                "OpenWeather API data for Paris weather forecast",
                "Google Maps API for location and distance data"
            ]
        }
    
    @staticmethod
    def get_mock_weather_data():
        """Mock weather data for testing"""
        return {
            "daily_forecasts": [
                {"date": "2025-01-15", "temp_high": 8, "temp_low": 3, "condition": "Clouds", "icon": "☁️"},
                {"date": "2025-01-16", "temp_high": 10, "temp_low": 4, "condition": "Clear", "icon": "☀️"},
                {"date": "2025-01-17", "temp_high": 7, "temp_low": 2, "condition": "Rain", "icon": "🌧️"}
            ],
            "summary": {
                "avg_high": 8,
                "avg_low": 3,
                "predominant_condition": "Mixed",
                "packing_suggestions": ["warm jacket", "umbrella", "comfortable shoes"]
            },
            "destination": "Paris, France"
        }
    
    @staticmethod
    def get_mock_maps_data():
        """Mock maps data for testing"""
        return {
            "travel_time": {
                "distance": "15 miles",
                "duration": "25 minutes",
                "duration_value": 1500
            },
            "place_details": {
                "name": "Test Location",
                "address": "123 Test Street, Test City",
                "rating": 4.2,
                "hours": "9:00 AM - 6:00 PM",
                "phone": "+1-555-0123"
            },
            "directions": {
                "routes": [
                    {
                        "legs": [
                            {
                                "distance": {"text": "15 miles", "value": 24140},
                                "duration": {"text": "25 minutes", "value": 1500}
                            }
                        ],
                        "overview_polyline": {"points": "mock_polyline_data"}
                    }
                ]
            }
        }
    
    @staticmethod
    def create_temp_pdf():
        """Create a temporary PDF file for testing"""
        import tempfile
        from reportlab.pdfgen import canvas
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            c = canvas.Canvas(tmp.name)
            c.drawString(100, 750, "Flight Confirmation")
            c.drawString(100, 730, "Flight: AA123")
            c.drawString(100, 710, "From: JFK to CDG")
            c.drawString(100, 690, "Date: December 15, 2024")
            c.drawString(100, 670, "Passenger: John Doe")
            c.save()
            return tmp.name
    
    @staticmethod
    def get_api_test_data():
        """Data for API endpoint testing"""
        return {
            "upload_data": {
                "trip_details": json.dumps({
                    "destination": "Test City",
                    "start_date": "2025-01-15",
                    "end_date": "2025-01-17",
                    "travelers": 1
                })
            },
            "preferences_data": {
                "interests": {"museums": True, "food": True},
                "budget": "medium",
                "pace": "moderate"
            }
        }
