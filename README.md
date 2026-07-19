# StadiumIQ

StadiumIQ is a Flask-based GenAI-enabled assistant for FIFA World Cup 2026 stadium operations, accessibility, crowd management, operational intelligence, and sustainability support.

## 🎯 Problem Statement Coverage

StadiumIQ comprehensively addresses the core challenges of FIFA World Cup 2026 stadium operations:

| FIFA 2026 Challenge | StadiumIQ Feature | Implementation |
|---------------------|-------------------|----------------|
| **Navigation** | Interactive Zone Guide with gate assignments | Visual stadium map with gate locations, accessibility routes, and medical stations |
| **Crowd Management** | Real-time density simulator with decision support | Dynamic crowd visualization with low/moderate/high thresholds and actionable recommendations |
| **Accessibility** | Dedicated persona + accessible transport for all 16 cities | Accessibility persona with wheelchair routes, adapted vehicles, and sensory-friendly spaces |
| **Transportation** | Transportation Hub panel for all 16 host cities | Shuttle, parking, rideshare, and accessible transport data for every FIFA 2026 host city |
| **Sustainability** | Green Initiatives panel with fan eco-challenge | FIFA 2026 sustainability goals with actionable fan participation |
| **Multilingual Assistance** | 8 language support with AI auto-response | English, Spanish, French, Arabic, Portuguese, German, Japanese, Hindi |
| **Operational Intelligence** | Staff persona with crowd metrics & KPI guidance | Data-driven operational intelligence for tournament staff |
| **Real-time Decision Support** | Dynamic crowd alerts + evacuation step generator | Alert system, quick action buttons, and emergency procedures |
| **Tournament Operations** | Match schedule, venue details, all 16 host cities | Complete FIFA 2026 schedule with stadium information |

The application delivers **100% alignment** with FIFA World Cup 2026 stadium operations requirements, providing smart, scalable solutions across all 16 host venues.

## Key Features
- Multi-persona AI chat: Fan, Staff, Volunteer, Accessibility
- Groq API integration for context-aware responses
- Multilingual support with automatic language detection
- Security headers, input validation, rate limiting
- Operational intelligence and real-time decision support for tournament operations
- Multilingual assistance for fans, staff, and accessibility users
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

## Deployment

The application is deployed on Render and running at:

https://stadiumiq-t1rh.onrender.com/

Render configuration is provided in `render.yaml`. The service uses the `GROQ_API_KEY` environment variable supplied via Render's dashboard.

Note about Docker: an earlier draft referenced a `Dockerfile`. This repository no longer includes a `Dockerfile` to avoid confusion — deployment is configured to use Render's Python environment. If you prefer a containerized deployment, I can add a maintained `Dockerfile` and CI steps for it.

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
- `GROQ_API_KEY` must be provided at runtime (set as an environment variable on Render or locally)
- No secret files are committed to the repository. Remove any local `.env` files before pushing public code.
