#!/bin/bash

echo "🚀 Installing Ollama for Llama 3 Local Model Support..."
echo "=" * 60

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is already installed!"
    echo "Current version: $(ollama --version)"
else
    echo "📥 Installing Ollama..."
    
    # Install Ollama
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Ollama installed successfully!"
    else
        echo "❌ Failed to install Ollama"
        exit 1
    fi
fi

echo ""
echo "🔧 Starting Ollama service..."
ollama serve &

# Wait a moment for service to start
sleep 3

echo ""
echo "📥 Downloading Llama 3.1 8B model..."
echo "This may take a while depending on your internet connection..."
ollama pull gemma3:1b

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup Complete!"
    echo "=" * 60
    echo "✅ Ollama installed and running"
    echo "✅ Llama 3.1 8B model downloaded"
    echo ""
    echo "🚀 You can now use the enhanced chatbot with:"
    echo "   python3 EDI_project_enhanced.py"
    echo ""
    echo "💡 Test with:"
    echo "   python3 test_enhanced_chatbot.py"
else
    echo ""
    echo "❌ Failed to download Llama 3 model"
    echo "You can still use the chatbot with Cohere fallback"
fi

echo ""
echo "🔍 To check if everything is working:"
echo "   ollama list"
echo "   curl http://localhost:11434/api/tags"
