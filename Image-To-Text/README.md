# Image to JSON Agent

A Python agent that converts images to structured JSON format using Google's Gemini Flash 1.5 model.

## Features

- 🖼️ Convert images to structured JSON
- 🤖 Powered by Google Gemini Flash 1.5
- 📝 OCR text extraction
- 🎯 Object detection and description
- 🔧 Customizable prompts
- 📊 Detailed metadata output
- 🚀 Command-line interface

## Prerequisites

- Python 3.8 or higher
- Google AI API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Installation

### 1. Clone or Download the Project

```bash
# If you have the files locally, navigate to the project directory
cd /path/to/image_to_json_agent
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 4. Set Up API Key

#### Option A: Environment Variable (Recommended)
```bash
# Set your Google AI API key
export GOOGLE_AI_API_KEY="your_api_key_here"

# To make it permanent, add to your shell profile:
echo 'export GOOGLE_AI_API_KEY="your_api_key_here"' >> ~/.bashrc
# or for zsh:
echo 'export GOOGLE_AI_API_KEY="your_api_key_here"' >> ~/.zshrc
```

#### Option B: .env File
```bash
# Create .env file
echo "GOOGLE_AI_API_KEY=your_api_key_here" > .env
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Convert an image to JSON
python image_to_json_agent.py path/to/your/image.jpg

# Specify output file
python image_to_json_agent.py path/to/your/image.jpg -o output.json

# Use custom prompt
python image_to_json_agent.py path/to/your/image.jpg -p "Extract all text and describe the objects in this image"

# Set API key directly
python image_to_json_agent.py path/to/your/image.jpg --api-key "your_api_key_here"
```

#### Advanced Usage
```bash
# Set maximum tokens for response
python image_to_json_agent.py path/to/your/image.jpg --max-tokens 8192

# Full example with all options
python image_to_json_agent.py ./sample_image.png \
    -o detailed_analysis.json \
    -p "Analyze this image and extract all text, objects, and colors" \
    --max-tokens 4096
```

### Python API Usage

```python
from image_to_json_agent import ImageToJSONAgent

# Initialize agent
agent = ImageToJSONAgent()  # Uses GOOGLE_AI_API_KEY env var
# or
agent = ImageToJSONAgent(api_key="your_api_key_here")

# Convert image to JSON
result = agent.convert_image_to_json("path/to/image.jpg")

if result["success"]:
    print("JSON Data:", result["json_data"])
    print("Metadata:", result["metadata"])
else:
    print("Error:", result["error"])

# Save to file
agent.save_json_output(result, "output.json")
```

## Example Output

The agent generates structured JSON with the following format:

```json
{
  "success": true,
  "json_data": {
    "description": "A detailed description of the image",
    "text_content": ["Any text found in the image"],
    "objects": ["List of detected objects"],
    "colors": ["Dominant colors"],
    "metadata": {
      "image_analysis": "Additional analysis"
    }
  },
  "metadata": {
    "image_path": "path/to/image.jpg",
    "image_size": [width, height],
    "model": "gemini-1.5-flash",
    "tokens_used": 150,
    "raw_response": "Full model response"
  }
}
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)

## Error Handling

The agent includes comprehensive error handling:

- Invalid image files
- Missing API keys
- Network connectivity issues
- API rate limits
- Malformed responses

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ValueError: API key not provided
   ```
   Solution: Set the `GOOGLE_AI_API_KEY` environment variable or pass it as a parameter.

2. **Invalid Image Error**
   ```
   ValueError: Invalid image file
   ```
   Solution: Ensure the image file exists and is in a supported format.

3. **Import Error**
   ```
   ModuleNotFoundError: No module named 'google.generativeai'
   ```
   Solution: Install dependencies with `pip install -r requirements.txt`

### Getting Help

- Check that your API key is valid and has sufficient quota
- Ensure your image file is not corrupted
- Verify your internet connection
- Check the Google AI API status

## Development

### Running Tests
```bash
# Install development dependencies
pip install pytest

# Run tests (if available)
pytest
```

### Code Formatting
```bash
# Format code with black
black image_to_json_agent.py

# Check code style
flake8 image_to_json_agent.py
```

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section above
- Review the Google AI documentation
- Open an issue in the project repository
