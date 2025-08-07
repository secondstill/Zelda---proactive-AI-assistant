#!/bin/bash

echo "Setting up voice assistant dependencies..."

if [ -d "venvc" ]; then
    echo "Activating virtual environment..."
    source venvc/bin/activate
    pip install -r requirements-voice.txt
    echo "Voice assistant dependencies installed! You can now use voice features."
else
    echo "Virtual environment not found. Please make sure venvc exists."
fi
