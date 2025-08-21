#!/usr/bin/env python3
"""
Harsh PRD Scoring Service - Condé Nast Traveler Standards
Evaluates guides against luxury travel publication standards
"""
import json
from typing import Dict, Any, List, Tuple
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
root_dir = Path(__file__).parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class HarshPRDScorer:
    """Strict scoring against luxury travel guide standards"""
    
    def __init__(self):
        self.scoring_criteria = {
            "personalization": {
                "weight": 15,
                "requirements": [
                    "Traveler name used throughout",
                    "Preferences reflected in recommendations",
                    "Customized itinerary based on travel dates",
                    "Personal welcome message",
                    "Tailored tips and suggestions"
                ]
            },
            "content_quality": {
                "weight": 25,
                "requirements": [
                    "Michelin-starred restaurants with chef names",
                    "Detailed descriptions with insider information",
                    "Current exhibitions and events",
                    "Exclusive experiences and VIP access",
                    "Hidden gems and local secrets"
                ]
            },
            "weather_integration": {
                "weight": 10,
                "requirements": [
                    "Daily weather forecasts",
                    "Weather-appropriate activity suggestions",
                    "Sunrise/sunset times",
                    "UV index and precipitation chances",
                    "Seasonal packing recommendations"
                ]
            },
            "location_intelligence": {
                "weight": 10,
                "requirements": [
                    "Interactive maps or map links",
                    "Neighborhood descriptions",
                    "Walking distances between attractions",
                    "Transportation options with costs",
                    "GPS coordinates for key locations"
                ]
            },
            "culinary_excellence": {
                "weight": 15,
                "requirements": [
                    "10+ restaurant recommendations",
                    "Reservation requirements and dress codes",
                    "Signature dishes and wine pairings",
                    "Price ranges and tasting menus",
                    "Local food markets and specialties"
                ]
            },
            "cultural_depth": {
                "weight": 10,
                "requirements": [
                    "Museum and gallery recommendations",
                    "Current exhibitions with dates",
                    "Private tour options",
                    "Photography policies",
                    "Best times to avoid crowds"
                ]
            },
            "contemporary_relevance": {
                "weight": 10,
                "requirements": [
                    "Current events during travel dates",
                    "New restaurant/hotel openings",
                    "Seasonal highlights",
                    "Local news and happenings",
                    "Limited-time opportunities"
                ]
            },
            "luxury_amenities": {
                "weight": 5,
                "requirements": [
                    "Spa and wellness options",
                    "Shopping districts and boutiques",
                    "VIP services and experiences",
                    "Concierge-level recommendations",
                    "Premium transportation options"
                ]
            }
        }
    
    def score_guide_harshly(self, guide: Dict[str, Any]) -> Tuple[float, Dict[str, float], List[str], str]:
        """
        Score guide with strict Condé Nast Traveler standards
        
        Returns:
            - Overall score (0-100)
            - Category scores
            - Detailed critiques
            - Grade (A-F with + and -)
        """
        
        total_score = 0
        category_scores = {}
        critiques = []
        
        # Check guide type - luxury guides get bonus consideration
        is_luxury = guide.get("guide_type") == "luxury_conde_nast_style"
        
        # 1. Personalization (15 points)
        personalization_score = 0
        personalization = guide.get("personalization", {})
        welcome = guide.get("welcome_message", "")
        
        if personalization.get("traveler"):
            personalization_score += 3
        else:
            critiques.append("❌ No traveler personalization - guide feels generic")
        
        if welcome and len(welcome) > 100:
            personalization_score += 3
        else:
            critiques.append("❌ Lacks personal welcome message")
        
        if guide.get("daily_itinerary") and len(guide.get("daily_itinerary", [])) > 0:
            # Check if itinerary mentions traveler name
            itinerary_str = str(guide.get("daily_itinerary"))
            if personalization.get("traveler", "") in itinerary_str:
                personalization_score += 3
        
        if guide.get("concierge_notes"):
            personalization_score += 3
        else:
            critiques.append("❌ Missing concierge-level service notes")
        
        if personalization.get("preferences"):
            personalization_score += 3
        
        category_scores["personalization"] = min(personalization_score, 15)
        
        # 2. Content Quality (25 points)
        content_score = 0
        
        # Check for Michelin-starred restaurants
        culinary = guide.get("culinary_guide", {})
        michelin = culinary.get("michelin_starred", [])
        
        if len(michelin) >= 3:
            content_score += 5
        elif len(michelin) > 0:
            content_score += 2
            critiques.append(f"⚠️ Only {len(michelin)} Michelin restaurants - need at least 3")
        else:
            critiques.append("❌ No Michelin-starred restaurants listed")
        
        # Check for detailed descriptions
        if any(len(str(r)) > 200 for r in culinary.get("michelin_starred", [])):
            content_score += 5
        else:
            critiques.append("❌ Restaurant descriptions lack detail")
        
        # Check for exclusive experiences
        cultural = guide.get("cultural_experiences", {})
        if cultural.get("exclusive_tours"):
            content_score += 5
        else:
            critiques.append("❌ No exclusive or VIP experiences offered")
        
        # Check for hidden gems
        if culinary.get("hidden_gems") and len(culinary.get("hidden_gems", [])) >= 3:
            content_score += 5
        else:
            critiques.append("❌ Insufficient hidden gems and local secrets")
        
        # Check for insider tips
        if guide.get("insider_tips") and len(guide.get("insider_tips", [])) >= 5:
            content_score += 5
        else:
            critiques.append("⚠️ Limited insider tips provided")
        
        category_scores["content_quality"] = min(content_score, 25)
        
        # 3. Weather Integration (10 points)
        weather_score = 0
        weather = guide.get("weather_forecast", {})
        
        if weather and not weather.get("error"):
            daily_forecasts = weather.get("daily_forecasts", [])
            
            if len(daily_forecasts) >= 3:
                weather_score += 4
            else:
                critiques.append("⚠️ Weather coverage incomplete")
            
            # Check for detailed weather info
            if daily_forecasts and daily_forecasts[0].get("humidity"):
                weather_score += 2
            
            if weather.get("packing_essentials"):
                weather_score += 2
            
            # Check if weather is integrated into itinerary
            itinerary = guide.get("daily_itinerary", [])
            if any("weather" in str(day).lower() for day in itinerary):
                weather_score += 2
        else:
            critiques.append("❌ No weather integration - unacceptable for luxury guide")
        
        category_scores["weather_integration"] = min(weather_score, 10)
        
        # 4. Location Intelligence (10 points)
        location_score = 0
        destination_intel = guide.get("destination_intelligence", {})
        
        if destination_intel.get("map_url"):
            location_score += 2
        else:
            critiques.append("❌ No map integration")
        
        if destination_intel.get("neighborhoods") and len(destination_intel.get("neighborhoods", [])) >= 2:
            location_score += 3
        else:
            critiques.append("❌ Insufficient neighborhood exploration")
        
        if destination_intel.get("coordinates"):
            location_score += 2
        
        if destination_intel.get("getting_around"):
            location_score += 3
        else:
            critiques.append("❌ No transportation guidance")
        
        category_scores["location_intelligence"] = min(location_score, 10)
        
        # 5. Culinary Excellence (15 points)
        culinary_score = 0
        all_restaurants = (
            len(culinary.get("michelin_starred", [])) +
            len(culinary.get("hidden_gems", [])) +
            len(guide.get("restaurants", []))
        )
        
        if all_restaurants >= 10:
            culinary_score += 5
        elif all_restaurants >= 5:
            culinary_score += 3
            critiques.append(f"⚠️ Only {all_restaurants} restaurants - luxury guides need 10+")
        else:
            critiques.append(f"❌ Severely lacking restaurants ({all_restaurants} found)")
        
        # Check for reservation requirements
        if culinary.get("reservations_required"):
            culinary_score += 3
        else:
            critiques.append("❌ No reservation guidance provided")
        
        # Check for wine bars/coffee culture
        if culinary.get("wine_bars") or culinary.get("coffee_culture"):
            culinary_score += 3
        
        # Check for variety
        if all_restaurants > 0:
            culinary_score += 4
        
        category_scores["culinary_excellence"] = min(culinary_score, 15)
        
        # 6. Cultural Depth (10 points)
        cultural_score = 0
        
        museums = cultural.get("museums", [])
        galleries = cultural.get("galleries", [])
        
        if len(museums) + len(galleries) >= 5:
            cultural_score += 5
        elif len(museums) + len(galleries) > 0:
            cultural_score += 2
            critiques.append("⚠️ Limited cultural attractions covered")
        else:
            critiques.append("❌ No museums or galleries mentioned")
        
        if cultural.get("performances"):
            cultural_score += 3
        
        if cultural.get("exclusive_tours"):
            cultural_score += 2
        
        category_scores["cultural_depth"] = min(cultural_score, 10)
        
        # 7. Contemporary Relevance (10 points)
        contemporary_score = 0
        contemporary = guide.get("contemporary_happenings", {})
        
        if contemporary.get("events") and len(contemporary.get("events", [])) > 0:
            contemporary_score += 4
        else:
            critiques.append("❌ No current events during travel dates")
        
        if contemporary.get("exhibitions"):
            contemporary_score += 2
        
        if contemporary.get("news"):
            contemporary_score += 2
        
        if contemporary.get("festivals"):
            contemporary_score += 2
        
        category_scores["contemporary_relevance"] = min(contemporary_score, 10)
        
        # 8. Luxury Amenities (5 points)
        luxury_score = 0
        
        if guide.get("wellness_spa"):
            luxury_score += 2
        else:
            critiques.append("⚠️ No spa/wellness recommendations")
        
        if guide.get("luxury_shopping"):
            luxury_score += 2
        
        if guide.get("accommodation", {}).get("amenities"):
            luxury_score += 1
        
        category_scores["luxury_amenities"] = min(luxury_score, 5)
        
        # Calculate total score
        total_score = sum(category_scores.values())
        
        # Apply harsh penalties
        penalties = []
        
        # Penalty for fallback mode
        if guide.get("fallback_mode"):
            penalty = 15
            total_score -= penalty
            penalties.append(f"📉 -15 points: Operating in fallback mode without real-time data")
        
        # Penalty for missing flight/hotel details
        if not guide.get("flight_details") and not guide.get("accommodation"):
            penalty = 5
            total_score -= penalty
            penalties.append(f"📉 -5 points: Missing travel logistics integration")
        
        # Penalty for short itinerary
        itinerary = guide.get("daily_itinerary", [])
        if len(itinerary) < 3:
            penalty = 10
            total_score -= penalty
            penalties.append(f"📉 -10 points: Itinerary too brief ({len(itinerary)} days)")
        
        # Bonus for exceptional quality
        bonuses = []
        
        if is_luxury:
            bonus = 5
            total_score += bonus
            bonuses.append(f"📈 +5 points: Luxury guide format")
        
        quality_indicators = guide.get("quality_indicators", {})
        if quality_indicators.get("personalization_level") == "high":
            bonus = 3
            total_score += bonus
            bonuses.append(f"📈 +3 points: High personalization")
        
        # Cap at 100
        total_score = max(0, min(total_score, 100))
        
        # Determine grade with harsh standards
        if total_score >= 95:
            grade = "A+"
        elif total_score >= 90:
            grade = "A"
        elif total_score >= 87:
            grade = "A-"
        elif total_score >= 83:
            grade = "B+"
        elif total_score >= 80:
            grade = "B"
        elif total_score >= 77:
            grade = "B-"
        elif total_score >= 73:
            grade = "C+"
        elif total_score >= 70:
            grade = "C"
        elif total_score >= 67:
            grade = "C-"
        elif total_score >= 63:
            grade = "D+"
        elif total_score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        # Add final critiques
        if total_score < 70:
            critiques.append("🚫 FAILS to meet luxury travel guide standards")
        elif total_score < 80:
            critiques.append("⚠️ Meets minimum standards but lacks excellence")
        elif total_score < 90:
            critiques.append("✓ Good quality but room for improvement")
        else:
            critiques.append("✨ Excellent - approaching Condé Nast standards")
        
        # Add penalties and bonuses to critiques
        critiques.extend(penalties)
        critiques.extend(bonuses)
        
        return total_score, category_scores, critiques, grade


