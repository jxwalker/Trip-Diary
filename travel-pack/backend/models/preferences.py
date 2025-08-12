"""
Canonical Preferences Model
Standardizes preference data structure across frontend and backend
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from enum import Enum

class PriceRange(str, Enum):
    BUDGET = "$"
    MODERATE = "$$"
    UPSCALE = "$$$"
    LUXURY = "$$$$"

class CuisineType(str, Enum):
    LOCAL = "Local Cuisine"
    ITALIAN = "Italian"
    JAPANESE = "Japanese"
    CHINESE = "Chinese"
    INDIAN = "Indian"
    MEXICAN = "Mexican"
    FRENCH = "French"
    THAI = "Thai"
    MEDITERRANEAN = "Mediterranean"
    AMERICAN = "American"
    VEGETARIAN = "Vegetarian"
    VEGAN = "Vegan"
    SEAFOOD = "Seafood"
    STEAKHOUSE = "Steakhouse"
    FUSION = "Fusion"

class DietaryRestriction(str, Enum):
    VEGETARIAN = "Vegetarian"
    VEGAN = "Vegan"
    GLUTEN_FREE = "Gluten-free"
    DAIRY_FREE = "Dairy-free"
    NUT_ALLERGY = "Nut allergy"
    HALAL = "Halal"
    KOSHER = "Kosher"
    LOW_SODIUM = "Low sodium"
    DIABETIC = "Diabetic-friendly"

class TravelStyle(str, Enum):
    LUXURY = "luxury"
    BUDGET = "budget"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    CULTURAL = "cultural"
    FOODIE = "foodie"
    FAMILY = "family"
    ROMANTIC = "romantic"
    BUSINESS = "business"
    SOLO = "solo"

class MealPreferences(BaseModel):
    breakfast: bool = True
    lunch: bool = True
    dinner: bool = True
    street_food: bool = False
    fine_dining: bool = False
    cafes: bool = True
    bars: bool = False

class DiningPreferences(BaseModel):
    cuisine_types: List[str] = Field(default_factory=lambda: ["Local Cuisine"])
    dietary_restrictions: List[str] = Field(default_factory=list)
    price_ranges: List[str] = Field(default_factory=lambda: ["$$", "$$$"])
    meal_preferences: MealPreferences = Field(default_factory=MealPreferences)
    
    @validator('price_ranges')
    def validate_price_ranges(cls, v):
        valid_ranges = ["$", "$$", "$$$", "$$$$"]
        for price in v:
            if price not in valid_ranges:
                raise ValueError(f"Invalid price range: {price}")
        return v

class CultureInterests(BaseModel):
    art_galleries: bool = False
    museums: bool = False
    historical_sites: bool = False
    architecture: bool = False
    theaters: bool = False
    local_culture: bool = True

class EntertainmentInterests(BaseModel):
    live_music: bool = False
    nightclubs: bool = False
    bars_pubs: bool = False
    comedy_clubs: bool = False
    festivals: bool = False
    concerts: bool = False

class OutdoorInterests(BaseModel):
    hiking: bool = False
    beaches: bool = False
    parks: bool = False
    water_sports: bool = False
    cycling: bool = False
    wildlife: bool = False

class ShoppingInterests(BaseModel):
    local_markets: bool = True
    luxury_shopping: bool = False
    souvenirs: bool = True
    malls: bool = False
    boutiques: bool = False
    antiques: bool = False

class WellnessInterests(BaseModel):
    spa: bool = False
    yoga: bool = False
    fitness: bool = False
    meditation: bool = False
    hot_springs: bool = False
    massage: bool = False

class Interests(BaseModel):
    culture: CultureInterests = Field(default_factory=CultureInterests)
    entertainment: EntertainmentInterests = Field(default_factory=EntertainmentInterests)
    outdoor: OutdoorInterests = Field(default_factory=OutdoorInterests)
    shopping: ShoppingInterests = Field(default_factory=ShoppingInterests)
    wellness: WellnessInterests = Field(default_factory=WellnessInterests)

class TravelPreferences(BaseModel):
    pace: str = Field(default="moderate", pattern="^(relaxed|moderate|packed)$")
    group_size: str = Field(default="couple", pattern="^(solo|couple|family|group)$")
    accommodation_type: str = Field(default="hotel", pattern="^(hotel|airbnb|hostel|resort|boutique)$")
    transportation: str = Field(default="mixed", pattern="^(walking|public_transit|taxi|rental_car|mixed)$")

class AccessibilityNeeds(BaseModel):
    wheelchair_access: bool = False
    hearing_impaired: bool = False
    visual_impaired: bool = False
    mobility_assistance: bool = False
    dietary_medical: bool = False
    service_animal: bool = False

class CanonicalPreferences(BaseModel):
    """
    Canonical preferences model that standardizes all preference data
    """
    # Profile info
    profile_name: str = "My Travel Profile"
    
    # Core preferences
    dining: DiningPreferences = Field(default_factory=DiningPreferences)
    interests: Interests = Field(default_factory=Interests)
    travel: TravelPreferences = Field(default_factory=TravelPreferences)
    accessibility: AccessibilityNeeds = Field(default_factory=AccessibilityNeeds)
    
    # Trip-specific
    travel_style: Optional[str] = None
    budget_level: Optional[str] = Field(default="moderate", pattern="^(budget|moderate|luxury)$")
    special_occasions: List[str] = Field(default_factory=list)
    must_see: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "profile_name": "Europe Explorer",
                "dining": {
                    "cuisine_types": ["Local Cuisine", "Italian"],
                    "dietary_restrictions": ["Vegetarian"],
                    "price_ranges": ["$$", "$$$"],
                    "meal_preferences": {
                        "breakfast": True,
                        "lunch": True,
                        "dinner": True,
                        "street_food": True,
                        "fine_dining": False,
                        "cafes": True,
                        "bars": False
                    }
                },
                "interests": {
                    "culture": {
                        "museums": True,
                        "historical_sites": True,
                        "local_culture": True
                    }
                },
                "travel": {
                    "pace": "moderate",
                    "group_size": "couple",
                    "accommodation_type": "hotel",
                    "transportation": "public_transit"
                },
                "travel_style": "cultural",
                "budget_level": "moderate"
            }
        }

class PreferencesTransformer:
    """
    Transform various preference formats into canonical model
    """
    
    @staticmethod
    def from_frontend(data: dict) -> CanonicalPreferences:
        """
        Transform frontend format (camelCase) to canonical (snake_case)
        """
        transformed = {}
        
        # Handle profile name
        if 'profileName' in data:
            transformed['profile_name'] = data['profileName']
        
        # Transform dining preferences
        if 'dining' in data:
            dining = data['dining']
            transformed['dining'] = {
                'cuisine_types': dining.get('cuisineTypes', ["Local Cuisine"]),
                'dietary_restrictions': dining.get('dietaryRestrictions', []),
                'price_ranges': dining.get('priceRanges', ["$$", "$$$"]),
                'meal_preferences': {}
            }
            
            # Handle meal preferences
            if 'mealPreferences' in dining:
                meal_prefs = dining['mealPreferences']
                transformed['dining']['meal_preferences'] = {
                    'breakfast': meal_prefs.get('breakfast', True),
                    'lunch': meal_prefs.get('lunch', True),
                    'dinner': meal_prefs.get('dinner', True),
                    'street_food': meal_prefs.get('streetFood', False),
                    'fine_dining': meal_prefs.get('fineDining', False),
                    'cafes': meal_prefs.get('cafes', True),
                    'bars': meal_prefs.get('bars', False)
                }
        
        # Transform interests
        if 'interests' in data:
            interests = data['interests']
            transformed['interests'] = {}
            
            # Culture interests
            if 'culture' in interests:
                culture = interests['culture']
                transformed['interests']['culture'] = {
                    'art_galleries': culture.get('artGalleries', False),
                    'museums': culture.get('museums', False),
                    'historical_sites': culture.get('historicalSites', False),
                    'architecture': culture.get('architecture', False),
                    'theaters': culture.get('theaters', False),
                    'local_culture': culture.get('localCulture', True)
                }
            
            # Similar transformations for other interest categories...
            # (entertainment, outdoor, shopping, wellness)
            
        # Transform travel preferences
        if 'travel' in data:
            travel = data['travel']
            transformed['travel'] = {
                'pace': travel.get('pace', 'moderate'),
                'group_size': travel.get('groupSize', 'couple'),
                'accommodation_type': travel.get('accommodationType', 'hotel'),
                'transportation': travel.get('transportation', 'mixed')
            }
        
        # Transform accessibility
        if 'accessibility' in data:
            access = data['accessibility']
            transformed['accessibility'] = {
                'wheelchair_access': access.get('wheelchairAccess', False),
                'hearing_impaired': access.get('hearingImpaired', False),
                'visual_impaired': access.get('visualImpaired', False),
                'mobility_assistance': access.get('mobilityAssistance', False),
                'dietary_medical': access.get('dietaryMedical', False),
                'service_animal': access.get('serviceAnimal', False)
            }
        
        # Handle other fields
        if 'travelStyle' in data:
            transformed['travel_style'] = data['travelStyle']
        if 'budgetLevel' in data:
            transformed['budget_level'] = data['budgetLevel']
        if 'specialOccasions' in data:
            transformed['special_occasions'] = data['specialOccasions']
        if 'mustSee' in data:
            transformed['must_see'] = data['mustSee']
        if 'avoid' in data:
            transformed['avoid'] = data['avoid']
        if 'notes' in data:
            transformed['notes'] = data['notes']
            
        return CanonicalPreferences(**transformed)
    
    @staticmethod
    def to_frontend(preferences: CanonicalPreferences) -> dict:
        """
        Transform canonical format (snake_case) to frontend (camelCase)
        """
        data = preferences.dict()
        
        # Transform to camelCase
        frontend_data = {
            'profileName': data.get('profile_name', 'My Travel Profile'),
            'dining': {
                'cuisineTypes': data['dining']['cuisine_types'],
                'dietaryRestrictions': data['dining']['dietary_restrictions'],
                'priceRanges': data['dining']['price_ranges'],
                'mealPreferences': {
                    'breakfast': data['dining']['meal_preferences']['breakfast'],
                    'lunch': data['dining']['meal_preferences']['lunch'],
                    'dinner': data['dining']['meal_preferences']['dinner'],
                    'streetFood': data['dining']['meal_preferences']['street_food'],
                    'fineDining': data['dining']['meal_preferences']['fine_dining'],
                    'cafes': data['dining']['meal_preferences']['cafes'],
                    'bars': data['dining']['meal_preferences']['bars']
                }
            },
            'interests': {
                'culture': {
                    'artGalleries': data['interests']['culture']['art_galleries'],
                    'museums': data['interests']['culture']['museums'],
                    'historicalSites': data['interests']['culture']['historical_sites'],
                    'architecture': data['interests']['culture']['architecture'],
                    'theaters': data['interests']['culture']['theaters'],
                    'localCulture': data['interests']['culture']['local_culture']
                }
                # Add other interest categories similarly...
            },
            'travel': {
                'pace': data['travel']['pace'],
                'groupSize': data['travel']['group_size'],
                'accommodationType': data['travel']['accommodation_type'],
                'transportation': data['travel']['transportation']
            },
            'accessibility': {
                'wheelchairAccess': data['accessibility']['wheelchair_access'],
                'hearingImpaired': data['accessibility']['hearing_impaired'],
                'visualImpaired': data['accessibility']['visual_impaired'],
                'mobilityAssistance': data['accessibility']['mobility_assistance'],
                'dietaryMedical': data['accessibility']['dietary_medical'],
                'serviceAnimal': data['accessibility']['service_animal']
            },
            'travelStyle': data.get('travel_style'),
            'budgetLevel': data.get('budget_level', 'moderate'),
            'specialOccasions': data.get('special_occasions', []),
            'mustSee': data.get('must_see', []),
            'avoid': data.get('avoid', []),
            'notes': data.get('notes')
        }
        
        return frontend_data