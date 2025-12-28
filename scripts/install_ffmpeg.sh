#!/bin/bash

echo "🔧 Installing FFmpeg (required for audio processing)"
echo ""

# Check if ffmpeg is already installed
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg is already installed"
    ffmpeg -version | head -n 1
    exit 0
fi

echo "FFmpeg not found. Installing..."
echo ""

# Detect OS and install
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux. Please run:"
    echo "  sudo apt-get update && sudo apt-get install -y ffmpeg"
    echo ""
    echo "Or for other Linux distros:"
    echo "  - Fedora/RHEL: sudo dnf install ffmpeg"
    echo "  - Arch: sudo pacman -S ffmpeg"
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS. Installing with Homebrew..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "Homebrew not found. Please install from: https://brew.sh"
        echo "Then run: brew install ffmpeg"
    fi
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "Detected Windows. Please:"
    echo "1. Download FFmpeg from: https://ffmpeg.org/download.html"
    echo "2. Extract and add to PATH"
    echo "Or use: choco install ffmpeg (if you have Chocolatey)"
fi

echo ""
echo "After installing FFmpeg, restart the backend server."
