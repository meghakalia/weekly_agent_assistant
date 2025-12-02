"""
Flask backend for Railway deployment
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys
from io import BytesIO
from PIL import Image
from datetime import datetime
import logging
import glob

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

try:
    from smart_shop.crew import SmartShop
    import google.generativeai as genai
except ImportError as e:
    logging.error(f"Import error: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transform_crewai_output_to_inventory(_crew_result=None):
    """
    Transform CrewAI output to frontend-compatible inventory format.
    """
    try:
        logger.info("Transforming CrewAI output from inventory.json")
        
        # Read from outputs directory
        output_dir = os.getenv('OUTPUT_DIR', './outputs')
        
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
def home():
    """Root endpoint"""
    return jsonify({
        "service": "Weekly Grocery Agent API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/api/process-inventory": "Process receipt image",
            "/api/generate-shopping-list": "Generate shopping list"
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    response = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Weekly Grocery Agent API",
        "version": "1.0.0"
    }
    return jsonify(response)


@app.route('/api/process-inventory', methods=['POST', 'OPTIONS'])
def process_inventory():
    """Process receipt image and extract inventory"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif, bmp, webp"}), 400
        
        # Read and validate image
        try:
            image_data = file.read()
            image = Image.open(BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            logger.error(f"Invalid image file: {str(e)}")
            return jsonify({"error": "Invalid image file"}), 400
        
        # Save image temporarily
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = '/tmp'
        os.makedirs(temp_dir, exist_ok=True)
        image_path = os.path.join(temp_dir, f"receipt_{timestamp}.jpg")
        
        image.save(image_path, 'JPEG', quality=95)
        logger.info(f"Saved image to: {image_path}")
        
        # Process with CrewAI
        try:
            logger.info("Initializing CrewAI system...")
            crew_instance = SmartShop()
            
            logger.info(f"Starting CrewAI processing for image: {image_path}")
            result = crew_instance.crew().kickoff(inputs={'image_path': image_path})
            
            logger.info(f"CrewAI processing complete")
            
            # Transform output
            inventory_result = transform_crewai_output_to_inventory(result)
            
            if inventory_result is None:
                logger.warning("Failed to transform CrewAI output")
                inventory_result = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "items": [{
                        "name": "Processing Complete",
                        "quantity": "1",
                        "unit": "unit",
                        "category": "info"
                    }],
                    "note": "Image processed but could not extract items."
                }
            
            # Cleanup
            try:
                os.remove(image_path)
            except:
                pass
            
            return jsonify(inventory_result)
            
        except Exception as e:
            logger.error(f"CrewAI processing error: {str(e)}", exc_info=True)
            
            # Cleanup on error
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except:
                pass
            
            return jsonify({
                "error": f"Error processing image: {str(e)}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "items": []
            }), 500
    
    except Exception as e:
        logger.error(f"Error in handler: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-shopping-list', methods=['POST', 'OPTIONS'])
def generate_shopping_list():
    """Generate shopping list based on current inventory"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get current inventory from request or default
        data = request.get_json() or {}
        current_inventory = data.get('inventory', {})
        
        # Load default grocery list
        default_list_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'default_grocery_list.json')
        
        if os.path.exists(default_list_path):
            with open(default_list_path, 'r') as f:
                default_list = json.load(f)
        else:
            default_list = {"items": []}
        
        # Simple logic: compare default list with current inventory
        shopping_list = []
        inventory_items = set(item.get('name', '').lower() for item in current_inventory.get('items', []))
        
        for item in default_list.get('items', []):
            item_name = item.get('name', '')
            if item_name.lower() not in inventory_items:
                shopping_list.append(item)
        
        response = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "items": shopping_list,
            "total_items": len(shopping_list)
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error generating shopping list: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
