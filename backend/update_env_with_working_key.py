#!/usr/bin/env python3
"""
Update .env file with working Google Maps API key
"""
import sys
import os
from pathlib import Path

def update_env_file(new_api_key):
    """Update the .env file with the new API key"""
    
    # Find the .env file
    env_file = Path(__file__).parent.parent.parent / ".env"
    
    if not env_file.exists():
        print(f"❌ .env file not found at {env_file}")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update the GOOGLE_MAPS_API_KEY line
    updated = False
    new_lines = []
    
    for line in lines:
        if line.startswith('GOOGLE_MAPS_API_KEY='):
            old_key = line.strip().split('=', 1)[1] if '=' in line else ''
            new_lines.append(f'GOOGLE_MAPS_API_KEY={new_api_key}\n')
            print(f"✅ Updated GOOGLE_MAPS_API_KEY")
            print(f"   Old: {old_key[:15]}...{old_key[-4:] if len(old_key) >= 4 else old_key}")
            print(f"   New: {new_api_key[:15]}...{new_api_key[-4:]}")
            updated = True
        else:
            new_lines.append(line)
    
    if not updated:
        # Add the key if it doesn't exist
        new_lines.append(f'\nGOOGLE_MAPS_API_KEY={new_api_key}\n')
        print(f"✅ Added GOOGLE_MAPS_API_KEY to .env file")
        print(f"   Key: {new_api_key[:15]}...{new_api_key[-4:]}")
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ .env file updated successfully")
    return True

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python update_env_with_working_key.py <API_KEY>")
        print("Example: python update_env_with_working_key.py AIzaSyDdNo79MWP...4vjo")
        return False
    
    api_key = sys.argv[1]
    
    if not api_key.startswith("AIza"):
        print("❌ Invalid API key format. Must start with 'AIza'")
        return False
    
    print("🔧 UPDATING .ENV FILE WITH WORKING API KEY")
    print("=" * 50)
    
    success = update_env_file(api_key)
    
    if success:
        print("\n🎉 SUCCESS!")
        print("✅ .env file updated with working API key")
        print("✅ Ready to test restaurant integration")
        print("\nNext steps:")
        print("1. cd backend && source venv/bin/activate")
        print("2. python tests/run_comprehensive_tests.py")
        print("3. All tests should now pass!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
