# AI_Smart_Assistent
AI College Assistant Web Application

## Project structure
- `backend/` — Flask API and college data source
- `frontend/` — responsive homepage, dashboard, and chat UI

## What this scaffold does
- Provides a homepage with college summary cards
- Lets students ask questions about timetable, attendance, notices, fees, faculty, and website info
- Supports a backend endpoint for college metadata and chat queries
- Includes a placeholder for connecting to a real college website or ERP portal

## Run locally
1. Install Python 3.10+ and pip
2. Open a terminal in `backend/`
3. Run:
   ```bash
   pip install -r requirements.txt
   pip install openai
   python app.py
   ```
5. To enable OpenAI-powered answers, set the environment variable `OPENAI_API_KEY` before starting the backend.

```bash
set OPENAI_API_KEY=your_key_here
python app.py
```
4. Open `http://127.0.0.1:5000` in your browser

## How to extend this project
- Replace `backend/college_data.json` with your college's real data
- Set `college_page_url` to your actual website or ERP URL
- Enhance `smart_answer()` in `backend/app.py` with OpenAI or another NLP service
- Add role-based pages for Student, Faculty, and Admin
- Build a React frontend if you want a richer SPA experience

## Suggested next features
- Live ERP connection for attendance and exam results
- Student login with JWT authentication
- Voice query support and multilingual responses
- Mobile app using React Native or Flutter
