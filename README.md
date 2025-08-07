# Zelda Habit Tracker (Production Ready)

## Features
- Minimalist, responsive UI
- Habits dashboard (GitHub-style grid)
- Motivational message API
- Chat with Zelda (AI therapist, via Ollama)
- Account page (placeholder)
- Secure, production-ready Flask setup

## Setup

1. **Clone the repo and enter the directory:**
   ```sh
   git clone <repo-url>
   cd zelda_clone
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set environment variables (recommended):**
   ```sh
   export SECRET_KEY='your-strong-secret-key'
   ```
5. **Start Ollama server:**
   ```sh
   ollama serve
   # Ensure llama3.2 is pulled: ollama pull llama3.2
   ```
6. **Run the app (development):**
   ```sh
   flask run --host=0.0.0.0
   # or
   python app.py
   ```
7. **Run in production (example with Gunicorn):**
   ```sh
   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
   ```

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
