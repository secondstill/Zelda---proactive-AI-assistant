#!/bin/bash

echo "Setting up Zelda AI Assistant..."

# Check if virtual environment exists
if [ ! -d "venvc" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venvc
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venvc/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install additional system dependencies for speech recognition
echo "Checking system dependencies..."

# For macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS - checking for portaudio..."
    if ! brew list portaudio &>/dev/null; then
        echo "Installing portaudio via Homebrew..."
        brew install portaudio
    fi
fi

# For Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux - you may need to install: sudo apt-get install python3-pyaudio"
fi

echo "Setup complete!"
echo ""
echo "To start Zelda AI Assistant:"
echo "1. source venvc/bin/activate"
echo "2. python app.py"
echo ""
echo "Then open http://localhost:5000 in your browser"
echo ""
echo "For desktop integration:"
echo "python desktop_integration.py web"
