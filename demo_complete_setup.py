#!/usr/bin/env python3
"""
Complete demonstration of the SmartShop crew with image processing.
This script shows the full setup and usage of the crew with environment variables.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_environment():
    """Check if environment is properly configured."""
    print("🔍 Checking environment configuration...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required variables
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key or api_key == 'your_google_ai_api_key_here':
        print("❌ GOOGLE_AI_API_KEY not properly configured")
        return False
    
    print("✅ Environment variables configured")
    return True


def demonstrate_crew_usage():
    """Demonstrate the crew usage with image processing."""
    print("\n🚀 Demonstrating SmartShop Crew with Image Processing")
    print("=" * 60)
    
    try:
        from smart_shop.crew import SmartShop
        
        # Initialize the crew (this will validate environment)
        print("📋 Initializing SmartShop crew...")
        crew_instance = SmartShop()
        
        print("✅ Crew initialized successfully!")
        
        # Show available agents
        print("\n👥 Available agents:")
        print("  - researcher: Data research specialist")
        print("  - reporting_analyst: Report generation specialist")
        print("  - image_processor: Image analysis specialist")
        
        # Show available tasks
        print("\n📝 Available tasks:")
        print("  - research_task: Conduct research on topics")
        print("  - reporting_task: Generate detailed reports")
        print("  - image_processing_task: Convert images to JSON")
        
        # Show crew configuration
        print("\n⚙️  Crew configuration:")
        print("  - Process: Sequential")
        print("  - Verbose: True")
        print("  - Image processing: Enabled with Gemini Flash 1.5")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing crew: {e}")
        return False


def demonstrate_tool_usage():
    """Demonstrate the image processing tool directly."""
    print("\n🛠️  Demonstrating Image Processing Tool")
    print("=" * 50)
    
    try:
        from smart_shop.tools.image_to_json_tool import ImageToJSONTool
        
        # Initialize the tool
        print("🔧 Initializing image processing tool...")
        tool = ImageToJSONTool()
        
        print("✅ Tool initialized successfully!")
        
        # Show tool capabilities
        print("\n🎯 Tool capabilities:")
        print("  - OCR: Extract text from images")
        print("  - Object detection: Identify objects and items")
        print("  - Visual analysis: Extract colors and shapes")
        print("  - Receipt processing: Specialized for receipts")
        print("  - JSON output: Structured data format")
        
        # Show configuration
        print(f"\n⚙️  Tool configuration:")
        print(f"  - Max tokens: {tool.max_tokens}")
        print(f"  - Temperature: {tool.temperature}")
        print(f"  - Output directory: {tool.output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing tool: {e}")
        return False


def show_usage_examples():
    """Show usage examples."""
    print("\n📚 Usage Examples")
    print("=" * 30)
    
    print("\n1. Basic crew usage:")
    print("""
    from smart_shop.crew import SmartShop
    
    crew_instance = SmartShop()
    result = crew_instance.crew().kickoff(inputs={
        'image_path': 'path/to/your/image.jpg'
    })
    """)
    
    print("\n2. Direct tool usage:")
    print("""
    from smart_shop.tools.image_to_json_tool import ImageToJSONTool
    
    tool = ImageToJSONTool()
    result = tool._run(
        image_path='receipt.jpg',
        custom_prompt='Extract all items and prices from this receipt',
        output_path='receipt_data.json'
    )
    """)
    
    print("\n3. Environment configuration:")
    print("""
    # In your .env file:
    GOOGLE_AI_API_KEY=your_api_key_here
    OUTPUT_DIR=./outputs
    MAX_TOKENS=4096
    TEMPERATURE=0.1
    """)


def main():
    """Main demonstration function."""
    print("🎬 SmartShop Crew with Image Processing - Complete Demo")
    print("=" * 70)
    
    # Step 1: Check environment
    if not check_environment():
        print("\n❌ Environment not properly configured.")
        print("Please run: python setup_environment.py")
        return 1
    
    # Step 2: Demonstrate crew
    if not demonstrate_crew_usage():
        print("\n❌ Crew initialization failed.")
        return 1
    
    # Step 3: Demonstrate tool
    if not demonstrate_tool_usage():
        print("\n❌ Tool initialization failed.")
        return 1
    
    # Step 4: Show usage examples
    show_usage_examples()
    
    print("\n🎉 Demo completed successfully!")
    print("\n📋 Next steps:")
    print("1. Process your images: python example_image_processing.py")
    print("2. Test the setup: python test_image_crew.py")
    print("3. Read the documentation: IMAGE_PROCESSING_README.md")
    print("4. Environment setup guide: ENVIRONMENT_SETUP.md")
    
    return 0


if __name__ == "__main__":
    exit(main())
