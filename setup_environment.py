#!/usr/bin/env python3
"""
Setup script for SmartShop Crew with Image Processing.
This script helps configure the environment for the crew.
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path('.env')
    template_file = Path('env_template.txt')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not template_file.exists():
        print("❌ env_template.txt not found")
        return False
    
    try:
        # Copy template to .env
        with open(template_file, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from template")
        print("📝 Please edit .env file and add your Google AI API key")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def validate_environment():
    """Validate that required environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['GOOGLE_AI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == 'your_google_ai_api_key_here':
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or invalid environment variables: {', '.join(missing_vars)}")
        print("Please edit your .env file and set valid values")
        return False
    
    print("✅ All required environment variables are set")
    return True


def test_crew_initialization():
    """Test that the crew can be initialized with the current environment."""
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from smart_shop.crew import SmartShop
        
        # Try to initialize the crew
        crew_instance = SmartShop()
        print("✅ Crew initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Crew initialization failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 SmartShop Crew Environment Setup")
    print("=" * 40)
    
    # Step 1: Create .env file
    print("\n1. Setting up environment file...")
    if not create_env_file():
        return 1
    
    # Step 2: Validate environment
    print("\n2. Validating environment...")
    if not validate_environment():
        print("\n📋 Next steps:")
        print("1. Edit the .env file")
        print("2. Set your GOOGLE_AI_API_KEY")
        print("3. Get your API key from: https://makersuite.google.com/app/apikey")
        print("4. Run this script again to validate")
        return 1
    
    # Step 3: Test crew initialization
    print("\n3. Testing crew initialization...")
    if not test_crew_initialization():
        return 1
    
    print("\n🎉 Environment setup complete!")
    print("\nYou can now use the SmartShop crew with image processing capabilities.")
    print("\nExample usage:")
    print("  python example_image_processing.py")
    print("  python test_image_crew.py")
    
    return 0


if __name__ == "__main__":
    exit(main())
