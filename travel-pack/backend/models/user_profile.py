"""
User Profile and Preferences Model
Centralized user profile management with saveable preferences
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class PriceRange(str, Enum):
    BUDGET = "$"
    MODERATE = "$$"
    UPSCALE = "$$$"
    LUXURY = "$$$$"

class TravelPace(str, Enum):
    RELAXED = "relaxed"
    BALANCED = "balanced"
    PACKED = "packed"

class GroupType(str, Enum):
    SOLO = "solo"
    COUPLE = "couple"
    FAMILY = "family"
    FRIENDS = "friends"
    BUSINESS = "business"

class ActivityLevel(int, Enum):
    MINIMAL = 1
    LIGHT = 2
    MODERATE = 3
    ACTIVE = 4
    VERY_ACTIVE = 5

class AdventureLevel(int, Enum):
    TOURIST = 1
    POPULAR = 2
    MIXED = 3
    ADVENTUROUS = 4
    EXPLORER = 5

class DiningPreferences(BaseModel):
    """Consolidated dining preferences"""
    cuisine_types: List[str] = Field(default_factory=lambda: ["Local Cuisine"])
    dietary_restrictions: List[str] = Field(default_factory=list)
    price_ranges: List[PriceRange] = Field(default_factory=lambda: [PriceRange.MODERATE])
    meal_preferences: Dict[str, bool] = Field(default_factory=lambda: {
        "breakfast": True,
        "brunch": False,
        "lunch": True,
        "dinner": True,
        "late_night": False,
        "street_food": False,
        "fine_dining": False,
        "casual_dining": True,
        "cafes": True,
        "bars": False
    })
    booking_preference: str = Field(default="flexible")  # "advance", "flexible", "walk-in"

class InterestPreferences(BaseModel):
    """Consolidated interests and activities"""
    categories: Dict[str, Dict[str, bool]] = Field(default_factory=lambda: {
        "culture": {
            "art_galleries": False,
            "museums": False,
            "historical_sites": False,
            "architecture": False,
            "theaters": False,
            "local_culture": True
        },
        "entertainment": {
            "live_music": False,
            "concerts": False,
            "nightclubs": False,
            "bars_pubs": False,
            "comedy_clubs": False,
            "casinos": False
        },
        "outdoors": {
            "nature_parks": False,
            "beaches": False,
            "hiking": False,
            "water_sports": False,
            "adventure_sports": False,
            "cycling": False
        },
        "lifestyle": {
            "shopping": False,
            "local_markets": False,
            "spa_wellness": False,
            "photography": False,
            "cooking_classes": False,
            "wine_tasting": False
        },
        "family": {
            "kid_friendly": False,
            "playgrounds": False,
            "zoos_aquariums": False,
            "theme_parks": False,
            "educational": False
        }
    })
    
    def get_active_interests(self) -> List[str]:
        """Get list of all active interests"""
        active = []
        for category, interests in self.categories.items():
            for interest, enabled in interests.items():
                if enabled:
                    active.append(interest)
        return active

class TravelPreferences(BaseModel):
    """Core travel style preferences"""
    pace: TravelPace = Field(default=TravelPace.BALANCED)
    group_type: GroupType = Field(default=GroupType.COUPLE)
    activity_level: ActivityLevel = Field(default=ActivityLevel.MODERATE)
    adventure_level: AdventureLevel = Field(default=AdventureLevel.MIXED)
    
    preferred_times: Dict[str, bool] = Field(default_factory=lambda: {
        "early_morning": False,  # 5am-8am
        "morning": True,         # 8am-12pm
        "afternoon": True,       # 12pm-5pm
        "evening": True,         # 5pm-9pm
        "late_night": False      # 9pm+
    })
    
    accommodation_preferences: Dict[str, any] = Field(default_factory=lambda: {
        "hotel_class": "3-4 star",
        "location_preference": "central",  # "central", "quiet", "near_transit"
        "amenities": ["wifi", "breakfast"],
        "budget_per_night": 150
    })

class UserProfile(BaseModel):
    """Complete user profile with all preferences"""
    profile_id: str
    user_email: Optional[str] = None
    profile_name: str = Field(default="My Travel Profile")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Core preferences
    dining: DiningPreferences = Field(default_factory=DiningPreferences)
    interests: InterestPreferences = Field(default_factory=InterestPreferences)
    travel_style: TravelPreferences = Field(default_factory=TravelPreferences)
    
    # Saved destinations and notes
    favorite_destinations: List[str] = Field(default_factory=list)
    travel_notes: Dict[str, str] = Field(default_factory=dict)
    
    # Quick preference templates
    quick_templates: Dict[str, str] = Field(default_factory=lambda: {
        "foodie": "Focus on local cuisine and unique dining",
        "culture": "Museums, history, and local culture",
        "adventure": "Outdoor activities and exploration",
        "relaxation": "Spa, beaches, and leisure",
        "family": "Kid-friendly activities and attractions",
        "budget": "Cost-effective options and free activities",
        "luxury": "Premium experiences and fine dining",
        "photography": "Scenic spots and Instagram-worthy locations"
    })
    
    def apply_template(self, template_name: str):
        """Apply a quick preference template"""
        templates = {
            "foodie": {
                "dining.meal_preferences.fine_dining": True,
                "dining.meal_preferences.street_food": True,
                "dining.meal_preferences.cafes": True,
                "dining.price_ranges": [PriceRange.MODERATE, PriceRange.UPSCALE],
                "interests.categories.lifestyle.cooking_classes": True,
                "interests.categories.lifestyle.wine_tasting": True,
                "interests.categories.lifestyle.local_markets": True
            },
            "culture": {
                "interests.categories.culture": {k: True for k in ["art_galleries", "museums", "historical_sites", "architecture", "local_culture"]},
                "travel_style.pace": TravelPace.BALANCED
            },
            "adventure": {
                "interests.categories.outdoors": {k: True for k in ["hiking", "adventure_sports", "nature_parks"]},
                "travel_style.activity_level": ActivityLevel.VERY_ACTIVE,
                "travel_style.adventure_level": AdventureLevel.EXPLORER
            },
            "relaxation": {
                "interests.categories.lifestyle.spa_wellness": True,
                "interests.categories.outdoors.beaches": True,
                "travel_style.pace": TravelPace.RELAXED,
                "travel_style.activity_level": ActivityLevel.LIGHT
            },
            "family": {
                "interests.categories.family": {k: True for k in self.interests.categories["family"].keys()},
                "travel_style.group_type": GroupType.FAMILY
            },
            "budget": {
                "dining.price_ranges": [PriceRange.BUDGET, PriceRange.MODERATE],
                "travel_style.accommodation_preferences.hotel_class": "2-3 star"
            },
            "luxury": {
                "dining.price_ranges": [PriceRange.UPSCALE, PriceRange.LUXURY],
                "dining.meal_preferences.fine_dining": True,
                "interests.categories.lifestyle.spa_wellness": True,
                "travel_style.accommodation_preferences.hotel_class": "5 star"
            }
        }
        
        if template_name in templates:
            # Apply template settings
            # This would need implementation based on your preference update logic
            pass
    
    def to_context(self) -> Dict:
        """Convert profile to context for prompt generation"""
        return {
            "cuisine_preferences": ", ".join(self.dining.cuisine_types),
            "dietary_restrictions": ", ".join(self.dining.dietary_restrictions) if self.dining.dietary_restrictions else "None",
            "price_ranges": ", ".join([p.value for p in self.dining.price_ranges]),
            "interests": ", ".join(self.interests.get_active_interests()),
            "travel_pace": self.travel_style.pace.value,
            "group_type": self.travel_style.group_type.value,
            "activity_level": self.travel_style.activity_level.value,
            "adventure_level": self.travel_style.adventure_level.value,
            "preferred_times": ", ".join([k for k, v in self.travel_style.preferred_times.items() if v])
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary of preferences"""
        active_interests = self.interests.get_active_interests()
        
        summary = f"""
Travel Profile: {self.profile_name}
Travel Style: {self.travel_style.group_type.value} traveler, {self.travel_style.pace.value} pace
Activity Level: {self.travel_style.activity_level.name}
Dining: {', '.join(self.dining.cuisine_types)} | {', '.join([p.value for p in self.dining.price_ranges])}
Interests: {', '.join(active_interests[:5]) if active_interests else 'General exploration'}
        """.strip()
        
        return summary

