#!/bin/bash

echo "🚀 Setting up AI Meeting Tracker - Prototype"
echo "✨ Pure Python virtual environment - no system dependencies needed!"
echo ""

# Check Python version
echo "Checking Python version (requires 3.8+)..."
python3 --version

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies (OpenAI Whisper + Ollama)..."
echo "This may take a few minutes and download ~1GB of packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Install Ollama (one-time): ./scripts/install_ollama.sh"
echo "2. Activate venv: cd backend && source venv/bin/activate"
echo "3. Run backend: python main.py"
