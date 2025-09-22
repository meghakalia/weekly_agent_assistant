# Inventory Management API

A Flask backend for processing inventory photos and generating smart shopping lists.

## Features

- 📸 Image upload and processing
- 📋 Inventory extraction from photos
- 🛒 Smart shopping list generation
- 🔄 RESTful API with JSON responses
- 🐍 Simple Flask setup for Mac compatibility

## Installation & Setup

### Local Development (Recommended for Mac)

1. **Create a virtual environment**
   \`\`\`bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   \`\`\`

2. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Start the Flask server**
   \`\`\`bash
   python app.py
   \`\`\`

   Or use the run script:
   \`\`\`bash
   chmod +x run.sh
   ./run.sh
   \`\`\`

The server will start at `http://localhost:8000`

## API Endpoints

### 1. Process Inventory Photo
- **POST** `/api/process-inventory`
- Upload an image file and get inventory information
- **Request**: Multipart form with image file
- **Response**: JSON with inventory items

### 2. Generate Shopping List
- **POST** `/api/generate-shopping-list`
- Generate shopping recommendations based on inventory
- **Request**: JSON with inventory data
- **Response**: JSON with shopping list items

### 3. Health Check
- **GET** `/health`
- Check if the API is running

## Connecting to Frontend

Make sure your frontend is configured to call:
- `http://localhost:8000/api/process-inventory`
- `http://localhost:8000/api/generate-shopping-list`

The backend is already configured to accept requests from `http://localhost:3000`.

## Next Steps

1. **Replace Mock Data**: Update the `process_image_to_inventory()` and `generate_shopping_suggestions()` functions with your actual AI/ML logic.

2. **Add Database**: Integrate with a database to store inventory history and user preferences.

3. **Add Authentication**: Implement user authentication if needed.

4. **Deploy**: Deploy to your preferred cloud platform (AWS, GCP, Azure, etc.).

## Development

The Flask server runs in debug mode during development. Any changes to the code will restart the server automatically.

## Troubleshooting

- **CORS Issues**: The Flask-CORS extension is configured to accept requests from localhost:3000
- **File Upload Issues**: Check file size limits (16MB max) and supported formats (png, jpg, jpeg, gif, bmp, webp)
- **Port Conflicts**: Change the port in `app.py` if 8000 is already in use
- **Mac Issues**: Flask should run smoothly on Mac with the simplified dependencies
