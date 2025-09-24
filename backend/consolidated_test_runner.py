#!/usr/bin/env python3
"""
Consolidated Test Runner
Organizes and executes all tests in logical categories with improved reporting
"""
import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import argparse

@dataclass
class TestResult:
    """Test execution result"""
    category: str
    name: str
    passed: bool
    duration: float
    output: str
    error: Optional[str] = None

@dataclass
class TestSuite:
    """Test suite configuration"""
    name: str
    description: str
    command: List[str]
    working_dir: str
    timeout: int = 300
    critical: bool = True

class ConsolidatedTestRunner:
    """Unified test runner for all test categories"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = datetime.now()
        
        self.test_suites = {
            "lint": TestSuite(
                name="Code Quality & Linting",
                description="Flake8, Black, isort, and other code quality checks",
                command=["python", "-m", "flake8", "src/", "tests/", "--max-line-length=120", "--extend-ignore=E203,W503"],
                working_dir=".",
                timeout=60,
                critical=True
            ),
            "type_check": TestSuite(
                name="Type Checking",
                description="MyPy static type analysis",
                command=["python", "-m", "mypy", "src/", "--ignore-missing-imports", "--no-strict-optional"],
                working_dir=".",
                timeout=120,
                critical=True
            ),
            "security": TestSuite(
                name="Security Scanning",
                description="Bandit security vulnerability scanning",
                command=["python", "-m", "bandit", "-r", "src/", "-f", "json"],
                working_dir=".",
                timeout=60,
                critical=True
            ),
            "unit": TestSuite(
                name="Unit Tests",
                description="Fast isolated unit tests",
                command=["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short", "--maxfail=5"],
                working_dir=".",
                timeout=180,
                critical=True
            ),
            "integration": TestSuite(
                name="Integration Tests",
                description="Service integration and API tests",
                command=["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short", "--maxfail=3"],
                working_dir=".",
                timeout=300,
                critical=True
            ),
            "api": TestSuite(
                name="API Tests",
                description="REST API endpoint tests",
                command=["python", "-m", "pytest", "tests/api/", "-v", "--tb=short"],
                working_dir=".",
                timeout=240,
                critical=True
            ),
            "performance": TestSuite(
                name="Performance Tests",
                description="Load testing and performance benchmarks",
                command=["python", "run_comprehensive_tests.py", "--performance-only"],
                working_dir=".",
                timeout=600,
                critical=False
            ),
            "guide_quality": TestSuite(
                name="Guide Quality Tests",
                description="Travel guide generation and quality evaluation",
                command=["python", "-m", "pytest", "tests/integration/", "-k", "guide", "-v"],
                working_dir=".",
                timeout=300,
                critical=True
            ),
            "pdf_generation": TestSuite(
                name="PDF Generation Tests",
                description="HTML and ReportLab PDF generation tests",
                command=["python", "-m", "pytest", "tests/", "-k", "pdf", "-v"],
                working_dir=".",
                timeout=180,
                critical=True
            ),
            "comprehensive": TestSuite(
                name="Comprehensive System Tests",
                description="End-to-end system validation",
                command=["python", "run_comprehensive_tests.py", "--quick"],
                working_dir=".",
                timeout=900,
                critical=False
            )
        }
    
    async def run_all_tests(
        self, 
        categories: Optional[List[str]] = None,
        fail_fast: bool = False,
        parallel: bool = False
    ) -> Dict[str, Any]:
        """Run all or specified test categories"""
        
        print("🧪 CONSOLIDATED TEST RUNNER")
        print("=" * 80)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        suites_to_run = {}
        if categories:
            for cat in categories:
                if cat in self.test_suites:
                    suites_to_run[cat] = self.test_suites[cat]
                else:
                    print(f"⚠️ Unknown test category: {cat}")
        else:
            suites_to_run = self.test_suites
        
        print(f"📋 Running {len(suites_to_run)} test suites")
        print()
        
        # Run tests
        if parallel and len(suites_to_run) > 1:
            await self._run_parallel(suites_to_run, fail_fast)
        else:
            await self._run_sequential(suites_to_run, fail_fast)
        
        return self._generate_report()
    
    async def _run_sequential(self, suites: Dict[str, TestSuite], fail_fast: bool):
        """Run test suites sequentially"""
        for category, suite in suites.items():
            print(f"🔄 {suite.name}")
            print(f"   {suite.description}")
            
            result = await self._execute_test_suite(category, suite)
            self.results.append(result)
            
            if result.passed:
                print(f"   ✅ PASSED ({result.duration:.1f}s)")
            else:
                print(f"   ❌ FAILED ({result.duration:.1f}s)")
                if result.error:
                    print(f"   Error: {result.error}")
                
                if fail_fast and suite.critical:
                    print(f"\n🛑 Stopping due to critical test failure")
                    break
            print()
    
    async def _run_parallel(self, suites: Dict[str, TestSuite], fail_fast: bool):
        """Run test suites in parallel (non-critical tests only)"""
        critical_suites = {k: v for k, v in suites.items() if v.critical}
        non_critical_suites = {k: v for k, v in suites.items() if not v.critical}
        
        if critical_suites:
            print("🔒 Running critical tests sequentially...")
            await self._run_sequential(critical_suites, fail_fast)
            
            critical_failed = any(not r.passed for r in self.results if r.category in critical_suites)
            if critical_failed and fail_fast:
                print("🛑 Critical tests failed, skipping non-critical tests")
                return
        
        if non_critical_suites:
            print("⚡ Running non-critical tests in parallel...")
            tasks = []
            for category, suite in non_critical_suites.items():
                task = self._execute_test_suite(category, suite)
                tasks.append(task)
            
            parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in parallel_results:
                if isinstance(result, TestResult):
                    self.results.append(result)
                    status = "✅ PASSED" if result.passed else "❌ FAILED"
                    print(f"   {result.name}: {status} ({result.duration:.1f}s)")
    
    async def _execute_test_suite(self, category: str, suite: TestSuite) -> TestResult:
        """Execute a single test suite"""
        start_time = datetime.now()
        
        try:
            original_cwd = os.getcwd()
            if suite.working_dir != ".":
                os.chdir(suite.working_dir)
            
            process = await asyncio.create_subprocess_exec(
                *suite.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=suite.working_dir if suite.working_dir != "." else None
            )
            
            try:
                stdout, _ = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=suite.timeout
                )
                output = stdout.decode('utf-8', errors='replace')
                passed = process.returncode == 0
                error = None if passed else f"Exit code: {process.returncode}"
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                output = f"Test suite timed out after {suite.timeout} seconds"
                passed = False
                error = "Timeout"
            
            os.chdir(original_cwd)
            
        except Exception as e:
            output = f"Failed to execute test suite: {str(e)}"
            passed = False
            error = str(e)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return TestResult(
            category=category,
            name=suite.name,
            passed=passed,
            duration=duration,
            output=output,
            error=error
        )
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        passed_tests = [r for r in self.results if r.passed]
        failed_tests = [r for r in self.results if not r.passed]
        
        report = {
            "summary": {
                "total_suites": len(self.results),
                "passed": len(passed_tests),
                "failed": len(failed_tests),
                "success_rate": len(passed_tests) / len(self.results) * 100 if self.results else 0,
                "total_duration": total_duration,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "results": [
                {
                    "category": r.category,
                    "name": r.name,
                    "passed": r.passed,
                    "duration": r.duration,
                    "error": r.error
                }
                for r in self.results
            ],
            "failed_tests": [
                {
                    "category": r.category,
                    "name": r.name,
                    "error": r.error,
                    "output": r.output[:1000] + "..." if len(r.output) > 1000 else r.output
                }
                for r in failed_tests
            ]
        }
        
        self._print_summary_report(report)
        return report
    
    def _print_summary_report(self, report: Dict[str, Any]):
        """Print formatted summary report"""
        summary = report["summary"]
        
        print("\n" + "=" * 80)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        print(f"🕐 Duration: {summary['total_duration']:.1f} seconds")
        print(f"📋 Total Suites: {summary['total_suites']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        if report["failed_tests"]:
            print(f"\n❌ FAILED TESTS:")
            for failed in report["failed_tests"]:
                print(f"  • {failed['name']}: {failed['error']}")
        
        print(f"\n🎯 Overall Result: {'✅ SUCCESS' if summary['failed'] == 0 else '❌ FAILURE'}")
        print("=" * 80)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Consolidated Test Runner")
    parser.add_argument(
        "--categories", 
        nargs="+", 
        help="Test categories to run",
        choices=["lint", "type_check", "security", "unit", "integration", "api", "performance", "guide_quality", "pdf_generation", "comprehensive"]
    )
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first critical failure")
    parser.add_argument("--parallel", action="store_true", help="Run non-critical tests in parallel")
    parser.add_argument("--output", help="Save report to JSON file")
    
    args = parser.parse_args()
    
    runner = ConsolidatedTestRunner()
    
    try:
        report = await runner.run_all_tests(
            categories=args.categories,
            fail_fast=args.fail_fast,
            parallel=args.parallel
        )
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved to: {args.output}")
        
        # Exit with appropriate code
        sys.exit(0 if report["summary"]["failed"] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
