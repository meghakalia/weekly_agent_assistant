from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths for grocery list files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DEFAULT_GROCERY_LIST_PATH = os.path.join(DATA_DIR, 'default_grocery_list.json')
CURRENT_GROCERY_LIST_PATH = os.path.join(DATA_DIR, 'current_grocery_list.json')

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
        os.makedirs(os.path.dirname(CURRENT_GROCERY_LIST_PATH), exist_ok=True)
        with open(CURRENT_GROCERY_LIST_PATH, 'w') as f:
            json.dump(grocery_list, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving grocery list: {e}")
        return False

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        """Generate shopping list based on current grocery list"""
        try:
            logger.info("Received generate-shopping-list request")
            
            # Load current grocery list
            grocery_list = load_current_grocery_list()
            if not grocery_list:
                logger.error("Could not load grocery list")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Grocery list not available"}).encode())
                return
            
            # Generate shopping list: items needed = max - current
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
            
            # Sort shopping list by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            shopping_items.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
            
            # Sort current items by percentage (lowest first)
            current_items.sort(key=lambda x: x.get('percentage', 0))
            
            logger.info(f"Generated shopping list with {len(shopping_items)} items")
            
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
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        
        except Exception as e:
            logger.error(f"Error generating shopping list: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_GET(self):
        """Handle GET request for grocery list"""
        try:
            grocery_list = load_current_grocery_list()
            if not grocery_list:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Could not load grocery list"}).encode())
                return
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(grocery_list).encode())
        
        except Exception as e:
            logger.error(f"Error getting grocery list: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
