#!/usr/bin/env python3
"""
Example usage of the Image to JSON Agent
Demonstrates different ways to use the agent for image analysis.
"""

import os
import json
from image_to_json_agent import ImageToJSONAgent


def example_basic_usage():
    """Basic example of using the agent."""
    print("=== Basic Usage Example ===")
    
    # Initialize agent (requires GOOGLE_AI_API_KEY environment variable)
    try:
        agent = ImageToJSONAgent()
        print("✅ Agent initialized successfully")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please set GOOGLE_AI_API_KEY environment variable")
        return
    
    # Example image path (replace with your actual image)
    image_path = "sample_image.jpg"
    
    if not os.path.exists(image_path):
        print(f"⚠️  Image file not found: {image_path}")
        print("Please provide a valid image file for testing")
        return
    
    # Convert image to JSON
    print(f"🔄 Processing image: {image_path}")
    result = agent.convert_image_to_json(image_path)
    
    if result["success"]:
        print("✅ Image processed successfully!")
        print(f"📊 Tokens used: {result['metadata']['tokens_used']}")
        print(f"🖼️  Image size: {result['metadata']['image_size']}")
        
        # Print a preview of the JSON data
        print("\n📄 JSON Data Preview:")
        print(json.dumps(result["json_data"], indent=2)[:500] + "...")
        
        # Save to file
        output_file = "example_output.json"
        agent.save_json_output(result, output_file)
        print(f"💾 Output saved to: {output_file}")
        
    else:
        print(f"❌ Error processing image: {result['error']}")


def example_custom_prompt():
    """Example with custom prompt."""
    print("\n=== Custom Prompt Example ===")
    
    try:
        agent = ImageToJSONAgent()
        
        image_path = "sample_image.jpg"
        if not os.path.exists(image_path):
            print(f"⚠️  Image file not found: {image_path}")
            return
        
        # Custom prompt for specific analysis
        custom_prompt = """
        Analyze this image and provide a detailed JSON response with:
        1. All text content (OCR)
        2. List of all objects and their positions
        3. Color palette analysis
        4. Any people and their activities
        5. Overall scene description
        
        Format the response as a structured JSON object.
        """
        
        print("🔄 Processing with custom prompt...")
        result = agent.convert_image_to_json(image_path, prompt=custom_prompt)
        
        if result["success"]:
            print("✅ Custom analysis completed!")
            print("📄 Custom Analysis Result:")
            print(json.dumps(result["json_data"], indent=2))
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_batch_processing():
    """Example of processing multiple images."""
    print("\n=== Batch Processing Example ===")
    
    try:
        agent = ImageToJSONAgent()
        
        # List of images to process
        image_files = ["image1.jpg", "image2.png", "image3.jpg"]
        
        results = []
        for image_file in image_files:
            if os.path.exists(image_file):
                print(f"🔄 Processing: {image_file}")
                result = agent.convert_image_to_json(image_file)
                results.append({
                    "file": image_file,
                    "result": result
                })
                
                if result["success"]:
                    print(f"✅ {image_file} processed successfully")
                else:
                    print(f"❌ {image_file} failed: {result['error']}")
            else:
                print(f"⚠️  Skipping {image_file} (file not found)")
        
        # Save batch results
        batch_output = "batch_results.json"
        with open(batch_output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Batch results saved to: {batch_output}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_error_handling():
    """Example demonstrating error handling."""
    print("\n=== Error Handling Example ===")
    
    try:
        agent = ImageToJSONAgent()
        
        # Test with non-existent file
        print("Testing with non-existent file...")
        result = agent.convert_image_to_json("non_existent.jpg")
        if not result["success"]:
            print(f"✅ Properly handled missing file: {result['error']}")
        
        # Test with invalid image (if you have one)
        invalid_image = "invalid.txt"
        if os.path.exists(invalid_image):
            print("Testing with invalid image...")
            result = agent.convert_image_to_json(invalid_image)
            if not result["success"]:
                print(f"✅ Properly handled invalid image: {result['error']}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def main():
    """Run all examples."""
    print("🚀 Image to JSON Agent - Example Usage")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv('GOOGLE_AI_API_KEY'):
        print("⚠️  GOOGLE_AI_API_KEY environment variable not set")
        print("Please set your Google AI API key:")
        print("export GOOGLE_AI_API_KEY='your_api_key_here'")
        return
    
    # Run examples
    example_basic_usage()
    example_custom_prompt()
    example_batch_processing()
    example_error_handling()
    
    print("\n🎉 All examples completed!")
    print("\nFor more information, see the README.md file")


if __name__ == "__main__":
    main()
