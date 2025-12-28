#!/bin/bash

echo "🤖 Installing Ollama and AI models"
echo ""

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed"
else
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo ""
echo "Pulling Llama 3.1 8B model (this may take a few minutes)..."
ollama pull llama3.1:8b

echo ""
echo "✅ Ollama setup complete!"
echo ""
echo "You can change models in backend/modules/task_extractor.py"
echo "Available models: llama3.1:8b, mistral:7b, llama2:7b"
echo ""
echo "To list installed models: ollama list"
echo "To run Ollama: ollama serve (runs in background automatically)"
