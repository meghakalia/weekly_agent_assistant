# Image to JSON Agent - Command Reference

This document contains all the commands needed to set up, run, and use the Image to JSON Agent.

## 🚀 Quick Start Commands

### 1. Environment Setup

```bash
# Navigate to project directory
cd /Users/rahulpyne/repo/smartshop

# Create virtual environment
python3 -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Activate virtual environment (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. API Key Setup

```bash
# Set your Google AI API key (replace with your actual key)
export GOOGLE_AI_API_KEY="your_actual_api_key_here"

# To make it permanent, add to your shell profile:
echo 'export GOOGLE_AI_API_KEY="your_actual_api_key_here"' >> ~/.zshrc
# or for bash:
echo 'export GOOGLE_AI_API_KEY="your_actual_api_key_here"' >> ~/.bashrc

# Reload your shell configuration
source ~/.zshrc  # or source ~/.bashrc
```

### 3. Verify Setup

```bash
# Check if everything is working
python image_to_json_agent.py --help
```

## 📋 All Commands

### Environment Commands

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install/upgrade dependencies
pip install -r requirements.txt
pip install --upgrade pip

# Deactivate virtual environment
deactivate
```

### API Key Commands

```bash
# Set API key for current session
export GOOGLE_AI_API_KEY="your_api_key_here"

# Check if API key is set
echo $GOOGLE_AI_API_KEY

# Set API key permanently (macOS/Linux)
echo 'export GOOGLE_AI_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc

# Set API key permanently (Windows)
# Add to environment variables through System Properties
```

### Basic Usage Commands

```bash
# Convert image to JSON (basic)
python image_to_json_agent.py path/to/image.jpg

# Convert with custom output file
python image_to_json_agent.py path/to/image.jpg -o my_output.json

# Convert with custom prompt
python image_to_json_agent.py path/to/image.jpg -p "Extract all text and describe objects"

# Convert with API key parameter
python image_to_json_agent.py path/to/image.jpg --api-key "your_api_key_here"

# Convert with custom token limit
python image_to_json_agent.py path/to/image.jpg --max-tokens 8192
```

### Advanced Usage Commands

```bash
# Full command with all options
python image_to_json_agent.py ./sample_image.png \
    -o detailed_analysis.json \
    -p "Analyze this image and extract all text, objects, and colors" \
    --max-tokens 4096

# Process multiple images (using shell loop)
for image in *.jpg; do
    python image_to_json_agent.py "$image" -o "${image%.jpg}.json"
done

# Process with different prompts
python image_to_json_agent.py image.jpg -p "Focus on text extraction only"
python image_to_json_agent.py image.jpg -p "Describe the scene and objects"
python image_to_json_agent.py image.jpg -p "Extract colors and visual elements"
```

### Development Commands

```bash
# Run example usage script
python example_usage.py

# Check code formatting
black image_to_json_agent.py

# Check code style
flake8 image_to_json_agent.py

# Run tests (if available)
pytest

# Install development dependencies
pip install pytest black flake8
```

### File Management Commands

```bash
# Create output directory
mkdir -p outputs

# Process all images in a directory
for img in images/*.{jpg,png,gif}; do
    if [ -f "$img" ]; then
        python image_to_json_agent.py "$img" -o "outputs/$(basename "$img").json"
    fi
done

# Clean up output files
rm -f *.json
rm -f outputs/*.json

# List all JSON outputs
ls -la *.json
```

### Troubleshooting Commands

```bash
# Check Python version
python3 --version

# Check pip version
pip3 --version

# Check installed packages
pip list

# Check if virtual environment is active
which python

# Verify API key is set
echo $GOOGLE_AI_API_KEY

# Test API connection
python -c "import google.generativeai as genai; print('API connection test')"

# Check image file
file path/to/your/image.jpg

# Validate image with Python
python -c "from PIL import Image; Image.open('path/to/image.jpg').verify(); print('Image is valid')"
```

### Batch Processing Commands

```bash
# Process all images in current directory
for file in *.{jpg,jpeg,png,gif,bmp,tiff,webp}; do
    if [ -f "$file" ]; then
        echo "Processing: $file"
        python image_to_json_agent.py "$file" -o "${file%.*}.json"
    fi
done

# Process with progress tracking
total=$(ls *.jpg *.png 2>/dev/null | wc -l)
count=0
for file in *.jpg *.png; do
    if [ -f "$file" ]; then
        count=$((count + 1))
        echo "[$count/$total] Processing: $file"
        python image_to_json_agent.py "$file" -o "${file%.*}.json"
    fi
done
```

### Utility Commands

```bash
# Make scripts executable
chmod +x image_to_json_agent.py
chmod +x example_usage.py
chmod +x setup_commands.sh

# Run setup script
./setup_commands.sh

# Check file permissions
ls -la *.py

# Create sample image for testing
# (You'll need to provide your own test image)
cp /path/to/your/test/image.jpg sample_image.jpg
```

## 🔧 Environment Variables

```bash
# Required
export GOOGLE_AI_API_KEY="your_api_key_here"

# Optional
export OUTPUT_DIR="./outputs"
export MAX_TOKENS="4096"
export DEFAULT_PROMPT="Analyze this image and provide structured JSON output"
```

## 📁 File Structure

```
smartshop/
├── image_to_json_agent.py    # Main agent script
├── example_usage.py          # Example usage script
├── requirements.txt          # Python dependencies
├── setup_commands.sh         # Automated setup script
├── README.md                 # Documentation
├── COMMANDS.md              # This command reference
├── env_example.txt          # Environment variables example
└── venv/                    # Virtual environment (created)
```

## 🚨 Common Issues and Solutions

### Issue: "API key not provided"
```bash
# Solution: Set the API key
export GOOGLE_AI_API_KEY="your_api_key_here"
```

### Issue: "ModuleNotFoundError"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: "Invalid image file"
```bash
# Solution: Check image format and file integrity
file path/to/image.jpg
python -c "from PIL import Image; Image.open('path/to/image.jpg').verify()"
```

### Issue: "Permission denied"
```bash
# Solution: Make scripts executable
chmod +x image_to_json_agent.py
```

## 📊 Performance Tips

```bash
# Use smaller images for faster processing
# Resize images before processing
python -c "
from PIL import Image
img = Image.open('large_image.jpg')
img.thumbnail((1024, 1024))
img.save('resized_image.jpg')
"

# Process in batches to avoid rate limits
# Add delays between requests if needed
```

## 🔍 Monitoring and Logging

```bash
# Run with verbose output
python image_to_json_agent.py image.jpg -v

# Save logs to file
python image_to_json_agent.py image.jpg 2>&1 | tee processing.log

# Monitor API usage
# Check your Google AI Studio dashboard for usage statistics
```

This command reference should help you get started and troubleshoot any issues with the Image to JSON Agent!
