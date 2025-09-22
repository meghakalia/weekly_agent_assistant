from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import base64
from io import BytesIO
from PIL import Image
import os

app = Flask(__name__)

# Enable CORS for frontend connection
CORS(app, origins=["http://localhost:3000", "https://your-frontend-domain.com"])

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image_to_inventory(image_data):
    """
    Process uploaded image and extract inventory information.
    Replace this with your actual AI/ML processing logic.
    """
    # Mock inventory data - replace with actual image processing
    mock_inventory = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "items": [
            {
                "name": "Milk",
                "quantity": 1,
                "unit": "bottle",
                "category": "dairy",
                "expiry_date": "2024-01-15"
            },
            {
                "name": "Bread",
                "quantity": 2,
                "unit": "loaves",
                "category": "bakery",
                "expiry_date": "2024-01-10"
            },
            {
                "name": "Eggs",
                "quantity": 12,
                "unit": "pieces",
                "category": "dairy",
                "expiry_date": "2024-01-20"
            },
            {
                "name": "Apples",
                "quantity": 6,
                "unit": "pieces",
                "category": "fruits",
                "expiry_date": "2024-01-18"
            },
            {
                "name": "Rice",
                "quantity": 1,
                "unit": "kg",
                "category": "grains"
            }
        ]
    }
    
    return mock_inventory

def generate_shopping_suggestions(inventory_data):
    """
    Generate shopping list based on inventory data.
    Replace this with your actual recommendation logic.
    """
    # Mock shopping list - replace with actual logic
    mock_shopping_list = {
        "items": [
            {
                "name": "Milk",
                "quantity": 2,
                "unit": "bottles",
                "category": "dairy",
                "priority": "high"
            },
            {
                "name": "Bread",
                "quantity": 1,
                "unit": "loaf",
                "category": "bakery",
                "priority": "medium"
            },
            {
                "name": "Bananas",
                "quantity": 1,
                "unit": "bunch",
                "category": "fruits",
                "priority": "low"
            },
            {
                "name": "Chicken",
                "quantity": 1,
                "unit": "kg",
                "category": "meat",
                "priority": "high"
            },
            {
                "name": "Yogurt",
                "quantity": 4,
                "unit": "cups",
                "category": "dairy",
                "priority": "medium"
            }
        ]
    }
    
    return mock_shopping_list

@app.route('/')
def root():
    return jsonify({"message": "Inventory Management API is running!"})

@app.route('/api/process-inventory', methods=['POST'])
def process_inventory():
    """
    Process uploaded image and return inventory information.
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
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
            return jsonify({"error": "Invalid image file"}), 400
        
        # Process image and get inventory
        inventory_result = process_image_to_inventory(image_data)
        
        return jsonify(inventory_result)
        
    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500

@app.route('/api/generate-shopping-list', methods=['POST'])
def generate_shopping_list():
    """
    Generate shopping list based on inventory data.
    """
    try:
        # Get JSON data from request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        
        if 'inventory_data' not in data:
            return jsonify({"error": "inventory_data is required"}), 400
        
        # Generate shopping suggestions
        shopping_list = generate_shopping_suggestions(data['inventory_data'])
        
        return jsonify(shopping_list)
        
    except Exception as e:
        return jsonify({"error": f"Error generating shopping list: {str(e)}"}), 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
