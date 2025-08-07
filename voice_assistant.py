import os
import tempfile
import subprocess
import re
import datetime
from flask import request, jsonify
import json

# Try to import speech recognition - fallback to simpler approach if not available
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

def handle_voice_command(audio_file):
    """Process voice commands using speech recognition and respond appropriately"""
    try:
        # Save the audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
            tmp_file.write(audio_file.read())
            tmp_file_path = tmp_file.name
        
        transcript = ""
        
        if SPEECH_RECOGNITION_AVAILABLE:
            # Convert webm to wav for speech recognition
            try:
                r = sr.Recognizer()
                r.energy_threshold = 300  # Adjust for background noise
                r.dynamic_energy_threshold = True
                
                # Convert webm to wav using ffmpeg
                wav_path = tmp_file_path.replace('.webm', '.wav')
                
                print(f"Converting audio from {tmp_file_path} to {wav_path}")
                
                # Convert using ffmpeg with better settings
                result = subprocess.run([
                    'ffmpeg', '-i', tmp_file_path, 
                    '-acodec', 'pcm_s16le',  # 16-bit PCM
                    '-ar', '16000',          # Sample rate 16kHz
                    '-ac', '1',              # Mono channel
                    '-y',                    # Overwrite output
                    wav_path
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"FFmpeg error: {result.stderr}")
                    raise subprocess.CalledProcessError(result.returncode, "ffmpeg")
                
                print(f"Audio converted successfully to {wav_path}")
                
                # Now try to recognize the WAV file
                with sr.AudioFile(wav_path) as source:
                    # Adjust for ambient noise
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = r.record(source)
                    
                    print("Attempting speech recognition...")
                    transcript = r.recognize_google(audio_data)
                    print(f"Recognized: {transcript}")
                
                # Clean up WAV file
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
                    
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg conversion failed: {e}")
                transcript = "Sorry, I couldn't process the audio format. Please try again."
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                transcript = "I couldn't understand what you said. Please speak clearly and try again."
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service: {e}")
                transcript = "Speech recognition service is temporarily unavailable."
            except Exception as e:
                print(f"Speech recognition error: {e}")
                transcript = "There was an error processing your voice. Please try again."
        else:
            # Fallback - simulate speech recognition for demo
            transcript = "Voice command received (speech recognition not fully installed)"
        
        # Clean up original temp file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        
        # Process the command
        if transcript and len(transcript.strip()) > 0 and "couldn't" not in transcript and "error" not in transcript:
            command_result = process_command(transcript)
            return {
                'transcript': transcript,
                **command_result
            }
        else:
            return {
                'transcript': transcript,
                'reply': transcript if "couldn't" in transcript or "error" in transcript else "I didn't catch that. Could you please try speaking again?",
                'action': 'error'
            }
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return {
            'transcript': '',
            'reply': "Sorry, there was an error processing your voice command. Please try again.",
            'action': 'error'
        }

def process_command(text):
    """Parse and process the transcribed command"""
    text_lower = text.lower()
    
    # Check for task commands first
    task_result = check_task_commands(text_lower, text)
    if task_result:
        return task_result
    
    # Check for habit tracking commands
    habit_result = check_habit_commands(text_lower)
    if habit_result:
        return habit_result
    
    # Check for general assistant commands
    general_result = check_general_commands(text_lower, text)
    if general_result:
        return general_result
    
    # If no specific command is detected, treat as a chat message
    from assistant import get_ai_reply
    reply = get_ai_reply(text)
    
    return {
        'reply': reply,
        'action': 'chat'
    }

def check_task_commands(text_lower, original_text):
    """Check for task-related commands"""
    
    # Add task/event patterns
    add_task_patterns = [
        r"(add|create|schedule|plan|set up|make|new)\s+(task|event|appointment|meeting|reminder|todo|item)",
        r"(remind me to|schedule|plan to|need to|have to|should)\s+(.+)",
        r"(tomorrow|today|next week|this week|monday|tuesday|wednesday|thursday|friday|saturday|sunday).+(meeting|appointment|call|task|event)"
    ]
    
    # Check for add task commands
    for pattern in add_task_patterns:
        match = re.search(pattern, text_lower)
        if match:
            # Extract task details
            task_text = extract_task_from_text(original_text)
            date_time = extract_datetime_from_text(original_text)
            
            if task_text:
                from app import create_task_via_voice
                result = create_task_via_voice(task_text, date_time)
                
                return {
                    'reply': f"I've added '{task_text}' to your tasks{' for ' + date_time if date_time else ''}.",
                    'action': 'task_updated',
                    'task_added': task_text
                }
    
    # Complete task patterns
    complete_patterns = [
        r"(complete|done|finished|mark as done|check off)\s+(.+)",
        r"(completed|did|finished)\s+(.+)"
    ]
    
    for pattern in complete_patterns:
        match = re.search(pattern, text_lower)
        if match:
            task_name = match.group(2).strip()
            
            return {
                'reply': f"Task completion will be available in the tasks page. You can mark '{task_name}' as complete there.",
                'action': 'task_info'
            }
    
    # List tasks patterns
    list_patterns = [
        r"(what|show|list|tell me).+(tasks|schedule|todo|events|appointments)",
        r"(what's|whats).+(on my|my).+(schedule|calendar|todo)",
        r"(show me|list).+(today|tomorrow|this week|next week)"
    ]
    
    for pattern in list_patterns:
        if re.search(pattern, text_lower):
            return {
                'reply': "You can view all your tasks on the Tasks page. I can help you add new tasks through voice commands!",
                'action': 'task_info'
            }
    
    return None

def extract_task_from_text(text):
    """Extract task description from natural language"""
    # Common patterns to extract the actual task
    patterns = [
        r"remind me to (.+)",
        r"schedule (.+)",
        r"add (.+) to",
        r"need to (.+)",
        r"have to (.+)",
        r"should (.+)",
        r"plan to (.+)",
        r"create (.+) task",
        r"new (.+) task",
        r"make (.+) appointment"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1).strip()
    
    # If no pattern matches, try to extract the main content
    # Remove common command words
    words_to_remove = ['add', 'create', 'schedule', 'plan', 'set up', 'make', 'new', 'task', 'event', 'appointment', 'meeting', 'reminder', 'todo', 'agenda', 'item']
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in words_to_remove]
    
    if len(filtered_words) > 2:
        return ' '.join(filtered_words)
    
    return text.strip()