class ProfileManager:
    """Manage user profiles and saved preferences"""
    
    @staticmethod
    async def save_profile(profile: UserProfile, storage_path: str = "data/profiles") -> bool:
        """Save user profile to storage"""
        import json
        import os
        from pathlib import Path
        
        Path(storage_path).mkdir(parents=True, exist_ok=True)
        profile_file = os.path.join(storage_path, f"{profile.profile_id}.json")
        
        profile.updated_at = datetime.now()
        
        with open(profile_file, 'w') as f:
            json.dump(profile.dict(), f, indent=2, default=str)
        
        return True
    
    @staticmethod
    async def load_profile(profile_id: str, storage_path: str = "data/profiles") -> Optional[UserProfile]:
        """Load user profile from storage"""
        import json
        import os
        
        profile_file = os.path.join(storage_path, f"{profile_id}.json")
        
        if not os.path.exists(profile_file):
            return None
        
        with open(profile_file, 'r') as f:
            data = json.load(f)
        
        return UserProfile(**data)
    
    @staticmethod
    async def list_profiles(storage_path: str = "data/profiles") -> List[Dict]:
        """List all available profiles"""
        import os
        import json
        from pathlib import Path
        
        Path(storage_path).mkdir(parents=True, exist_ok=True)
        profiles = []
        
        for file in os.listdir(storage_path):
            if file.endswith('.json'):
                file_path = os.path.join(storage_path, file)
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    profiles.append({
                        "profile_id": data.get("profile_id"),
                        "profile_name": data.get("profile_name"),
                        "updated_at": data.get("updated_at")
                    })
        
        return profiles