#!/bin/bash

# Image to JSON Agent - Setup Commands
# This script contains all the commands needed to set up and run the agent

echo "🚀 Image to JSON Agent - Setup Commands"
echo "========================================"

# Check if Python is installed
echo "📋 Checking Python installation..."
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found: $(python3 --version)"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is available
echo "📋 Checking pip installation..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 found"
else
    echo "❌ pip3 not found. Please install pip."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo "✅ pip upgraded"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Check API key
echo "🔑 Checking API key setup..."
if [ -z "$GOOGLE_AI_API_KEY" ]; then
    echo "⚠️  GOOGLE_AI_API_KEY not set"
    echo "Please set your Google AI API key:"
    echo "export GOOGLE_AI_API_KEY='your_api_key_here'"
    echo ""
    echo "To get an API key:"
    echo "1. Go to https://makersuite.google.com/app/apikey"
    echo "2. Create a new API key"
    echo "3. Copy the key and set it as shown above"
else
    echo "✅ API key is set"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x image_to_json_agent.py
chmod +x example_usage.py
echo "✅ Scripts made executable"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Set your API key: export GOOGLE_AI_API_KEY='your_api_key_here'"
echo "2. Test the agent: python image_to_json_agent.py your_image.jpg"
echo "3. Run examples: python example_usage.py"
echo ""
echo "📖 For more information, see README.md"