def extract_datetime_from_text(text):
    """Extract date/time information from text"""
    text_lower = text.lower()
    
    # Simple date/time extraction
    if 'tomorrow' in text_lower:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')
    elif 'today' in text_lower:
        return datetime.date.today().strftime('%Y-%m-%d')
    elif 'next week' in text_lower:
        next_week = datetime.date.today() + datetime.timedelta(weeks=1)
        return next_week.strftime('%Y-%m-%d')
    elif 'this week' in text_lower:
        return datetime.date.today().strftime('%Y-%m-%d')
    
    # Days of the week
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for i, day in enumerate(days):
        if day in text_lower:
            # Find the next occurrence of this day
            today = datetime.date.today()
            days_ahead = i - today.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            target_date = today + datetime.timedelta(days_ahead)
            return target_date.strftime('%Y-%m-%d')
    
    return None

def check_general_commands(text_lower, original_text):
    """Check for general assistant commands"""
    
    # Time/date queries
    if any(phrase in text_lower for phrase in ['what time', 'current time', 'what day', 'what date']):
        now = datetime.datetime.now()
        return {
            'reply': f"It's currently {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}.",
            'action': 'time_query'
        }
    
    # Weather (placeholder)
    if any(phrase in text_lower for phrase in ['weather', 'temperature', 'forecast']):
        return {
            'reply': "I don't have access to weather data yet, but you can check your local weather app or ask me to add weather integration!",
            'action': 'weather_query'
        }
    
    # System commands
    if any(phrase in text_lower for phrase in ['open', 'launch', 'start']):
        # Extract app name
        apps = ['safari', 'chrome', 'firefox', 'mail', 'calendar', 'notes', 'messages', 'facetime', 'music', 'spotify']
        for app in apps:
            if app in text_lower:
                return {
                    'reply': f"I would open {app} for you, but I need permission to control your system. You can manually open {app} for now.",
                    'action': 'system_command',
                    'app': app
                }
    
    return None

