#!/usr/bin/env python3
"""
Quick test script to verify all imports and basic functionality
Run this before deploying to catch errors early
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🧪 Testing Weekly Grocery Agent Setup")
print("=" * 50)

# Test 1: Environment variables
print("\n1️⃣ Checking environment variables...")
from dotenv import load_dotenv
load_dotenv()

gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
if gemini_key:
    print(f"✅ Gemini API key found: {gemini_key[:20]}...")
else:
    print("❌ Gemini API key not found in .env")
    sys.exit(1)

# Test 2: Flask imports
print("\n2️⃣ Testing Flask imports...")
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    print("✅ Flask imports successful")
except ImportError as e:
    print(f"❌ Flask import error: {e}")
    sys.exit(1)

# Test 3: Image processing
print("\n3️⃣ Testing image processing...")
try:
    from PIL import Image
    from io import BytesIO
    print("✅ PIL/Pillow imports successful")
except ImportError as e:
    print(f"❌ PIL import error: {e}")
    sys.exit(1)

# Test 4: Google Gemini
print("\n4️⃣ Testing Google Generative AI...")
try:
    import google.generativeai as genai
    genai.configure(api_key=gemini_key)
    print("✅ Google Generative AI configured")
except Exception as e:
    print(f"❌ Gemini error: {e}")
    sys.exit(1)

# Test 5: CrewAI
print("\n5️⃣ Testing CrewAI imports...")
try:
    from smart_shop.crew import SmartShop
    print("✅ CrewAI SmartShop imported successfully")
except ImportError as e:
    print(f"❌ CrewAI import error: {e}")
    print("   Make sure you're in the project root directory")
    sys.exit(1)

# Test 6: Backend main
print("\n6️⃣ Testing backend main...")
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    # Don't actually import to avoid running the app
    backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'main.py')
    if os.path.exists(backend_path):
        print("✅ Backend main.py exists")
    else:
        print("❌ Backend main.py not found")
        sys.exit(1)
except Exception as e:
    print(f"❌ Backend error: {e}")
    sys.exit(1)

# Test 7: Data files
print("\n7️⃣ Checking data files...")
data_dir = os.path.join(os.path.dirname(__file__), 'data')
if os.path.exists(data_dir):
    print("✅ Data directory exists")
    default_list = os.path.join(data_dir, 'default_grocery_list.json')
    if os.path.exists(default_list):
        print("✅ Default grocery list found")
    else:
        print("⚠️  Default grocery list not found (may be created at runtime)")
else:
    print("⚠️  Data directory not found (will be created)")

# Test 8: Outputs directory
print("\n8️⃣ Checking outputs directory...")
outputs_dir = os.path.join(os.path.dirname(__file__), 'outputs')
if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir)
    print("✅ Created outputs directory")
else:
    print("✅ Outputs directory exists")

print("\n" + "=" * 50)
print("✅ ALL TESTS PASSED!")
print("\nYou're ready to deploy! 🚀")
print("\nNext steps:")
print("1. Commit and push: git add -A && git commit -m 'Fix dependencies' && git push")
print("2. Deploy on Render dashboard")
print("3. Add GEMINI_API_KEY to Render environment variables")
print("\nTo test locally, run: chmod +x test_local.sh && ./test_local.sh")
