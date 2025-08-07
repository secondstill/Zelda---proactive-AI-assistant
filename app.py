import os
from flask import Flask, render_template, jsonify, request, abort
from werkzeug.middleware.proxy_fix import ProxyFix
import json
import sqlite3
from assistant import get_ai_reply, get_motivation_message

# Import voice assistant module
try:
    from voice_assistant import handle_voice_command
    VOICE_ENABLED = True
except ImportError:
    print("Voice assistant module could not be loaded. Please install required dependencies.")
    VOICE_ENABLED = False

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

DB_FILE = 'habits.db'

# Database initialization
def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create habits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT '#2ecc40'
        )
    ''')
    
    # Create habit_dates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_dates (
            habit_id INTEGER,
            date TEXT,
            checked INTEGER DEFAULT 0,
            PRIMARY KEY (habit_id, date),
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
    ''')
    
    # Create tasks table for the new task management system
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'medium',
            category TEXT DEFAULT 'other',
            due_date TEXT,
            completed BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/habits')
def habits():
    return render_template('habits.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/chat-simple')
def chat_simple():
    """Educational version of the chat interface"""
    return render_template('chat_simple.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/tasks')
def tasks():
    """Modern task management interface"""
    return render_template('tasks.html')

# Task Management API Endpoints
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks ORDER BY 
            CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
            created_at DESC
        ''')
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row['id'],
                'title': row['title'],
                'description': row['description'],
                'priority': row['priority'],
                'category': row['category'],
                'dueDate': row['due_date'],
                'completed': bool(row['completed']),
                'createdAt': row['created_at']
            })
        
        conn.close()
        return jsonify({'success': True, 'tasks': tasks})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (title, description, priority, category, due_date, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data.get('description', ''),
            data.get('priority', 'medium'),
            data.get('category', 'other'),
            data.get('dueDate'),
            False,
            data['createdAt']
        ))
        
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'task_id': task_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    """Mark a task as completed"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/motivation')
def get_motivation():
    message = get_motivation_message()
    return jsonify({'motivation': message})

# --- HABIT TRACKER MULTI-HABIT SUPPORT ---
# habits.json structure:
# {
#   "Habit Name": {"dates": {"YYYY-MM-DD": true, ...}, "color": "#hex"},
#   ...
# }

def create_task_in_db(task_data):
    """Helper function to create a task in the database (used by voice assistant)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (title, description, priority, category, due_date, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_data['title'],
            task_data.get('description', ''),
            task_data.get('priority', 'medium'),
            task_data.get('category', 'other'),
            task_data.get('dueDate'),
            False,
            task_data['createdAt']
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating task: {e}")
        return False

def get_habits_from_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Try the new schema first, fallback to old schema
    try:
        c.execute('SELECT id, name, color FROM habits')
        rows = c.fetchall()
        
        habits = {}
        for habit_id, name, color in rows:
            c.execute('SELECT date, checked FROM habit_dates WHERE habit_id=?', (habit_id,))
            dates = {row[0]: bool(row[1]) for row in c.fetchall()}
            habits[name] = {'dates': dates, 'color': color or '#2ecc40'}
    except sqlite3.OperationalError:
        # Fallback to old schema or create empty structure
        habits = {}
    
    conn.close()
    return habits

def save_habit_date(habit_name, date):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id FROM habits WHERE name=?', (habit_name,))
    row = c.fetchone()
    if not row:
        c.execute('INSERT INTO habits (name) VALUES (?)', (habit_name,))
        habit_id = c.lastrowid
    else:
        habit_id = row[0]
    c.execute('SELECT checked FROM habit_dates WHERE habit_id=? AND date=?', (habit_id, date))
    row = c.fetchone()
    if row:
        new_checked = 0 if row[0] else 1
        c.execute('UPDATE habit_dates SET checked=? WHERE habit_id=? AND date=?', (new_checked, habit_id, date))
    else:
        new_checked = 1
        c.execute('INSERT INTO habit_dates (habit_id, date, checked) VALUES (?, ?, ?)', (habit_id, date, new_checked))
    conn.commit()
    conn.close()

def add_habit_to_db(habit_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO habits (name) VALUES (?)', (habit_name,))
    conn.commit()
    conn.close()

def update_habit_color_in_db(habit_name, color):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE habits SET color=? WHERE name=?', (color, habit_name))
    conn.commit()
    conn.close()

def rename_habit_in_db(old_name, new_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('UPDATE habits SET name=? WHERE name=?', (new_name, old_name))
    conn.commit()
    conn.close()

def delete_habit_from_db(habit_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM habits WHERE name=?', (habit_name,))
    conn.commit()
    conn.close()

# --- HABIT TRACKING API ENDPOINTS ---

@app.route('/api/habits', methods=['GET', 'POST'])
def habits_api():
    if request.method == 'POST':
        habit_name = request.json.get('habit')
        date = request.json.get('date')
        if habit_name and date:
            save_habit_date(habit_name, date)
    habits = get_habits_from_db()
    return jsonify({'habits': habits})

@app.route('/api/habits/new', methods=['POST'])
def add_habit():
    habit_name = request.json.get('habit')
    if habit_name:
        add_habit_to_db(habit_name)
    habits = get_habits_from_db()
    return jsonify({'habits': habits})

@app.route('/api/habits/color', methods=['POST'])
def update_habit_color():
    habit_name = request.json.get('habit')
    color = request.json.get('color')
    if habit_name and color:
        update_habit_color_in_db(habit_name, color)
    habits = get_habits_from_db()
    return jsonify({'habits': habits})

@app.route('/api/habits/rename', methods=['POST'])
def rename_habit():
    old = request.json.get('old')
    new = request.json.get('new')
    if old and new:
        rename_habit_in_db(old, new)
    habits = get_habits_from_db()
    return jsonify({'habits': habits})

@app.route('/api/habits/delete', methods=['POST'])
def delete_habit():
    habit = request.json.get('habit')
    if habit:
        delete_habit_from_db(habit)
    habits = get_habits_from_db()
    return jsonify({'habits': habits})

@app.route('/api/chat', methods=['POST'])
def chat_api():
    user_message = request.json.get('message', '')
    
    # Proactively detect and create habits/tasks from user messages
    detected_actions = detect_and_create_items(user_message)
    
    reply = get_ai_reply(user_message)
    
    # If we detected and created something, modify the reply to acknowledge it
    if detected_actions:
        if detected_actions.get('habits'):
            habit_names = ", ".join(detected_actions['habits'])
            reply = f"Perfect! I've added '{habit_names}' to your habits tracker. {reply}"
        if detected_actions.get('tasks'):
            task_names = ", ".join(detected_actions['tasks'])
            reply = f"Great! I've created the task '{task_names}' for you. {reply}"
    
    return jsonify({'reply': reply})

def detect_and_create_items(message):
    """Detect habit and task creation from user messages and create them automatically"""
    import re
    from datetime import datetime
    
    message_lower = message.lower()
    created_items = {'habits': [], 'tasks': []}
    
    # Habit detection patterns
    habit_patterns = [
        r"i want to (?:start|begin|create|add|track) (?:a )?habit (?:called |named |of )?['\"]?([^'\".,!?]+)['\"]?",
        r"(?:create|add|start|track) (?:a |the )?habit[:\s]+['\"]?([^'\".,!?]+)['\"]?",
        r"i (?:want to|need to|should) (?:start|begin) ([^.,!?]+daily|[^.,!?]+every day|drinking water|exercising|reading|meditation|yoga)",
        r"help me (?:track|start|create) (?:a )?habit (?:of |for )?['\"]?([^'\".,!?]+)['\"]?",
        r"i'm (?:starting|beginning) (?:a |the )?habit (?:of |for )?['\"]?([^'\".,!?]+)['\"]?",
    ]
    
    # Task detection patterns  
    task_patterns = [
        r"i need to (?:do|complete|finish|work on) ([^.,!?]+)",
        r"(?:create|add|make) (?:a |the )?task[:\s]+['\"]?([^'\".,!?]+)['\"]?",
        r"remind me to ([^.,!?]+)",
        r"i have to ([^.,!?]+)",
        r"(?:schedule|plan) ([^.,!?]+)",
    ]
    
    # Check for habits
    for pattern in habit_patterns:
        matches = re.findall(pattern, message_lower, re.IGNORECASE)
        for match in matches:
            habit_name = match.strip().title()
            if habit_name and len(habit_name) > 2:
                # Clean up the habit name
                habit_name = re.sub(r'(daily|every day|everyday)$', '', habit_name).strip()
                add_habit_to_db(habit_name)
                created_items['habits'].append(habit_name)
    
    # Check for tasks
    for pattern in task_patterns:
        matches = re.findall(pattern, message_lower, re.IGNORECASE)
        for match in matches:
            task_title = match.strip().title()
            if task_title and len(task_title) > 2:
                task_data = {
                    'title': task_title,
                    'description': '',
                    'priority': 'medium',
                    'category': 'other',
                    'dueDate': None,
                    'createdAt': datetime.now().isoformat()
                }
                if create_task_in_db(task_data):
                    created_items['tasks'].append(task_title)
    
    return created_items if (created_items['habits'] or created_items['tasks']) else None

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route('/api/voice', methods=['POST'])
def handle_voice():
    """Handle voice command requests"""
    try:
        print("🎤 Voice request received")
        
        if 'audio' not in request.files:
            print("❌ No audio file in request")
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        print(f"📁 Audio file: {audio_file.filename}, size: {audio_file.content_length}")
        
        # Process the voice command
        result = handle_voice_command(audio_file)
        print(f"✅ Voice processing result: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Voice processing error: {str(e)}")
        return jsonify({
            'transcript': '',
            'reply': 'Sorry, there was an error processing your voice command.',
            'action': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
