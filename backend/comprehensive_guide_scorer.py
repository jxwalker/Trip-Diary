#!/usr/bin/env python3
"""
Comprehensive Guide Scoring System
Combines all evaluation mechanisms for complete guide assessment
"""
import json
import asyncio
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from datetime import datetime

from src.services.guide_validator import GuideValidator
from prd_scoring_service import PRDScoringService
from harsh_prd_scorer import HarshPRDScorer
from llm_reviewer import LLMReviewer
from tests.integration.guide_evaluation_module import GuideEvaluator

class ComprehensiveGuideScorer:
    """Unified scoring system combining all evaluation mechanisms"""
    
    def __init__(self):
        self.guide_validator = GuideValidator()
        self.prd_scorer = PRDScoringService()
        self.harsh_scorer = HarshPRDScorer()
        self.llm_reviewer = LLMReviewer()
        try:
            self.ai_evaluator = GuideEvaluator()
        except ValueError as e:
            print(f"⚠️ AI Evaluator not available: {e}")
            self.ai_evaluator = None
        
        self.scoring_weights = {
            "content_completeness": 25,  # Basic validation + content richness
            "prd_compliance": 20,        # PRD requirements adherence
            "luxury_standards": 15,      # Harsh luxury travel standards
            "user_experience": 15,       # LLM reviewer practical assessment
            "ai_quality_analysis": 25    # AI-powered detailed analysis
        }
    
    async def score_guide_comprehensively(
        self, 
        guide: Dict[str, Any], 
        trip_document: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive scoring using all evaluation mechanisms
        
        Returns complete scoring breakdown with improvement suggestions
        """
        print("🔍 Running Comprehensive Guide Evaluation...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "guide_destination": guide.get("destination", "Unknown"),
            "evaluation_summary": {},
            "detailed_scores": {},
            "improvement_plan": [],
            "iteration_recommendations": []
        }
        
        is_valid, errors, validation_details = self.guide_validator.validate_guide(guide)
        validation_score = 100 if is_valid else max(0, 100 - len(errors) * 10)
        
        results["detailed_scores"]["validation"] = {
            "score": validation_score,
            "is_valid": is_valid,
            "errors": errors,
            "details": validation_details
        }
        
        prd_score, prd_categories, prd_suggestions = self.prd_scorer.score_guide(guide)
        results["detailed_scores"]["prd_compliance"] = {
            "score": prd_score,
            "categories": prd_categories,
            "suggestions": prd_suggestions
        }
        
        harsh_score, harsh_categories, harsh_critiques, harsh_grade = self.harsh_scorer.score_guide_harshly(guide)
        results["detailed_scores"]["luxury_standards"] = {
            "score": harsh_score,
            "grade": harsh_grade,
            "categories": harsh_categories,
            "critiques": harsh_critiques
        }
        
        ux_score, ux_strengths, ux_improvements = self.llm_reviewer.review_guide(guide)
        results["detailed_scores"]["user_experience"] = {
            "score": ux_score,
            "strengths": ux_strengths,
            "improvements": ux_improvements
        }
        
        if self.ai_evaluator and trip_document:
            try:
                ai_evaluation = await self.ai_evaluator.evaluate_guide(guide, trip_document)
                results["detailed_scores"]["ai_analysis"] = {
                    "overall_score": ai_evaluation.overall_score,
                    "categories": {
                        "personalization": ai_evaluation.personalization.score if ai_evaluation.personalization else 0,
                        "content_quality": ai_evaluation.content_quality.score if ai_evaluation.content_quality else 0,
                        "layout_structure": ai_evaluation.layout_structure.score if ai_evaluation.layout_structure else 0,
                        "weather_integration": ai_evaluation.weather_integration.score if ai_evaluation.weather_integration else 0,
                        "attractions_quality": ai_evaluation.attractions_quality.score if ai_evaluation.attractions_quality else 0,
                        "restaurants_quality": ai_evaluation.restaurants_quality.score if ai_evaluation.restaurants_quality else 0,
                        "practical_info": ai_evaluation.practical_info.score if ai_evaluation.practical_info else 0,
                        "daily_itinerary": ai_evaluation.daily_itinerary.score if ai_evaluation.daily_itinerary else 0,
                        "glossy_magazine_style": ai_evaluation.glossy_magazine_style.score if ai_evaluation.glossy_magazine_style else 0,
                        "completeness": ai_evaluation.completeness.score if ai_evaluation.completeness else 0
                    }
                }
            except Exception as e:
                print(f"⚠️ AI evaluation failed: {e}")
                results["detailed_scores"]["ai_analysis"] = {"score": 0, "error": str(e)}
        else:
            results["detailed_scores"]["ai_analysis"] = {"score": 0, "error": "AI evaluator not available or no trip document"}
        
        ai_score = results["detailed_scores"]["ai_analysis"].get("overall_score", 0)
        weighted_scores = {
            "content_completeness": validation_score * self.scoring_weights["content_completeness"] / 100,
            "prd_compliance": prd_score * self.scoring_weights["prd_compliance"] / 100,
            "luxury_standards": harsh_score * self.scoring_weights["luxury_standards"] / 100,
            "user_experience": ux_score * self.scoring_weights["user_experience"] / 100,
            "ai_quality_analysis": ai_score * self.scoring_weights["ai_quality_analysis"] / 100
        }
        
        overall_score = sum(weighted_scores.values())
        
        results["evaluation_summary"] = {
            "overall_score": round(overall_score, 1),
            "weighted_scores": weighted_scores,
            "grade": self._get_letter_grade(overall_score),
            "passes_requirements": overall_score >= 70,
            "ready_for_production": overall_score >= 85
        }
        
        results["improvement_plan"] = self._generate_improvement_plan(results["detailed_scores"])
        results["iteration_recommendations"] = self._generate_iteration_recommendations(overall_score, results["detailed_scores"])
        
        return results
    
    def _get_letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 95: return "A+"
        elif score >= 90: return "A"
        elif score >= 87: return "A-"
        elif score >= 83: return "B+"
        elif score >= 80: return "B"
        elif score >= 77: return "B-"
        elif score >= 73: return "C+"
        elif score >= 70: return "C"
        elif score >= 60: return "D"
        else: return "F"
    
    def _generate_improvement_plan(self, detailed_scores: Dict) -> List[str]:
        """Generate prioritized improvement recommendations"""
        improvements = []
        
        if detailed_scores["validation"]["score"] < 100:
            improvements.extend([f"🔴 CRITICAL: {error}" for error in detailed_scores["validation"]["errors"]])
        
        if detailed_scores["prd_compliance"]["score"] < 70:
            improvements.extend([f"🟡 PRD: {suggestion}" for suggestion in detailed_scores["prd_compliance"]["suggestions"][:3]])
        
        if detailed_scores["luxury_standards"]["score"] < 70:
            luxury_critiques = [c for c in detailed_scores["luxury_standards"]["critiques"] if "❌" in c]
            improvements.extend([f"⭐ LUXURY: {critique}" for critique in luxury_critiques[:3]])
        
        ux_improvements = [imp for imp in detailed_scores["user_experience"]["improvements"] if "❌" in imp or "🚨" in imp]
        improvements.extend([f"👤 UX: {imp}" for imp in ux_improvements[:3]])
        
        return improvements[:10]  # Top 10 priorities
    
    def _generate_iteration_recommendations(self, overall_score: float, detailed_scores: Dict) -> List[str]:
        """Generate specific recommendations for next iteration"""
        recommendations = []
        
        if overall_score < 50:
            recommendations.append("Focus on basic content completeness - add missing restaurants, attractions, and itinerary details")
            recommendations.append("Ensure all API integrations are working and providing real data")
        elif overall_score < 70:
            recommendations.append("Improve content quality and depth - add more detailed descriptions and insider tips")
            recommendations.append("Enhance personalization based on user preferences")
        elif overall_score < 85:
            recommendations.append("Polish magazine-style presentation and visual appeal")
            recommendations.append("Add luxury amenities and exclusive experiences")
        else:
            recommendations.append("Fine-tune details and ensure perfect execution across all categories")
        
        return recommendations
    
    def print_scoring_summary(self, scoring_results: Dict[str, Any]):
        """Print a formatted summary of scoring results"""
        
        summary = scoring_results["evaluation_summary"]
        detailed = scoring_results["detailed_scores"]
        
        print(f"\n📊 SCORING SUMMARY")
        print(f"   Overall Score: {summary['overall_score']}/100 (Grade: {summary['grade']})")
        print(f"   Production Ready: {'✅ YES' if summary['ready_for_production'] else '❌ NO'}")
        
        print(f"\n📋 Category Breakdown:")
        print(f"   • Validation: {detailed['validation']['score']}/100")
        print(f"   • PRD Compliance: {detailed['prd_compliance']['score']}/100")
        print(f"   • Luxury Standards: {detailed['luxury_standards']['score']}/100")
        print(f"   • User Experience: {detailed['user_experience']['score']}/100")
        
        if 'ai_analysis' in detailed and 'overall_score' in detailed['ai_analysis']:
            print(f"   • AI Analysis: {detailed['ai_analysis']['overall_score']}/10")
        
        # Show top improvement priorities
        if scoring_results.get("improvement_plan"):
            print(f"\n🎯 Top Priorities:")
            for priority in scoring_results["improvement_plan"][:3]:
                print(f"   • {priority}")
        
        print()

    def print_scoring_summary(self, results: Dict[str, Any]):
        """Print formatted scoring summary"""
        print("\n" + "=" * 80)
        print("🏆 COMPREHENSIVE GUIDE SCORING SUMMARY")
        print("=" * 80)
        
        summary = results["evaluation_summary"]
        print(f"📍 Destination: {results['guide_destination']}")
        print(f"📊 Overall Score: {summary['overall_score']}/100 (Grade: {summary['grade']})")
        print(f"✅ Passes Requirements: {'YES' if summary['passes_requirements'] else 'NO'}")
        print(f"🚀 Production Ready: {'YES' if summary['ready_for_production'] else 'NO'}")
        
        print(f"\n📈 Weighted Category Scores:")
        for category, score in summary['weighted_scores'].items():
            print(f"  • {category.replace('_', ' ').title()}: {score:.1f}")
        
        print(f"\n🔍 Detailed Scores:")
        detailed = results["detailed_scores"]
        print(f"  • Validation: {detailed['validation']['score']}/100")
        print(f"  • PRD Compliance: {detailed['prd_compliance']['score']}/100")
        print(f"  • Luxury Standards: {detailed['luxury_standards']['score']}/100 (Grade: {detailed['luxury_standards']['grade']})")
        print(f"  • User Experience: {detailed['user_experience']['score']}/100")
        ai_score = detailed['ai_analysis'].get('overall_score', 0)
        print(f"  • AI Analysis: {ai_score}/100")
        
        if results["improvement_plan"]:
            print(f"\n💡 Top Improvement Priorities:")
            for i, improvement in enumerate(results["improvement_plan"][:5], 1):
                print(f"  {i}. {improvement}")
        
        print("\n" + "=" * 80)
