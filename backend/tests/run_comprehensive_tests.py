#!/usr/bin/env python3
"""
Comprehensive Test Runner for Google Places Integration
Runs all tests and provides clear status on what's working and what needs setup
NO MOCKS, NO FALLBACKS, NO SKIPPED TESTS - Real API testing only
"""
import subprocess
import sys
import os
from pathlib import Path

# Add the backend src directory to Python path
backend_dir = Path(__file__).parent.parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

def run_test_suite(test_file, description, required_apis=False):
    """Run a test suite and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    if required_apis:
        print("⚠️  This test requires Google APIs to be enabled")
    else:
        print("✅ This test works without enabled APIs")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            f"tests/integration/{test_file}", 
            "-v", "-s"
        ], capture_output=True, text=True, cwd=backend_dir)
        
        print(f"\n📊 Test Results:")
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ ALL TESTS PASSED")
        else:
            print("❌ SOME TESTS FAILED")
        
        # Print stdout (test output)
        if result.stdout:
            print(f"\n📝 Test Output:")
            print(result.stdout)
        
        # Print stderr (errors) if any
        if result.stderr:
            print(f"\n🚨 Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def check_api_key():
    """Check if API key is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key:
        print(f"✅ API Key configured: {api_key[:10]}...")
        return True
    else:
        print("❌ API Key not configured")
        return False

def main():
    """Run comprehensive test suite"""
    print("🚀 COMPREHENSIVE GOOGLE PLACES INTEGRATION TEST SUITE")
    print("=" * 60)
    print("Testing Google Places API integration with NO MOCKS, NO FALLBACKS")
    print("Real API testing only - ensuring production readiness")
    
    # Check API key
    print(f"\n🔑 API Key Status:")
    api_key_ok = check_api_key()
    
    if not api_key_ok:
        print("\n❌ Cannot proceed without API key. Please add GOOGLE_MAPS_API_KEY to .env file")
        return False
    
    # Test suites to run
    test_suites = [
        {
            "file": "test_google_places_configuration.py",
            "description": "Configuration and Environment Tests",
            "required_apis": False,
            "purpose": "Verify service configuration, API key format, and basic setup"
        },
        {
            "file": "test_google_places_readiness.py", 
            "description": "Service Readiness and Implementation Tests",
            "required_apis": False,
            "purpose": "Verify service implementation, data structures, and business logic"
        },
        {
            "file": "test_google_api_enablement.py",
            "description": "API Enablement Detection Tests",
            "required_apis": True,
            "purpose": "Detect which Google APIs are enabled and provide setup guidance"
        },
        {
            "file": "test_enhanced_google_places_service.py",
            "description": "Full Integration Tests with Real API Calls",
            "required_apis": True,
            "purpose": "Test complete functionality with real Google Places API calls"
        }
    ]
    
    results = {}
    
    # Run each test suite
    for suite in test_suites:
        print(f"\n📋 Purpose: {suite['purpose']}")
        success = run_test_suite(
            suite["file"], 
            suite["description"], 
            suite["required_apis"]
        )
        results[suite["description"]] = success
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*60}")
    
    passed_tests = []
    failed_tests = []
    
    for test_name, success in results.items():
        if success:
            passed_tests.append(test_name)
            print(f"✅ {test_name}")
        else:
            failed_tests.append(test_name)
            print(f"❌ {test_name}")
    
    print(f"\n📈 Results: {len(passed_tests)} passed, {len(failed_tests)} failed")
    
    # Provide guidance based on results
    if len(failed_tests) == 0:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Google Places integration is fully functional")
        print("✅ Ready for production use")
    else:
        print(f"\n⚠️  Some tests failed - this is expected if Google APIs are not enabled")
        
        # Check if it's just API enablement issues
        config_and_readiness_passed = (
            "Configuration and Environment Tests" in passed_tests and
            "Service Readiness and Implementation Tests" in passed_tests
        )
        
        if config_and_readiness_passed:
            print("\n✅ Good news: Core implementation is solid!")
            print("✅ Configuration tests passed")
            print("✅ Service readiness tests passed")
            print("\n🔧 Next steps:")
            print("1. Enable Google APIs in Google Cloud Console")
            print("2. See docs/GOOGLE_API_SETUP_REQUIRED.md for detailed instructions")
            print("3. Re-run tests after enabling APIs")
        else:
            print("\n❌ Core implementation issues detected")
            print("🔧 Need to fix implementation before proceeding")
    
    # Specific guidance
    print(f"\n📚 Documentation:")
    print("- Setup guide: docs/GOOGLE_API_SETUP_REQUIRED.md")
    print("- API costs: docs/google-places-setup.md")
    
    print(f"\n🧪 Test Philosophy:")
    print("- NO MOCKS: All tests use real APIs when available")
    print("- NO FALLBACKS: Tests fail clearly when APIs aren't enabled")
    print("- NO SKIPPED TESTS: Every test provides actionable feedback")
    print("- PRODUCTION READY: Tests ensure real-world reliability")
    
    return len(failed_tests) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
