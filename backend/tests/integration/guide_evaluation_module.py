"""
AI-Powered Guide Evaluation Module
Automatically evaluates travel guide quality using LLM analysis
Provides detailed scoring for continuous improvement
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment
load_dotenv()


@dataclass
class GuideScore:
    """Individual scoring category"""
    category: str
    score: float  # 0-10
    max_score: float = 10.0
    feedback: str = ""
    specific_issues: List[str] = None
    strengths: List[str] = None
    
    def __post_init__(self):
        if self.specific_issues is None:
            self.specific_issues = []
        if self.strengths is None:
            self.strengths = []


@dataclass
class GuideEvaluation:
    """Complete guide evaluation results"""
    overall_score: float
    max_score: float = 100.0
    
    # Individual category scores
    personalization: GuideScore = None
    content_quality: GuideScore = None
    layout_structure: GuideScore = None
    weather_integration: GuideScore = None
    attractions_quality: GuideScore = None
    restaurants_quality: GuideScore = None
    practical_info: GuideScore = None
    daily_itinerary: GuideScore = None
    glossy_magazine_style: GuideScore = None
    completeness: GuideScore = None
    
    # Metadata
    evaluation_timestamp: str = ""
    evaluator_version: str = "1.0"
    guide_destination: str = ""
    guide_duration_days: int = 0
    
    def __post_init__(self):
        if self.evaluation_timestamp == "":
            self.evaluation_timestamp = datetime.now().isoformat()


class GuideEvaluator:
    """
    AI-powered guide evaluator that assesses travel guide quality
    Uses OpenAI GPT-4 to provide detailed analysis and scoring
    """
    
    def __init__(self):
        self.openai_client = None
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.openai_client = openai.AsyncOpenAI(api_key=api_key)
        else:
            raise ValueError("OpenAI API key required for guide evaluation")
    
    async def evaluate_guide(
        self,
        guide: Dict[str, Any],
        trip_document: Dict[str, Any],
        evaluation_criteria: Dict[str, Any] = None
    ) -> GuideEvaluation:
        """
        Comprehensive guide evaluation
        
        Args:
            guide: Generated travel guide
            trip_document: Original trip details/preferences
            evaluation_criteria: Custom evaluation criteria
            
        Returns:
            Complete evaluation with scores and feedback
        """
        print(f"🔍 Evaluating guide for {guide.get('destination', 'Unknown')}")
        
        # Default evaluation criteria
        if evaluation_criteria is None:
            evaluation_criteria = self._get_default_criteria()
        
        # Extract key information
        destination = guide.get('destination', 'Unknown')
        duration = guide.get('trip_duration_days', 0)
        
        # Evaluate each category
        evaluation_tasks = [
            self._evaluate_personalization(guide, trip_document),
            self._evaluate_content_quality(guide),
            self._evaluate_layout_structure(guide),
            self._evaluate_weather_integration(guide),
            self._evaluate_attractions_quality(guide),
            self._evaluate_restaurants_quality(guide),
            self._evaluate_practical_info(guide),
            self._evaluate_daily_itinerary(guide),
            self._evaluate_glossy_magazine_style(guide),
            self._evaluate_completeness(guide)
        ]
        
        # Run evaluations concurrently
        results = await asyncio.gather(*evaluation_tasks, return_exceptions=True)
        
        # Process results
        scores = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"⚠️  Evaluation task {i} failed: {result}")
                # Create default score for failed evaluation
                category_names = [
                    'personalization', 'content_quality', 'layout_structure',
                    'weather_integration', 'attractions_quality', 'restaurants_quality',
                    'practical_info', 'daily_itinerary', 'glossy_magazine_style', 'completeness'
                ]
                scores[category_names[i]] = GuideScore(
                    category=category_names[i],
                    score=0.0,
                    feedback="Evaluation failed due to technical error"
                )
            else:
                scores[result.category] = result
        
        # Calculate overall score
        total_score = sum(score.score for score in scores.values())
        
        # Create evaluation
        evaluation = GuideEvaluation(
            overall_score=total_score,
            personalization=scores.get('personalization'),
            content_quality=scores.get('content_quality'),
            layout_structure=scores.get('layout_structure'),
            weather_integration=scores.get('weather_integration'),
            attractions_quality=scores.get('attractions_quality'),
            restaurants_quality=scores.get('restaurants_quality'),
            practical_info=scores.get('practical_info'),
            daily_itinerary=scores.get('daily_itinerary'),
            glossy_magazine_style=scores.get('glossy_magazine_style'),
            completeness=scores.get('completeness'),
            guide_destination=destination,
            guide_duration_days=duration
        )
        
        return evaluation
    
    async def _evaluate_personalization(self, guide: Dict, trip_document: Dict) -> GuideScore:
        """Evaluate how well the guide is personalized to user preferences"""
        
        preferences = trip_document.get('preferences', {})
        interests = preferences.get('specialInterests', [])
        cuisine_types = preferences.get('cuisineTypes', [])
        price_range = preferences.get('priceRange', '')
        
        prompt = f"""
        Evaluate how well this travel guide is personalized to the user's specific preferences.
        
        USER PREFERENCES:
        - Special interests: {interests}
        - Cuisine preferences: {cuisine_types}
        - Price range: {price_range}
        - Travel style: {preferences.get('travelStyle', 'Not specified')}
        - Group type: {preferences.get('groupType', 'Not specified')}
        
        GUIDE CONTENT:
        - Restaurants: {len(guide.get('restaurants', []))} recommendations
        - Attractions: {len(guide.get('attractions', []))} recommendations
        - Summary: {guide.get('summary', '')[:200]}...
        
        EVALUATION CRITERIA:
        - Do restaurant recommendations match cuisine preferences?
        - Do attractions align with stated interests?
        - Is the price range respected in recommendations?
        - Does the writing style match the travel style?
        - Are recommendations appropriate for the group type?
        
        Provide a score from 0-10 and detailed feedback on personalization quality.
        """
        
        return await self._get_llm_evaluation(prompt, "personalization")
    
    async def _evaluate_content_quality(self, guide: Dict) -> GuideScore:
        """Evaluate overall content quality and writing"""
        
        prompt = f"""
        Evaluate the overall content quality of this travel guide.
        
        GUIDE CONTENT:
        - Summary: {guide.get('summary', '')}
        - Destination insights: {guide.get('destination_insights', '')}
        - Number of restaurants: {len(guide.get('restaurants', []))}
        - Number of attractions: {len(guide.get('attractions', []))}
        - Hidden gems: {len(guide.get('hidden_gems', []))}
        
        EVALUATION CRITERIA:
        - Writing quality and engagement
        - Accuracy and specificity of information
        - Depth of local insights
        - Variety and uniqueness of recommendations
        - Professional travel writing standards
        
        Score from 0-10 with detailed feedback on content quality.
        """
        
        return await self._get_llm_evaluation(prompt, "content_quality")
    
    async def _evaluate_layout_structure(self, guide: Dict) -> GuideScore:
        """Evaluate guide structure and organization"""
        
        sections = list(guide.keys())
        has_itinerary = bool(guide.get('daily_itinerary'))
        has_practical = bool(guide.get('practical_info'))
        
        prompt = f"""
        Evaluate the structure and organization of this travel guide.
        
        GUIDE STRUCTURE:
        - Available sections: {sections}
        - Has daily itinerary: {has_itinerary}
        - Has practical information: {has_practical}
        - Total sections: {len(sections)}
        
        EVALUATION CRITERIA:
        - Logical flow and organization
        - Completeness of essential sections
        - Easy navigation and readability
        - Professional guide structure
        - Information hierarchy
        
        Score from 0-10 with feedback on structure and layout.
        """
        
        return await self._get_llm_evaluation(prompt, "layout_structure")
    
    async def _evaluate_weather_integration(self, guide: Dict) -> GuideScore:
        """Evaluate weather information integration"""
        
        weather_data = guide.get('weather', [])
        weather_summary = guide.get('weather_summary', {})
        
        prompt = f"""
        Evaluate the weather integration in this travel guide.
        
        WEATHER INFORMATION:
        - Weather data available: {bool(weather_data)}
        - Number of weather days: {len(weather_data)}
        - Weather summary: {bool(weather_summary)}
        - Sample weather data: {weather_data[:2] if weather_data else 'None'}
        
        EVALUATION CRITERIA:
        - Presence of weather information
        - Accuracy and detail of forecasts
        - Integration with daily activities
        - Practical weather advice
        - Seasonal considerations
        
        Score from 0-10 with feedback on weather integration quality.
        """
        
        return await self._get_llm_evaluation(prompt, "weather_integration")
    
    async def _evaluate_attractions_quality(self, guide: Dict) -> GuideScore:
        """Evaluate attractions recommendations quality"""
        
        attractions = guide.get('attractions', [])
        
        prompt = f"""
        Evaluate the quality of attraction recommendations in this travel guide.
        
        ATTRACTIONS DATA:
        - Number of attractions: {len(attractions)}
        - Sample attractions: {attractions[:3] if attractions else 'None'}
        
        EVALUATION CRITERIA:
        - Variety and diversity of attractions
        - Mix of popular and hidden gems
        - Practical information (hours, prices, addresses)
        - Quality of descriptions
        - Relevance to destination
        
        Score from 0-10 with detailed feedback on attractions quality.
        """
        
        return await self._get_llm_evaluation(prompt, "attractions_quality")

    async def _evaluate_restaurants_quality(self, guide: Dict) -> GuideScore:
        """Evaluate restaurant recommendations quality"""

        restaurants = guide.get('restaurants', [])

        prompt = f"""
        Evaluate the quality of restaurant recommendations in this travel guide.

        RESTAURANTS DATA:
        - Number of restaurants: {len(restaurants)}
        - Sample restaurants: {restaurants[:3] if restaurants else 'None'}

        EVALUATION CRITERIA:
        - Variety of cuisine types and price ranges
        - Mix of local favorites and popular spots
        - Practical information (addresses, reservation info)
        - Quality of descriptions and recommendations
        - Authenticity and local insight

        Score from 0-10 with detailed feedback on restaurant quality.
        """

        return await self._get_llm_evaluation(prompt, "restaurants_quality")

    async def _evaluate_practical_info(self, guide: Dict) -> GuideScore:
        """Evaluate practical information completeness and quality"""

        practical_info = guide.get('practical_info', {})

        prompt = f"""
        Evaluate the practical information in this travel guide.

        PRACTICAL INFORMATION:
        - Available categories: {list(practical_info.keys()) if practical_info else 'None'}
        - Transportation info: {bool(practical_info.get('transportation'))}
        - Currency info: {bool(practical_info.get('currency'))}
        - Safety info: {bool(practical_info.get('safety'))}
        - Sample content: {str(practical_info)[:300] if practical_info else 'None'}

        EVALUATION CRITERIA:
        - Completeness of essential practical information
        - Accuracy and usefulness of advice
        - Coverage of transportation, currency, safety, tipping
        - Local customs and etiquette
        - Emergency information

        Score from 0-10 with feedback on practical information quality.
        """

        return await self._get_llm_evaluation(prompt, "practical_info")

    async def _evaluate_daily_itinerary(self, guide: Dict) -> GuideScore:
        """Evaluate daily itinerary quality and detail"""

        itinerary = guide.get('daily_itinerary', [])

        prompt = f"""
        Evaluate the daily itinerary in this travel guide.

        ITINERARY DATA:
        - Number of days: {len(itinerary)}
        - Sample day: {itinerary[0] if itinerary else 'None'}

        EVALUATION CRITERIA:
        - Detailed daily activities and timing
        - Logical flow and geographic efficiency
        - Balance of activities (culture, food, relaxation)
        - Practical considerations (travel time, opening hours)
        - Flexibility and alternatives

        Score from 0-10 with feedback on itinerary quality.
        """

        return await self._get_llm_evaluation(prompt, "daily_itinerary")

    async def _evaluate_glossy_magazine_style(self, guide: Dict) -> GuideScore:
        """Evaluate if guide has glossy magazine style and presentation"""

        summary = guide.get('summary', '')
        insights = guide.get('destination_insights', '')

        prompt = f"""
        Evaluate if this travel guide has the style and quality of a glossy travel magazine.

        CONTENT SAMPLES:
        - Summary: {summary}
        - Destination insights: {insights[:300]}...
        - Hidden gems: {len(guide.get('hidden_gems', []))} items
        - Neighborhoods: {len(guide.get('neighborhoods', []))} areas

        GLOSSY MAGAZINE CRITERIA:
        - Engaging, sophisticated writing style
        - Rich descriptive language and storytelling
        - Insider knowledge and exclusive recommendations
        - Professional travel journalism quality
        - Aspirational and inspiring tone
        - Visual appeal through descriptions

        Score from 0-10 on glossy magazine style quality.
        """

        return await self._get_llm_evaluation(prompt, "glossy_magazine_style")

    async def _evaluate_completeness(self, guide: Dict) -> GuideScore:
        """Evaluate overall guide completeness"""

        required_fields = ['summary', 'destination_insights', 'daily_itinerary',
                          'restaurants', 'attractions', 'practical_info']
        present_fields = [field for field in required_fields if guide.get(field)]

        prompt = f"""
        Evaluate the completeness of this travel guide.

        COMPLETENESS CHECK:
        - Required fields present: {len(present_fields)}/{len(required_fields)}
        - Missing fields: {set(required_fields) - set(present_fields)}
        - Additional features: weather={bool(guide.get('weather'))}, events={bool(guide.get('events'))}, hidden_gems={bool(guide.get('hidden_gems'))}

        EVALUATION CRITERIA:
        - All essential sections present
        - Sufficient detail in each section
        - No major gaps in information
        - Value-added features included
        - Ready for traveler use

        Score from 0-10 on guide completeness.
        """

        return await self._get_llm_evaluation(prompt, "completeness")

    async def _get_llm_evaluation(self, prompt: str, category: str) -> GuideScore:
        """Get LLM evaluation for a specific category"""

        system_prompt = """You are a professional travel guide evaluator with 20+ years of experience in travel journalism and guidebook publishing.

        Evaluate the travel guide content based on the criteria provided. Respond with a JSON object containing:
        {
            "score": <float 0-10>,
            "feedback": "<detailed feedback paragraph>",
            "specific_issues": ["<issue 1>", "<issue 2>", ...],
            "strengths": ["<strength 1>", "<strength 2>", ...]
        }

        Be thorough, constructive, and specific in your evaluation. Consider both professional standards and traveler needs."""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            content = response.choices[0].message.content

            # Parse JSON response
            try:
                result = json.loads(content)
                return GuideScore(
                    category=category,
                    score=float(result.get('score', 0)),
                    feedback=result.get('feedback', ''),
                    specific_issues=result.get('specific_issues', []),
                    strengths=result.get('strengths', [])
                )
            except json.JSONDecodeError:
                # Fallback parsing if JSON fails
                return GuideScore(
                    category=category,
                    score=5.0,  # Default middle score
                    feedback=f"LLM evaluation completed but JSON parsing failed. Raw response: {content[:200]}...",
                    specific_issues=["JSON parsing error"],
                    strengths=[]
                )

        except Exception as e:
            return GuideScore(
                category=category,
                score=0.0,
                feedback=f"Evaluation failed due to error: {str(e)}",
                specific_issues=[f"Technical error: {str(e)}"],
                strengths=[]
            )

    def _get_default_criteria(self) -> Dict[str, Any]:
        """Get default evaluation criteria"""
        return {
            "personalization_weight": 1.0,
            "content_quality_weight": 1.0,
            "layout_structure_weight": 1.0,
            "weather_integration_weight": 1.0,
            "attractions_quality_weight": 1.0,
            "restaurants_quality_weight": 1.0,
            "practical_info_weight": 1.0,
            "daily_itinerary_weight": 1.0,
            "glossy_magazine_style_weight": 1.0,
            "completeness_weight": 1.0
        }

    def save_evaluation(self, evaluation: GuideEvaluation, output_path: str = None) -> str:
        """Save evaluation results to JSON file"""

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"guide_evaluation_{timestamp}.json"

        # Convert to dict for JSON serialization
        evaluation_dict = asdict(evaluation)

        with open(output_path, 'w') as f:
            json.dump(evaluation_dict, f, indent=2, default=str)

        return output_path

    def print_evaluation_summary(self, evaluation: GuideEvaluation):
        """Print a formatted evaluation summary"""

        print("\n" + "="*80)
        print(f"🏆 GUIDE EVALUATION SUMMARY")
        print("="*80)
        print(f"📍 Destination: {evaluation.guide_destination}")
        print(f"📅 Duration: {evaluation.guide_duration_days} days")
        print(f"🎯 Overall Score: {evaluation.overall_score:.1f}/100")
        print(f"📊 Grade: {self._get_letter_grade(evaluation.overall_score)}")

        print("\n📋 CATEGORY SCORES:")
        print("-" * 50)

        categories = [
            evaluation.personalization,
            evaluation.content_quality,
            evaluation.layout_structure,
            evaluation.weather_integration,
            evaluation.attractions_quality,
            evaluation.restaurants_quality,
            evaluation.practical_info,
            evaluation.daily_itinerary,
            evaluation.glossy_magazine_style,
            evaluation.completeness
        ]

        for category in categories:
            if category:
                print(f"{category.category.replace('_', ' ').title():25} {category.score:4.1f}/10")

        print("\n🎯 TOP STRENGTHS:")
        all_strengths = []
        for category in categories:
            if category and category.strengths:
                all_strengths.extend(category.strengths)

        for i, strength in enumerate(all_strengths[:5], 1):
            print(f"  {i}. {strength}")

        print("\n⚠️  AREAS FOR IMPROVEMENT:")
        all_issues = []
        for category in categories:
            if category and category.specific_issues:
                all_issues.extend(category.specific_issues)

        for i, issue in enumerate(all_issues[:5], 1):
            print(f"  {i}. {issue}")

        print("\n" + "="*80)

    def _get_letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 80:
            return "A (Very Good)"
        elif score >= 70:
            return "B (Good)"
        elif score >= 60:
            return "C (Fair)"
        elif score >= 50:
            return "D (Poor)"
        else:
            return "F (Failing)"
