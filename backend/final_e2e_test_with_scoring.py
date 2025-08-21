#!/usr/bin/env python3
"""
Final End-to-End Test with PRD Scoring
Tests the complete workflow from PDF upload to guide generation and PRD compliance scoring
"""
import requests
import json
import asyncio
from pathlib import Path
from datetime import datetime
from prd_scoring_service import PRDScoringService

async def run_complete_test():
    """Run complete end-to-end test with scoring"""
    
    backend_url = "http://localhost:8000"
    pdf_path = Path("data/samples/paris_trip_march2025.pdf")
    
    print("\n" + "=" * 80)
    print("🚀 COMPLETE END-TO-END TEST WITH PRD SCORING 🚀")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Backend: {backend_url}")
    print(f"Test PDF: {pdf_path}")
    print("=" * 80)
    
    # Phase 1: Upload and Extract
    print("\n📤 PHASE 1: PDF Upload and Extraction")
    print("-" * 60)
    
    with open(pdf_path, "rb") as f:
        files = {"file": ("paris_trip.pdf", f, "application/pdf")}
        response = requests.post(f"{backend_url}/api/upload", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        return False
    
    data = response.json()
    trip_id = data.get("trip_id")
    extracted_data = data.get("extracted_data", {})
    
    print(f"✅ Upload successful! Trip ID: {trip_id}")
    print(f"✅ Extracted: {len(extracted_data.get('flights', []))} flights, "
          f"{len(extracted_data.get('hotels', []))} hotels, "
          f"{len(extracted_data.get('passengers', []))} passengers")
    
    # Phase 2: Generate Guide (try fast first, fallback if needed)
    print("\n🎯 PHASE 2: Guide Generation")
    print("-" * 60)
    
    guide = None
    guide_type = None
    
    # Try fast guide with external APIs
    print("Attempting fast guide generation with external APIs...")
    try:
        response = requests.post(
            f"{backend_url}/api/generate-enhanced-guide/{trip_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") != "error":
                guide = result.get("guide")
                guide_type = "fast_enhanced"
                print("✅ Fast guide generated successfully!")
    except requests.Timeout:
        print("⚠️ Fast guide timed out")
    
    # Fallback to offline generation if needed
    if not guide:
        print("Using fallback guide generation (no external APIs)...")
        response = requests.post(
            f"{backend_url}/api/generate-fallback-guide/{trip_id}",
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            guide = result.get("guide")
            guide_type = "fallback"
            print("✅ Fallback guide generated successfully!")
        else:
            print(f"❌ Guide generation failed: {response.status_code}")
            return False
    
    # Save guide for inspection
    guide_file = f"test_guide_{trip_id}.json"
    with open(guide_file, "w") as f:
        json.dump(guide, f, indent=2)
    print(f"💾 Guide saved to {guide_file}")
    
    # Phase 3: PRD Scoring
    print("\n📊 PHASE 3: PRD Compliance Scoring")
    print("-" * 60)
    
    scorer = PRDScoringService()
    score, categories, suggestions = scorer.score_guide(guide)
    
    print(f"Overall Score: {score}/100")
    print(f"Grade: {'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F'}")
    print(f"Meets Requirements: {'✅ Yes' if score >= 70 else '❌ No'}")
    
    print("\n📈 Category Breakdown:")
    for category, cat_score in categories.items():
        print(f"  • {category.replace('_', ' ').title()}: {cat_score}")
    
    # Phase 4: LLM Feedback
    print("\n🤖 PHASE 4: LLM Evaluation")
    print("-" * 60)
    
    llm_feedback = await scorer.get_llm_feedback(guide)
    
    if not llm_feedback.get("error"):
        print(f"LLM Score: {llm_feedback.get('score', 'N/A')}/100")
        print(f"Meets PRD: {llm_feedback.get('meets_prd', 'Unknown')}")
        
        if llm_feedback.get("strengths"):
            print("\n✅ Strengths:")
            for strength in llm_feedback.get("strengths", []):
                print(f"  • {strength}")
        
        if llm_feedback.get("weaknesses"):
            print("\n⚠️ Weaknesses:")
            for weakness in llm_feedback.get("weaknesses", []):
                print(f"  • {weakness}")
        
        if llm_feedback.get("improvements"):
            print("\n💡 Improvements Needed:")
            for improvement in llm_feedback.get("improvements", []):
                print(f"  • {improvement}")
    else:
        print(f"⚠️ LLM evaluation skipped: {llm_feedback.get('error')}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"✅ PDF Upload: Success")
    print(f"✅ Data Extraction: {len(extracted_data.get('flights', []))} flights, "
          f"{len(extracted_data.get('hotels', []))} hotels")
    print(f"✅ Guide Generation: {guide_type.replace('_', ' ').title()}")
    print(f"✅ PRD Score: {score}/100 (Grade: {'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D' if score >= 60 else 'F'})")
    print(f"✅ Compliance: {'PASS' if score >= 70 else 'FAIL'}")
    
    if suggestions:
        print("\n📝 Top Improvements Needed:")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"  {i}. {suggestion}")
    
    # Save full results
    results = {
        "timestamp": datetime.now().isoformat(),
        "trip_id": trip_id,
        "guide_type": guide_type,
        "prd_score": score,
        "category_scores": categories,
        "suggestions": suggestions,
        "llm_feedback": llm_feedback,
        "passed": score >= 70
    }
    
    results_file = f"test_results_{trip_id}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Full results saved to {results_file}")
    
    return score >= 70

if __name__ == "__main__":
    success = asyncio.run(run_complete_test())
    
    if success:
        print("\n🎉 TEST PASSED - Guide meets PRD requirements!")
    else:
        print("\n❌ TEST FAILED - Guide does not meet PRD requirements")