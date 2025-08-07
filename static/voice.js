// Voice Assistant Interface

// Global variables for recording
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let voiceAssistantActive = false;

// Initialize voice assistant functionality
function initVoiceAssistant() {
    const voiceButton = document.createElement('button');
    voiceButton.id = 'voice-assistant-btn';
    voiceButton.className = 'voice-assistant-btn';
    voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
    voiceButton.title = 'Voice Assistant';
    
    // Status indicator
    const statusIndicator = document.createElement('div');
    statusIndicator.id = 'voice-status';
    statusIndicator.className = 'voice-status';
    statusIndicator.textContent = 'Click to speak';
    
    // Voice assistant container
    const voiceContainer = document.createElement('div');
    voiceContainer.id = 'voice-assistant';
    voiceContainer.className = 'voice-assistant';
    voiceContainer.appendChild(voiceButton);
    voiceContainer.appendChild(statusIndicator);
    
    document.body.appendChild(voiceContainer);
    
    // Speech feedback element (where assistant responses will show)
    const speechFeedback = document.createElement('div');
    speechFeedback.id = 'speech-feedback';
    speechFeedback.className = 'speech-feedback';
    document.body.appendChild(speechFeedback);
    
    // Set up event listeners
    voiceButton.addEventListener('click', toggleRecording);
    
    // Check if browser supports required APIs
    if (!navigator.mediaDevices || !window.MediaRecorder) {
        statusIndicator.textContent = 'Voice recording not supported in this browser';
        voiceButton.disabled = true;
        return;
    }
    
    // Load FontAwesome for icons if not already loaded
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const fontAwesome = document.createElement('link');
        fontAwesome.rel = 'stylesheet';
        fontAwesome.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css';
        document.head.appendChild(fontAwesome);
    }
}

// Toggle recording state
function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

// Start recording audio
function startRecording() {
    const voiceButton = document.getElementById('voice-assistant-btn');
    const statusIndicator = document.getElementById('voice-status');
    
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
            
            mediaRecorder.addEventListener('stop', processAudio);
            
            // Update UI to show recording state
            isRecording = true;
            voiceButton.classList.add('recording');
            voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
            statusIndicator.textContent = 'Listening...';
            
            // Start recording
            mediaRecorder.start();
            
            // Auto-stop after 10 seconds if user doesn't stop manually
            setTimeout(() => {
                if (isRecording) {
                    stopRecording();
                }
            }, 10000);
        })
        .catch(error => {
            console.error('Error accessing microphone:', error);
            statusIndicator.textContent = 'Could not access microphone';
        });
}

// Stop recording audio
function stopRecording() {
    if (mediaRecorder && isRecording) {
        // Update UI
        isRecording = false;
        const voiceButton = document.getElementById('voice-assistant-btn');
        const statusIndicator = document.getElementById('voice-status');
        
        voiceButton.classList.remove('recording');
        voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        statusIndicator.textContent = 'Processing...';
        
        // Stop the recorder
        mediaRecorder.stop();
        
        // Stop all audio tracks
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
}

// Process the recorded audio
function processAudio() {
    const statusIndicator = document.getElementById('voice-status');
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    
    formData.append('audio', audioBlob, 'recording.webm');
    
    // Send to server for processing
    fetch('/api/voice', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        statusIndicator.textContent = 'Click to speak';
        
        // Display transcription and response
        if (data.transcript) {
            showSpeechFeedback('You: ' + data.transcript);
        }
        
        if (data.reply) {
            // Wait a moment before showing the AI response (feels more natural)
            setTimeout(() => {
                showSpeechFeedback('Zelda: ' + data.reply, true);
                speakResponse(data.reply);
                
                // If there was an action performed, refresh relevant data
                if (data.action === 'habit_updated') {
                    loadHabits(); // Reload habits if they were updated
                }
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Error processing audio:', error);
        statusIndicator.textContent = 'Error processing speech';
    });
}

// Display speech feedback on screen
function showSpeechFeedback(text, isAssistant = false) {
    const feedbackContainer = document.getElementById('speech-feedback');
    const message = document.createElement('div');
    message.className = isAssistant ? 'assistant-message' : 'user-message';
    message.textContent = text;
    
    feedbackContainer.appendChild(message);
    feedbackContainer.scrollTop = feedbackContainer.scrollHeight;
    
    // Show the feedback container if not already visible
    feedbackContainer.classList.add('active');
    
    // Auto-hide feedback after 8 seconds of no new messages
    clearTimeout(window.feedbackTimeout);
    window.feedbackTimeout = setTimeout(() => {
        feedbackContainer.classList.remove('active');
    }, 8000);
}

// Speak the assistant's response with enhanced voice settings
function speakResponse(text) {
    // Check if browser supports speech synthesis
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.85;  // Slightly slower for clarity
        utterance.pitch = 1.2;  // Higher pitch for friendlier tone
        utterance.volume = 0.9; // Slightly lower volume
        
        // Enhanced voice selection for more natural sound
        const voices = window.speechSynthesis.getVoices();
        const preferredVoices = [
            'Samantha',           // macOS premium voice
            'Victoria',           // macOS premium voice  
            'Karen',              // macOS premium voice
            'Allison',            // macOS premium voice
            'Google UK English Female',
            'Microsoft Zira',     // Windows
            'Microsoft Aria',     // Windows
            'Google Deutsch Female',
            'Alex'                // Fallback
        ];
        
        let selectedVoice = null;
        for (const voiceName of preferredVoices) {
            selectedVoice = voices.find(voice => 
                voice.name.includes(voiceName) || 
                voice.name.toLowerCase().includes('female') ||
                (voice.gender && voice.gender === 'female')
            );
            if (selectedVoice) break;
        }
        
        if (selectedVoice) {
            utterance.voice = selectedVoice;
            console.log(`🎙️ Using voice: ${selectedVoice.name}`);
        }
        
        // Add slight pause before speaking for natural flow
        setTimeout(() => {
            window.speechSynthesis.speak(utterance);
        }, 200);
    }
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    // Check if we're on a page that should have the voice assistant
    if (document.body.classList.contains('no-voice-assistant')) {
        return;
    }
    
    initVoiceAssistant();
    
    // Prefetch voices (helps with speech synthesis)
    if ('speechSynthesis' in window) {
        window.speechSynthesis.getVoices();
    }
});
