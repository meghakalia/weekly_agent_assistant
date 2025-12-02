from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import base64
from io import BytesIO
from PIL import Image
import os
import logging

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from smart_shop.crew import SmartShop
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for all origins (update with your Vercel domain for production)
CORS(app, origins=["*"])  # Allow all origins for now

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Grocery list file paths
DEFAULT_GROCERY_LIST_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'default_grocery_list.json')
CURRENT_GROCERY_LIST_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'current_grocery_list.json')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_default_grocery_list():
    """Load the default weekly grocery list template."""
    try:
        with open(DEFAULT_GROCERY_LIST_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading default grocery list: {e}")
        return None

def load_current_grocery_list():
    """Load the current grocery list, or create from default if doesn't exist."""
    try:
        if os.path.exists(CURRENT_GROCERY_LIST_PATH):
            with open(CURRENT_GROCERY_LIST_PATH, 'r') as f:
                return json.load(f)
        else:
            # Create from default
            default_list = load_default_grocery_list()
            if default_list:
                save_current_grocery_list(default_list)
                return default_list
            return None
    except Exception as e:
        logger.error(f"Error loading current grocery list: {e}")
        return None

def save_current_grocery_list(grocery_list):
    """Save the current grocery list to file."""
    try:
        with open(CURRENT_GROCERY_LIST_PATH, 'w') as f:
            json.dump(grocery_list, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving grocery list: {e}")
        return False

def match_item_to_grocery_key(item_name, grocery_list):
    """
    Use Gemini AI to match a receipt item to the closest default grocery key.

    Args:
        item_name: The item name from the receipt (e.g., "FF BS BREAST", "KS DICED TOM")
        grocery_list: The default grocery list with categories

    Returns:
        Tuple of (category, key) or (None, None) if no match
    """
    try:
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            return None, None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Build list of available grocery items
        available_items = []
        for category, items in grocery_list.get('categories', {}).items():
            for key in items.keys():
                available_items.append(f"{category}:{key}")

        items_str = ", ".join(available_items)

        # Create prompt
        prompt = f"""Match the following grocery item from a receipt to the closest standard grocery item key.

Receipt Item: "{item_name}"

Available grocery item keys (in format category:key):
{items_str}

Instructions:
1. Interpret what the receipt item actually is (e.g., "FF BS BREAST" = "chicken breast", "KS DICED TOM" = "canned tomatoes")
2. Find the best matching category:key from the available list
3. If no close match exists, return "new_item:custom" to indicate it should be added as a new item
4. Return ONLY the category:key pair, nothing else

Examples:
- "FF BS BREAST" → "meat_poultry:chicken_breast"
- "KS DICED TOM" → "pantry:canned_tomatoes"
- "18CT EGGS" → "dairy_eggs:eggs"
- "GRND TURKEY" → "meat_poultry:ground_turkey"

Now match: "{item_name}"
Return only the category:key"""

        response = model.generate_content(prompt)
        result = response.text.strip()

        # Parse result
        if ':' in result:
            category, key = result.split(':', 1)
            category = category.strip()
            key = key.strip()

            # Validate the match exists
            if category in grocery_list.get('categories', {}) and key in grocery_list['categories'][category]:
                logger.info(f"Matched '{item_name}' to {category}:{key}")
                return category, key
            elif category == "new_item":
                logger.info(f"'{item_name}' is a new item, will be added")
                return "new_item", key

        logger.warning(f"Could not match '{item_name}' to grocery list")
        return None, None

    except Exception as e:
        logger.error(f"Error matching item '{item_name}': {e}")
        return None, None

def update_grocery_list_from_inventory(inventory_data):
    """
    Update the current grocery list based on detected inventory items.

    Args:
        inventory_data: The inventory data from CrewAI (from inventory.json)

    Returns:
        Updated grocery list
    """
    try:
        # Load current grocery list
        grocery_list = load_current_grocery_list()
        if not grocery_list:
            logger.error("Could not load grocery list")
            return None

        # Get inventory items
        inventory = inventory_data.get('inventory', {})
        items = inventory.get('items', [])

        logger.info(f"Updating grocery list with {len(items)} inventory items")

        # Process each item
        for item in items:
            item_name = item.get('item', '')
            quantity = item.get('quantity', 0)

            if not item_name:
                continue

            # Match to grocery key using AI
            category, key = match_item_to_grocery_key(item_name, grocery_list)

            if category and category != "new_item":
                # Update existing item
                if category in grocery_list['categories'] and key in grocery_list['categories'][category]:
                    current_qty = grocery_list['categories'][category][key].get('quantity', 0)
                    new_qty = current_qty + quantity
                    grocery_list['categories'][category][key]['quantity'] = new_qty
                    logger.info(f"Updated {category}:{key} quantity from {current_qty} to {new_qty}")
            elif category == "new_item":
                # Add as new item in a custom category
                if 'custom' not in grocery_list['categories']:
                    grocery_list['categories']['custom'] = {}

                # Create a safe key from item name
                safe_key = item_name.lower().replace(' ', '_').replace('-', '_')

                grocery_list['categories']['custom'][safe_key] = {
                    "quantity": quantity,
                    "max_per_week": quantity * 2,  # Default max is 2x current
                    "unit": "unit",
                    "original_name": item_name
                }
                logger.info(f"Added new custom item: {safe_key} with quantity {quantity}")

        # Save updated list
        grocery_list['last_updated'] = datetime.now().isoformat()
        save_current_grocery_list(grocery_list)

        return grocery_list

    except Exception as e:
        logger.error(f"Error updating grocery list from inventory: {e}", exc_info=True)
        return None

def transform_crewai_output_to_inventory(_crew_result=None):
    """
    Transform CrewAI output to frontend-compatible inventory format.

    The CrewAI crew creates inventory.json in the outputs folder.
    We read that file and transform it to the frontend format.

    Args:
        _crew_result: Crew execution result (unused, we read from file instead)

    Expected inventory.json format:
    {
      "inventory": {
        "date": "04/20/2016",
        "items": [{"item": "...", "quantity": 1, "price": 23.99}],
        "total_items": 9,
        "total_value": 89.13
      }
    }

    Expected Frontend format:
    {
      "date": "YYYY-MM-DD",
      "items": [{"name": "...", "quantity": "..."}]
    }
    """
    try:
        logger.info("Transforming CrewAI output from inventory.json")

        # The crew creates files in the outputs directory
        # Read the latest inventory file
        import glob
        output_dir = os.getenv('OUTPUT_DIR', './outputs')

        # Try to find inventory.json first
        inventory_path = os.path.join(output_dir, 'inventory.json')
        inventory_data = None

        if os.path.exists(inventory_path):
            logger.info(f"Reading inventory from {inventory_path}")
            with open(inventory_path, 'r') as f:
                inventory_data = json.load(f)
        else:
            # Try to find inventory_*.json files
            inventory_files = glob.glob(os.path.join(output_dir, 'inventory_*.json'))
            if inventory_files:
                latest_file = max(inventory_files, key=os.path.getctime)
                logger.info(f"Reading inventory from {latest_file}")
                with open(latest_file, 'r') as f:
                    inventory_data = json.load(f)

        if not inventory_data:
            logger.error("No inventory file found")
            return None

        # Extract inventory data
        inventory = inventory_data.get('inventory', {})
        inventory_items = inventory.get('items', [])
        inventory_date = inventory.get('date', datetime.now().strftime("%Y-%m-%d"))

        # Transform items to frontend format
        items = []
        for item_data in inventory_items:
            if isinstance(item_data, dict):
                item_name = item_data.get('item', 'Unknown')
                quantity = item_data.get('quantity', 1)
                price = item_data.get('price', 0.00)

                items.append({
                    "name": item_name,
                    "quantity": f"{quantity} @ ${price:.2f}",
                    "unit": "unit",
                    "category": "grocery",
                    "price": price
                })

        # If no items found, return None
        if not items:
            logger.warning("No items found in inventory")
            return None

        logger.info(f"Successfully transformed {len(items)} items")

        return {
            "date": inventory_date,
            "items": items,
            "total_items": inventory.get('total_items', len(items)),
            "total_value": inventory.get('total_value', 0.00),
            "subtotal": inventory.get('subtotal', 0.00),
            "tax": inventory.get('tax', 0.00)
        }

    except Exception as e:
        logger.error(f"Error transforming CrewAI output: {str(e)}", exc_info=True)
        return None

@app.route('/')
def root():
    return jsonify({"message": "Inventory Management API is running!"})

@app.route('/process-inventory', methods=['POST'])
def process_inventory():
    """
    Process uploaded image and return inventory information.
    Frontend sends to: /process-inventory
    """
    try:
        logger.info("Received process-inventory request")

        # Check if file is present - frontend sends as 'image'
        if 'image' not in request.files:
            logger.error("No image file in request")
            return jsonify({"error": "No file provided"}), 400

        file = request.files['image']

        # Check if file is selected
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({"error": "File must be an image"}), 400

        # Read image data
        image_data = file.read()

        # Validate image can be opened
        try:
            image = Image.open(BytesIO(image_data))
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            logger.error(f"Invalid image file: {str(e)}")
            return jsonify({"error": "Invalid image file"}), 400

        # Save image to temporary file for CrewAI processing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(f"receipt_{timestamp}.jpg")
        image_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save the image
        image.save(image_path, 'JPEG', quality=95)
        logger.info(f"Saved image to: {image_path}")

        # Process image with CrewAI
        try:
            logger.info("Initializing CrewAI system...")
            crew_instance = SmartShop()

            logger.info(f"Starting CrewAI processing for image: {image_path}")
            result = crew_instance.crew().kickoff(inputs={'image_path': image_path})

            logger.info(f"CrewAI processing complete. Result: {result}")

            # Transform CrewAI output to frontend format
            inventory_result = transform_crewai_output_to_inventory(result)

            if inventory_result is None:
                logger.warning("Failed to transform CrewAI output, using fallback")
                # Fallback to mock data if transformation fails
                inventory_result = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "items": [
                        {
                            "name": "Processing Complete",
                            "quantity": "1",
                            "unit": "unit",
                            "category": "info"
                        }
                    ],
                    "note": "Image processed but could not extract items. Check outputs folder for raw data."
                }
            else:
                # Update grocery list with detected items
                logger.info("Updating grocery list with detected inventory items...")
                try:
                    # Read inventory.json to get the full data
                    output_dir = os.getenv('OUTPUT_DIR', './outputs')
                    inventory_path = os.path.join(output_dir, 'inventory.json')

                    if os.path.exists(inventory_path):
                        with open(inventory_path, 'r') as f:
                            inventory_data = json.load(f)

                        # Update grocery list
                        updated_grocery_list = update_grocery_list_from_inventory(inventory_data)
                        if updated_grocery_list:
                            logger.info("Successfully updated grocery list")
                        else:
                            logger.warning("Failed to update grocery list")
                    else:
                        logger.warning("inventory.json not found, skipping grocery list update")
                except Exception as e:
                    logger.error(f"Error updating grocery list: {e}")

            # Cleanup temporary file
            try:
                os.remove(image_path)
                logger.info(f"Cleaned up temporary file: {image_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary file: {str(e)}")

            return jsonify(inventory_result)

        except Exception as e:
            logger.error(f"CrewAI processing error: {str(e)}", exc_info=True)

            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Full traceback: {error_details}")

            # Cleanup temporary file on error
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except:
                pass

            # Return detailed error for debugging
            return jsonify({
                "error": f"Error processing image with AI: {str(e)}",
                "error_type": type(e).__name__,
                "error_details": str(e),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "items": [],
                "debug_info": "Check Flask terminal for full error details"
            }), 500

    except Exception as e:
        logger.error(f"Error in process_inventory endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

@app.route('/api/generate-shopping-list', methods=['POST'])
def generate_shopping_list():
    """
    Generate shopping list based on current grocery list (max - current quantity).
    """
    try:
        logger.info("Received generate-shopping-list request")

        # Load current grocery list
        grocery_list = load_current_grocery_list()
        if not grocery_list:
            logger.error("Could not load grocery list")
            return jsonify({"error": "Grocery list not available"}), 500

        # Generate shopping list: items needed = max - current
        # Also generate current inventory list: items you have
        shopping_items = []
        current_items = []

        categories = grocery_list.get('categories', {})
        for category_name, category_items in categories.items():
            for item_key, item_data in category_items.items():
                current_qty = item_data.get('quantity', 0)
                max_qty = item_data.get('max_per_week', 0)
                needed_qty = max_qty - current_qty
                item_name = item_data.get('original_name', item_key.replace('_', ' ').title())
                unit = item_data.get('unit', 'unit')

                # Add to shopping list if needed
                if needed_qty > 0:
                    shopping_items.append({
                        "name": item_name,
                        "quantity": f"{needed_qty} {unit}",
                        "category": category_name,
                        "priority": "high" if needed_qty >= max_qty * 0.8 else "medium" if needed_qty >= max_qty * 0.5 else "low"
                    })

                # Add to current inventory if you have any
                if current_qty > 0:
                    current_items.append({
                        "name": item_name,
                        "quantity": f"{current_qty} {unit}",
                        "max": f"{max_qty} {unit}",
                        "category": category_name,
                        "percentage": int((current_qty / max_qty * 100)) if max_qty > 0 else 0
                    })

        # Sort shopping list by priority (high first)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        shopping_items.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))

        # Sort current items by percentage (lowest first - running out soon)
        current_items.sort(key=lambda x: x.get('percentage', 0))

        logger.info(f"Generated shopping list with {len(shopping_items)} items to buy")
        logger.info(f"Current inventory has {len(current_items)} items in stock")

        result = {
            "shopping_list": {
                "items": shopping_items,
                "total": len(shopping_items)
            },
            "current_inventory": {
                "items": current_items,
                "total": len(current_items)
            }
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error generating shopping list: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error generating shopping list: {str(e)}"}), 500

@app.route('/api/reset-grocery-list', methods=['POST'])
def reset_grocery_list():
    """
    Reset the current grocery list to default (all quantities to 0).
    """
    try:
        logger.info("Resetting grocery list to default")

        default_list = load_default_grocery_list()
        if not default_list:
            return jsonify({"error": "Could not load default grocery list"}), 500

        # Save as current
        save_current_grocery_list(default_list)

        return jsonify({
            "success": True,
            "message": "Grocery list reset to default"
        })

    except Exception as e:
        logger.error(f"Error resetting grocery list: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-grocery-list', methods=['GET'])
def get_grocery_list():
    """
    Get the current grocery list.
    """
    try:
        grocery_list = load_current_grocery_list()
        if not grocery_list:
            return jsonify({"error": "Could not load grocery list"}), 500

        return jsonify(grocery_list)

    except Exception as e:
        logger.error(f"Error getting grocery list: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload-grocery-list', methods=['POST'])
def upload_grocery_list():
    """
    Upload/update the current grocery list.
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        grocery_list = request.get_json()

        # Validate basic structure
        if 'categories' not in grocery_list:
            return jsonify({"error": "Invalid grocery list format"}), 400

        # Save the list
        grocery_list['last_updated'] = datetime.now().isoformat()
        save_current_grocery_list(grocery_list)

        return jsonify({
            "success": True,
            "message": "Grocery list updated successfully"
        })

    except Exception as e:
        logger.error(f"Error uploading grocery list: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "crewai": "enabled"
    })

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    
    # Get port from environment variable (Railway/Render provide this)
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Starting server on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
