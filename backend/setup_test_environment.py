#!/usr/bin/env python3
"""
Setup Test Environment
Ensures all dependencies and configurations are ready for testing
"""
import subprocess
import sys
import os
from pathlib import Path


def install_dependencies():
    """Install required dependencies for testing"""
    
    print("📦 Installing test dependencies...")
    
    # Core dependencies for testing
    test_dependencies = [
        "openai>=1.3.0",
        "requests>=2.31.0",
        "reportlab>=4.0.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.2.0",
        "httpx>=0.25.0"
    ]
    
    try:
        for dep in test_dependencies:
            print(f"   Installing {dep}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Failed to install {dep}: {result.stderr}")
                return False
        
        print("✅ All test dependencies installed")
        return True
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def create_env_file():
    """Create .env file template if it doesn't exist"""
    
    print("🔧 Setting up environment configuration...")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    env_template = """# Trip Diary Environment Configuration

# OpenAI API Key (required for guide evaluation)
OPENAI_API_KEY=your_openai_api_key_here

# Perplexity API Key (required for guide generation)
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Optional: Other LLM API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
XAI_API_KEY=your_xai_key_here

# Database Configuration (optional for testing)
DATABASE_URL=sqlite:///trip_diary.db

# Performance Settings
PERPLEXITY_TIMEOUT=20
PERPLEXITY_MODEL=sonar
PERPLEXITY_MAX_TOKENS=3000

# Logging Level
LOG_LEVEL=INFO
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_template)
        
        print("✅ Created .env template file")
        print("⚠️  Please edit .env and add your API keys before testing")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def create_directories():
    """Create necessary directories for testing"""
    
    print("📁 Creating test directories...")
    
    directories = [
        "uploads",
        "tests/integration",
        "logs",
        "reports"
    ]
    
    try:
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        print("✅ Test directories created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return False


def check_api_keys():
    """Check if API keys are configured"""
    
    print("🔑 Checking API key configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_keys = {
        "OPENAI_API_KEY": "OpenAI (required for guide evaluation)",
        "PERPLEXITY_API_KEY": "Perplexity (required for guide generation)"
    }
    
    missing_keys = []
    
    for key, description in required_keys.items():
        value = os.getenv(key)
        if not value or value == f"your_{key.lower()}_here":
            missing_keys.append(f"{key} ({description})")
        else:
            print(f"✅ {key} configured")
    
    if missing_keys:
        print("⚠️  Missing or placeholder API keys:")
        for key in missing_keys:
            print(f"   • {key}")
        print("\n💡 Update your .env file with real API keys before testing")
        return False
    
    print("✅ All required API keys configured")
    return True


def verify_backend_files():
    """Verify that required backend files exist"""
    
    print("📋 Verifying backend files...")
    
    required_files = [
        "main.py",
        "src/api/app_factory.py",
        "src/services/optimized_guide_service.py",
        "src/services/optimized_perplexity_service.py",
        "tests/integration/guide_evaluation_module.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        return False
    
    print("✅ All required backend files present")
    return True


def run_quick_test():
    """Run a quick test to verify setup"""
    
    print("🧪 Running quick setup verification...")
    
    try:
        # Test imports
        import openai
        import requests
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Test OpenAI client creation
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("your_"):
            client = openai.OpenAI(api_key=api_key)
            print("✅ OpenAI client can be created")
        else:
            print("⚠️  OpenAI client not testable (API key not set)")
        
        # Test basic HTTP request
        response = requests.get("https://httpbin.org/status/200", timeout=5)
        if response.status_code == 200:
            print("✅ HTTP requests working")
        
        print("✅ Quick verification passed")
        return True
        
    except Exception as e:
        print(f"❌ Quick verification failed: {e}")
        return False


def main():
    """Main setup function"""
    
    print("🚀 TRIP DIARY TEST ENVIRONMENT SETUP")
    print("=" * 50)
    
    success = True
    
    # Step 1: Install dependencies
    if not install_dependencies():
        success = False
    
    # Step 2: Create .env file
    if not create_env_file():
        success = False
    
    # Step 3: Create directories
    if not create_directories():
        success = False
    
    # Step 4: Verify backend files
    if not verify_backend_files():
        success = False
    
    # Step 5: Check API keys
    api_keys_ok = check_api_keys()
    
    # Step 6: Run quick test
    if api_keys_ok:
        if not run_quick_test():
            success = False
    
    print("\n" + "=" * 50)
    
    if success and api_keys_ok:
        print("🎉 TEST ENVIRONMENT SETUP COMPLETE!")
        print("✅ Ready to run workflow tests")
        print("\n💡 Next steps:")
        print("   1. python run_workflow_test.py")
        print("   2. Check the generated reports")
        return 0
    elif success:
        print("⚠️  SETUP MOSTLY COMPLETE")
        print("🔑 Please configure API keys in .env file")
        print("\n💡 Next steps:")
        print("   1. Edit .env file with your API keys")
        print("   2. python run_workflow_test.py")
        return 0
    else:
        print("❌ SETUP FAILED")
        print("Fix the errors above before running tests")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
