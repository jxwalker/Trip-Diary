#!/usr/bin/env python3
"""
Test runner for weather service tests
"""

import os
import sys
import subprocess
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")


def run_unit_tests():
    """Run unit tests"""
    print_header("Running Unit Tests")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "unit/",
        "-v",
        "--tb=short",
        "-m", "not integration"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0


def run_integration_tests():
    """Run integration tests (if API key is available)"""
    print_header("Running Integration Tests")
    
    if not os.getenv("OPENWEATHER_API_KEY"):
        print(f"{YELLOW}⚠️  OPENWEATHER_API_KEY not set. Skipping integration tests.{RESET}")
        print(f"   To run integration tests:")
        print(f"   1. Get a free API key at https://openweathermap.org/api")
        print(f"   2. Set OPENWEATHER_API_KEY environment variable")
        return True
    
    cmd = [
        sys.executable, "-m", "pytest",
        "integration/",
        "-v",
        "--tb=short",
        "-m", "integration"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0


def check_weather_api():
    """Quick check if weather API is working"""
    print_header("Checking Weather API Configuration")
    
    import asyncio
    sys.path.append(str(Path(__file__).parent.parent))
    from services.weather_service import WeatherService
    
    async def test_api():
        service = WeatherService()
        
        if not service.api_key:
            print(f"{YELLOW}⚠️  No API key configured{RESET}")
            return False
        
        print(f"{GREEN}✓ API key found{RESET}")
        
        # Try a simple API call
        from datetime import datetime, timedelta
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        print("Testing API call to OpenWeatherMap...")
        result = await service.get_weather_forecast("London", start_date, end_date)
        
        if "error" in result and result["error"]:
            print(f"{RED}✗ API call failed: {result['error']}{RESET}")
            return False
        elif result.get("daily_forecasts"):
            print(f"{GREEN}✓ API call successful{RESET}")
            print(f"  Retrieved {len(result['daily_forecasts'])} day(s) of forecast")
            return True
        else:
            print(f"{YELLOW}⚠️  API returned no data{RESET}")
            return False
    
    return asyncio.run(test_api())


def main():
    """Main test runner"""
    print(f"{BOLD}Weather Service Test Suite{RESET}")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print(f"{RED}Python 3.7+ required{RESET}")
        sys.exit(1)
    
    # Install pytest if needed
    try:
        import pytest
    except ImportError:
        print(f"{YELLOW}Installing pytest...{RESET}")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"])
    
    # Check weather API
    api_ok = check_weather_api()
    
    # Run tests
    unit_passed = run_unit_tests()
    integration_passed = run_integration_tests()
    
    # Summary
    print_header("Test Summary")
    
    if unit_passed:
        print(f"{GREEN}✓ Unit tests passed{RESET}")
    else:
        print(f"{RED}✗ Unit tests failed{RESET}")
    
    if integration_passed:
        if os.getenv("OPENWEATHER_API_KEY"):
            print(f"{GREEN}✓ Integration tests passed{RESET}")
        else:
            print(f"{YELLOW}○ Integration tests skipped (no API key){RESET}")
    else:
        print(f"{RED}✗ Integration tests failed{RESET}")
    
    if api_ok:
        print(f"{GREEN}✓ Weather API is working{RESET}")
    else:
        print(f"{YELLOW}○ Weather API not configured or not working{RESET}")
    
    # Exit code
    if unit_passed and integration_passed:
        print(f"\n{GREEN}{BOLD}All tests passed! 🎉{RESET}")
        sys.exit(0)
    else:
        print(f"\n{RED}{BOLD}Some tests failed{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()