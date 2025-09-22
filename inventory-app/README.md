# Inventory App with SmartShop Crew Integration

This FastAPI application integrates the SmartShop Crew for intelligent image processing and inventory management.

## 🚀 Features

- **Smart Image Processing**: Uses SmartShop Crew with AI vision to extract inventory data from receipt images
- **Automatic Data Extraction**: Converts receipt images to structured inventory data
- **Fallback Support**: Graceful fallback to mock data if crew processing fails
- **RESTful API**: Clean API endpoints for frontend integration

## 📋 Prerequisites

- Python 3.10+
- Google AI API key
- All SmartShop Crew dependencies

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd inventory-app
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy from parent directory
cp ../env_template.txt .env

# Edit .env and add your Google AI API key
GOOGLE_AI_API_KEY=your_google_ai_api_key_here
```

### 3. Test Integration

```bash
python test_crew_integration.py
```

### 4. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 API Endpoints

### Upload and Process Image

```http
POST /upload-image
Content-Type: multipart/form-data

Form data:
- image: (file) - Receipt image to process
```

**Response:**
```json
{
  "date": "2024-01-15",
  "items": [
    {
      "name": "Milk",
      "quantity": 1,
      "unit": "bottle",
      "category": "dairy",
      "expiry_date": "2024-01-20"
    }
  ]
}
```

### Generate Shopping List

```http
POST /generate-shopping-list
Content-Type: application/json

{
  "inventory_data": {
    "date": "2024-01-15",
    "items": [...]
  }
}
```

## 🧠 SmartShop Crew Integration

The application uses the SmartShop Crew for intelligent image processing:

### Image Processing Flow

1. **Image Upload**: Receipt image is uploaded via API
2. **Temporary Storage**: Image is saved to temporary file
3. **Crew Workflow**: SmartShop Crew kickoff method processes the image using full agent workflow
4. **Task Execution**: Image processing task is executed by specialized agents
5. **Data Extraction**: Structured data is extracted from the receipt
6. **Inventory Conversion**: Receipt items are converted to inventory format
7. **Response**: Structured inventory data is returned

### Crew Components Used

- **SmartShop Crew**: Full multi-agent workflow for image processing
- **Image Processing Agent**: Specialized in computer vision and OCR
- **Image Processing Task**: Structured task for receipt analysis
- **Image to JSON Tool**: Converts images to structured JSON format
- **AI Vision Model**: Google's Gemini Flash 1.5 for image analysis
- **Crew Kickoff**: Orchestrates the full agent workflow

### Error Handling

- **Graceful Fallback**: Falls back to mock data if crew processing fails
- **Environment Validation**: Checks for required API keys
- **Temporary File Cleanup**: Automatically cleans up temporary files

## 📁 Project Structure

```
inventory-app/
├── main.py                    # FastAPI application with crew integration
├── requirements.txt           # Python dependencies
├── test_crew_integration.py   # Integration tests
├── README.md                  # This file
└── ../src/smart_shop/         # SmartShop Crew components
    ├── crew.py               # Main crew configuration
    ├── tools/                # Crew tools
    └── config/                # Agent and task configurations
```

## 🔍 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'smart_shop'"**
- Ensure the `src` directory is in the Python path
- Check that crew components are properly installed

**"GOOGLE_AI_API_KEY not set"**
- Set your Google AI API key in the `.env` file
- Ensure the key is valid and active

**"Crew initialization failed"**
- Check that all crew dependencies are installed
- Verify environment variables are set correctly
- Run the integration test to diagnose issues

### Debug Mode

Enable verbose logging by setting environment variables:

```bash
export VERBOSE=true
export GOOGLE_AI_API_KEY=your_key_here
```

## 🚀 Usage Examples

### Python Client

```python
import requests

# Upload and process image
with open('receipt.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post('http://localhost:8000/upload-image', files=files)
    inventory_data = response.json()

print(f"Extracted {len(inventory_data['items'])} items")
```

### JavaScript/Frontend

```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

const response = await fetch('/upload-image', {
    method: 'POST',
    body: formData
});

const inventoryData = await response.json();
console.log('Extracted items:', inventoryData.items);
```

## 📊 Performance

- **Processing Time**: ~2-5 seconds per image (depending on image size)
- **Accuracy**: High accuracy for receipt processing with structured output
- **Fallback**: Automatic fallback ensures service availability
- **Memory**: Efficient temporary file handling

## 🔄 Development

### Running Tests

```bash
# Test crew integration
python test_crew_integration.py

# Test with sample images
python -c "
import requests
with open('sample_receipt.jpg', 'rb') as f:
    response = requests.post('http://localhost:8000/upload-image', files={'image': f})
    print(response.json())
"
```

### Adding New Features

1. **New Crew Agents**: Add to `src/smart_shop/config/agents.yaml`
2. **New Tasks**: Add to `src/smart_shop/config/tasks.yaml`
3. **New Tools**: Create in `src/smart_shop/tools/`
4. **API Endpoints**: Add to `main.py`

## 📚 Documentation

- [SmartShop Crew Documentation](../README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [CrewAI Documentation](https://docs.crewai.com/)

## 🤝 Support

For issues with the inventory app integration:
1. Check the troubleshooting section above
2. Run the integration tests
3. Verify environment configuration
4. Review the SmartShop Crew documentation