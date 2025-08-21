"""
Check API key configuration before running tests
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
root_dir = Path(__file__).parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

def check_api_keys():
    """Check which API keys are configured"""
    print("\n🔐 API Key Configuration Check")
    print("=" * 60)
    
    keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Perplexity": os.getenv("PERPLEXITY_API_KEY"),
        "OpenWeather": os.getenv("OPENWEATHER_API_KEY"),
        "Google Maps": os.getenv("GOOGLE_MAPS_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "XAI": os.getenv("XAI_API_KEY"),
        "Sambanova": os.getenv("SAMBANOVA_API_KEY")
    }
    
    required = ["OpenAI"]  # Required for extraction
    optional = ["Perplexity", "OpenWeather", "Google Maps"]  # For enhanced features
    
    print("\nRequired Keys:")
    for key in required:
        value = keys[key]
        if value and len(value) > 5:
            print(f"✅ {key}: Configured (length: {len(value)})")
        else:
            print(f"❌ {key}: Not configured")
    
    print("\nOptional Keys (for enhanced features):")
    for key in optional:
        value = keys[key]
        if value and len(value) > 5:
            print(f"✅ {key}: Configured (length: {len(value)})")
        else:
            print(f"⚠️  {key}: Not configured (some features may be limited)")
    
    print("\nAlternative LLM Providers:")
    for key in ["Anthropic", "XAI", "Sambanova"]:
        value = keys[key]
        if value and len(value) > 5:
            print(f"✅ {key}: Available (length: {len(value)})")
        else:
            print(f"   {key}: Not configured")
    
    # Check if we can run basic extraction
    can_extract = bool(keys["OpenAI"])
    
    # Check if we can generate full guides
    can_generate_guide = bool(keys["Perplexity"])
    
    print("\n" + "=" * 60)
    print("📊 Capabilities:")
    print(f"  • Basic extraction: {'✅ Yes' if can_extract else '❌ No'}")
    print(f"  • Enhanced guides: {'✅ Yes' if can_generate_guide else '⚠️  Limited (no Perplexity API)'}")
    
    if not can_generate_guide:
        print("\n⚠️  Note: Without Perplexity API, guide generation will be limited.")
        print("    The system will generate basic guides without real-time data.")
    
    return can_extract, can_generate_guide

if __name__ == "__main__":
    check_api_keys()