def evaluate_guide_harshly(guide_file_path: str) -> Dict[str, Any]:
    """Evaluate a guide file with harsh scoring"""
    
    with open(guide_file_path, 'r') as f:
        guide = json.load(f)
    
    scorer = HarshPRDScorer()
    score, categories, critiques, grade = scorer.score_guide_harshly(guide)
    
    print("\n" + "=" * 80)
    print("⚖️ HARSH PRD COMPLIANCE EVALUATION - CONDÉ NAST STANDARDS")
    print("=" * 80)
    
    print(f"\n📊 Overall Score: {score}/100 (Grade: {grade})")
    print(f"🎯 Verdict: {'✅ PASSES' if score >= 70 else '❌ FAILS'} luxury standards")
    
    print("\n📈 Category Breakdown:")
    for category, cat_score in categories.items():
        max_score = scorer.scoring_criteria[category]["weight"]
        percentage = (cat_score / max_score * 100) if max_score > 0 else 0
        bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
        print(f"  {category.replace('_', ' ').title():25} {bar} {cat_score}/{max_score} ({percentage:.0f}%)")
    
    print("\n🔍 Detailed Critique:")
    for i, critique in enumerate(critiques, 1):
        print(f"  {critique}")
    
    print("\n📝 Requirements for A+ Grade (95+ points):")
    print("  • Full weather integration with daily forecasts")
    print("  • 10+ restaurant recommendations with Michelin stars")
    print("  • Interactive maps and neighborhood guides")
    print("  • Contemporary events and happenings")
    print("  • Personalized throughout with traveler's name")
    print("  • Exclusive experiences and VIP access")
    print("  • Complete travel logistics integration")
    
    print("\n" + "=" * 80)
    
    return {
        "score": score,
        "grade": grade,
        "categories": categories,
        "critiques": critiques,
        "passes": score >= 70
    }


if __name__ == "__main__":
    import sys
    import glob
    
    if len(sys.argv) < 2:
        # Find the most recent guide
        guide_files = glob.glob("*guide*.json")
        if guide_files:
            guide_file = sorted(guide_files)[-1]
            print(f"Evaluating most recent guide: {guide_file}")
        else:
            print("Usage: python harsh_prd_scorer.py <guide_json_file>")
            sys.exit(1)
    else:
        guide_file = sys.argv[1]
    
    result = evaluate_guide_harshly(guide_file)