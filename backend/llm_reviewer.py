#!/usr/bin/env python
"""
LLM Reviewer - Provides harsh critique and actionable feedback on travel guides
"""
import json
import os
from typing import Dict, Any, List, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load environment
root_dir = Path(__file__).parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class LLMReviewer:
    """Harsh critic for travel guide quality"""
    
    def __init__(self):
        self.review_criteria = {
            "user_experience": {
                "weight": 20,
                "checks": [
                    "Is the guide immediately useful?",
                    "Can a traveler follow this without confusion?",
                    "Are recommendations specific with addresses?",
                    "Is timing realistic for activities?",
                    "Does it feel personalized or generic?"
                ]
            },
            "content_completeness": {
                "weight": 20,
                "checks": [
                    "Are there enough restaurants (10+)?",
                    "Are attractions well-described?",
                    "Is weather data actionable?",
                    "Are events current and real?",
                    "Is transportation clearly explained?"
                ]
            },
            "technical_quality": {
                "weight": 15,
                "checks": [
                    "No mock or placeholder data",
                    "All API integrations working",
                    "No timeout errors",
                    "Proper error handling",
                    "Fast response times"
                ]
            },
            "personalization": {
                "weight": 15,
                "checks": [
                    "Budget preferences respected",
                    "Dietary restrictions noted",
                    "Interests reflected in recommendations",
                    "Pace preferences considered",
                    "Language preferences applied"
                ]
            },
            "practical_value": {
                "weight": 15,
                "checks": [
                    "Budget estimates realistic",
                    "Emergency info complete",
                    "Packing list appropriate",
                    "Accessibility info provided",
                    "Booking/reservation guidance"
                ]
            },
            "innovation": {
                "weight": 15,
                "checks": [
                    "Flight tracking functional",
                    "Smart features add value",
                    "Multi-language works properly",
                    "Neighborhoods well-described",
                    "Photos enhance experience"
                ]
            }
        }
    
    def review_guide(self, guide: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """
        Provide harsh but constructive review
        Returns: (score, strengths, improvements_needed)
        """
        
        score = 0
        strengths = []
        improvements = []
        detailed_feedback = []
        
        # 1. User Experience Review
        ux_score = 0
        if guide.get("daily_itinerary") and len(guide["daily_itinerary"]) >= 7:
            ux_score += 5
            strengths.append("✅ Full week itinerary provided")
        else:
            improvements.append("❌ Itinerary incomplete or missing")
        
        if guide.get("culinary_guide", {}).get("michelin_starred"):
            restaurants = guide["culinary_guide"]["michelin_starred"]
            if len(restaurants) >= 10:
                ux_score += 5
                strengths.append("✅ Excellent restaurant selection")
            else:
                improvements.append(f"⚠️ Only {len(restaurants)} restaurants (need 10+)")
        else:
            improvements.append("❌ No restaurant recommendations")
        
        if guide.get("insider_tips") and len(guide["insider_tips"]) >= 5:
            ux_score += 5
            strengths.append("✅ Good insider tips")
        else:
            improvements.append("❌ Lacks insider knowledge")
        
        personalization = guide.get("personalization", {})
        if personalization.get("traveler") and personalization.get("preferences"):
            ux_score += 5
            strengths.append("✅ Personalized content")
        else:
            improvements.append("❌ Generic, not personalized")
        
        score += ux_score
        
        # 2. Content Completeness
        content_score = 0
        
        # Check weather - handle both list and dict formats
        weather = guide.get("weather_forecast", [])
        if isinstance(weather, list) and len(weather) > 0:
            content_score += 4
            strengths.append("✅ Weather data included")
        elif isinstance(weather, dict) and not weather.get("error"):
            content_score += 4
            strengths.append("✅ Weather data included")
        else:
            improvements.append("❌ Missing weather information")
        
        # Check events
        events = guide.get("contemporary_happenings", {}).get("events", [])
        if len(events) >= 5:
            content_score += 4
            strengths.append("✅ Current events included")
        else:
            improvements.append(f"⚠️ Only {len(events)} events (need 5+)")
        
        # Check transportation
        if guide.get("local_transportation"):
            content_score += 4
            strengths.append("✅ Transportation guide present")
        else:
            improvements.append("❌ No transportation information")
        
        # Check maps/neighborhoods
        neighborhoods = guide.get("destination_intelligence", {}).get("neighborhoods", [])
        if len(neighborhoods) >= 3:
            content_score += 4
            strengths.append("✅ Neighborhood information included")
        else:
            improvements.append("❌ Insufficient neighborhood data")
        
        # Check accessibility
        if guide.get("accessibility_information"):
            content_score += 4
            strengths.append("✅ Accessibility info provided")
        else:
            improvements.append("❌ No accessibility information")
        
        score += content_score
        
        # 3. Technical Quality
        tech_score = 0
        
        # Check for errors
        has_errors = False
        for key in ["weather_forecast", "culinary_guide", "contemporary_happenings"]:
            value = guide.get(key, {})
            if isinstance(value, dict) and value.get("error"):
                has_errors = True
                improvements.append(f"❌ Error in {key}")
        
        if not has_errors:
            tech_score += 7
            strengths.append("✅ No API errors")
        
        # Check for mock data
        guide_str = str(guide).lower()
        if "mock" not in guide_str and "placeholder" not in guide_str:
            tech_score += 8
            strengths.append("✅ No mock data detected")
        else:
            improvements.append("❌ Contains mock/placeholder data")
        
        score += tech_score
        
        # 4. Personalization Quality
        personal_score = 0
        
        if guide.get("smart_packing_list"):
            personal_score += 5
            strengths.append("✅ Smart packing list")
        else:
            improvements.append("❌ No packing recommendations")
        
        if guide.get("budget_tracking"):
            personal_score += 5
            strengths.append("✅ Budget tracking included")
        else:
            improvements.append("❌ No budget information")
        
        if guide.get("flight_tracking"):
            personal_score += 5
            strengths.append("✅ Flight tracking active")
        else:
            improvements.append("⚠️ Flight tracking not configured")
        
        score += personal_score
        
        # 5. Practical Value
        practical_score = 0
        
        if guide.get("emergency_contacts"):
            practical_score += 5
            strengths.append("✅ Emergency contacts provided")
        else:
            improvements.append("❌ Missing emergency information")
        
        reservations = guide.get("culinary_guide", {}).get("reservations_required", [])
        if reservations:
            practical_score += 5
            strengths.append("✅ Reservation guidance included")
        else:
            improvements.append("❌ No reservation information")
        
        if guide.get("quality_indicators", {}).get("has_photos"):
            practical_score += 5
            strengths.append("✅ Visual content included")
        else:
            improvements.append("⚠️ No photos or visual content")
        
        score += practical_score
        
        # 6. Innovation Score
        innovation_score = 0
        
        enhanced = guide.get("enhanced_features", {})
        if enhanced:
            feature_count = sum(1 for v in enhanced.values() if v)
            if feature_count >= 5:
                innovation_score += 10
                strengths.append(f"✅ {feature_count} enhanced features active")
            else:
                improvements.append(f"⚠️ Only {feature_count} enhanced features")
        
        if guide.get("localization"):
            innovation_score += 5
            strengths.append("✅ Multi-language support")
        else:
            improvements.append("⚠️ No localization features")
        
        score += innovation_score
        
        # Performance Issues
        performance_issues = []
        
        # Check guide size (performance concern)
        guide_size = len(json.dumps(guide))
        if guide_size > 100000:  # 100KB
            performance_issues.append(f"⚠️ Large response size: {guide_size/1000:.1f}KB")
        
        # Check for missing critical data
        critical_missing = []
        if not guide.get("daily_itinerary"):
            critical_missing.append("daily_itinerary")
        if not guide.get("culinary_guide"):
            critical_missing.append("restaurants")
        if not guide.get("weather_forecast"):
            critical_missing.append("weather")
        
        if critical_missing:
            improvements.append(f"🚨 CRITICAL: Missing {', '.join(critical_missing)}")
            score -= 10  # Penalty for missing critical features
        
        # Final Recommendations
        if score < 50:
            improvements.append("🔴 MAJOR REWORK NEEDED - Guide is not production ready")
        elif score < 70:
            improvements.append("🟡 IMPROVEMENTS NEEDED - Address critical issues first")
        elif score < 85:
            improvements.append("🟢 GOOD - Minor improvements will make it excellent")
        else:
            strengths.append("🌟 EXCELLENT - Ready for production use")
        
        # Specific actionable feedback
        if len(restaurants) < 10 if 'restaurants' in locals() else True:
            improvements.append("ACTION: Increase restaurant count to 10+ with variety")
        
        if not guide.get("destination_intelligence", {}).get("map_url"):
            improvements.append("ACTION: Add map integration for better navigation")
        
        if performance_issues:
            improvements.extend(performance_issues)
        
        return score, strengths, improvements

def review_guide_file(filepath: str):
    """Review a guide from file"""
    
    with open(filepath, 'r') as f:
        guide = json.load(f)
    
    reviewer = LLMReviewer()
    score, strengths, improvements = reviewer.review_guide(guide)
    
    print("\n" + "=" * 80)
    print("📝 LLM REVIEWER - HARSH CRITIQUE & FEEDBACK")
    print("=" * 80)
    
    print(f"\n📊 OVERALL SCORE: {score}/100")
    
    if score >= 85:
        print("🌟 VERDICT: EXCELLENT - Production Ready")
    elif score >= 70:
        print("✅ VERDICT: GOOD - Minor improvements needed")
    elif score >= 50:
        print("⚠️ VERDICT: ACCEPTABLE - Significant improvements needed")
    else:
        print("❌ VERDICT: POOR - Major rework required")
    
    print("\n💪 STRENGTHS:")
    for strength in strengths:
        print(f"   {strength}")
    
    print("\n🔧 IMPROVEMENTS NEEDED:")
    for improvement in improvements:
        print(f"   {improvement}")
    
    print("\n" + "=" * 80)
    
    return score, strengths, improvements

if __name__ == "__main__":
    import sys
    import glob
    
    # Find the most recent guide
    if len(sys.argv) > 1:
        guide_file = sys.argv[1]
    else:
        guide_files = glob.glob("*guide*.json")
        if guide_files:
            guide_file = sorted(guide_files)[-1]
            print(f"Reviewing: {guide_file}")
        else:
            print("No guide files found")
            sys.exit(1)
    
    score, strengths, improvements = review_guide_file(guide_file)
    
    # Exit with error if score is too low
    sys.exit(0 if score >= 70 else 1)
