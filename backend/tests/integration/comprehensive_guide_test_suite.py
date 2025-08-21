#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for Travel Guide Generation
Tests guide creation, evaluation, and continuous improvement
"""
import asyncio
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tests.integration.guide_evaluation_module import GuideEvaluator, GuideEvaluation


class ComprehensiveGuideTestSuite:
    """
    Comprehensive test suite that:
    1. Tests guide generation with various scenarios
    2. Evaluates guide quality using AI
    3. Tracks performance metrics
    4. Provides improvement recommendations
    """
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.evaluator = GuideEvaluator()
        self.test_results = []
        self.performance_metrics = {
            "total_tests": 0,
            "successful_generations": 0,
            "average_generation_time": 0.0,
            "average_quality_score": 0.0,
            "quality_scores": []
        }
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        
        print("🚀 Starting Comprehensive Guide Test Suite")
        print("=" * 80)
        
        # Test scenarios
        test_scenarios = self._get_test_scenarios()
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 Test {i}/{len(test_scenarios)}: {scenario['name']}")
            print("-" * 60)
            
            try:
                # Generate guide
                guide_result = await self._test_guide_generation(scenario)
                
                if guide_result['success']:
                    # Evaluate guide quality
                    evaluation = await self._evaluate_guide_quality(
                        guide_result['guide'], 
                        scenario['trip_document']
                    )
                    
                    # Store results
                    test_result = {
                        "scenario": scenario['name'],
                        "generation_time": guide_result['generation_time'],
                        "guide_data": guide_result['guide'],
                        "evaluation": evaluation,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    self.test_results.append(test_result)
                    self._update_performance_metrics(test_result)
                    
                    # Print summary
                    self._print_test_summary(test_result)
                    
                else:
                    print(f"❌ Guide generation failed: {guide_result['error']}")
                    
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Generate final report
        final_report = await self._generate_final_report()
        
        return final_report
    
    async def _test_guide_generation(self, scenario: Dict) -> Dict[str, Any]:
        """Test guide generation for a specific scenario"""
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/generate-enhanced-guide",
                json=scenario['request_data'],
                timeout=90
            )
            
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                guide_data = response.json()
                guide = guide_data.get('guide', guide_data)
                
                return {
                    "success": True,
                    "guide": guide,
                    "generation_time": generation_time,
                    "response_status": response.status_code
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                    "generation_time": generation_time
                }
                
        except Exception as e:
            generation_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "generation_time": generation_time
            }
    
    async def _evaluate_guide_quality(self, guide: Dict, trip_document: Dict) -> GuideEvaluation:
        """Evaluate guide quality using AI evaluator"""
        
        print("🔍 Evaluating guide quality with AI...")
        
        evaluation = await self.evaluator.evaluate_guide(guide, trip_document)
        
        return evaluation
    
    def _get_test_scenarios(self) -> List[Dict[str, Any]]:
        """Get comprehensive test scenarios"""
        
        base_date = datetime.now() + timedelta(days=30)
        start_date = base_date.strftime("%Y-%m-%d")
        end_date = (base_date + timedelta(days=4)).strftime("%Y-%m-%d")
        
        scenarios = [
            {
                "name": "Luxury Couple - Paris",
                "request_data": {
                    "destination": "Paris, France",
                    "start_date": start_date,
                    "end_date": end_date,
                    "hotel_info": {
                        "name": "Hotel Plaza Athénée",
                        "address": "25 Avenue Montaigne, 75008 Paris, France"
                    },
                    "preferences": {
                        "travelStyle": "luxury",
                        "groupType": "couple",
                        "walkingTolerance": 3,
                        "adventureLevel": 2,
                        "nightlife": 4,
                        "priceRange": "$$$$",
                        "cuisineTypes": ["French", "Michelin", "Fine Dining"],
                        "specialInterests": ["museums", "art", "fashion", "wine", "architecture"],
                        "preferredTimes": {"morning": True, "afternoon": True, "evening": True}
                    },
                    "use_optimized_service": True
                },
                "trip_document": {
                    "destination": "Paris, France",
                    "preferences": {
                        "travelStyle": "luxury",
                        "groupType": "couple",
                        "specialInterests": ["museums", "art", "fashion", "wine", "architecture"],
                        "cuisineTypes": ["French", "Michelin", "Fine Dining"],
                        "priceRange": "$$$$"
                    }
                }
            },
            {
                "name": "Budget Backpacker - Tokyo",
                "request_data": {
                    "destination": "Tokyo, Japan",
                    "start_date": start_date,
                    "end_date": end_date,
                    "hotel_info": {
                        "name": "Shibuya Hostel",
                        "address": "Shibuya, Tokyo, Japan"
                    },
                    "preferences": {
                        "travelStyle": "budget",
                        "groupType": "solo",
                        "walkingTolerance": 5,
                        "adventureLevel": 4,
                        "nightlife": 3,
                        "priceRange": "$",
                        "cuisineTypes": ["Japanese", "Street Food", "Local"],
                        "specialInterests": ["culture", "temples", "anime", "technology", "food"],
                        "preferredTimes": {"morning": True, "afternoon": True, "evening": True}
                    },
                    "use_optimized_service": True
                },
                "trip_document": {
                    "destination": "Tokyo, Japan",
                    "preferences": {
                        "travelStyle": "budget",
                        "groupType": "solo",
                        "specialInterests": ["culture", "temples", "anime", "technology", "food"],
                        "cuisineTypes": ["Japanese", "Street Food", "Local"],
                        "priceRange": "$"
                    }
                }
            },
            {
                "name": "Family Adventure - Costa Rica",
                "request_data": {
                    "destination": "San José, Costa Rica",
                    "start_date": start_date,
                    "end_date": (base_date + timedelta(days=6)).strftime("%Y-%m-%d"),
                    "hotel_info": {
                        "name": "Family Resort Costa Rica",
                        "address": "San José, Costa Rica"
                    },
                    "preferences": {
                        "travelStyle": "adventure",
                        "groupType": "family",
                        "walkingTolerance": 3,
                        "adventureLevel": 4,
                        "nightlife": 1,
                        "priceRange": "$$",
                        "cuisineTypes": ["Local", "International", "Kid-friendly"],
                        "specialInterests": ["nature", "wildlife", "adventure", "beaches", "family"],
                        "preferredTimes": {"morning": True, "afternoon": True, "evening": False}
                    },
                    "use_optimized_service": True
                },
                "trip_document": {
                    "destination": "San José, Costa Rica",
                    "preferences": {
                        "travelStyle": "adventure",
                        "groupType": "family",
                        "specialInterests": ["nature", "wildlife", "adventure", "beaches", "family"],
                        "cuisineTypes": ["Local", "International", "Kid-friendly"],
                        "priceRange": "$$"
                    }
                }
            },
            {
                "name": "Business Traveler - New York",
                "request_data": {
                    "destination": "New York, NY",
                    "start_date": start_date,
                    "end_date": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                    "hotel_info": {
                        "name": "Manhattan Business Hotel",
                        "address": "Midtown Manhattan, New York, NY"
                    },
                    "preferences": {
                        "travelStyle": "business",
                        "groupType": "solo",
                        "walkingTolerance": 2,
                        "adventureLevel": 1,
                        "nightlife": 2,
                        "priceRange": "$$$",
                        "cuisineTypes": ["American", "International", "Quick"],
                        "specialInterests": ["business", "networking", "efficiency", "landmarks"],
                        "preferredTimes": {"morning": True, "afternoon": False, "evening": True}
                    },
                    "use_optimized_service": True
                },
                "trip_document": {
                    "destination": "New York, NY",
                    "preferences": {
                        "travelStyle": "business",
                        "groupType": "solo",
                        "specialInterests": ["business", "networking", "efficiency", "landmarks"],
                        "cuisineTypes": ["American", "International", "Quick"],
                        "priceRange": "$$$"
                    }
                }
            }
        ]
        
        return scenarios
    
    def _update_performance_metrics(self, test_result: Dict):
        """Update performance metrics with test result"""
        
        self.performance_metrics["total_tests"] += 1
        self.performance_metrics["successful_generations"] += 1
        
        # Update average generation time
        current_avg = self.performance_metrics["average_generation_time"]
        total_tests = self.performance_metrics["total_tests"]
        new_time = test_result["generation_time"]
        
        self.performance_metrics["average_generation_time"] = (
            (current_avg * (total_tests - 1) + new_time) / total_tests
        )
        
        # Update quality scores
        quality_score = test_result["evaluation"].overall_score
        self.performance_metrics["quality_scores"].append(quality_score)
        self.performance_metrics["average_quality_score"] = (
            sum(self.performance_metrics["quality_scores"]) / 
            len(self.performance_metrics["quality_scores"])
        )
    
    def _print_test_summary(self, test_result: Dict):
        """Print summary for individual test"""
        
        evaluation = test_result["evaluation"]
        
        print(f"⏱️  Generation Time: {test_result['generation_time']:.1f}s")
        print(f"🏆 Overall Score: {evaluation.overall_score:.1f}/100")
        print(f"📊 Grade: {self.evaluator._get_letter_grade(evaluation.overall_score)}")
        
        # Top 3 strengths and issues
        all_strengths = []
        all_issues = []
        
        categories = [
            evaluation.personalization, evaluation.content_quality,
            evaluation.attractions_quality, evaluation.restaurants_quality,
            evaluation.glossy_magazine_style
        ]
        
        for category in categories:
            if category:
                all_strengths.extend(category.strengths)
                all_issues.extend(category.specific_issues)
        
        if all_strengths:
            print("✅ Top Strengths:")
            for strength in all_strengths[:3]:
                print(f"   • {strength}")
        
        if all_issues:
            print("⚠️  Key Issues:")
            for issue in all_issues[:3]:
                print(f"   • {issue}")
    
    async def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST SUITE RESULTS")
        print("="*80)
        
        # Performance summary
        metrics = self.performance_metrics
        print(f"🎯 Tests Completed: {metrics['total_tests']}")
        print(f"✅ Successful Generations: {metrics['successful_generations']}")
        print(f"⏱️  Average Generation Time: {metrics['average_generation_time']:.1f}s")
        print(f"🏆 Average Quality Score: {metrics['average_quality_score']:.1f}/100")
        
        # Quality distribution
        if metrics['quality_scores']:
            scores = metrics['quality_scores']
            print(f"📈 Quality Range: {min(scores):.1f} - {max(scores):.1f}")
            
            # Grade distribution
            grades = [self.evaluator._get_letter_grade(score) for score in scores]
            grade_counts = {}
            for grade in grades:
                grade_letter = grade.split()[0]  # Get just the letter
                grade_counts[grade_letter] = grade_counts.get(grade_letter, 0) + 1
            
            print("📊 Grade Distribution:")
            for grade, count in sorted(grade_counts.items()):
                print(f"   {grade}: {count} guides")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        print("-" * 60)
        
        for i, result in enumerate(self.test_results, 1):
            evaluation = result["evaluation"]
            print(f"{i}. {result['scenario']}")
            print(f"   Score: {evaluation.overall_score:.1f}/100 | Time: {result['generation_time']:.1f}s")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"comprehensive_test_report_{timestamp}.json"
        
        report_data = {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": metrics['total_tests'],
                "successful_generations": metrics['successful_generations'],
                "average_generation_time": metrics['average_generation_time'],
                "average_quality_score": metrics['average_quality_score'],
                "quality_scores": metrics['quality_scores']
            },
            "detailed_results": []
        }
        
        # Add detailed results (convert evaluation objects to dicts)
        for result in self.test_results:
            detailed_result = result.copy()
            # Convert evaluation to dict for JSON serialization
            from dataclasses import asdict
            detailed_result["evaluation"] = asdict(result["evaluation"])
            report_data["detailed_results"].append(detailed_result)
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Recommendations
        self._print_improvement_recommendations()
        
        return report_data
    
    def _print_improvement_recommendations(self):
        """Print improvement recommendations based on test results"""
        
        print("\n🎯 IMPROVEMENT RECOMMENDATIONS:")
        print("-" * 60)
        
        if not self.test_results:
            print("No test results available for recommendations.")
            return
        
        # Analyze common issues across all tests
        all_issues = []
        low_scoring_categories = {}
        
        for result in self.test_results:
            evaluation = result["evaluation"]
            
            # Collect all issues
            categories = [
                evaluation.personalization, evaluation.content_quality,
                evaluation.layout_structure, evaluation.weather_integration,
                evaluation.attractions_quality, evaluation.restaurants_quality,
                evaluation.practical_info, evaluation.daily_itinerary,
                evaluation.glossy_magazine_style, evaluation.completeness
            ]
            
            for category in categories:
                if category:
                    all_issues.extend(category.specific_issues)
                    
                    # Track low-scoring categories
                    if category.score < 7.0:
                        cat_name = category.category
                        if cat_name not in low_scoring_categories:
                            low_scoring_categories[cat_name] = []
                        low_scoring_categories[cat_name].append(category.score)
        
        # Most common issues
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if common_issues:
            print("🔧 Most Common Issues:")
            for issue, count in common_issues:
                print(f"   • {issue} (appears in {count} tests)")
        
        # Consistently low-scoring categories
        if low_scoring_categories:
            print("\n📉 Categories Needing Improvement:")
            for category, scores in low_scoring_categories.items():
                avg_score = sum(scores) / len(scores)
                print(f"   • {category.replace('_', ' ').title()}: {avg_score:.1f}/10 average")
        
        # Performance recommendations
        avg_time = self.performance_metrics["average_generation_time"]
        if avg_time > 30:
            print(f"\n⚡ Performance: Average generation time ({avg_time:.1f}s) exceeds 30s target")
            print("   Consider optimizing API calls or caching strategies")
        
        avg_quality = self.performance_metrics["average_quality_score"]
        if avg_quality < 80:
            print(f"\n🎯 Quality: Average score ({avg_quality:.1f}/100) below 80 target")
            print("   Focus on content quality and personalization improvements")


async def main():
    """Run the comprehensive test suite"""
    
    # Check if backend is running
    backend_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{backend_url}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Backend not responding properly at {backend_url}")
            return
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to backend at {backend_url}")
        print("   Make sure your backend server is running:")
        print("   cd backend && python main.py")
        return
    
    # Run comprehensive tests
    test_suite = ComprehensiveGuideTestSuite(backend_url)
    
    try:
        final_report = await test_suite.run_comprehensive_tests()
        
        print("\n🎉 Comprehensive testing completed!")
        print("   Use the detailed report to guide your development improvements.")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
