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
from smart_shop.tools.image_to_json_tool import ImageToJSONTool


def test_image_tool():
    """Test the image to JSON tool directly."""
    print("Testing ImageToJSONTool...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if we have the required environment variable
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key or api_key == 'your_google_ai_api_key_here':
        print("❌ GOOGLE_AI_API_KEY environment variable not set or invalid")
        print("Please:")
        print("1. Copy env_template.txt to .env")
        print("2. Edit .env and set your Google AI API key")
        print("3. Get your API key from: https://makersuite.google.com/app/apikey")
        print("4. Run: python setup_environment.py")
        return False
    
    # Test with the existing image
    image_path = "src/smart_shop/images/CostcoBill2.jpeg"
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return False
    
    try:
        tool = ImageToJSONTool()
        
        # Use a specific prompt to ensure we get data from the actual image
        result = tool._run(
            image_path=image_path,
            output_path="test_output.json"
        )
        
        print("✅ ImageToJSONTool test successful!")
        print(f"📁 Output saved to: test_output.json")
        
        # Show detailed preview of the extracted data
        import json
        result_data = json.loads(result)
        if result_data.get('success'):
            print("\n📋 Extracted information preview:")
            json_data = result_data.get('json_data', {})
            if 'image_description' in json_data:
                print(f"  Description: {json_data['image_description'][:100]}...")
            if 'text' in json_data and 'items_purchased' in json_data['text']:
                items = json_data['text']['items_purchased']
                print(f"  Items found: {len(items)}")
                for i, item in enumerate(items[:3]):  # Show first 3 items
                    print(f"    {i+1}. {item.get('item', 'Unknown')} - ${item.get('price', 0)}")
            if 'text' in json_data and 'totals' in json_data['text']:
                totals = json_data['text']['totals']
                print(f"  Total: ${totals.get('total', 0)}")
        else:
            print(f"❌ Error in result: {result_data.get('error', 'Unknown error')}")
            return False
        
        print(f"📊 Full result preview: {result[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ ImageToJSONTool test failed: {e}")
        return False


def test_crew_integration():
    """Test the crew integration with image processing."""
    print("\nTesting Crew Integration...")
    
    try:
        from smart_shop.crew import SmartShop
        
        # Initialize the crew
        crew_instance = SmartShop()
        
        # Check if the image_processor agent exists
        if hasattr(crew_instance, 'image_processor'):
            print("✅ Image processor agent found in crew")
        else:
            print("❌ Image processor agent not found in crew")
            print(f"Available agents: {[attr for attr in dir(crew_instance) if not attr.startswith('_')]}")
            return False
        
        # Check if the image_processing_task exists
        if hasattr(crew_instance, 'image_processing_task'):
            print("✅ Image processing task found in crew")
        else:
            print("❌ Image processing task not found in crew")
            return False
        
        print("✅ Crew integration test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Crew integration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Testing Image Processing Crew Integration")
    print("=" * 50)
    
    # Test 1: Direct tool test
    tool_success = test_image_tool()
    
    # Test 2: Crew integration test
    crew_success = test_crew_integration()
    
    print("\n" + "=" * 50)
    if tool_success and crew_success:
        print("🎉 All tests passed! Image processing crew is ready to use.")
        print("\nTo use the image processing crew:")
        print("1. Set your GOOGLE_AI_API_KEY environment variable")
        print("2. Call the crew with an image path")
        print("3. The crew will process the image and generate JSON output")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
