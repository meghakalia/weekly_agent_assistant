#!/bin/bash

# Exit on error
set -e

echo "🔧 Starting build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create outputs directory
echo "📁 Creating outputs directory..."
mkdir -p outputs /tmp/outputs

echo "✅ Build complete!"
