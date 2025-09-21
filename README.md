# SmartShop Crew with Image Processing

Welcome to the SmartShop Crew project, powered by [crewAI](https://crewai.com) with advanced image processing capabilities. This system combines multi-agent AI collaboration with computer vision to process images and convert them to structured JSON format using Google's Gemini Flash 1.5 model.

## 🚀 Features

- **Multi-Agent AI System**: Collaborative agents for research, reporting, and image processing
- **Image Processing**: Convert images to structured JSON using AI vision
- **OCR Capabilities**: Extract text from images and documents
- **Receipt Processing**: Specialized for processing receipts and invoices
- **Object Detection**: Identify objects, people, and items in images
- **Visual Analysis**: Extract colors, shapes, and visual elements

## 📋 Prerequisites

- Python 3.10+ (Python 3.13.5 recommended)
- Google AI API key (for image processing)
- Internet connection for AI model access

## 🛠️ Installation

### Step 1: Install Python Dependencies

Install all required dependencies:

```bash
# Install core dependencies
python -m pip install crewai python-dotenv google-generativeai Pillow

# Or install all at once
python -m pip install crewai python-dotenv google-generativeai Pillow openai pydantic
```

### Step 2: Verify Installation

Check that all modules are installed correctly:

```bash
python -c "import crewai, google.generativeai, PIL; print('✅ All dependencies installed successfully!')"
```

## 🔧 Environment Setup

### Step 1: Create Environment File

Copy the environment template:

```bash
cp env_template.txt .env
```

### Step 2: Configure Your API Keys

Edit the `.env` file and add your Google AI API key:

```bash
# Required: Google AI API Key for image processing
GOOGLE_AI_API_KEY=your_actual_google_ai_api_key_here

# Optional: Configuration settings
OUTPUT_DIR=./outputs
MAX_TOKENS=4096
TEMPERATURE=0.1
VERBOSE=true
```

### Step 3: Get Your Google AI API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and paste it in your `.env` file

### Step 4: Verify Environment Setup

Run the automated setup script:

```bash
python setup_environment.py
```

This will:
- ✅ Validate your environment variables
- ✅ Test crew initialization
- ✅ Verify all dependencies are working

## 🧪 Testing the Setup

### Quick Test

Test the basic functionality:

```bash
python test_image_crew.py
```

Expected output:
```
🧪 Testing Image Processing Crew Integration
==================================================
Testing ImageToJSONTool...
✅ ImageToJSONTool test successful!
📁 Output saved to: test_output.json

Testing Crew Integration...
✅ Image processor agent found in crew
✅ Image processing task found in crew
✅ Crew integration test successful!

🎉 All tests passed! Image processing crew is ready to use.
```

### Demo Test

Run the complete demonstration:

```bash
python demo_complete_setup.py
```

### Image Processing Test

Test image processing with a sample image:

```bash
python test_image_crew.py
```

## 🖼️ Using Image Processing

### Basic Usage

Process an image and convert it to JSON:

```python
from smart_shop.tools.image_to_json_tool import ImageToJSONTool

# Initialize the tool
tool = ImageToJSONTool()

# Process an image
result = tool._run(
    image_path='path/to/your/image.jpg',
    custom_prompt='Analyze this receipt and extract all items and prices',
    output_path='analysis.json'
)
```

### Crew Usage

Use the full crew system:

```python
from smart_shop.crew import SmartShop

# Initialize the crew
crew_instance = SmartShop()

# Process an image through the crew
result = crew_instance.crew().kickoff(inputs={
    'image_path': 'path/to/your/image.jpg'
})
```

## 📁 Project Structure

```
smart_shop/
├── src/smart_shop/
│   ├── crew.py                    # Main crew configuration
│   ├── config/
│   │   ├── agents.yaml           # Agent definitions
│   │   └── tasks.yaml            # Task definitions
│   └── tools/
│       └── image_to_json_tool.py # Image processing tool
├── .env                          # Environment variables
├── env_template.txt             # Environment template
├── setup_environment.py         # Setup script
└── test_image_crew.py           # Test script
```

## 🎯 Available Agents

- **Researcher**: Conducts research on specified topics
- **Reporting Analyst**: Creates detailed reports from research data
- **Image Processor**: Converts images to structured JSON format

## 📝 Available Tasks

- **Research Task**: Gathers information on specified topics
- **Reporting Task**: Generates comprehensive reports
- **Image Processing Task**: Analyzes images and extracts structured data

## 🔍 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'crewai'"**
```bash
python -m pip install crewai
```

**"GOOGLE_AI_API_KEY not set"**
- Check your `.env` file has the correct API key
- Ensure the key is valid and active

**"Image file not found"**
- Verify the image path is correct
- Check file permissions

**"Python command not found"**
- Use `python3` instead of `python`
- Or create an alias: `alias python=python3`

### Debug Mode

Enable verbose logging by setting `VERBOSE=true` in your `.env` file.

## 📚 Documentation

- Check the troubleshooting section above for common issues
- Review the setup instructions in this README
- Visit [crewAI documentation](https://docs.crewai.com) for advanced usage

## 🚀 Quick Start Commands

```bash
# 1. Setup environment
python setup_environment.py

# 2. Test the system
python test_image_crew.py

# 3. Run demo
python demo_complete_setup.py

# 4. Test image processing
python test_image_crew.py
```

## 🤝 Support

For support, questions, or feedback:
- Check the troubleshooting section above
- Review the documentation files
- Visit [crewAI documentation](https://docs.crewai.com)
- Join the [crewAI Discord](https://discord.com/invite/X4JWnZnxPb)
- Reach out through the [GitHub repository](https://github.com/joaomdmoura/crewai)

Let's create wonders together with the power and simplicity of crewAI! 🚀
