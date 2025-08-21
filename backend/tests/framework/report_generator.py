"""
HTML Report Generator
Beautiful, interactive test reports with charts and detailed analysis
"""
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import base64

from .test_runner import TestReport, TestResult, TestStatus, TestCategory


class HTMLReportGenerator:
    """Generate beautiful HTML test reports"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
    
    async def generate_report(self, report: TestReport, output_path: str) -> None:
        """Generate comprehensive HTML report"""
        html_content = self._generate_html(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html(self, report: TestReport) -> str:
        """Generate complete HTML report"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TripCraft AI - Test Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .card-shadow {{ box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
        .status-passed {{ color: #10b981; }}
        .status-failed {{ color: #ef4444; }}
        .status-error {{ color: #f59e0b; }}
        .status-skipped {{ color: #6b7280; }}
        .animate-fade-in {{ animation: fadeIn 0.5s ease-in; }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="gradient-bg text-white py-8">
        <div class="container mx-auto px-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-4xl font-bold mb-2">
                        <i class="fas fa-flask mr-3"></i>TripCraft AI Test Report
                    </h1>
                    <p class="text-xl opacity-90">Comprehensive Integration Test Results</p>
                </div>
                <div class="text-right">
                    <div class="text-2xl font-bold">{report.success_rate:.1f}%</div>
                    <div class="text-sm opacity-75">Success Rate</div>
                </div>
            </div>
        </div>
    </header>

    <!-- Summary Cards -->
    <section class="py-8">
        <div class="container mx-auto px-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
                {self._generate_summary_cards(report)}
            </div>
        </div>
    </section>

    <!-- Charts Section -->
    <section class="py-8">
        <div class="container mx-auto px-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <div class="bg-white rounded-lg card-shadow p-6">
                    <h3 class="text-xl font-semibold mb-4">
                        <i class="fas fa-chart-pie mr-2"></i>Test Results Distribution
                    </h3>
                    <canvas id="resultsChart" width="400" height="200"></canvas>
                </div>
                <div class="bg-white rounded-lg card-shadow p-6">
                    <h3 class="text-xl font-semibold mb-4">
                        <i class="fas fa-chart-bar mr-2"></i>Tests by Category
                    </h3>
                    <canvas id="categoryChart" width="400" height="200"></canvas>
                </div>
            </div>
        </div>
    </section>

    <!-- Test Details -->
    <section class="py-8">
        <div class="container mx-auto px-6">
            <div class="bg-white rounded-lg card-shadow p-6">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-2xl font-semibold">
                        <i class="fas fa-list-check mr-2"></i>Test Details
                    </h3>
                    <div class="flex space-x-2">
                        <button onclick="filterTests('all')" class="filter-btn bg-blue-500 text-white px-4 py-2 rounded">All</button>
                        <button onclick="filterTests('passed')" class="filter-btn bg-green-500 text-white px-4 py-2 rounded">Passed</button>
                        <button onclick="filterTests('failed')" class="filter-btn bg-red-500 text-white px-4 py-2 rounded">Failed</button>
                        <button onclick="filterTests('error')" class="filter-btn bg-yellow-500 text-white px-4 py-2 rounded">Errors</button>
                    </div>
                </div>
                
                <div class="overflow-x-auto">
                    <table class="w-full table-auto">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-4 py-3 text-left">Status</th>
                                <th class="px-4 py-3 text-left">Test Name</th>
                                <th class="px-4 py-3 text-left">Category</th>
                                <th class="px-4 py-3 text-left">Duration</th>
                                <th class="px-4 py-3 text-left">Tags</th>
                                <th class="px-4 py-3 text-left">Details</th>
                            </tr>
                        </thead>
                        <tbody id="testTableBody">
                            {self._generate_test_rows(report.results)}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </section>

    <!-- Performance Metrics -->
    {self._generate_performance_section(report)}

    <!-- Environment Info -->
    <section class="py-8">
        <div class="container mx-auto px-6">
            <div class="bg-white rounded-lg card-shadow p-6">
                <h3 class="text-xl font-semibold mb-4">
                    <i class="fas fa-server mr-2"></i>Environment Information
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div class="bg-gray-50 p-4 rounded">
                        <div class="text-sm text-gray-600">Environment</div>
                        <div class="font-semibold">{report.environment}</div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded">
                        <div class="text-sm text-gray-600">API Base URL</div>
                        <div class="font-semibold">{report.api_base_url}</div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded">
                        <div class="text-sm text-gray-600">Test Duration</div>
                        <div class="font-semibold">{report.duration_seconds:.2f}s</div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded">
                        <div class="text-sm text-gray-600">Start Time</div>
                        <div class="font-semibold">{report.start_time.strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded">
                        <div class="text-sm text-gray-600">End Time</div>
                        <div class="font-semibold">{report.end_time.strftime('%Y-%m-%d %H:%M:%S') if report.end_time else 'N/A'}</div>
                    </div>
                    <div class="bg-gray-50 p-4 rounded">
                        <div class="text-sm text-gray-600">Report Generated</div>
                        <div class="font-semibold">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-12">
        <div class="container mx-auto px-6 text-center">
            <p>&copy; 2024 TripCraft AI - Automated Test Report</p>
            <p class="text-sm text-gray-400 mt-2">Generated by Advanced Test Framework</p>
        </div>
    </footer>

    <script>
        {self._generate_javascript(report)}
    </script>
</body>
</html>
        """
    
    def _generate_summary_cards(self, report: TestReport) -> str:
        """Generate summary cards HTML"""
        cards = [
            {
                "title": "Total Tests",
                "value": str(report.total_tests),
                "icon": "fas fa-vial",
                "color": "blue"
            },
            {
                "title": "Passed",
                "value": str(report.passed_tests),
                "icon": "fas fa-check-circle",
                "color": "green"
            },
            {
                "title": "Failed",
                "value": str(report.failed_tests),
                "icon": "fas fa-times-circle",
                "color": "red"
            },
            {
                "title": "Errors",
                "value": str(report.error_tests),
                "icon": "fas fa-exclamation-triangle",
                "color": "yellow"
            },
            {
                "title": "Duration",
                "value": f"{report.duration_seconds:.2f}s",
                "icon": "fas fa-clock",
                "color": "purple"
            }
        ]
        
        html = ""
        for card in cards:
            html += f"""
            <div class="bg-white rounded-lg card-shadow p-6 animate-fade-in">
                <div class="flex items-center">
                    <div class="text-{card['color']}-500 text-3xl mr-4">
                        <i class="{card['icon']}"></i>
                    </div>
                    <div>
                        <div class="text-2xl font-bold text-gray-800">{card['value']}</div>
                        <div class="text-sm text-gray-600">{card['title']}</div>
                    </div>
                </div>
            </div>
            """
        
        return html
    
    def _generate_test_rows(self, results: List[TestResult]) -> str:
        """Generate test table rows"""
        html = ""
        
        for result in results:
            status_icon = self._get_status_icon(result.status)
            status_class = f"status-{result.status.value}"
            
            tags_html = " ".join([
                f'<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">{tag}</span>'
                for tag in result.tags
            ])
            
            details_btn = ""
            if result.error_message or result.response_data:
                details_btn = f'<button onclick="showDetails(\'{result.name}\')" class="text-blue-500 hover:text-blue-700"><i class="fas fa-info-circle"></i></button>'
            
            html += f"""
            <tr class="test-row border-b hover:bg-gray-50" data-status="{result.status.value}">
                <td class="px-4 py-3">
                    <span class="{status_class} text-lg">{status_icon}</span>
                </td>
                <td class="px-4 py-3 font-medium">{result.name}</td>
                <td class="px-4 py-3">
                    <span class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">{result.category.value}</span>
                </td>
                <td class="px-4 py-3">{result.duration_ms:.2f}ms</td>
                <td class="px-4 py-3">{tags_html}</td>
                <td class="px-4 py-3">{details_btn}</td>
            </tr>
            """
        
        return html
    
    def _generate_performance_section(self, report: TestReport) -> str:
        """Generate performance metrics section"""
        # Calculate performance metrics
        durations = [r.duration_ms for r in report.results]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        # Find slowest tests
        slowest_tests = sorted(report.results, key=lambda x: x.duration_ms, reverse=True)[:5]
        
        return f"""
        <section class="py-8">
            <div class="container mx-auto px-6">
                <div class="bg-white rounded-lg card-shadow p-6">
                    <h3 class="text-xl font-semibold mb-6">
                        <i class="fas fa-tachometer-alt mr-2"></i>Performance Metrics
                    </h3>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <div class="bg-blue-50 p-4 rounded">
                            <div class="text-sm text-blue-600">Average Duration</div>
                            <div class="text-2xl font-bold text-blue-800">{avg_duration:.2f}ms</div>
                        </div>
                        <div class="bg-green-50 p-4 rounded">
                            <div class="text-sm text-green-600">Fastest Test</div>
                            <div class="text-2xl font-bold text-green-800">{min_duration:.2f}ms</div>
                        </div>
                        <div class="bg-red-50 p-4 rounded">
                            <div class="text-sm text-red-600">Slowest Test</div>
                            <div class="text-2xl font-bold text-red-800">{max_duration:.2f}ms</div>
                        </div>
                    </div>
                    
                    <div>
                        <h4 class="text-lg font-semibold mb-4">Slowest Tests</h4>
                        <div class="space-y-2">
                            {self._generate_slowest_tests(slowest_tests)}
                        </div>
                    </div>
                </div>
            </div>
        </section>
        """
    
    def _generate_slowest_tests(self, slowest_tests: List[TestResult]) -> str:
        """Generate slowest tests list"""
        html = ""
        for test in slowest_tests:
            html += f"""
            <div class="flex justify-between items-center bg-gray-50 p-3 rounded">
                <span class="font-medium">{test.name}</span>
                <span class="text-gray-600">{test.duration_ms:.2f}ms</span>
            </div>
            """
        return html
    
    def _get_status_icon(self, status: TestStatus) -> str:
        """Get icon for test status"""
        icons = {
            TestStatus.PASSED: "✅",
            TestStatus.FAILED: "❌",
            TestStatus.ERROR: "⚠️",
            TestStatus.SKIPPED: "⏭️",
            TestStatus.PENDING: "⏳",
            TestStatus.RUNNING: "🔄"
        }
        return icons.get(status, "❓")
    
    def _generate_javascript(self, report: TestReport) -> str:
        """Generate JavaScript for interactive features"""
        # Prepare data for charts
        results_data = {
            "passed": report.passed_tests,
            "failed": report.failed_tests,
            "error": report.error_tests,
            "skipped": report.skipped_tests
        }
        
        # Category data
        category_counts = {}
        for result in report.results:
            category = result.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return f"""
        // Chart.js configurations
        const resultsCtx = document.getElementById('resultsChart').getContext('2d');
        new Chart(resultsCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Passed', 'Failed', 'Errors', 'Skipped'],
                datasets: [{{
                    data: [{results_data['passed']}, {results_data['failed']}, {results_data['error']}, {results_data['skipped']}],
                    backgroundColor: ['#10b981', '#ef4444', '#f59e0b', '#6b7280'],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {{
            type: 'bar',
            data: {{
                labels: {list(category_counts.keys())},
                datasets: [{{
                    label: 'Tests',
                    data: {list(category_counts.values())},
                    backgroundColor: '#667eea',
                    borderColor: '#764ba2',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Filter functionality
        function filterTests(status) {{
            const rows = document.querySelectorAll('.test-row');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // Update button styles
            buttons.forEach(btn => {{
                btn.classList.remove('bg-blue-600');
                btn.classList.add('bg-blue-500');
            }});
            event.target.classList.remove('bg-blue-500');
            event.target.classList.add('bg-blue-600');
            
            // Filter rows
            rows.forEach(row => {{
                if (status === 'all' || row.dataset.status === status) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}
        
        // Test details modal (simplified)
        function showDetails(testName) {{
            alert('Test details for: ' + testName + '\\n\\nDetailed modal implementation would go here.');
        }}
        
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
        """
