#!/usr/bin/env python
"""
Test script for SmartShop CrewAI agent to validate inventory detection and processing.

This script:
1. Initializes the SmartShop crew
2. Processes an image (receipt/bill) to extract items
3. Creates an inventory from the extracted data
4. Prints the detected inventory items
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from smart_shop.crew import SmartShop

# Load environment variables
load_dotenv()

def print_banner(text):
    """Print a formatted banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_section(title):
    """Print a section header."""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}\n")

def validate_environment():
    """Validate that required environment variables are set."""
    print_section("Environment Validation")

    # Check for GEMINI_API_KEY
    gemini_key = os.getenv('GEMINI_API_KEY')

    if not gemini_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment!")
        print("Please set GEMINI_API_KEY in your .env file")
        return False

    # Set GOOGLE_AI_API_KEY if not already set (for compatibility with tools)
    if not os.getenv('GOOGLE_AI_API_KEY'):
        os.environ['GOOGLE_AI_API_KEY'] = gemini_key
        print("✓ Set GOOGLE_AI_API_KEY from GEMINI_API_KEY for tool compatibility")

    print(f"✓ GEMINI_API_KEY: {gemini_key[:10]}...{gemini_key[-4:]}")
    print(f"✓ GOOGLE_AI_API_KEY: {os.getenv('GOOGLE_AI_API_KEY')[:10]}...{os.getenv('GOOGLE_AI_API_KEY')[-4:]}")

    return True

def find_test_image():
    """Find a test image to process."""
    print_section("Finding Test Image")

    # List of potential test image locations
    test_images = [
        "./data/Costco-Receipt-600x800.jpg",
        "./src/smart_shop/images/CostcoBill.jpeg",
        "./src/smart_shop/images/CostcoBill2.jpeg"
    ]

    for image_path in test_images:
        if os.path.exists(image_path):
            abs_path = os.path.abspath(image_path)
            print(f"✓ Found test image: {abs_path}")
            return abs_path

    print("❌ ERROR: No test image found!")
    print("Searched locations:")
    for path in test_images:
        print(f"  - {path}")
    return None

def read_latest_json(output_dir, pattern):
    """Read the latest JSON file matching the pattern."""
    import glob

    files = glob.glob(os.path.join(output_dir, pattern))
    if not files:
        return None, None

    latest_file = max(files, key=os.path.getctime)

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f), latest_file
    except Exception as e:
        print(f"❌ Error reading {latest_file}: {e}")
        return None, None

def print_inventory_items(inventory_data):
    """Print inventory items in a formatted way."""
    if not inventory_data:
        print("❌ No inventory data available")
        return

    print_section("Detected Inventory Items")

    inventory = inventory_data.get("inventory", {})
    items = inventory.get("items", [])

    if not items:
        print("❌ No items found in inventory")
        return

    print(f"📅 Date: {inventory.get('date', 'N/A')}")
    print(f"📦 Total Items: {inventory.get('total_items', 0)}")
    print(f"💰 Total Value: ${inventory.get('total_value', 0.00):.2f}")

    if 'subtotal' in inventory:
        print(f"💵 Subtotal: ${inventory.get('subtotal', 0.00):.2f}")
    if 'tax' in inventory:
        print(f"💸 Tax: ${inventory.get('tax', 0.00):.2f}")

    print("\n📋 Items List:")
    print(f"{'#':<4} {'Item Name':<40} {'Qty':<8} {'Price':<10}")
    print("─" * 70)

    for idx, item in enumerate(items, 1):
        item_name = item.get('item', 'Unknown')
        quantity = item.get('quantity', 0)
        price = item.get('price', 0.00)
        print(f"{idx:<4} {item_name:<40} {quantity:<8} ${price:<9.2f}")

    print("─" * 70)

def run_crew_test(image_path):
    """Run the SmartShop crew with the given image."""
    print_banner("SmartShop CrewAI Agent Test")

    print(f"Test Image: {image_path}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Prepare inputs for the crew
    inputs = {
        'image_path': image_path,
        'current_year': str(datetime.now().year)
    }

    print_section("Initializing SmartShop Crew")

    try:
        # Initialize the crew
        smart_shop = SmartShop()
        print("✓ SmartShop crew initialized successfully")

        # Get the crew
        crew = smart_shop.crew()
        print("✓ Crew configuration loaded")

        print_section("Running Crew Tasks")
        print("This will:")
        print("  1. Process the image and extract data (Image Processor Agent)")
        print("  2. Create inventory from extracted data (Inventory Manager Agent)")
        print("\nPlease wait, this may take a minute...\n")

        # Run the crew
        result = crew.kickoff(inputs=inputs)

        print_section("Crew Execution Completed")
        print("✓ Crew execution finished successfully")

        # Read and display the results
        output_dir = os.getenv('OUTPUT_DIR', './outputs')

        # Read image analysis result
        image_data, image_file = read_latest_json(output_dir, "image_analysis_*.json")
        if image_file:
            print(f"\n✓ Image Analysis File: {image_file}")
            if image_data and image_data.get('success'):
                print("✓ Image processing successful")

        # Read inventory result
        inventory_data, inventory_file = read_latest_json(output_dir, "inventory_*.json")
        if inventory_file:
            print(f"✓ Inventory File: {inventory_file}")
            if inventory_data:
                print("✓ Inventory creation successful")

                # Print the inventory items
                print_inventory_items(inventory_data)

        # Print the final crew result
        print_section("Final Crew Result")
        print(result)

        print_banner("Test Completed Successfully ✓")
        return True

    except Exception as e:
        print_section("ERROR")
        print(f"❌ An error occurred: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        print_banner("Test Failed ✗")
        return False

def main():
    """Main test function."""
    # Validate environment
    if not validate_environment():
        sys.exit(1)

    # Find test image
    image_path = find_test_image()
    if not image_path:
        sys.exit(1)

    # Run the crew test
    success = run_crew_test(image_path)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
