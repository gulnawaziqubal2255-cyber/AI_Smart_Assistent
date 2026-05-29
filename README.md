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
   python app.py
   ```

4. (Optional) To use a `.env` file, copy `backend/.env.example` to `backend/.env` and set your `OPENAI_API_KEY` there. Do NOT commit `.env`.

5. To enable OpenAI-powered answers via environment variable:

```bash
set OPENAI_API_KEY=your_key_here
python app.py
```

6. Open `http://127.0.0.1:5000` in your browser

## Secrets & Safety
- Do not paste your API keys into chat or public repos. The strings you posted look like API keys — never share them publicly.
- If you accidentally exposed a key, rotate it immediately from your OpenAI dashboard and delete the old key.

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
