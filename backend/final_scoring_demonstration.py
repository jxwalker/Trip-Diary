#!/usr/bin/env python3
"""
Final Scoring Demonstration
Shows comprehensive scoring rubric and iterative improvement with enhanced mock guides
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.append('.')

from comprehensive_guide_scorer import ComprehensiveGuideScorer
from iterative_guide_improver import IterativeGuideImprover

async def demonstrate_scoring_system():
    """Demonstrate the comprehensive scoring system and iterative improvements"""
    
    print("🏆 COMPREHENSIVE SCORING RUBRIC DEMONSTRATION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    paris_trip_data = {
        "destination": "Paris, France",
        "start_date": "2025-03-15",
        "end_date": "2025-03-22",
        "hotel_info": {
            "name": "Hilton Paris Opera",
            "address": "108 Rue Saint-Lazare, 75008 Paris, France",
            "check_in": "2025-03-15",
            "check_out": "2025-03-22",
            "phone": "+33 1 40 08 44 44",
            "coordinates": {"lat": 48.8756, "lng": 2.3264}
        },
        "preferences": {
            "interests": {
                "artGalleries": True,
                "museums": True,
                "historicalSites": True,
                "theater": True,
                "liveMusic": True,
                "fineDining": True,
                "localCuisine": True,
                "shopping": True,
                "architecture": True,
                "nightlife": True
            },
            "cuisines": ["French", "Italian", "Japanese", "Mediterranean"],
            "dietary": [],
            "priceRange": ["moderate", "expensive", "luxury"],
            "pace": "moderate",
            "walkingLevel": 4,
            "groupType": "couple",
            "preferredTimes": {
                "morning": True,
                "afternoon": True,
                "evening": True
            },
            "specialInterests": ["art", "culture", "food", "architecture"],
            "travelStyle": "luxury",
            "budget": "high"
        },
        "extracted_data": {
            "flights": [
                {
                    "flight_number": "BA2303",
                    "airline": "British Airways",
                    "departure": {"airport": "LHR", "date": "2025-03-15", "time": "10:30"},
                    "arrival": {"airport": "CDG", "date": "2025-03-15", "time": "12:45"}
                }
            ],
            "passengers": [
                {"name": "John Smith", "email": "john.smith@email.com"},
                {"name": "Jane Smith"}
            ]
        }
    }
    
    output_dir = Path("output/final_scoring_demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scorer = ComprehensiveGuideScorer()
    improver = IterativeGuideImprover()
    
    print(f"\n📋 COMPREHENSIVE SCORING RUBRIC")
    print("=" * 50)
    print(f"🎯 Target Score: 85+ (Production Ready)")
    print(f"📊 Scoring Components:")
    for component, weight in scorer.scoring_weights.items():
        print(f"  • {component.replace('_', ' ').title()}: {weight}%")
    
    iteration_results = []
    
    for iteration in range(1, 4):
        print(f"\n🔄 ITERATION {iteration}")
        print("-" * 40)
        
        enhanced_preferences = paris_trip_data["preferences"].copy()
        if iteration > 1:
            enhanced_preferences["priceRange"] = ["expensive", "luxury"]
            enhanced_preferences["interests"]["fineDining"] = True
            enhanced_preferences["travelStyle"] = "luxury"
        if iteration > 2:
            enhanced_preferences["interests"]["shopping"] = True
            enhanced_preferences["interests"]["artGalleries"] = True
            enhanced_preferences["walkingLevel"] = 5
        
        print(f"  📝 Generating enhanced guide (iteration {iteration})...")
        guide = improver._create_enhanced_mock_guide(
            paris_trip_data, 
            enhanced_preferences, 
            iteration
        )
        
        print(f"  🔍 Running comprehensive evaluation...")
        scoring_results = await scorer.score_guide_comprehensively(guide, paris_trip_data)
        
        pdf_path = None
        try:
            print(f"  📄 Generating magazine-quality PDF...")
            itinerary = {
                "trip_summary": {
                    "destination": paris_trip_data["destination"],
                    "start_date": paris_trip_data["start_date"],
                    "end_date": paris_trip_data["end_date"],
                    "duration": f"{len(guide.get('daily_itinerary', []))} days"
                },
                "accommodations": [paris_trip_data["hotel_info"]],
                "flights": paris_trip_data.get("extracted_data", {}).get("flights", [])
            }
            
            pdf_filename = output_dir / f"paris_guide_iteration_{iteration}.pdf"
            pdf_path = await asyncio.to_thread(
                improver.pdf_renderer.render_magazine_pdf,
                guide=guide,
                itinerary=itinerary,
                output_path=pdf_filename
            )
            
            file_size = pdf_path.stat().st_size
            print(f"    ✅ PDF generated: {pdf_path.name} ({file_size / 1024:.1f} KB)")
            
        except Exception as e:
            print(f"    ⚠️  PDF generation skipped: {e}")
        
        iteration_result = {
            "iteration": iteration,
            "scoring_results": scoring_results,
            "pdf_path": str(pdf_path) if pdf_path else None,
            "guide_summary": {
                "restaurants": len(guide.get("restaurants", [])),
                "attractions": len(guide.get("attractions", [])),
                "itinerary_days": len(guide.get("daily_itinerary", []))
            }
        }
        iteration_results.append(iteration_result)
        
        overall_score = scoring_results["evaluation_summary"]["overall_score"]
        grade = scoring_results["evaluation_summary"]["grade"]
        ready = scoring_results["evaluation_summary"]["ready_for_production"]
        
        print(f"  📊 Score: {overall_score}/100 (Grade: {grade})")
        print(f"  🎯 Production Ready: {'✅ YES' if ready else '❌ NO'}")
        
        scorer.print_scoring_summary(scoring_results)
    
    print(f"\n🏆 FINAL ANALYSIS")
    print("=" * 80)
    
    scores = [r["scoring_results"]["evaluation_summary"]["overall_score"] for r in iteration_results]
    print(f"📈 Score Progression: {' → '.join(f'{s:.1f}' for s in scores)}")
    print(f"📊 Total Improvement: +{scores[-1] - scores[0]:.1f} points")
    print(f"📊 Average per Iteration: +{(scores[-1] - scores[0]) / (len(scores) - 1):.1f} points")
    
    target_achieved = scores[-1] >= 85.0
    print(f"🎯 Target Achievement: {'✅ SUCCESS' if target_achieved else '❌ NEEDS MORE WORK'} (Target: 85+)")
    
    print(f"\n📋 CATEGORY BREAKDOWN (Final Iteration):")
    final_scores = iteration_results[-1]["scoring_results"]["detailed_scores"]
    print(f"  • Validation: {final_scores['validation']['score']}/100")
    print(f"  • PRD Compliance: {final_scores['prd_compliance']['score']}/100")
    print(f"  • Luxury Standards: {final_scores['luxury_standards']['score']}/100")
    print(f"  • User Experience: {final_scores['user_experience']['score']}/100")
    if 'ai_analysis' in final_scores and 'overall_score' in final_scores['ai_analysis']:
        print(f"  • AI Analysis: {final_scores['ai_analysis']['overall_score']}/10")
    
    results_file = output_dir / "comprehensive_scoring_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "trip_data": paris_trip_data,
            "iteration_results": iteration_results,
            "final_analysis": {
                "score_progression": scores,
                "total_improvement": scores[-1] - scores[0],
                "target_achieved": target_achieved,
                "final_score": scores[-1]
            }
        }, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to: {output_dir}")
    print(f"📄 Final PDF: {iteration_results[-1]['pdf_path'] if iteration_results[-1]['pdf_path'] else 'Not generated'}")
    
    return iteration_results

if __name__ == "__main__":
    asyncio.run(demonstrate_scoring_system())
