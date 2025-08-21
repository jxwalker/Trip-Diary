#!/usr/bin/env python3
"""
Master Test Runner for Trip Diary
Comprehensive CLI-driven test system with menu interface
"""
import asyncio
import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class MasterTestRunner:
    """Master test runner with comprehensive menu system"""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.test_results = {}
        
        # Discover available tests
        self.available_tests = self._discover_tests()
    
    def print(self, *args, **kwargs):
        """Print with rich if available, otherwise standard print"""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)
    
    def _discover_tests(self) -> Dict[str, Dict[str, Any]]:
        """Discover all available test files and scripts"""
        
        tests = {
            "prd_validation": {
                "name": "PRD Requirements Validation",
                "description": "Test against Product Requirements Document",
                "script": "run_prd_tests.py",
                "category": "validation",
                "priority": 1
            },
            "comprehensive_tests": {
                "name": "Comprehensive Integration Tests",
                "description": "Full system integration testing",
                "script": "run_comprehensive_tests.py",
                "category": "integration",
                "priority": 2
            },
            "unit_tests": {
                "name": "Unit Tests",
                "description": "Individual component tests",
                "script": "pytest tests/test_*.py -v",
                "category": "unit",
                "priority": 3
            },
            "api_tests": {
                "name": "API Integration Tests",
                "description": "API endpoint testing",
                "script": "run_tests.py --categories api",
                "category": "api",
                "priority": 4
            },
            "service_tests": {
                "name": "Service Tests",
                "description": "Service layer testing",
                "script": "pytest tests/test_*service*.py -v",
                "category": "services",
                "priority": 5
            },
            "workflow_tests": {
                "name": "Workflow Tests",
                "description": "End-to-end workflow testing",
                "script": "run_workflow_test.py",
                "category": "workflow",
                "priority": 6
            },
            "performance_tests": {
                "name": "Performance Tests",
                "description": "Performance and benchmarking",
                "script": "pytest tests/integration/performance_benchmark.py -v",
                "category": "performance",
                "priority": 7
            }
        }
        
        # Filter tests that actually exist
        existing_tests = {}
        for test_id, test_info in tests.items():
            script_path = Path(test_info["script"].split()[0])
            if script_path.exists() or test_info["script"].startswith("pytest"):
                existing_tests[test_id] = test_info
        
        return existing_tests
    
    def display_main_menu(self):
        """Display main test menu"""
        
        if self.console:
            table = Table(title="🧪 Trip Diary Master Test Runner", box=box.ROUNDED)
            table.add_column("Option", style="cyan", no_wrap=True)
            table.add_column("Test Suite", style="magenta")
            table.add_column("Description", style="green")
            table.add_column("Category", style="yellow")
            
            # Add test options
            for i, (test_id, test_info) in enumerate(self.available_tests.items(), 1):
                table.add_row(
                    str(i),
                    test_info["name"],
                    test_info["description"],
                    test_info["category"].title()
                )
            
            # Add special options
            table.add_row("A", "Run All Tests", "Execute all available tests", "All")
            table.add_row("R", "View Results", "Show previous test results", "Results")
            table.add_row("C", "Clean Results", "Clear test result files", "Cleanup")
            table.add_row("0", "Exit", "Exit test runner", "Exit")
            
            self.console.print(table)
        
        else:
            print("\n🧪 Trip Diary Master Test Runner")
            print("=" * 60)
            
            for i, (test_id, test_info) in enumerate(self.available_tests.items(), 1):
                print(f"{i}. {test_info['name']} - {test_info['description']}")
            
            print("A. Run All Tests - Execute all available tests")
            print("R. View Results - Show previous test results")
            print("C. Clean Results - Clear test result files")
            print("0. Exit - Exit test runner")
    
    async def run_test_suite(self, test_id: str) -> Dict[str, Any]:
        """Run a specific test suite"""
        
        if test_id not in self.available_tests:
            return {"error": f"Unknown test suite: {test_id}"}
        
        test_info = self.available_tests[test_id]
        
        self.print(f"\n🚀 Running {test_info['name']}")
        self.print(f"📝 {test_info['description']}")
        self.print("-" * 60)
        
        start_time = datetime.now()
        
        try:
            # Prepare command
            if test_info["script"].startswith("pytest"):
                cmd = test_info["script"].split()
            else:
                cmd = ["python3", test_info["script"]]
            
            # Run the test
            if RICH_AVAILABLE:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task(f"Running {test_info['name']}...", total=None)
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=600  # 10 minute timeout
                    )
            else:
                print(f"Running {test_info['name']}...")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600
                )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Process results
            test_result = {
                "test_id": test_id,
                "name": test_info["name"],
                "category": test_info["category"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": duration,
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Display results
            if test_result["success"]:
                self.print(f"✅ {test_info['name']} completed successfully")
                self.print(f"⏱️  Duration: {duration:.2f} seconds")
            else:
                self.print(f"❌ {test_info['name']} failed")
                self.print(f"⏱️  Duration: {duration:.2f} seconds")
                self.print(f"🔍 Error: {result.stderr[:200]}...")
            
            # Save results
            self.test_results[test_id] = test_result
            self._save_test_results()
            
            return test_result
        
        except subprocess.TimeoutExpired:
            self.print(f"⏰ {test_info['name']} timed out after 10 minutes")
            return {"error": "Test timed out"}
        
        except Exception as e:
            self.print(f"❌ Error running {test_info['name']}: {e}")
            return {"error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all available test suites"""
        
        self.print("\n🚀 Running All Test Suites")
        self.print("=" * 60)
        
        all_results = {
            "start_time": datetime.now().isoformat(),
            "test_results": {},
            "summary": {
                "total_tests": len(self.available_tests),
                "successful_tests": 0,
                "failed_tests": 0,
                "total_duration": 0
            }
        }
        
        # Run tests in priority order
        sorted_tests = sorted(
            self.available_tests.items(),
            key=lambda x: x[1]["priority"]
        )
        
        for test_id, test_info in sorted_tests:
            result = await self.run_test_suite(test_id)
            all_results["test_results"][test_id] = result
            
            if result.get("success", False):
                all_results["summary"]["successful_tests"] += 1
            else:
                all_results["summary"]["failed_tests"] += 1
            
            if "duration" in result:
                all_results["summary"]["total_duration"] += result["duration"]
        
        all_results["end_time"] = datetime.now().isoformat()
        
        # Display summary
        self._display_test_summary(all_results)
        
        return all_results
    
    def _display_test_summary(self, results: Dict[str, Any]):
        """Display test summary"""
        
        summary = results["summary"]
        
        if self.console:
            table = Table(title="🎯 Test Execution Summary", box=box.ROUNDED)
            table.add_column("Test Suite", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Duration", style="green")
            
            for test_id, result in results["test_results"].items():
                test_name = self.available_tests[test_id]["name"]
                status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
                duration = f"{result.get('duration', 0):.2f}s"
                
                table.add_row(test_name, status, duration)
            
            self.console.print(table)
            
            # Overall summary
            success_rate = (summary["successful_tests"] / summary["total_tests"]) * 100
            
            summary_panel = Panel(
                f"Total Tests: {summary['total_tests']}\n"
                f"Successful: {summary['successful_tests']}\n"
                f"Failed: {summary['failed_tests']}\n"
                f"Success Rate: {success_rate:.1f}%\n"
                f"Total Duration: {summary['total_duration']:.2f}s",
                title="Overall Results",
                border_style="green" if success_rate >= 80 else "yellow" if success_rate >= 60 else "red"
            )
            self.console.print(summary_panel)
        
        else:
            print("\n🎯 Test Execution Summary")
            print("=" * 40)
            
            for test_id, result in results["test_results"].items():
                test_name = self.available_tests[test_id]["name"]
                status = "PASSED" if result.get("success", False) else "FAILED"
                duration = f"{result.get('duration', 0):.2f}s"
                print(f"{test_name}: {status} ({duration})")
            
            success_rate = (summary["successful_tests"] / summary["total_tests"]) * 100
            print(f"\nOverall: {summary['successful_tests']}/{summary['total_tests']} ({success_rate:.1f}%)")
    
    def _save_test_results(self):
        """Save test results to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
    
    def view_previous_results(self):
        """View previous test results"""
        
        # Find recent result files
        result_files = list(Path(".").glob("*test_results_*.json"))
        result_files.extend(list(Path(".").glob("prd_test_results_*.json")))
        result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not result_files:
            self.print("📁 No previous test results found")
            return
        
        self.print("📊 Recent Test Results:")
        for i, file_path in enumerate(result_files[:5], 1):
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            self.print(f"{i}. {file_path.name} ({file_time.strftime('%Y-%m-%d %H:%M:%S')})")
        
        if RICH_AVAILABLE:
            choice = Prompt.ask("Select file to view (1-5)", choices=[str(i) for i in range(1, min(6, len(result_files)+1))])
            selected_file = result_files[int(choice)-1]
        else:
            choice = input("Select file to view (1-5): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(result_files):
                selected_file = result_files[int(choice)-1]
            else:
                print("Invalid choice")
                return
        
        # Display selected results
        try:
            with open(selected_file, 'r') as f:
                results = json.load(f)
            
            self.print(f"\n📄 Results from {selected_file.name}")
            self.print(json.dumps(results, indent=2))
        
        except Exception as e:
            self.print(f"❌ Error reading results: {e}")
    
    def clean_results(self):
        """Clean up old result files"""
        
        result_files = list(Path(".").glob("*test_results_*.json"))
        result_files.extend(list(Path(".").glob("prd_test_results_*.json")))
        
        if not result_files:
            self.print("📁 No result files to clean")
            return
        
        if RICH_AVAILABLE:
            confirm = Confirm.ask(f"Delete {len(result_files)} result files?")
        else:
            confirm = input(f"Delete {len(result_files)} result files? (y/N): ").lower().startswith('y')
        
        if confirm:
            for file_path in result_files:
                file_path.unlink()
            self.print(f"🗑️  Deleted {len(result_files)} result files")
        else:
            self.print("❌ Cleanup cancelled")
    
    async def run_interactive_menu(self):
        """Run interactive menu system"""
        
        while True:
            self.display_main_menu()
            
            if RICH_AVAILABLE:
                choices = [str(i) for i in range(1, len(self.available_tests)+1)] + ["A", "R", "C", "0"]
                choice = Prompt.ask("\nSelect an option", choices=choices).upper()
            else:
                choice = input("\nSelect an option: ").strip().upper()
            
            if choice == "0":
                self.print("👋 Goodbye!")
                break
            
            elif choice == "A":
                await self.run_all_tests()
            
            elif choice == "R":
                self.view_previous_results()
            
            elif choice == "C":
                self.clean_results()
            
            elif choice.isdigit():
                test_index = int(choice) - 1
                test_ids = list(self.available_tests.keys())
                
                if 0 <= test_index < len(test_ids):
                    test_id = test_ids[test_index]
                    await self.run_test_suite(test_id)
                else:
                    self.print("❌ Invalid choice")
            
            else:
                self.print("❌ Invalid choice")
            
            if choice != "0":
                input("\nPress Enter to continue...")


async def main():
    """Main entry point"""
    
    runner = MasterTestRunner()
    
    try:
        await runner.run_interactive_menu()
    
    except KeyboardInterrupt:
        runner.print("\n⚠️  Test runner interrupted")
    
    except Exception as e:
        runner.print(f"\n❌ Test runner failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
