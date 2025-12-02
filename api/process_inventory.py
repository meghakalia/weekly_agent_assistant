from http.server import BaseHTTPRequestHandler
import json
import base64
import os
import sys
from io import BytesIO
from PIL import Image
from datetime import datetime
import logging

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
        import glob
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

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """Handle POST request for image processing"""
        try:
            # Parse content type
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' not in content_type:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Content-Type must be multipart/form-data"}).encode())
                return
            
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No data provided"}).encode())
                return
            
            # Read and parse multipart data
            body = self.rfile.read(content_length)
            
            # Simple multipart parsing (looking for image data)
            # In production, use a proper multipart parser
            parts = body.split(b'Content-Type: image/')
            if len(parts) < 2:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "No image found in request"}).encode())
                return
            
            # Extract image data (everything after the second CRLF CRLF)
            image_part = parts[1]
            double_crlf = image_part.find(b'\r\n\r\n')
            if double_crlf == -1:
                double_crlf = image_part.find(b'\n\n')
            
            if double_crlf != -1:
                image_data = image_part[double_crlf + 4:]
                # Remove trailing boundary
                boundary_end = image_data.rfind(b'--')
                if boundary_end != -1:
                    image_data = image_data[:boundary_end]
                image_data = image_data.rstrip(b'\r\n')
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid image format"}).encode())
                return
            
            # Validate image
            try:
                image = Image.open(BytesIO(image_data))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                logger.error(f"Invalid image file: {str(e)}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid image file"}).encode())
                return
            
            # Save image temporarily
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = '/tmp'
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
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(inventory_result).encode())
                
            except Exception as e:
                logger.error(f"CrewAI processing error: {str(e)}", exc_info=True)
                
                # Cleanup on error
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except:
                    pass
                
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": f"Error processing image: {str(e)}",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "items": []
                }).encode())
        
        except Exception as e:
            logger.error(f"Error in handler: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
