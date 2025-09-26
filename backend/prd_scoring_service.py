#!/usr/bin/env python3
"""
PRD Scoring Service - Evaluates generated guides against PRD requirements
"""
import json
from typing import Dict, Any, List, Tuple
import openai
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
root_dir = Path(__file__).parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

class PRDScoringService:
    """Service to score generated guides against PRD requirements"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def score_guide(self, guide: Dict[str, Any]) -> Tuple[int, Dict[str, Any], List[str]]:
        """
        Score a guide against PRD requirements
        
        Returns:
            - Overall score (0-100)
            - Category scores
            - List of improvement suggestions
        """
        
        # PRD Requirements from the original spec
        prd_requirements = {
            "core_features": {
                "personalization": "Guide should be personalized based on extracted travel data",
                "comprehensive_info": "Must include weather, restaurants, attractions, events",
                "practical_details": "Transportation, money, cultural tips, packing suggestions",
                "daily_itinerary": "Day-by-day schedule with activities and recommendations",
                "real_time_data": "Current weather and event information (if available)"
            },
            "content_richness": {
                "restaurants": "At least 5-10 restaurant recommendations with details",
                "attractions": "Major attractions with descriptions and visit info",
                "events": "Current events during travel dates",
                "neighborhoods": "Area descriptions and highlights",
                "hidden_gems": "Unique local recommendations"
            },
            "usability": {
                "organization": "Well-structured and easy to navigate",
                "completeness": "All essential travel information included",
                "accuracy": "Information matches extracted trip data",
                "actionability": "Practical, actionable recommendations"
            }
        }
        
        # Automated scoring
        scores = {}
        total_score = 0
        max_score = 0
        suggestions = []
        
        # Check core features
        if guide.get("summary"):
            scores["summary"] = 10
        else:
            scores["summary"] = 0
            suggestions.append("Add a comprehensive summary")
        
        # Check daily itinerary
        itinerary = guide.get("daily_itinerary") or guide.get("itinerary", [])
        if itinerary and len(itinerary) > 0:
            scores["itinerary"] = 20
            if len(itinerary) < 3:
                scores["itinerary"] = 10
                suggestions.append("Expand itinerary to cover all trip days")
        else:
            scores["itinerary"] = 0
            suggestions.append("Add daily itinerary with activities")
        
        # Check restaurants
        restaurants = guide.get("restaurants", [])
        if len(restaurants) >= 5:
            scores["restaurants"] = 15
        elif len(restaurants) >= 3:
            scores["restaurants"] = 10
            suggestions.append("Add more restaurant recommendations (aim for 5-10)")
        else:
            scores["restaurants"] = 5
            suggestions.append("Include at least 5 restaurant recommendations")
        
        # Check attractions
        attractions = guide.get("attractions", [])
        if len(attractions) >= 5:
            scores["attractions"] = 15
        elif len(attractions) >= 3:
            scores["attractions"] = 10
            suggestions.append("Add more attraction recommendations")
        else:
            scores["attractions"] = 5
            suggestions.append("Include major tourist attractions")
        
        # Check weather (if not fallback mode)
        if not guide.get("fallback_mode"):
            weather = guide.get("weather", [])
            if weather and len(weather) > 0:
                scores["weather"] = 10
            else:
                scores["weather"] = 0
                suggestions.append("Include weather forecast information")
        else:
            scores["weather"] = 5  # Partial credit for fallback mode
        
        # Check practical info
        practical = guide.get("practical_info", {})
        if practical:
            info_count = sum(1 for v in practical.values() if v and len(v) > 0)
            scores["practical_info"] = min(info_count * 2, 10)
            if info_count < 4:
                suggestions.append("Add more practical travel information")
        else:
            scores["practical_info"] = 0
            suggestions.append("Include practical travel tips")
        
        # Check events (if not fallback mode)
        if not guide.get("fallback_mode"):
            events = guide.get("events", [])
            if events and len(events) > 0:
                scores["events"] = 10
            else:
                scores["events"] = 0
                suggestions.append("Add current events and activities")
        else:
            scores["events"] = 5  # Partial credit
        
        # Check flight and hotel info
        if guide.get("flight_info") or guide.get("flights"):
            scores["flight_info"] = 5
        else:
            suggestions.append("Include flight information from booking")
        
        if guide.get("hotel_info") or guide.get("hotels"):
            scores["hotel_info"] = 5
        else:
            suggestions.append("Include hotel details from booking")
        
        # Calculate total score
        total_score = sum(scores.values())
        
        # Bonus points for additional features
        if guide.get("hidden_gems"):
            total_score += 5
        if guide.get("neighborhoods"):
            total_score += 5
        
        # Cap at 100
        total_score = min(total_score, 100)
        
        # Category breakdown
        category_scores = {
            "personalization": scores.get("summary", 0) + scores.get("itinerary", 0),
            "content_richness": scores.get("restaurants", 0) + scores.get("attractions", 0) + scores.get("events", 0),
            "practical_value": scores.get("practical_info", 0) + scores.get("weather", 0),
            "completeness": scores.get("flight_info", 0) + scores.get("hotel_info", 0)
        }
        
        return total_score, category_scores, suggestions
    
    async def get_llm_feedback(self, guide: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed feedback from LLM about guide quality"""
        
        if not self.openai_api_key:
            return {
                "error": "OpenAI API key not configured",
                "feedback": "Cannot provide LLM feedback without API key"
            }
        
        # Prepare guide summary for LLM
        guide_summary = {
            "has_summary": bool(guide.get("summary")),
            "itinerary_days": len(guide.get("daily_itinerary", [])),
            "restaurants_count": len(guide.get("restaurants", [])),
            "attractions_count": len(guide.get("attractions", [])),
            "has_weather": bool(guide.get("weather")),
            "has_practical_info": bool(guide.get("practical_info")),
            "has_events": bool(guide.get("events")),
            "is_fallback": guide.get("fallback_mode", False)
        }
        
        prompt = f"""
        Evaluate this travel guide against PRD requirements for a personalized travel assistant.
        
        PRD Requirements:
        1. Rich, personalized travel guide with weather, maps, and recommendations
        2. Comprehensive information including restaurants, attractions, events
        3. Daily itinerary with specific activities
        4. Practical travel information (transportation, money, cultural tips)
        5. Real-time data integration when available
        
        Guide Summary:
        {json.dumps(guide_summary, indent=2)}
        
        Sample Content:
        - Summary: {guide.get('summary', 'Not provided')[:200]}
        - Restaurant example: {json.dumps(guide.get('restaurants', [{}])[0] if guide.get('restaurants') else 'None')}
        - Attraction example: {json.dumps(guide.get('attractions', [{}])[0] if guide.get('attractions') else 'None')}
        
        Provide:
        1. Overall quality score (0-100)
        2. Strengths (3-5 points)
        3. Weaknesses (3-5 points)
        4. Specific improvements needed
        5. Does it meet PRD requirements? (Yes/Partial/No)
        
        Format as JSON with keys: score, strengths, weaknesses, improvements, meets_prd
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=os.getenv("PRIMARY_MODEL", "xai/grok-4-fast-free"),
                messages=[
                    {"role": "system", "content": "You are a product quality evaluator for a travel guide application."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            feedback = json.loads(response.choices[0].message.content)
            return feedback
            
        except Exception as e:
            return {
                "error": str(e),
                "feedback": "Failed to get LLM feedback"
            }


def score_guide_file(guide_file_path: str) -> Dict[str, Any]:
    """Score a guide from a JSON file"""
    
    with open(guide_file_path, 'r') as f:
        guide = json.load(f)
    
    scorer = PRDScoringService()
    score, categories, suggestions = scorer.score_guide(guide)
    
    result = {
        "overall_score": score,
        "category_scores": categories,
        "suggestions": suggestions,
        "meets_requirements": score >= 70,
        "grade": "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"
    }
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # Find the most recent fallback guide
        import glob
        guide_files = glob.glob("fallback_guide_*.json")
        if guide_files:
            guide_file = sorted(guide_files)[-1]
            print(f"Scoring most recent guide: {guide_file}")
        else:
            print("Usage: python prd_scoring_service.py <guide_json_file>")
            sys.exit(1)
    else:
        guide_file = sys.argv[1]
    
    result = score_guide_file(guide_file)
    
    print("\n" + "=" * 60)
    print("📊 PRD COMPLIANCE SCORE")
    print("=" * 60)
    print(f"Overall Score: {result['overall_score']}/100 (Grade: {result['grade']})")
    print(f"Meets Requirements: {'✅ Yes' if result['meets_requirements'] else '❌ No'}")
    
    print("\n📈 Category Scores:")
    for category, score in result['category_scores'].items():
        print(f"  • {category.replace('_', ' ').title()}: {score}")
    
    if result['suggestions']:
        print("\n💡 Improvement Suggestions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    print("\n" + "=" * 60)
