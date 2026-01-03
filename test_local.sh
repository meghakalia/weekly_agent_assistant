#!/bin/bash

# Local Testing Script for Weekly Grocery Agent
# Run this to test before deploying to Render

set -e

echo "🧪 Weekly Grocery Agent - Local Testing"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "env_grocery_agent" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv env_grocery_agent
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env_grocery_agent/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your API keys"
    exit 1
fi

# Export environment variables
echo "🔑 Loading environment variables..."
export $(cat .env | grep -v '^#' | xargs)
export OUTPUT_DIR=./outputs
export PORT=8080

# Create outputs directory
mkdir -p outputs

# Test imports
echo ""
echo "🔍 Testing Python imports..."
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from smart_shop.crew import SmartShop
    print('✅ CrewAI imports working')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)

try:
    import google.generativeai as genai
    print('✅ Google Generative AI working')
except Exception as e:
    print(f'❌ Gemini import error: {e}')
    sys.exit(1)

try:
    from flask import Flask
    print('✅ Flask imports working')
except Exception as e:
    print(f'❌ Flask import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "🚀 Starting Flask server..."
    echo "   Backend URL: http://localhost:8080"
    echo "   Health check: http://localhost:8080/health"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the server
    python -m gunicorn backend.main:app --bind 0.0.0.0:8080 --timeout 300 --workers 1 --log-level info --reload
else
    echo ""
    echo "❌ Tests failed! Please fix errors before deploying."
    exit 1
fi
