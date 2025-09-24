"""
Guide Content Validator
Ensures travel guides always have minimum required content
Prevents blank guides from being returned to users
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class GuideValidator:
    """Validates travel guide completeness and quality"""
    
    REQUIRED_FIELDS = [
        'summary',
        'destination_insights', 
        'daily_itinerary',
        'restaurants',
        'attractions',
        'practical_info'
    ]
    
    MINIMUM_CONTENT_REQUIREMENTS = {
        'summary': 50,  # Minimum characters
        'destination_insights': 50,
        'daily_itinerary': 1,  # Minimum items
        'restaurants': 1,
        'attractions': 1,
        'practical_info': 1  # Should have at least one category
    }
    
    @classmethod
    def validate_guide(cls, guide: Dict) -> Tuple[bool, List[str], Dict]:
        """
        Validate a travel guide for completeness
        
        Returns:
            (is_valid, errors, validation_details)
        """
        errors = []
        details = {}
        
        # Check required fields exist
        for field in cls.REQUIRED_FIELDS:
            if field not in guide:
                errors.append(f"Missing required field: {field}")
                details[f"has_{field}"] = False
            else:
                details[f"has_{field}"] = True
        
        # Check content quality
        if guide.get('summary'):
            summary_length = len(guide['summary'].strip())
            details['summary_length'] = summary_length
            if summary_length < cls.MINIMUM_CONTENT_REQUIREMENTS['summary']:
                errors.append(f"Summary too short: {summary_length} chars (minimum {cls.MINIMUM_CONTENT_REQUIREMENTS['summary']})")
        else:
            details['summary_length'] = 0
            errors.append("Summary is empty or missing")
        
        if guide.get('destination_insights'):
            insights = guide['destination_insights']
            if isinstance(insights, dict):
                insights_text = ""
                for key, value in insights.items():
                    if isinstance(value, str):
                        insights_text += f"{value} "
                    elif isinstance(value, list):
                        insights_text += " ".join(str(item) for item in value) + " "
                insights_length = len(insights_text.strip())
            elif isinstance(insights, str):
                insights_length = len(insights.strip())
            else:
                insights_length = 0
            
            details['insights_length'] = insights_length
            if insights_length < cls.MINIMUM_CONTENT_REQUIREMENTS['destination_insights']:
                errors.append(f"Destination insights too short: {insights_length} chars")
        else:
            details['insights_length'] = 0
            errors.append("Destination insights are empty or missing")
        
        # Check daily itinerary
        itinerary = guide.get('daily_itinerary', [])
        details['itinerary_days'] = len(itinerary)
        if len(itinerary) < cls.MINIMUM_CONTENT_REQUIREMENTS['daily_itinerary']:
            errors.append("Daily itinerary is empty")
        else:
            # Check itinerary quality
            empty_days = 0
            for day in itinerary:
                activities = day.get('activities', [])
                if not activities or len(activities) == 0:
                    empty_days += 1
                else:
                    activity_lengths = []
                    for activity in activities:
                        if isinstance(activity, dict):
                            name = activity.get('name', '')
                            description = activity.get('description', '')
                            activity_text = f"{name} {description}".strip()
                            activity_lengths.append(len(activity_text))
                        elif isinstance(activity, str):
                            activity_lengths.append(len(activity.strip()))
                        else:
                            activity_lengths.append(0)
                    
                    if all(length < 10 for length in activity_lengths):
                        empty_days += 1  # Activities are too short/generic
            
            details['empty_itinerary_days'] = empty_days
            if empty_days > 0:
                errors.append(f"{empty_days} days have empty or inadequate activities")
        
        # Check restaurants
        restaurants = guide.get('restaurants', [])
        details['restaurants_count'] = len(restaurants)
        if len(restaurants) < cls.MINIMUM_CONTENT_REQUIREMENTS['restaurants']:
            errors.append("No restaurant recommendations")
        else:
            # Check restaurant quality
            incomplete_restaurants = 0
            for restaurant in restaurants:
                if not restaurant.get('name') or len(restaurant.get('name', '').strip()) < 3:
                    incomplete_restaurants += 1
            details['incomplete_restaurants'] = incomplete_restaurants
            if incomplete_restaurants > len(restaurants) // 2:  # More than half are incomplete
                errors.append("Too many incomplete restaurant entries")
        
        # Check attractions
        attractions = guide.get('attractions', [])
        details['attractions_count'] = len(attractions)
        if len(attractions) < cls.MINIMUM_CONTENT_REQUIREMENTS['attractions']:
            errors.append("No attraction recommendations")
        else:
            # Check attraction quality
            incomplete_attractions = 0
            for attraction in attractions:
                if not attraction.get('name') or len(attraction.get('name', '').strip()) < 3:
                    incomplete_attractions += 1
            details['incomplete_attractions'] = incomplete_attractions
            if incomplete_attractions > len(attractions) // 2:
                errors.append("Too many incomplete attraction entries")
        
        # Check practical info
        practical_info = guide.get('practical_info', {})
        if not practical_info or not isinstance(practical_info, dict):
            errors.append("Practical information is missing")
            details['practical_info_categories'] = 0
        else:
            categories = len([k for k, v in practical_info.items() if v])
            details['practical_info_categories'] = categories
            if categories < cls.MINIMUM_CONTENT_REQUIREMENTS['practical_info']:
                errors.append("Practical information is incomplete")
        
        # Check weather integration
        weather = guide.get('weather', [])
        details['has_weather'] = len(weather) > 0
        if weather:
            details['weather_days'] = len(weather)
        
        # Overall validation
        is_valid = len(errors) == 0
        details['is_valid'] = is_valid
        details['error_count'] = len(errors)
        
        return is_valid, errors, details
    
    @classmethod
    def enhance_incomplete_guide(cls, guide: Dict) -> Dict:
        """
        DO NOT ENHANCE - Return error instead of adding fallback content
        """
        # NO FALLBACK CONTENT - Return error guide
        return {
            "error": "Guide validation failed",
            "message": "Unable to generate complete guide due to API failures. Please check your API configuration.",
            "validation_failed": True,
            "original_guide": guide,
            "timestamp": "validation_error"
        }
    

    
    @classmethod
    def log_validation_results(cls, guide: Dict, is_valid: bool, errors: List[str], details: Dict):
        """Log validation results for monitoring"""
        if is_valid:
            logger.info(f"Guide validation passed: {details.get('restaurants_count', 0)} restaurants, "
                       f"{details.get('attractions_count', 0)} attractions, "
                       f"{details.get('itinerary_days', 0)} days")
        else:
            logger.warning(f"Guide validation failed with {len(errors)} errors: {', '.join(errors[:3])}")
            logger.debug(f"Full validation details: {details}")
