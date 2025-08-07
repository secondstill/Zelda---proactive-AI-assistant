import requests
import random


def get_ai_reply(user_message):
    """Get AI reply with fallback responses if Ollama is not available"""
    prompt = (
        "You are Zelda, an intelligent and sophisticated AI personal assistant. You are professional, helpful, and empathetic. Your purpose is to help users manage their daily tasks, build productive habits, and achieve their goals through personalized guidance and support. You provide clear, actionable advice while maintaining a warm but professional tone. You can help with task management, habit tracking, productivity tips, and general life organization. Always be encouraging and focus on helping users organize their lives better.\n\nUser: "
        f"{user_message}\nZelda:"
    )
    
    try:
        print("🤖 Attempting to connect to Ollama...")
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': prompt,
                'stream': False
            },
            timeout=10  # Reduced timeout
        )
        response.raise_for_status()
        data = response.json()
        reply = data.get('response', 'I am here for you. How can I help?')
        print("✅ Got response from Ollama")
        return reply
        
    except requests.exceptions.ConnectionError:
        print("❌ Ollama not available, using fallback responses")
        return get_fallback_response(user_message)
    except Exception as e:
        print(f"❌ Error with Ollama: {str(e)}")
        return get_fallback_response(user_message)


def get_fallback_response(user_message):
    """Provide intelligent fallback responses when Ollama is not available"""
    message_lower = user_message.lower()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        responses = [
            "Hello! I'm Zelda, your intelligent personal assistant. I'm here to help you organize your life, manage tasks, and build productive habits. How can I assist you today?",
            "Hi there! Zelda here, ready to help you tackle your goals and optimize your daily routine. What would you like to work on?",
            "Good day! I'm Zelda, and I'm excited to help you achieve more and live more efficiently. What's on your agenda today?"
        ]
        
    # How are you responses
    elif any(word in message_lower for word in ['how are you', 'how do you feel', 'what\'s up']):
        responses = [
            "I'm functioning optimally and ready to help you succeed! As your AI assistant, I'm always here to support your productivity and well-being. What can I help you accomplish?",
            "I'm doing excellently, thank you for asking! I'm particularly energized when helping users like you reach their potential. How can I assist you today?",
            "I'm at your service and operating at full capacity! I love helping people organize their lives and achieve their goals. What would you like to focus on?"
        ]
        
    # Habit-related responses
    elif any(word in message_lower for word in ['habit', 'routine', 'daily', 'exercise', 'workout', 'reading', 'water']):
        responses = [
            "That's fantastic that you're thinking about habits! 💪 Building consistent routines is one of the best investments you can make. What specific habit would you like to work on?",
            "I love helping with habits! 🎯 Small, consistent actions create amazing results over time. Tell me more about what you'd like to improve.",
            "Habits are the foundation of success! 🌱 Whether it's exercise, reading, or any other routine, I'm here to help you stay consistent. What's your goal?"
        ]
        
    # Task/productivity responses
    elif any(word in message_lower for word in ['task', 'work', 'productive', 'busy', 'schedule', 'plan', 'organize']):
        responses = [
            "Let's tackle those tasks together! 📝 I can help you organize your day and stay focused. What's the most important thing you need to accomplish?",
            "Productivity is all about smart planning and consistent action! ⚡ I'm here to help you prioritize and get things done. What's on your to-do list?",
            "Great mindset! 🚀 Breaking big goals into manageable tasks is the key to success. How can I help you organize your day?",
            "I love helping with organization! 📋 The Tasks page is perfect for keeping track of everything you need to do. What would you like to add first?"
        ]
        
    # Goal and achievement responses
    elif any(word in message_lower for word in ['goal', 'achieve', 'success', 'improve', 'better', 'progress']):
        responses = [
            "I'm excited to help you reach your goals! 🎯 Every small step counts toward bigger achievements. What specific area would you like to focus on?",
            "Success is built one day at a time! 🌟 Let's break down your goals into actionable steps. What would you like to work on first?",
            "Progress is the best motivator! 📈 I can help you track your improvements in both tasks and habits. What's your main focus right now?"
        ]
        
    # Motivation/encouragement
    elif any(word in message_lower for word in ['tired', 'stressed', 'difficult', 'hard', 'struggle', 'help']):
        responses = [
            "I hear you, and I want you to know that what you're feeling is completely valid. 💙 Every challenge is an opportunity to grow stronger. Let's take this one step at a time.",
            "You're being so brave by reaching out! 🌟 Remember, even the smallest progress is still progress. What's one tiny thing we can do right now to make you feel better?",
            "I'm here for you! 🤗 Life can be challenging, but you have more strength than you realize. Let's find a small, manageable way to move forward together."
        ]
        
    # Default friendly responses
    else:
        responses = [
            "That's interesting! 😊 I'm here to help you with whatever you're working on. Whether it's building better habits, staying organized, or just having a friendly chat - I'm all ears!",
            "I appreciate you sharing that with me! 🌟 As your AI companion, I'm here to support you in creating positive changes in your life. How can we make today a little bit better?",
            "Thanks for talking with me! 💫 I love helping people discover their potential and build amazing routines. What aspect of your life would you like to improve?"
        ]
    
    return random.choice(responses)


def get_motivation_message():
    """Get motivational message with fallback if Ollama is not available"""
    try:
        print("🤖 Getting motivation from Ollama...")
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': "Give me a short, positive motivational message for today.",
                'stream': False
            },
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        message = data.get('response', 'Stay motivated!')
        print("✅ Got motivation from Ollama")
        return message
        
    except Exception:
        print("❌ Using fallback motivation")
        motivational_messages = [
            "Every small step counts! You're building something amazing. 🌟",
            "Today is full of possibilities. Let's make it count! 💪",
            "You have the power to create positive change. Believe in yourself! ✨",
            "Progress, not perfection. You're doing great! 🚀",
            "Your future self will thank you for the effort you put in today! 🌱",
            "Small consistent actions lead to extraordinary results! 🎯",
            "You're stronger than you think and capable of more than you imagine! 💫"
        ]
        return random.choice(motivational_messages)
