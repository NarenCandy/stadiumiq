# StadiumIQ

StadiumIQ is a Flask-based GenAI assistant for FIFA World Cup 2026 stadium operations, accessibility, crowd management, and sustainability support.

## Key Features
- Multi-persona AI chat: Fan, Staff, Volunteer, Accessibility
- Groq API integration for context-aware responses
- Multilingual support with automatic language detection
- Security headers, input validation, rate limiting
- Docker-ready and Render-ready deployment

## Local Setup
1. Create a Python 3.11 virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set the Groq API key in your environment:

```powershell
set GROQ_API_KEY=your_api_key
```

4. Start the app:

```bash
python app.py
```

5. Open http://127.0.0.1:5000

## Docker
Build and run locally without storing secrets in the repository:

```bash
docker build -t stadiumiq .
docker run -e GROQ_API_KEY=your_api_key -p 10000:10000 stadiumiq
```

## Render Deployment
`render.yaml` is configured for Render with `GROQ_API_KEY` supplied as an environment variable.

## Quality Checks
- `python -m flake8 app tests`
- `python -m mypy app`
- `python -m pytest tests/ -q`

## Project Layout
- `app.py` — application entrypoint
- `app/__init__.py` — Flask factory and middleware
- `app/config.py` — config validation
- `app/constants.py` — stadium data and persona prompts
- `app/routes/chat.py` — chat and health endpoints
- `app/services/ai_service.py` — Groq API wrapper
- `app/utils/validators.py` — request validation and sanitization
- `tests/` — pytest suite

## Environment
- `GROQ_API_KEY` must be provided at runtime
- No secret files are committed to the repository
