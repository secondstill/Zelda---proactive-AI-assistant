# Zelda Habit Tracker 

## Features
- Minimalist, responsive UI
- Habits dashboard (GitHub-style grid)
- Motivational message API
- Chat with Zelda (AI therapist, via Ollama)
- Account page (placeholder)
- Secure, production-ready Flask setup

# 🧚‍♀️ Zelda - Proactive AI Assistant

<div align="center">

![Zelda AI Assistant](https://img.shields.io/badge/AI-Assistant-purple?style=for-the-badge&logo=robot&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405e?style=for-the-badge&logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**A modern, proactive AI assistant that understands you, anticipates your needs, and helps you build better habits.**

[✨ Live Demo](#) • [📖 Documentation](#installation) • [🎯 Features](#features) • [🚀 Quick Start](#quick-start)

</div>

---

## 🌟 What Makes Zelda Special?

Zelda isn't just another chatbot. She's a **proactive AI companion** that:

- 🎯 **Automatically detects** when you mention habits or tasks in conversation
- 🧠 **Learns from your patterns** and suggests improvements
- 🎤 **Responds to voice commands** with natural speech
- 📊 **Visualizes your progress** with beautiful, interactive charts
- 💎 **Elegant interface** that feels premium and intuitive

## ✨ Features

### 🤖 Intelligent Chat System
- **Proactive Detection**: Automatically creates habits and tasks from natural conversation
- **Context Awareness**: Remembers your goals and provides relevant suggestions
- **Motivational Responses**: Encouraging feedback tailored to your progress

### 🎯 Smart Habit Tracking
- **Visual Calendar**: Beautiful color-coded habit tracking
- **Streak Counting**: Monitor your consistency with visual feedback
- **Custom Colors**: Personalize each habit with your favorite colors
- **Quick Actions**: One-click habit logging

### ✅ Advanced Task Management
- **Priority Levels**: High, medium, low priority organization
- **Categories**: Work, personal, health, and custom categories
- **Due Dates**: Never miss a deadline with smart reminders
- **Progress Tracking**: Visual completion status

### 🎤 Voice Integration
- **Speech Recognition**: Natural voice commands using Whisper AI
- **Text-to-Speech**: Zelda responds with synthesized voice
- **Hands-Free Operation**: Complete voice-controlled experience

### 🎨 Premium UI/UX
- **Modern Design**: Clean, elegant interface across all pages
- **Responsive Layout**: Perfect on desktop, tablet, and mobile
- **Smooth Animations**: Delightful micro-interactions
- **Dark Mode Ready**: Eye-friendly design for any time of day

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- pip package manager
- Modern web browser

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/secondstill/Zelda---proactive-AI-assistant.git
cd Zelda---proactive-AI-assistant
```

2. **Set up virtual environment** (recommended)
```bash
python -m venv zelda_env
source zelda_env/bin/activate  # On Windows: zelda_env\Scripts\activate
```

3. **Install core dependencies**
```bash
pip install -r requirements.txt
```

4. **For voice features** (optional)
```bash
pip install -r requirements-voice.txt
```

5. **Run the application**
```bash
python app.py
```

6. **Open your browser** and navigate to `http://localhost:5000`

## 🎮 Usage Examples

### Creating Habits Through Chat
```
You: "I want to start drinking more water daily"
Zelda: "Perfect! I've added 'Drinking More Water' to your habits tracker. 
       Staying hydrated is crucial for your health! Would you like me to 
       set up a reminder schedule?"
```

### Voice Commands
```
🎤 "Hey Zelda, add a task to call mom tomorrow"
🗣️ "Great! I've created the task 'Call Mom' for you. Is there anything 
    specific you'd like to discuss with her?"
```

### Smart Suggestions
```
Zelda notices you've been consistent with exercise for 7 days:
"🎉 Amazing! You've maintained your exercise habit for a full week! 
 Would you like to add a nutrition tracking habit to complement your fitness journey?"
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python) with SQLite database
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Integration**: Ollama for local AI processing
- **Voice Processing**: OpenAI Whisper for speech recognition
- **Speech Synthesis**: Web Speech API
- **Database**: SQLite with proper relational schema
- **Deployment**: WSGI-ready for various hosting platforms

## 📁 Project Structure

```
zelda/
├── app.py                 # Main Flask application
├── assistant.py           # AI logic and responses
├── voice_assistant.py     # Voice processing module
├── habits.db             # SQLite database
├── requirements.txt      # Core dependencies
├── requirements-voice.txt # Voice feature dependencies
├── static/              # CSS, JS, and assets
│   ├── style.css       # Main stylesheet
│   ├── chat.css        # Chat interface styles
│   ├── habit.css       # Habit tracker styles
│   └── *.js           # JavaScript modules
├── templates/          # HTML templates
│   ├── home.html      # Landing page
│   ├── chat.html      # Chat interface
│   ├── habits.html    # Habit tracker
│   ├── tasks.html     # Task management
│   └── account.html   # User account
└── zelda/             # Additional modules
```

## 🎯 Roadmap

- [ ] **Mobile App**: Native iOS/Android applications
- [ ] **Cloud Sync**: Multi-device synchronization
- [ ] **Advanced Analytics**: Detailed progress insights
- [ ] **Integrations**: Calendar, fitness trackers, smart home devices
- [ ] **Collaborative Features**: Shared habits and accountability partners
- [ ] **AI Coaching**: Personalized improvement suggestions

## 🤝 Contributing

We love contributions! Here's how you can help make Zelda even better:

1. **Fork the repository**
2. **Create your feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Start development server with auto-reload
python app.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** for excellent speech recognition
- **Ollama** for local AI processing capabilities
- **Flask community** for the robust web framework
- **All contributors** who help make Zelda better

## 📞 Support

- 🐛 **Bug Reports**: [Create an issue](https://github.com/secondstill/Zelda---proactive-AI-assistant/issues)
- 💡 **Feature Requests**: [Start a discussion](https://github.com/secondstill/Zelda---proactive-AI-assistant/discussions)
- 📧 **Contact**: [mail](mailto:gauthambalamurali@gmail.com)

---


## Security
- CSRF protection enabled
- Secure cookies
- Error pages for 404/500
- All secrets/config via environment variables

## Deployment
- Use a production WSGI server (e.g., Gunicorn, uWSGI)
- Set `SECRET_KEY` and any other secrets as environment variables
- Serve static files via a reverse proxy (e.g., Nginx)

---

**Enjoy your disciplined life with Zelda!**
