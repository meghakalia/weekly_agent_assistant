"""
Flask backend for Render deployment
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
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Ensure OUTPUT_DIR is set and exists (important for Vercel)
output_dir = os.getenv('OUTPUT_DIR', './outputs')
os.makedirs(output_dir, exist_ok=True)
logger = logging.getLogger(__name__)
logger.info(f"Output directory set to: {output_dir}")

# Ensure both API key environment variables are set
# Some tools check GOOGLE_AI_API_KEY, others check GEMINI_API_KEY
gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
if gemini_key:
    if not os.getenv('GEMINI_API_KEY'):
        os.environ['GEMINI_API_KEY'] = gemini_key
    if not os.getenv('GOOGLE_AI_API_KEY'):
        os.environ['GOOGLE_AI_API_KEY'] = gemini_key

try:
    from smart_shop.crew import SmartShop
    import google.generativeai as genai
except ImportError as e:
    logging.error(f"Import error: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log API key status (without exposing the full key)
gemini_key_status = "SET" if os.getenv('GEMINI_API_KEY') else "NOT SET"
google_key_status = "SET" if os.getenv('GOOGLE_AI_API_KEY') else "NOT SET"
logger.info(f"API Key Status - GEMINI_API_KEY: {gemini_key_status}, GOOGLE_AI_API_KEY: {google_key_status}")

if gemini_key_status == "SET":
    key = os.getenv('GEMINI_API_KEY')
    logger.info(f"GEMINI_API_KEY present: {key[:20]}...{key[-4:] if len(key) > 24 else ''}")


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
        
        # Check multiple possible output directories (Vercel uses /tmp)
        possible_dirs = [
            os.getenv('OUTPUT_DIR', './outputs'),
            './outputs',
            '/tmp',
            os.getcwd()  # Current working directory
        ]
        
        inventory_data = None
        inventory_files = []
        
        # Search all possible directories
        for output_dir in possible_dirs:
            if not os.path.exists(output_dir):
                continue
                
            logger.info(f"Checking directory: {output_dir}")
            
            # First try inventory.json
            inventory_path = os.path.join(output_dir, 'inventory.json')
            if os.path.exists(inventory_path):
                logger.info(f"Reading inventory from {inventory_path}")
                with open(inventory_path, 'r') as f:
                    inventory_data = json.load(f)
                break
            
            # Then try inventory_*.json files
            found_files = glob.glob(os.path.join(output_dir, 'inventory_*.json'))
            if found_files:
                inventory_files.extend(found_files)
        
        # If we found timestamped files, use the latest one
        if not inventory_data and inventory_files:
            latest_file = max(inventory_files, key=os.path.getctime)
            logger.info(f"Reading inventory from {latest_file}")
            with open(latest_file, 'r') as f:
                inventory_data = json.load(f)
        
        if not inventory_data:
            logger.error("No inventory file found in any directory")
            logger.error(f"Searched directories: {possible_dirs}")
            return None
        
        # Extract inventory data
        inventory = inventory_data.get('inventory', {})
        inventory_items = inventory.get('items', [])
        inventory_date = inventory.get('date', datetime.now().strftime("%Y-%m-%d"))
        
        logger.info(f"Inventory data structure: {list(inventory_data.keys())}")
        logger.info(f"Inventory items count: {len(inventory_items)}")
        logger.info(f"First item sample: {inventory_items[0] if inventory_items else 'NO ITEMS'}")
        
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
        
        # Process with CrewAI with retry logic
        try:
            logger.info("Initializing CrewAI system...")
            logger.info(f"API Keys available: GEMINI={bool(os.getenv('GEMINI_API_KEY'))}, GOOGLE={bool(os.getenv('GOOGLE_AI_API_KEY'))}")
            
            # Retry logic for rate limiting
            max_retries = 3
            retry_delay = 20  # Start with 20 seconds as suggested by error
            result = None
            
            for attempt in range(max_retries):
                try:
                    crew_instance = SmartShop()
                    
                    logger.info(f"Starting CrewAI processing (attempt {attempt + 1}/{max_retries}) for image: {image_path}")
                    result = crew_instance.crew().kickoff(inputs={'image_path': image_path})
                    
                    logger.info(f"CrewAI processing complete. Result type: {type(result)}")
                    logger.info(f"CrewAI result preview: {str(result)[:200]}...")
                    break  # Success, exit retry loop
                    
                except Exception as crew_error:
                    error_msg = str(crew_error)
                    
                    # Check if it's a rate limit error
                    if 'RateLimitError' in error_msg or '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                        if attempt < max_retries - 1:
                            logger.warning(f"Rate limit hit. Waiting {retry_delay}s before retry {attempt + 2}/{max_retries}...")
                            time.sleep(retry_delay)
                            retry_delay *= 1.5  # Exponential backoff
                            continue
                        else:
                            logger.error("Rate limit exceeded after all retries")
                            raise Exception("Gemini API rate limit exceeded. Please wait a minute and try again.")
                    else:
                        # Not a rate limit error, raise immediately
                        raise
            
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
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {repr(e)}")
            
            # Check if it's a rate limit issue
            is_rate_limit = 'RateLimitError' in str(e) or '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e)
            
            # Check if it's an API key issue
            is_api_key_issue = 'api' in str(e).lower() or 'key' in str(e).lower() or 'auth' in str(e).lower()
            
            if is_api_key_issue:
                logger.error("This appears to be an API key related error!")
                logger.error(f"GEMINI_API_KEY set: {bool(os.getenv('GEMINI_API_KEY'))}")
                logger.error(f"GOOGLE_AI_API_KEY set: {bool(os.getenv('GOOGLE_AI_API_KEY'))}")
            
            # Cleanup on error
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except:
                pass
            
            # User-friendly error message
            if is_rate_limit:
                error_msg = "Gemini API rate limit exceeded (free tier: 5 requests/minute). Please wait 1-2 minutes and try again."
            elif is_api_key_issue:
                error_msg = "API authentication error. Please check your Gemini API key configuration."
            else:
                error_msg = f"Error processing image: {str(e)}"
            
            return jsonify({
                "error": error_msg,
                "error_type": type(e).__name__,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "items": [],
                "retry_after": 60 if is_rate_limit else None
            }), 503 if is_rate_limit else 500
    
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
        
        logger.info(f"Received inventory data: {current_inventory}")
        
        # Load default grocery list
        default_list_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'default_grocery_list.json')
        
        if os.path.exists(default_list_path):
            with open(default_list_path, 'r') as f:
                default_list = json.load(f)
        else:
            logger.error(f"Default grocery list not found at {default_list_path}")
            default_list = {"categories": {}}
        
        # Extract inventory items (lowercase for comparison)
        inventory_items_lower = set()
        current_inv_items = []
        
        for item in current_inventory.get('items', []):
            item_name = item.get('name', '').lower()
            inventory_items_lower.add(item_name)
            
            # Prepare current inventory for response
            current_inv_items.append({
                "name": item.get('name', ''),
                "quantity": item.get('quantity', ''),
                "max": "",  # You can add max calculation if needed
                "percentage": 100  # Assume 100% if we have it
            })
        
        logger.info(f"Current inventory items: {list(inventory_items_lower)}")
        
        # Generate shopping list from default categories
        shopping_list_items = []
        
        # Handle both old format (items array) and new format (categories object)
        if 'categories' in default_list:
            # New nested format
            for category, items in default_list.get('categories', {}).items():
                for item_key, item_data in items.items():
                    # Convert item_key from snake_case to readable format
                    item_name = item_key.replace('_', ' ').title()
                    
                    # Check if item is NOT in current inventory
                    if item_name.lower() not in inventory_items_lower:
                        max_qty = item_data.get('max_per_week', 1)
                        unit = item_data.get('unit', 'unit')
                        
                        shopping_list_items.append({
                            "name": item_name,
                            "quantity": f"{max_qty} {unit}"
                        })
        elif 'items' in default_list:
            # Old flat format
            for item in default_list.get('items', []):
                item_name = item.get('name', '')
                if item_name.lower() not in inventory_items_lower:
                    shopping_list_items.append(item)
        
        logger.info(f"Generated {len(shopping_list_items)} shopping list items")
        
        # Format response to match frontend expectations
        response = {
            "shopping_list": {
                "items": shopping_list_items,
                "total": len(shopping_list_items)
            },
            "current_inventory": {
                "items": current_inv_items,
                "total": len(current_inv_items)
            },
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error generating shopping list: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
