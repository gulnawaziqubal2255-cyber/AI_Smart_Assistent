# AI_Smart_Assistent
AI College Assistant Web Application for Galgotias University

## Project structure
- `backend/` — Flask API, college metadata, and OpenAI integration logic
- `frontend/` — static web UI, chat interface, dashboard, campus contact panel, and quick actions

## Current features
- Homepage with live college summary cards and campus/contact panel
- Chat assistant for timetable, attendance, notices, fees, faculty, and website info
- OpenAI status indicator showing whether GPT mode is enabled
- Quick action buttons for common queries
- Popular question panel for fast user guidance
- Dedicated college contact and campus info section
- Local fallback answer logic when OpenAI is unavailable

## Run locally
1. Install Python 3.10+ and pip
2. Open a terminal in the project root or `backend/`
3. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser

## Optional: OpenAI mode
1. Copy `backend/.env.example` to `backend/.env`
2. Add your key:
   ```text
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Restart the app
4. The frontend will show `OpenAI enabled` when GPT mode is active

## Notes
- Use `backend/college_data.json` to update the college profile, departments, notices, events, timetable, attendance, fees, faculty, and contact info.
- The app currently serves static frontend assets from `frontend/` and exposes two main backend endpoints:
  - `GET /api/college-data`
  - `POST /api/query`

## Security
- Never commit `.env` or API keys to a public repository
- `.gitignore` should already exclude environment files and secrets
- If a key is exposed accidentally, rotate it immediately in the OpenAI dashboard

## Ideas for future improvements
- Add an admin page to edit `college_data.json` from the browser
- Add student login and JWT-based authentication
- Connect to the real Galgotias ERP for live attendance, fee status, and exam schedules
- Add voice input or multilingual support
- Deploy with Docker or a cloud hosting service
