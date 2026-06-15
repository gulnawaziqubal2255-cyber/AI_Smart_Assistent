from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
import requests
try:
    import openai
except ImportError:
    openai = None
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'college_data.json')
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    college_data = json.load(f)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '').strip()
OPENAI_ENABLED = bool(openai and OPENAI_API_KEY)
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

    contact = college_data.get('contact', {})
    contact_info = (
        f"Address: {contact.get('address', 'N/A')}\n"
        f"Phone: {contact.get('phone', 'N/A')}\n"
        f"Email: {contact.get('email', 'N/A')}\n"
        f"Campus size: {contact.get('campus_size', 'N/A')}\n"
        f"Established: {contact.get('established', 'N/A')}\n"
    )

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
        f"Timetables: {', '.join(college_data.get('timetable', {}).keys())}\n"
        f"Contact:\n{contact_info}\n"
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

    if any(term in query for term in ['exam', 'test', 'evaluation', 'paper']):
        return answer_exam(query)

    if any(term in query for term in ['student', 'roll', 'roll no', 'roll number', 'name']):
        return answer_student(query)

    if any(term in query for term in ['about college', 'about', 'information', 'who are', 'what is']):
        return college_data.get('about', 'This is your AI College Assistant for academic information.')

    return answer_general(query)


def smart_answer(query, role='student'):
    query_text = query.strip()
    if not query_text:
        return {
            'answer': 'Please type a question about your college timetable, notices, attendance, fees, or faculty.',
            'source': 'prompt'
        }

    if openai and OPENAI_API_KEY:
        answer = get_openai_response(query_text)
        if answer:
            return {'answer': answer, 'source': 'openai'}

    return {'answer': local_answer(query_text.lower()), 'source': 'fallback'}


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
    """Answer questions about faculty members"""
    faculty_list = college_data.get('faculty', [])
    
    # Search for specific faculty by expertise if mentioned
    if 'ai' in query or 'machine' in query or 'ml' in query:
        faculty_matches = [f for f in faculty_list if 'AI' in f.get('expertise', '') or 'ML' in f.get('expertise', '')]
        if faculty_matches:
            result = '🎓 Faculty Members (AI/ML Experts):\n'
            for f in faculty_matches:
                result += f"\n👨‍🏫 {f['name']}\n"
                result += f"   Subject: {f['subject']}\n"
                result += f"   Designation: {f['designation']}\n"
                result += f"   Expertise: {f.get('expertise', 'N/A')}\n"
                result += f"   Available: {f.get('availability', 'N/A')}"
            return result
    
    # Show all faculty by default
    result = '🎓 All Faculty Members:\n'
    for i, f in enumerate(faculty_list, 1):
        result += f"\n{i}. {f['name']}\n"
        result += f"   Subject: {f['subject']}\n"
        result += f"   Designation: {f['designation']}\n"
        result += f"   Expertise: {f.get('expertise', 'N/A')}\n"
        result += f"   Available: {f.get('availability', 'N/A')}"
    return result


def answer_website():
    url = college_data.get('college_page_url')
    if not url:
        return 'No college website is configured yet. Please update the backend data source.'

    return (f'The college portal is available at {url}. '
            'Use your Galgotias University login credentials to access the ERP portal for attendance, notices, and academic updates.')


def answer_general(query):
    return ('I am your AI College Assistant. Ask me about timetable, attendance, notices, fees, faculty, '
            'exams, or student information. For example: "Show me the exam schedule" or "What is Priya\'s attendance?"')


def answer_exam(query):
    """Answer questions about exam schedule"""
    exams = college_data.get('exam_schedule', [])
    if not exams:
        return 'No exam schedule available.'
    
    exam_info = 'Upcoming Exam Schedule:\n'
    for exam in exams:
        exam_info += f"- {exam['subject']}: {exam['date']} at {exam['time']}\n"
    return exam_info


