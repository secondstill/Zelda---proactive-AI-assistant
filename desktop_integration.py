#!/usr/bin/env python3
"""
Zelda AI Assistant - Desktop Integration
This script provides system-level integration for the Zelda AI assistant.
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from datetime import datetime, timedelta
import json

def open_app(app_name):
    """Open applications on macOS"""
    app_commands = {
        'safari': 'open -a Safari',
        'chrome': 'open -a "Google Chrome"',
        'firefox': 'open -a Firefox',
        'mail': 'open -a Mail',
        'calendar': 'open -a Calendar',
        'notes': 'open -a Notes',
        'messages': 'open -a Messages',
        'facetime': 'open -a FaceTime',
        'music': 'open -a Music',
        'spotify': 'open -a Spotify',
        'finder': 'open -a Finder',
        'terminal': 'open -a Terminal',
        'vscode': 'open -a "Visual Studio Code"',
        'xcode': 'open -a Xcode'
    }
    
    app_name = app_name.lower().strip()
    if app_name in app_commands:
        try:
            subprocess.run(app_commands[app_name], shell=True, check=True)
            return f"Opened {app_name.title()}"
        except subprocess.CalledProcessError:
            return f"Could not open {app_name.title()}"
    else:
        return f"I don't know how to open {app_name}. Supported apps: {', '.join(app_commands.keys())}"

def get_system_info():
    """Get basic system information"""
    try:
        # Get current time
        now = datetime.now()
        time_str = now.strftime("%I:%M %p on %A, %B %d, %Y")
        
        # Get battery info (macOS)
        try:
            battery_info = subprocess.check_output(['pmset', '-g', 'batt'], universal_newlines=True)
            battery_percentage = battery_info.split('\t')[1].split(';')[0] if '\t' in battery_info else "Unknown"
        except:
            battery_percentage = "Unknown"
        
        # Get network status
        try:
            network_check = subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True, timeout=3)
            network_status = "Connected" if network_check.returncode == 0 else "Disconnected"
        except:
            network_status = "Unknown"
        
        return {
            'time': time_str,
            'battery': battery_percentage,
            'network': network_status
        }
    except Exception as e:
        return {'error': str(e)}

def create_reminder(text, when=None):
    """Create a system reminder (macOS)"""
    try:
        # Basic reminder creation using AppleScript
        script = f'''
        tell application "Reminders"
            make new reminder with properties {{name:"{text}"}}
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return f"Created reminder: {text}"
    except:
        return "Could not create system reminder"

def show_notification(title, message):
    """Show a system notification"""
    try:
        subprocess.run([
            'osascript', '-e', 
            f'display notification "{message}" with title "{title}"'
        ], check=True)
        return True
    except:
        return False

def start_voice_listener():
    """Start continuous voice listening (placeholder for now)"""
    print("Voice listener would start here...")
    print("For full implementation, integrate with speech recognition")

def main():
    """Main desktop integration function"""
    print("Zelda AI Assistant - Desktop Integration")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python desktop_integration.py open <app_name>")
        print("  python desktop_integration.py info")
        print("  python desktop_integration.py reminder '<text>'")
        print("  python desktop_integration.py notify '<title>' '<message>'")
        print("  python desktop_integration.py web")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'open' and len(sys.argv) > 2:
        app_name = sys.argv[2]
        result = open_app(app_name)
        print(result)
        
    elif command == 'info':
        info = get_system_info()
        print(f"System Information:")
        print(f"Time: {info.get('time', 'Unknown')}")
        print(f"Battery: {info.get('battery', 'Unknown')}")
        print(f"Network: {info.get('network', 'Unknown')}")
        
    elif command == 'reminder' and len(sys.argv) > 2:
        text = ' '.join(sys.argv[2:])
        result = create_reminder(text)
        print(result)
        
    elif command == 'notify' and len(sys.argv) > 3:
        title = sys.argv[2]
        message = ' '.join(sys.argv[3:])
        success = show_notification(title, message)
        print("Notification sent" if success else "Could not send notification")
        
    elif command == 'web':
        # Open Zelda web interface
        webbrowser.open('http://localhost:5000')
        print("Opening Zelda web interface...")
        
    elif command == 'listen':
        print("Starting voice listener...")
        start_voice_listener()
        
    else:
        print("Unknown command. Use: open, info, reminder, notify, web, or listen")

if __name__ == '__main__':
    main()
