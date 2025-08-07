# README: Installing Voice Assistant Features

## Basic Setup (Already Working)
The voice assistant interface is already set up in your application, allowing:
- Microphone recording interface
- Speech synthesis (for Zelda to speak responses)
- UI elements for voice interaction

## Enabling Full Voice Recognition
To enable full voice recognition with OpenAI Whisper, install the required dependencies:

```
# Activate your virtual environment first
source venvc/bin/activate  

# Install the voice recognition dependencies
pip install -r requirements-voice.txt
```

## What's Included
- **OpenAI Whisper**: State-of-the-art speech recognition model
- **PyAudio**: For audio recording and processing
- **Torch**: Required for Whisper model
- **Transformers**: NLP capabilities for understanding commands

## Usage Examples
Once fully enabled, you can use voice commands like:
- "Complete my meditation habit for today"
- "Create a new habit called drink water"
- "Did I finish my exercise habit?"

## Troubleshooting
If you encounter issues with Whisper installation:
1. Make sure you have the latest pip: `pip install --upgrade pip`
2. For macOS, you might need `portaudio`: `brew install portaudio`
3. For Linux, install: `sudo apt-get install python3-pyaudio`

## Lightweight Alternative
If you prefer a simpler solution without the large model downloads:
- Set WHISPER_ENABLED = False in voice_assistant.py
- This will use a simpler speech recognition method
