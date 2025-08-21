#!/usr/bin/env python3
"""
Performance Benchmarking Module
Tracks guide generation performance over time and identifies regressions
"""
import asyncio
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import requests


@dataclass
class PerformanceBenchmark:
    """Performance benchmark result"""
    timestamp: str
    test_name: str
    destination: str
    generation_time: float
    success: bool
    guide_completeness_score: float
    api_calls_made: int
    cache_hits: int
    error_message: str = ""
    
    def __post_init__(self):
        if self.timestamp == "":
            self.timestamp = datetime.now().isoformat()


@dataclass
class BenchmarkSummary:
    """Summary of benchmark results"""
    total_tests: int
    successful_tests: int
    average_generation_time: float
    median_generation_time: float
    p95_generation_time: float
    fastest_generation: float
    slowest_generation: float
    average_completeness: float
    success_rate: float
    timestamp: str = ""
    
    def __post_init__(self):
        if self.timestamp == "":
            self.timestamp = datetime.now().isoformat()


class PerformanceBenchmarker:
    """
    Performance benchmarking system that:
    1. Runs standardized performance tests
    2. Tracks metrics over time
    3. Identifies performance regressions
    4. Provides optimization recommendations
    """
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.benchmark_results: List[PerformanceBenchmark] = []
        self.benchmark_history_file = "performance_benchmark_history.json"
    
    async def run_performance_benchmark(self, iterations: int = 5) -> BenchmarkSummary:
        """Run comprehensive performance benchmark"""
        
        print(f"🚀 Running Performance Benchmark ({iterations} iterations)")
        print("=" * 70)
        
        # Standard test scenarios for consistent benchmarking
        test_scenarios = self._get_benchmark_scenarios()
        
        all_results = []
        
        for scenario in test_scenarios:
            print(f"\n📋 Testing: {scenario['name']}")
            print("-" * 50)
            
            scenario_results = []
            
            for i in range(iterations):
                print(f"   Iteration {i+1}/{iterations}...", end=" ")
                
                result = await self._run_single_benchmark(scenario)
                scenario_results.append(result)
                all_results.append(result)
                
                if result.success:
                    print(f"✅ {result.generation_time:.1f}s")
                else:
                    print(f"❌ Failed: {result.error_message[:50]}")
            
            # Print scenario summary
            successful_results = [r for r in scenario_results if r.success]
            if successful_results:
                times = [r.generation_time for r in successful_results]
                avg_time = statistics.mean(times)
                print(f"   📊 Average: {avg_time:.1f}s | Success: {len(successful_results)}/{iterations}")
        
        # Generate summary
        summary = self._generate_benchmark_summary(all_results)
        
        # Save results
        self._save_benchmark_results(all_results, summary)
        
        # Print summary
        self._print_benchmark_summary(summary)
        
        return summary
    
    async def _run_single_benchmark(self, scenario: Dict) -> PerformanceBenchmark:
        """Run a single benchmark test"""
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/generate-enhanced-guide",
                json=scenario['request_data'],
                timeout=120  # 2 minute timeout for benchmarking
            )
            
            generation_time = time.time() - start_time
            
            if response.status_code == 200:
                guide_data = response.json()
                guide = guide_data.get('guide', guide_data)
                
                # Calculate completeness score
                completeness_score = self._calculate_completeness_score(guide)
                
                # Extract performance metrics if available
                perf_stats = guide.get('performance_stats', {})
                api_calls = perf_stats.get('concurrent_requests', 1)
                cache_hits = 1 if perf_stats.get('cache_used', False) else 0
                
                return PerformanceBenchmark(
                    timestamp=datetime.now().isoformat(),
                    test_name=scenario['name'],
                    destination=scenario['request_data']['destination'],
                    generation_time=generation_time,
                    success=True,
                    guide_completeness_score=completeness_score,
                    api_calls_made=api_calls,
                    cache_hits=cache_hits
                )
            else:
                return PerformanceBenchmark(
                    timestamp=datetime.now().isoformat(),
                    test_name=scenario['name'],
                    destination=scenario['request_data']['destination'],
                    generation_time=generation_time,
                    success=False,
                    guide_completeness_score=0.0,
                    api_calls_made=0,
                    cache_hits=0,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            generation_time = time.time() - start_time
            return PerformanceBenchmark(
                timestamp=datetime.now().isoformat(),
                test_name=scenario['name'],
                destination=scenario['request_data']['destination'],
                generation_time=generation_time,
                success=False,
                guide_completeness_score=0.0,
                api_calls_made=0,
                cache_hits=0,
                error_message=str(e)
            )
    
    def _get_benchmark_scenarios(self) -> List[Dict]:
        """Get standardized benchmark scenarios"""
        
        base_date = datetime.now() + timedelta(days=30)
        start_date = base_date.strftime("%Y-%m-%d")
        end_date = (base_date + timedelta(days=3)).strftime("%Y-%m-%d")
        
        return [
            {
                "name": "Standard European City",
                "request_data": {
                    "destination": "Amsterdam, Netherlands",
                    "start_date": start_date,
                    "end_date": end_date,
                    "hotel_info": {"name": "Canal Hotel", "address": "Amsterdam Center"},
                    "preferences": {
                        "travelStyle": "balanced",
                        "groupType": "couple",
                        "specialInterests": ["museums", "culture", "food"],
                        "cuisineTypes": ["Local", "International"],
                        "priceRange": "$$"
                    },
                    "use_optimized_service": True
                }
            },
            {
                "name": "Asian Megacity",
                "request_data": {
                    "destination": "Singapore",
                    "start_date": start_date,
                    "end_date": end_date,
                    "hotel_info": {"name": "Marina Bay Hotel", "address": "Marina Bay, Singapore"},
                    "preferences": {
                        "travelStyle": "luxury",
                        "groupType": "solo",
                        "specialInterests": ["food", "shopping", "architecture"],
                        "cuisineTypes": ["Asian", "Fusion"],
                        "priceRange": "$$$"
                    },
                    "use_optimized_service": True
                }
            },
            {
                "name": "American City",
                "request_data": {
                    "destination": "San Francisco, CA",
                    "start_date": start_date,
                    "end_date": end_date,
                    "hotel_info": {"name": "Union Square Hotel", "address": "Union Square, SF"},
                    "preferences": {
                        "travelStyle": "adventure",
                        "groupType": "friends",
                        "specialInterests": ["technology", "nature", "food"],
                        "cuisineTypes": ["American", "International"],
                        "priceRange": "$$"
                    },
                    "use_optimized_service": True
                }
            }
        ]
    
    def _calculate_completeness_score(self, guide: Dict) -> float:
        """Calculate guide completeness score (0-100)"""
        
        required_fields = [
            'summary', 'destination_insights', 'daily_itinerary',
            'restaurants', 'attractions', 'practical_info'
        ]
        
        score = 0.0
        
        # Check required fields (60 points)
        for field in required_fields:
            if field in guide and guide[field]:
                if field in ['summary', 'destination_insights']:
                    # Text fields - check length
                    if len(str(guide[field]).strip()) >= 50:
                        score += 10
                elif field in ['daily_itinerary', 'restaurants', 'attractions']:
                    # List fields - check count
                    if isinstance(guide[field], list) and len(guide[field]) >= 1:
                        score += 10
                elif field == 'practical_info':
                    # Dict field - check categories
                    if isinstance(guide[field], dict) and len(guide[field]) >= 3:
                        score += 10
        
        # Check additional features (40 points)
        additional_features = [
            ('weather', 10),
            ('events', 5),
            ('hidden_gems', 10),
            ('neighborhoods', 5),
            ('validation_passed', 10)
        ]
        
        for feature, points in additional_features:
            if feature in guide and guide[feature]:
                score += points
        
        return min(score, 100.0)
    
    def _generate_benchmark_summary(self, results: List[PerformanceBenchmark]) -> BenchmarkSummary:
        """Generate benchmark summary from results"""
        
        successful_results = [r for r in results if r.success]
        
        if not successful_results:
            return BenchmarkSummary(
                total_tests=len(results),
                successful_tests=0,
                average_generation_time=0.0,
                median_generation_time=0.0,
                p95_generation_time=0.0,
                fastest_generation=0.0,
                slowest_generation=0.0,
                average_completeness=0.0,
                success_rate=0.0
            )
        
        times = [r.generation_time for r in successful_results]
        completeness_scores = [r.guide_completeness_score for r in successful_results]
        
        return BenchmarkSummary(
            total_tests=len(results),
            successful_tests=len(successful_results),
            average_generation_time=statistics.mean(times),
            median_generation_time=statistics.median(times),
            p95_generation_time=self._percentile(times, 95),
            fastest_generation=min(times),
            slowest_generation=max(times),
            average_completeness=statistics.mean(completeness_scores),
            success_rate=(len(successful_results) / len(results)) * 100
        )
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _save_benchmark_results(self, results: List[PerformanceBenchmark], summary: BenchmarkSummary):
        """Save benchmark results to file"""
        
        # Load existing history
        history = self._load_benchmark_history()
        
        # Add new results
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "summary": asdict(summary),
            "detailed_results": [asdict(r) for r in results]
        }
        
        history.append(new_entry)
        
        # Save updated history
        with open(self.benchmark_history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)
        
        print(f"\n💾 Benchmark results saved to {self.benchmark_history_file}")
    
    def _load_benchmark_history(self) -> List[Dict]:
        """Load benchmark history from file"""
        
        try:
            with open(self.benchmark_history_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _print_benchmark_summary(self, summary: BenchmarkSummary):
        """Print formatted benchmark summary"""
        
        print("\n" + "="*70)
        print("📊 PERFORMANCE BENCHMARK SUMMARY")
        print("="*70)
        
        print(f"🎯 Tests: {summary.successful_tests}/{summary.total_tests} successful ({summary.success_rate:.1f}%)")
        print(f"⏱️  Average Time: {summary.average_generation_time:.1f}s")
        print(f"📈 Median Time: {summary.median_generation_time:.1f}s")
        print(f"🚀 Fastest: {summary.fastest_generation:.1f}s")
        print(f"🐌 Slowest: {summary.slowest_generation:.1f}s")
        print(f"📊 95th Percentile: {summary.p95_generation_time:.1f}s")
        print(f"✅ Average Completeness: {summary.average_completeness:.1f}/100")
        
        # Performance assessment
        print("\n🎯 PERFORMANCE ASSESSMENT:")
        print("-" * 40)
        
        if summary.average_generation_time <= 20:
            print("⚡ Excellent: Average time ≤ 20s")
        elif summary.average_generation_time <= 30:
            print("✅ Good: Average time ≤ 30s")
        elif summary.average_generation_time <= 45:
            print("⚠️  Fair: Average time ≤ 45s")
        else:
            print("❌ Poor: Average time > 45s")
        
        if summary.success_rate >= 95:
            print("✅ Excellent: Success rate ≥ 95%")
        elif summary.success_rate >= 90:
            print("⚠️  Good: Success rate ≥ 90%")
        else:
            print("❌ Poor: Success rate < 90%")
        
        if summary.average_completeness >= 85:
            print("✅ Excellent: Completeness ≥ 85/100")
        elif summary.average_completeness >= 70:
            print("⚠️  Good: Completeness ≥ 70/100")
        else:
            print("❌ Poor: Completeness < 70/100")
    
    def analyze_performance_trends(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        
        history = self._load_benchmark_history()
        
        if len(history) < 2:
            print("⚠️  Not enough historical data for trend analysis")
            return {}
        
        # Filter recent results
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_history = [
            entry for entry in history
            if datetime.fromisoformat(entry['timestamp']) >= cutoff_date
        ]
        
        if len(recent_history) < 2:
            print(f"⚠️  Not enough data in last {days_back} days for trend analysis")
            return {}
        
        print(f"\n📈 PERFORMANCE TRENDS (Last {days_back} days)")
        print("=" * 60)
        
        # Extract metrics over time
        timestamps = [entry['timestamp'] for entry in recent_history]
        avg_times = [entry['summary']['average_generation_time'] for entry in recent_history]
        success_rates = [entry['summary']['success_rate'] for entry in recent_history]
        completeness_scores = [entry['summary']['average_completeness'] for entry in recent_history]
        
        # Calculate trends
        time_trend = self._calculate_trend(avg_times)
        success_trend = self._calculate_trend(success_rates)
        completeness_trend = self._calculate_trend(completeness_scores)
        
        print(f"⏱️  Generation Time: {time_trend['direction']} ({time_trend['change']:.1f}s change)")
        print(f"✅ Success Rate: {success_trend['direction']} ({success_trend['change']:.1f}% change)")
        print(f"📊 Completeness: {completeness_trend['direction']} ({completeness_trend['change']:.1f} point change)")
        
        # Recommendations
        print("\n🎯 TREND RECOMMENDATIONS:")
        print("-" * 30)
        
        if time_trend['direction'] == "📈 Improving":
            print("✅ Performance is improving - keep up the good work!")
        elif time_trend['direction'] == "📉 Declining":
            print("⚠️  Performance declining - investigate recent changes")
        
        return {
            "time_trend": time_trend,
            "success_trend": success_trend,
            "completeness_trend": completeness_trend,
            "data_points": len(recent_history)
        }
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and magnitude"""
        
        if len(values) < 2:
            return {"direction": "📊 Insufficient data", "change": 0.0}
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change = second_avg - first_avg
        
        if abs(change) < 0.1:  # Minimal change threshold
            direction = "➡️  Stable"
        elif change > 0:
            direction = "📈 Improving" if "time" not in str(values) else "📉 Declining"  # For time, increase is bad
        else:
            direction = "📉 Declining" if "time" not in str(values) else "📈 Improving"  # For time, decrease is good
        
        return {
            "direction": direction,
            "change": abs(change),
            "first_period_avg": first_avg,
            "second_period_avg": second_avg
        }


async def main():
    """Run performance benchmark"""
    
    benchmarker = PerformanceBenchmarker()
    
    # Run benchmark
    summary = await benchmarker.run_performance_benchmark(iterations=3)
    
    # Analyze trends if historical data exists
    benchmarker.analyze_performance_trends()
    
    print("\n🎉 Performance benchmarking completed!")


if __name__ == "__main__":
    asyncio.run(main())
