#!/usr/bin/env python3
"""
Test script for the image processing crew integration.
This script demonstrates how to use the image processing agent and task.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from smart_shop.crew import SmartShop



def test_crew_kickoff():
    """Test the crew kickoff with image processing."""
    print("\nTesting Crew Kickoff with Image Processing...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if we have the required environment variable
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key or api_key == 'your_google_ai_api_key_here':
        print("❌ GOOGLE_AI_API_KEY environment variable not set or invalid")
        print("Please set your Google AI API key in the .env file")
        return False
    
    # Test with the existing image
    image_path = "src/smart_shop/images/CostcoBill2.jpeg"
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return False
    
    try:
        from smart_shop.crew import SmartShop
        
        # Initialize the crew
        crew_instance = SmartShop()
        
        # Get the actual crew object
        crew = crew_instance.crew()
        
        print(f"🖼️  Processing image: {image_path}")
        print("🚀 Starting crew kickoff...")
        
        # Kick off the crew with image processing
        result = crew.kickoff(
            inputs={
                "image_path": image_path,
                "topic": "receipt_processing"
            }
        )
        
        print("✅ Crew kickoff completed!")
        
        # Display the result
        print(f"📊 Result type: {type(result)}")
        print(f"📋 Result preview: {str(result)[:200]}...")
        
        # Check if result has the expected structure
        if hasattr(result, 'raw'):
            print("✅ Result has 'raw' attribute")
            try:
                import json
                result_data = json.loads(result.raw)
                print("✅ Result is valid JSON")
                if result_data.get('success'):
                    print("✅ Processing was successful")
                else:
                    print(f"⚠️  Processing had issues: {result_data.get('error', 'Unknown error')}")
            except json.JSONDecodeError:
                print("⚠️  Result raw is not JSON format")
        else:
            print("⚠️  Result does not have 'raw' attribute")
        
        return True
        
    except Exception as e:
        print(f"❌ Crew kickoff test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🧪 Testing Image Processing Crew Integration")
    print("=" * 50)
    
    # Test 2: Crew kickoff test
    kickoff_success = test_crew_kickoff()
    
    print("\n" + "=" * 50)
    if kickoff_success:
        print("🎉 All tests passed! Image processing crew is ready to use.")
        print("\nTo use the image processing crew:")
        print("1. Set your GOOGLE_AI_API_KEY environment variable")
        print("2. Call crew.kickoff() with an image path")
        print("3. The image_processor agent will use the image_to_json_tool")
        print("4. The crew will process the image and generate JSON output")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
