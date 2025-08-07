import os
import tempfile
import whisper
import openai
from flask import request, jsonify
import re
import datetime

# Load whisper model once at startup
# Using 'base' model for good balance of accuracy and speed
# Options: 'tiny', 'base', 'small', 'medium', 'large'
model = whisper.load_model("base")

def handle_voice_command(audio_file):
    """Process voice commands using Whisper and respond appropriately"""
    # Transcribe the audio using Whisper
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
            tmp_file.write(audio_file.read())
            tmp_file_path = tmp_file.name
        
        # Transcribe using Whisper
        result = model.transcribe(tmp_file_path)
        transcript = result["text"].strip()
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        if not transcript:
            return {
                'transcript': '',
                'reply': "I couldn't hear what you said. Could you please speak again?"
            }
            
        # Process the command and generate a response
        command_result = process_command(transcript)
        
        return {
            'transcript': transcript,
            **command_result  # This unpacks the reply and any action flags
        }
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return {
            'transcript': '',
            'reply': "Sorry, there was an error processing your voice command."
        }

def process_command(text):
    """Parse and process the transcribed command"""
    text_lower = text.lower()
    
    # Check for habit tracking commands
    habit_result = check_habit_commands(text_lower)
    if habit_result:
        return habit_result
    
    # If no specific command is detected, treat as a chat message
    from app import get_ai_reply
    reply = get_ai_reply(text)
    
    return {
        'reply': reply,
        'action': 'chat'
    }

def check_habit_commands(text):
    """Check for habit-related commands in the text"""
    # Pattern for completing a habit today
    complete_pattern = r"(complete|finished|did|mark|check|done|completed).*?(habit|task|chore|activity|goal).*?(called|named|labeled|known as)?[\s\"]*([\w\s]+?)[\s\"]*(?:today|now|just now|for today|for the day)?[\.\?]?$"
    
    # Pattern for adding a new habit
    add_pattern = r"(add|create|make|start).*?(habit|task|chore|activity|goal).*?(called|named|labeled)?[\s\"]*([\w\s]+?)[\s\"]*[\.\?]?$"
    
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
                'reply': f"Great job! I've marked '{best_match}' as complete for today.",
                'action': 'habit_updated'
            }
        else:
            return {
                'reply': f"I couldn't find a habit called '{habit_name}'. Would you like to create it?",
                'action': 'habit_not_found'
            }
    
    # Check for adding a new habit
    add_match = re.search(add_pattern, text)
    if add_match:
        habit_name = add_match.group(4).strip()
        if habit_name:
            from app import add_habit_to_db
            add_habit_to_db(habit_name)
            
            return {
                'reply': f"I've added a new habit called '{habit_name}'. Would you like to mark it as complete for today?",
                'action': 'habit_created'
            }
    
    # If not a habit command, return None so we pass to general chat
    return None