def check_habit_commands(text):
    """Check for habit-related commands in the text"""
    # Pattern for completing a habit today
    complete_pattern = r"(complete|finished|did|mark|check|done|completed).*?(habit|task|chore|activity|goal).*?(called|named|labeled|known as)?[\s\"]*([\w\s]+?)[\s\"]*(?:today|now|just now|for today|for the day)?[\.\?]?$"
    
    # Pattern for adding a new habit
    add_habit_pattern = r"(add|create|make|start).*?(habit|routine).*?(called|named|labeled)?[\s\"]*([\w\s]+?)[\s\"]*[\.\?]?$"
    
    # NEW: Pattern for creating tasks (more sophisticated than habits)
    add_task_pattern = r"(add|create|make|schedule).*?(task|appointment|meeting|reminder|todo).*?(called|named|labeled|for|to)?[\s\"]*([\w\s]+?)[\s\"]*(?:with|at|by|due|priority)?[\s\"]*(high|medium|low|urgent|important)?.*?[\.\?]?$"
    
    # Check for task creation (prioritize over habit creation)
    task_match = re.search(add_task_pattern, text, re.IGNORECASE)
    if task_match:
        task_title = task_match.group(4).strip()
        priority_text = task_match.group(5)
        
        # Determine priority
        priority = 'medium'  # default
        if priority_text:
            if priority_text.lower() in ['high', 'urgent', 'important']:
                priority = 'high'
            elif priority_text.lower() in ['low']:
                priority = 'low'
        
        # Smart priority detection from task title
        title_lower = task_title.lower()
        if any(word in title_lower for word in ['urgent', 'asap', 'important', 'critical', 'deadline']):
            priority = 'high'
        elif any(word in title_lower for word in ['someday', 'maybe', 'eventually', 'when possible']):
            priority = 'low'
        
        # Smart category detection
        category = 'other'  # default
        if any(word in title_lower for word in ['meeting', 'call', 'email', 'project', 'work', 'office']):
            category = 'work'
        elif any(word in title_lower for word in ['exercise', 'gym', 'doctor', 'health', 'workout']):
            category = 'health'
        elif any(word in title_lower for word in ['learn', 'study', 'read', 'course', 'training']):
            category = 'learning'
        elif any(word in title_lower for word in ['family', 'friend', 'personal', 'home', 'shopping']):
            category = 'personal'
        
        if task_title:
            # Create task in database
            import datetime
            task_data = {
                'title': task_title,
                'description': f'Created via voice command: "{text}"',
                'priority': priority,
                'category': category,
                'dueDate': None,  # Could be enhanced to parse dates from speech
                'completed': False,
                'createdAt': datetime.datetime.now().isoformat()
            }
            
            try:
                from app import create_task_in_db
                success = create_task_in_db(task_data)
                
                if success:
                    return {
                        'reply': f"Perfect! I've created a {priority} priority task: '{task_title}' in your {category} category. The task has been added to your task management system.",
                        'action': 'task_created'
                    }
                else:
                    return {
                        'reply': f"I understood you want to create the task '{task_title}', but there was an issue saving it. Please try again or add it manually.",
                        'action': 'task_error'
                    }
            except Exception as e:
                return {
                    'reply': f"I understood you want to create the task '{task_title}', but the task system isn't available right now. Let me remember that for you instead.",
                    'action': 'task_fallback'
                }
    
    # Check for completing a habit
    complete_match = re.search(complete_pattern, text)
    if complete_match:
        habit_name = complete_match.group(4).strip()
        from app import get_habits_from_db, save_habit_date
        
        habits = get_habits_from_db()
        
        # Find the best matching habit name
        best_match = None
        if habit_name:
            # Simple fuzzy match for habit names
            for existing_habit in habits.keys():
                if habit_name.lower() in existing_habit.lower() or existing_habit.lower() in habit_name.lower():
                    best_match = existing_habit
                    break
        
        if best_match:
            # Get today's date
            today = datetime.date.today().isoformat()
            save_habit_date(best_match, today)
            
            return {
                'reply': f"Excellent work! I've marked '{best_match}' as complete for today. Keep up the great momentum!",
                'action': 'habit_updated'
            }
        else:
            return {
                'reply': f"I couldn't find a habit called '{habit_name}'. Would you like me to create it as a new habit or perhaps you meant to create a task instead?",
                'action': 'habit_not_found'
            }
    
    # Check for adding a new habit
    habit_match = re.search(add_habit_pattern, text)
    if habit_match:
        habit_name = habit_match.group(4).strip()
        if habit_name:
            from app import add_habit_to_db
            add_habit_to_db(habit_name)
            
            return {
                'reply': f"Great choice! I've added '{habit_name}' as a new habit to track. Building consistent habits is key to long-term success. Would you like to mark it as complete for today?",
                'action': 'habit_created'
            }
    
    # If not a habit or task command, return None so we pass to general chat
    return None
