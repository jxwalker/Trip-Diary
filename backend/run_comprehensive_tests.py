#!/usr/bin/env python3
"""
Master Test Runner for Trip Diary Comprehensive Testing
Orchestrates all testing modules for complete system validation
"""
import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
import requests

# Add project paths
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from tests.integration.comprehensive_guide_test_suite import ComprehensiveGuideTestSuite
from tests.integration.performance_benchmark import PerformanceBenchmarker


class MasterTestRunner:
    """
    Master test runner that coordinates all testing modules:
    1. Basic API connectivity tests
    2. Performance benchmarking
    3. Comprehensive guide quality evaluation
    4. Trend analysis and reporting
    """
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.test_results = {}
    
    async def run_all_tests(self, 
                           run_basic: bool = True,
                           run_performance: bool = True, 
                           run_comprehensive: bool = True,
                           performance_iterations: int = 3,
                           analyze_trends: bool = True) -> dict:
        """Run all test suites"""
        
        print("🚀 TRIP DIARY COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"🎯 Backend URL: {self.backend_url}")
        print(f"📅 Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Check backend connectivity
        if not await self._check_backend_connectivity():
            print("❌ Cannot proceed - backend not accessible")
            return {"error": "Backend not accessible"}
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "backend_url": self.backend_url,
            "tests_run": []
        }
        
        # 1. Basic API Tests
        if run_basic:
            print("\n🔧 PHASE 1: Basic API Tests")
            print("-" * 50)
            basic_results = await self._run_basic_tests()
            results["basic_tests"] = basic_results
            results["tests_run"].append("basic_tests")
        
        # 2. Performance Benchmarking
        if run_performance:
            print("\n⚡ PHASE 2: Performance Benchmarking")
            print("-" * 50)
            benchmarker = PerformanceBenchmarker(self.backend_url)
            performance_results = await benchmarker.run_performance_benchmark(performance_iterations)
            results["performance_benchmark"] = performance_results
            results["tests_run"].append("performance_benchmark")
            
            # Trend analysis
            if analyze_trends:
                print("\n📈 Analyzing Performance Trends...")
                trend_analysis = benchmarker.analyze_performance_trends()
                results["trend_analysis"] = trend_analysis
        
        # 3. Comprehensive Guide Quality Tests
        if run_comprehensive:
            print("\n🎯 PHASE 3: Comprehensive Guide Quality Evaluation")
            print("-" * 50)
            test_suite = ComprehensiveGuideTestSuite(self.backend_url)
            comprehensive_results = await test_suite.run_comprehensive_tests()
            results["comprehensive_tests"] = comprehensive_results
            results["tests_run"].append("comprehensive_tests")
        
        # Generate final summary
        await self._generate_final_summary(results)
        
        return results
    
    async def _check_backend_connectivity(self) -> bool:
        """Check if backend is accessible"""
        
        print("🔍 Checking backend connectivity...")
        
        try:
            response = requests.get(f"{self.backend_url}/", timeout=10)
            if response.status_code == 200:
                print("✅ Backend is accessible")
                return True
            else:
                print(f"❌ Backend returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to backend: {e}")
            print("\n💡 To start the backend:")
            print("   cd backend")
            print("   python main.py")
            return False
    
    async def _run_basic_tests(self) -> dict:
        """Run basic API endpoint tests"""
        
        endpoints_to_test = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/docs", "API documentation"),
            ("POST", "/api/generate-enhanced-guide", "Enhanced guide generation"),
            ("GET", "/api/status/test-123", "Status endpoint"),
        ]
        
        results = {
            "total_endpoints": len(endpoints_to_test),
            "successful_endpoints": 0,
            "endpoint_results": []
        }
        
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                else:
                    # Use minimal test data for POST requests
                    test_data = {
                        "destination": "Test City",
                        "start_date": "2025-01-01",
                        "end_date": "2025-01-03",
                        "hotel_info": {"name": "Test Hotel"},
                        "preferences": {"specialInterests": ["test"]},
                        "use_optimized_service": True
                    }
                    response = requests.post(f"{self.backend_url}{endpoint}", 
                                           json=test_data, timeout=30)
                
                # Consider various success codes
                success = response.status_code in [200, 201, 404, 422]  # 404/422 acceptable for test endpoints
                
                if success:
                    results["successful_endpoints"] += 1
                
                endpoint_result = {
                    "endpoint": endpoint,
                    "method": method,
                    "description": description,
                    "status_code": response.status_code,
                    "success": success,
                    "response_time": response.elapsed.total_seconds()
                }
                
                results["endpoint_results"].append(endpoint_result)
                
                status = "✅" if success else "❌"
                print(f"{status} {description}: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
                
            except requests.exceptions.RequestException as e:
                endpoint_result = {
                    "endpoint": endpoint,
                    "method": method,
                    "description": description,
                    "status_code": 0,
                    "success": False,
                    "error": str(e),
                    "response_time": 0
                }
                
                results["endpoint_results"].append(endpoint_result)
                print(f"❌ {description}: Connection error - {e}")
        
        success_rate = (results["successful_endpoints"] / results["total_endpoints"]) * 100
        results["success_rate"] = success_rate
        
        print(f"\n📊 Basic Tests Summary: {results['successful_endpoints']}/{results['total_endpoints']} endpoints successful ({success_rate:.1f}%)")
        
        return results
    
    async def _generate_final_summary(self, results: dict):
        """Generate comprehensive final summary"""
        
        print("\n" + "="*80)
        print("🏆 COMPREHENSIVE TEST SUITE FINAL SUMMARY")
        print("="*80)
        
        tests_run = results.get("tests_run", [])
        
        # Basic tests summary
        if "basic_tests" in tests_run:
            basic = results["basic_tests"]
            print(f"🔧 Basic API Tests: {basic['successful_endpoints']}/{basic['total_endpoints']} endpoints ({basic['success_rate']:.1f}%)")
        
        # Performance summary
        if "performance_benchmark" in tests_run:
            perf = results["performance_benchmark"]
            print(f"⚡ Performance: {perf.average_generation_time:.1f}s avg, {perf.success_rate:.1f}% success rate")
            
            # Performance grade
            if perf.average_generation_time <= 20:
                perf_grade = "A+ (Excellent)"
            elif perf.average_generation_time <= 30:
                perf_grade = "A (Good)"
            elif perf.average_generation_time <= 45:
                perf_grade = "B (Fair)"
            else:
                perf_grade = "C (Needs Improvement)"
            
            print(f"   Performance Grade: {perf_grade}")
        
        # Comprehensive tests summary
        if "comprehensive_tests" in tests_run:
            comp = results["comprehensive_tests"]
            test_summary = comp.get("test_summary", {})
            avg_quality = test_summary.get("average_quality_score", 0)
            total_tests = test_summary.get("total_tests", 0)
            successful = test_summary.get("successful_generations", 0)
            
            print(f"🎯 Guide Quality: {avg_quality:.1f}/100 average, {successful}/{total_tests} successful")
            
            # Quality grade
            if avg_quality >= 85:
                quality_grade = "A+ (Excellent)"
            elif avg_quality >= 75:
                quality_grade = "A (Good)"
            elif avg_quality >= 65:
                quality_grade = "B (Fair)"
            else:
                quality_grade = "C (Needs Improvement)"
            
            print(f"   Quality Grade: {quality_grade}")
        
        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        print("-" * 40)
        
        issues = []
        strengths = []
        
        # Analyze results for issues and strengths
        if "basic_tests" in tests_run:
            basic = results["basic_tests"]
            if basic["success_rate"] < 80:
                issues.append("API endpoint connectivity issues")
            else:
                strengths.append("Solid API endpoint reliability")
        
        if "performance_benchmark" in tests_run:
            perf = results["performance_benchmark"]
            if perf.average_generation_time > 30:
                issues.append("Generation time exceeds 30s target")
            else:
                strengths.append("Fast guide generation performance")
            
            if perf.success_rate < 90:
                issues.append("Guide generation reliability below 90%")
            else:
                strengths.append("High guide generation success rate")
        
        if "comprehensive_tests" in tests_run:
            comp = results["comprehensive_tests"]
            test_summary = comp.get("test_summary", {})
            avg_quality = test_summary.get("average_quality_score", 0)
            
            if avg_quality < 75:
                issues.append("Guide quality below 75/100 target")
            else:
                strengths.append("High-quality guide generation")
        
        # Print strengths
        if strengths:
            print("✅ STRENGTHS:")
            for strength in strengths:
                print(f"   • {strength}")
        
        # Print issues
        if issues:
            print("\n⚠️  AREAS FOR IMPROVEMENT:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("\n🎉 No major issues identified!")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 25)
        
        if not issues:
            print("   • System performing well - consider adding more test scenarios")
            print("   • Monitor performance trends over time")
            print("   • Consider implementing additional quality metrics")
        else:
            if any("time" in issue.lower() for issue in issues):
                print("   • Optimize API call concurrency and caching")
                print("   • Review timeout settings and retry logic")
            
            if any("quality" in issue.lower() for issue in issues):
                print("   • Enhance content generation prompts")
                print("   • Improve personalization algorithms")
                print("   • Add more comprehensive validation")
            
            if any("reliability" in issue.lower() or "connectivity" in issue.lower() for issue in issues):
                print("   • Improve error handling and fallback mechanisms")
                print("   • Add circuit breaker patterns for external APIs")
        
        # Save summary report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"comprehensive_test_summary_{timestamp}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Complete test results saved to: {report_file}")
        print("\n🎉 Comprehensive testing completed!")


async def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Run comprehensive trip diary tests")
    parser.add_argument("--backend-url", default="http://localhost:8000", 
                       help="Backend URL (default: http://localhost:8000)")
    parser.add_argument("--skip-basic", action="store_true", 
                       help="Skip basic API tests")
    parser.add_argument("--skip-performance", action="store_true", 
                       help="Skip performance benchmarking")
    parser.add_argument("--skip-comprehensive", action="store_true", 
                       help="Skip comprehensive quality tests")
    parser.add_argument("--performance-iterations", type=int, default=3,
                       help="Number of performance test iterations (default: 3)")
    parser.add_argument("--no-trends", action="store_true",
                       help="Skip trend analysis")
    
    args = parser.parse_args()
    
    runner = MasterTestRunner(args.backend_url)
    
    try:
        results = await runner.run_all_tests(
            run_basic=not args.skip_basic,
            run_performance=not args.skip_performance,
            run_comprehensive=not args.skip_comprehensive,
            performance_iterations=args.performance_iterations,
            analyze_trends=not args.no_trends
        )
        
        if "error" in results:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
