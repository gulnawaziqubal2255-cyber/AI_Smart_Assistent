from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import requests
try:
    import openai
except ImportError:
    openai = None

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'college_data.json')
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    college_data = json.load(f)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


def fetch_college_page(url):
    """Optional helper to fetch a college web page and return plain text or None."""
    if not url:
        return None
    try:
        response = requests.get(url, timeout=6)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def build_openai_prompt(query):
    about = college_data.get('about', '')
    notices = '\n'.join([f"- {n['title']} ({n['date']})" for n in college_data.get('notices', [])])
    events = '\n'.join([f"- {e['title']} ({e['date']})" for e in college_data.get('events', [])])
    departments = ', '.join(college_data.get('departments', []))
    faculty_list = '\n'.join([f"- {f['name']} ({f['subject']})" for f in college_data.get('faculty', [])])

    prompt = (
        f"You are an AI college assistant for {college_data.get('college_name')} at Galgotias University. "
        f"Use the college information below to answer the user's question clearly and politely. "
        f"If the user asks for information not available in the provided data, tell them you cannot access it directly and suggest contacting the college admin.\n\n"
        f"College info:\n"
        f"About: {about}\n"
        f"Website: {college_data.get('college_page_url')}\n"
        f"Departments: {departments}\n"
        f"Events:\n{events}\n"
        f"Notices:\n{notices}\n"
        f"Faculty:\n{faculty_list}\n"
        f"Tuition fees: {college_data.get('fees', {}).get('general')}\n"
        f"Hostel fees: {college_data.get('fees', {}).get('hostel')}\n"
        f"Attendance summary: {college_data.get('attendance', {}).get('summary')}\n"
        f"Timetables: {', '.join(college_data.get('timetable', {}).keys())}\n\n"
        f"Answer the following question from the user:\n{query}\n"
        f"Keep the response short, friendly, and useful."
    )
    return prompt


def get_openai_response(query):
    if not openai or not OPENAI_API_KEY:
        return None

    prompt = build_openai_prompt(query)
    try:
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful AI assistant for a college student.'},
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=300,
            temperature=0.3,
        )
        answer = completion.choices[0].message.content.strip()
        return answer
    except Exception:
        return None


def local_answer(query):
    if any(term in query for term in ['timetable', 'schedule', 'class', 'period', 'subject']):
        return answer_timetable(query)

    if any(term in query for term in ['attendance', 'present', 'absent', 'percent']):
        return answer_attendance(query)

    if any(term in query for term in ['notice', 'circular', 'announcement', 'news']):
        return answer_notices()

    if any(term in query for term in ['fee', 'fees', 'tuition', 'hostel', 'payment', 'scholarship']):
        return answer_fee(query)

    if any(term in query for term in ['teacher', 'faculty', 'professor', 'mentor', 'staff']):
        return answer_faculty(query)

    if any(term in query for term in ['website', 'web page', 'website link', 'college page']):
        return answer_website()

    if any(term in query for term in ['about college', 'about', 'information', 'who are', 'what is']):
        return college_data.get('about', 'This is your AI College Assistant for academic information.')

    return answer_general(query)


def smart_answer(query, role='student'):
    query_text = query.strip()
    if not query_text:
        return 'Please type a question about your college timetable, notices, attendance, fees, or faculty.'

    if openai and OPENAI_API_KEY:
        answer = get_openai_response(query_text)
        if answer:
            return answer

    return local_answer(query_text.lower())


def answer_timetable(query):
    if 'computer' in query or 'cse' in query:
        return college_data['timetable']['CSE']
    if 'mechanical' in query or 'mech' in query:
        return college_data['timetable']['ME']
    if 'civil' in query:
        return college_data['timetable']['Civil']
    return college_data['timetable']['CSE']


def answer_attendance(query):
    if 'my' in query or 'roll' in query or 'student' in query:
        return college_data['attendance']['current']
    return f"Attendance summary: {college_data['attendance']['summary']}"


def answer_notices():
    notices = college_data['notices']
    return 'Latest notices:\n' + '\n'.join([f"- {n['title']} ({n['date']})" for n in notices])


def answer_fee(query):
    if 'hostel' in query:
        return college_data['fees']['hostel']
    if 'scholarship' in query:
        return college_data['fees']['scholarship']
    return college_data['fees']['general']


def answer_faculty(query):
    if 'ai' in query or 'machine' in query:
        faculty = [f for f in college_data['faculty'] if 'AI' in f['expertise'] or 'ML' in f['expertise']]
        if faculty:
            return '\n'.join([f"{f['name']} — {f['designation']} ({f['subject']})" for f in faculty])
    return 'Faculty list:\n' + '\n'.join([f"- {f['name']} ({f['subject']})" for f in college_data['faculty']])


def answer_website():
    url = college_data.get('college_page_url')
    if not url:
        return 'No college website is configured yet. Please update the backend data source.'

    text = fetch_college_page(url)
    if text:
        return f'The college website is available at {url}. I can also use this page to provide more detailed answers when connected.'
    return f'The college website is available at {url}, but I could not fetch it right now.'


def answer_general(query):
    return ('I am your AI College Assistant. Ask me about timetable, attendance, notices, fees, faculty, '
            'or the college website. For example: "Show me the exam notice" or "What is the Computer Science schedule?"')


@app.route('/api/query', methods=['POST'])
def api_query():
    body = request.get_json(force=True)
    query = body.get('query', '')
    role = body.get('role', 'student')
    answer = smart_answer(query, role)
    return jsonify({'answer': answer})


@app.route('/api/college-data', methods=['GET'])
def api_college_data():
    data = {
        'name': college_data.get('college_name'),
        'about': college_data.get('about'),
        'stats': college_data.get('stats'),
        'notices': college_data.get('notices'),
        'events': college_data.get('events'),
        'departments': college_data.get('departments'),
        'website': college_data.get('college_page_url')
    }
    return jsonify(data)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def frontend(path):
    if path != '' and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