def answer_student(query):
    """Answer questions about students"""
    students = college_data.get('students', [])
    query_lower = query.lower()
    
    # Try to find a specific student by name or roll number
    for student in students:
        if student['name'].lower() in query_lower or student['roll_no'].lower() in query_lower:
            result = f"\n👤 Student Details:\n\n"
            result += f"Name: {student['name']}\n"
            result += f"Roll No: {student['roll_no']}\n"
            result += f"Department: {student['department']}\n"
            result += f"Semester: {student['semester']}\n"
            result += f"CGPA: {student['cgpa']}\n\n"
            result += f"📊 Attendance:\n"
            result += f"   Overall: {student['attendance']['overall']}%\n"
            for subject, percent in student['attendance'].items():
                if subject != 'overall':
                    result += f"   • {subject}: {percent}%\n"
            result += f"\n💰 Fee Status: {student['fee_status']}"
            if student['fee_status'] == 'Pending':
                result += f" (₹{student['fee_amount']} due)\n"
            else:
                result += "\n"
            result += f"🏠 Hostel: {student['hostel']}"
            return result
    
    # Check for fee-related queries
    if 'fee' in query_lower or 'pending' in query_lower:
        pending_students = [s for s in students if s['fee_status'] == 'Pending']
        if pending_students:
            result = "💰 Students with Pending Fees:\n\n"
            for s in pending_students:
                result += f"• {s['name']} ({s['roll_no']}) - ₹{s['fee_amount']} due\n"
            return result
    
    # Default: show all students
    result = "👥 All Students in Class:\n\n"
    for i, student in enumerate(students, 1):
        result += f"{i}. {student['name']}\n"
        result += f"   Roll No: {student['roll_no']}\n"
        result += f"   CGPA: {student['cgpa']} | Attendance: {student['attendance']['overall']}%\n"
        result += f"   Fee: {student['fee_status']}\n\n"
    return result


@app.route('/api/query', methods=['POST'])
def api_query():
    body = request.get_json(force=True)
    query = body.get('query', '')
    role = body.get('role', 'student')
    result = smart_answer(query, role)
    return jsonify({
        'answer': result.get('answer'),
        'source': result.get('source', 'fallback')
    })


@app.route('/api/college-data', methods=['GET'])
def api_college_data():
    data = {
        'name': college_data.get('college_name'),
        'about': college_data.get('about'),
        'stats': college_data.get('stats'),
        'notices': college_data.get('notices'),
        'events': college_data.get('events'),
        'departments': college_data.get('departments'),
        'website': college_data.get('college_page_url'),
        'contact': college_data.get('contact'),
        'openai_enabled': OPENAI_ENABLED
    }
    return jsonify(data)


@app.route('/api/students', methods=['GET'])
def api_get_students():
    """Get all students in the system"""
    students = college_data.get('students', [])
    return jsonify({'students': students})


@app.route('/api/student/<roll_no>', methods=['GET'])
def api_get_student(roll_no):
    """Get a specific student by roll number"""
    students = college_data.get('students', [])
    student = next((s for s in students if s['roll_no'] == roll_no), None)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student)


@app.route('/api/student/search', methods=['POST'])
def api_search_student():
    """Search for a student by name or roll number"""
    body = request.get_json(force=True)
    query = body.get('query', '').lower().strip()
    
    if not query:
        return jsonify({'error': 'Please provide a search query'}), 400
    
    students = college_data.get('students', [])
    matches = [s for s in students if query in s['name'].lower() or query in s['roll_no'].lower()]
    
    if not matches:
        return jsonify({'error': 'No students found matching your query'}), 404
    
    return jsonify({'students': matches})


@app.route('/api/faculty/search', methods=['POST'])
def api_search_faculty():
    """Search for faculty by name or subject"""
    body = request.get_json(force=True)
    query = body.get('query', '').lower().strip()
    
    if not query:
        return jsonify({'error': 'Please provide a search query'}), 400
    
    faculty = college_data.get('faculty', [])
    matches = [f for f in faculty if query in f['name'].lower() or query in f['subject'].lower()]
    
    if not matches:
        return jsonify({'error': 'No faculty found matching your query'}), 404
    
    return jsonify({'faculty': matches})


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def frontend(path):
    if path != '' and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
