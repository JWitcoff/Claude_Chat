#!/bin/bash
# Setup script for Claude Voice Commands

set -e

echo "🚀 Setting up Claude Voice Commands..."
echo "======================================"

# Check Python version
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run: python3 -m venv venv"
    exit 1
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your ElevenLabs API key:"
    echo "   ELEVENLABS_API_KEY=your_api_key_here"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your ElevenLabs API key to .env file"
echo "2. Test your microphone: python tests/test_microphone.py"
echo "3. Run interactive test: python tests/test_microphone.py --interactive"
echo ""
echo "🎤 Ready to build voice commands!"