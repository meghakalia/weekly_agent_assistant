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
sys.path.append("/Users/megha/Documents/repos/weekly_grocery_agent/src")

from smart_shop.crew import SmartShop

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for frontend connection
CORS(app, origins=["http://localhost:3000", "https://your-frontend-domain.com"])

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    Generate shopping list based on inventory data.
    """
    try:
        logger.info("Received generate-shopping-list request")

        # Get JSON data from request
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        logger.info(f"Request data: {data}")

        # Frontend sends 'inventory' and 'selected_items'
        if 'inventory' not in data:
            logger.error("Missing inventory in request")
            return jsonify({"error": "inventory is required"}), 400

        inventory_data = data['inventory']
        selected_items = data.get('selected_items', [])

        logger.info(f"Inventory items: {len(inventory_data.get('items', []))}, Selected: {len(selected_items)}")

        # Generate shopping suggestions based on selected items
        # For now, using intelligent mock data based on actual inventory
        shopping_items = []

        # Add complementary items based on what's in inventory
        inventory_items = inventory_data.get('items', [])

        for item in inventory_items:
            item_name = item.get('name', '').lower()

            # Suggest complementary items
            if 'milk' in item_name:
                shopping_items.append({
                    "name": "Cereal",
                    "quantity": "1 box",
                    "category": "breakfast",
                    "priority": "medium"
                })
            elif 'bread' in item_name:
                shopping_items.append({
                    "name": "Butter",
                    "quantity": "1 pack",
                    "category": "dairy",
                    "priority": "low"
                })
            elif 'egg' in item_name:
                shopping_items.append({
                    "name": "Bacon",
                    "quantity": "1 pack",
                    "category": "meat",
                    "priority": "medium"
                })

        # Add some staples if list is empty
        if not shopping_items:
            shopping_items = [
                {
                    "name": "Fresh Vegetables",
                    "quantity": "1 bag",
                    "category": "produce",
                    "priority": "high"
                },
                {
                    "name": "Cooking Oil",
                    "quantity": "1 bottle",
                    "category": "pantry",
                    "priority": "medium"
                },
                {
                    "name": "Salt & Pepper",
                    "quantity": "1 set",
                    "category": "spices",
                    "priority": "low"
                }
            ]

        shopping_list = {
            "items": shopping_items[:8]  # Limit to 8 items
        }

        logger.info(f"Generated shopping list with {len(shopping_list['items'])} items")
        return jsonify(shopping_list)

    except Exception as e:
        logger.error(f"Error generating shopping list: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error generating shopping list: {str(e)}"}), 500

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
    app.run(host='0.0.0.0', port=8000, debug=True)
