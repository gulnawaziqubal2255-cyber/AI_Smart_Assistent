const chatWindow = document.getElementById('chatWindow');
const queryForm = document.getElementById('queryForm');
const queryInput = document.getElementById('queryInput');
const heroStats = document.getElementById('heroStats');
const dashboardGrid = document.getElementById('dashboardGrid');
const scrollToChat = document.getElementById('scrollToChat');
const QUICK_ACTIONS = [
  { label: 'Latest Notices', query: 'Show me the latest notices' },
  { label: 'Exam Schedule', query: 'When are the exams scheduled?' },
  { label: 'All Students', query: 'Show me all students' },
  { label: 'Faculty List', query: 'Who are the faculty members?' },
  { label: 'Pending Fees', query: 'Which students have pending fees?' },
  { label: 'Hostel Info', query: 'Tell me about hostel fees' }
];
const FAQ_ITEMS = [
  'Show me all students',
  'Who are the faculty members?',
  'Which students have pending fees?',
  'What is the exam schedule?',
  'Tell me about faculty availability'
];

function addMessage(text, role, source) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = text;
  if (role === 'assistant' && source) {
    const sourceTag = document.createElement('div');
    sourceTag.className = 'message-source';
    sourceTag.textContent = `Source: ${source === 'openai' ? 'OpenAI GPT' : source === 'fallback' ? 'Local college data' : 'System'}`;
    div.appendChild(document.createElement('br'));
    div.appendChild(sourceTag);
  }
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function loadCollegeData() {
  try {
    const response = await fetch('/api/college-data');
    const data = await response.json();
    renderHeroStats(data.stats);
    renderDashboardCards(data);
    renderCampusContact(data);
    renderOpenAIStatus(data.openai_enabled);
    renderQuickActions();
    renderFAQ();
  } catch (error) {
    console.error('Unable to load college data:', error);
  }
}

function renderHeroStats(stats) {
  if (!stats) return;
  const items = [
    { label: 'Students', value: stats.students },
    { label: 'Departments', value: stats.departments },
    { label: 'Faculty', value: stats.faculty },
    { label: 'Notices', value: stats.notices }
  ];
  heroStats.innerHTML = items.map(item => `
    <div class="stat-card">
      <strong>${item.value}</strong>
      <span>${item.label}</span>
    </div>
  `).join('');
}

function renderDashboardCards(data) {
  if (!data) return;
  const cards = [
    {
      title: 'College Overview',
      content: data.about || 'Your AI-powered campus assistant for students and faculty.'
    },
    {
      title: 'Departments',
      content: data.departments.map(dep => `• ${dep}`).join('\n')
    },
    {
      title: 'Upcoming Events',
      content: data.events.map(ev => `• ${ev.title} (${ev.date})`).join('\n')
    }
  ];
  dashboardGrid.innerHTML = cards.map(card => `
    <div class="dashboard-card">
      <h3>${card.title}</h3>
      <p>${card.content.replace(/\n/g, '<br>')}</p>
    </div>
  `).join('');
}

function renderOpenAIStatus(enabled) {
  const status = document.getElementById('openaiStatus');
  if (!status) return;
  status.textContent = enabled ? 'OpenAI enabled — richer answers available' : 'OpenAI disabled — using local college data';
  status.className = `status-pill ${enabled ? 'status-enabled' : 'status-disabled'}`;
}

function renderQuickActions() {
  const container = document.getElementById('quickActions');
  if (!container) return;
  container.innerHTML = QUICK_ACTIONS.map(action => `
    <button type="button" class="quick-action-button" data-query="${action.query}">
      ${action.label}
    </button>
  `).join('');
  container.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', () => sendQuery(button.dataset.query));
  });
}

function renderFAQ() {
  const faqContainer = document.getElementById('faqList');
  if (!faqContainer) return;
  faqContainer.innerHTML = FAQ_ITEMS.map(item => `
    <button type="button" class="faq-item">${item}</button>
  `).join('');
  faqContainer.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', () => sendQuery(button.textContent));
  });
}

function renderCampusContact(data) {
  const contact = data.contact || {};
  const lines = [
    contact.address,
    contact.phone && `Phone: ${contact.phone}`,
    contact.email && `Email: ${contact.email}`,
    contact.campus_size && `Campus size: ${contact.campus_size}`,
    contact.established && `Established: ${contact.established}`
  ].filter(Boolean);
  const contactText = lines.length ? lines.join('\n') : 'Contact details are being updated.';
  document.getElementById('campusContactText').innerHTML = contactText.replace(/\n/g, '<br>');
}

async function sendQuery(message) {
  addMessage(message, 'user');
  try {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: message, role: 'student' })
    });
    const data = await response.json();
    addMessage(data.answer, 'assistant', data.source);
  } catch (error) {
    addMessage('Unable to contact the backend. Please start the server and try again.', 'assistant', 'error');
  }
}

queryForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = queryInput.value.trim();
  if (message) {
    sendQuery(message);
    queryInput.value = '';
  }
});

// Student search functionality
const studentSearch = document.getElementById('studentSearch');
if (studentSearch) {
  studentSearch.addEventListener('input', async (e) => {
    const query = e.target.value.trim();
    if (query.length < 2) {
      document.getElementById('studentResult').innerHTML = '';
      return;
    }

    try {
      const response = await fetch('/api/student/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      if (response.ok) {
        const data = await response.json();
        displayStudentResults(data.students);
      } else {
        document.getElementById('studentResult').innerHTML = '<p class="no-results">No students found</p>';
      }
    } catch (error) {
      console.error('Error searching students:', error);
    }
  });
}

// Faculty search functionality
const facultySearch = document.getElementById('facultySearch');
if (facultySearch) {
  facultySearch.addEventListener('input', async (e) => {
    const query = e.target.value.trim();
    if (query.length < 2) {
      document.getElementById('facultyResult').innerHTML = '';
      return;
    }

    try {
      const response = await fetch('/api/faculty/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      if (response.ok) {
        const data = await response.json();
        displayFacultyResults(data.faculty);
      } else {
        document.getElementById('facultyResult').innerHTML = '<p class="no-results">No faculty found</p>';
      }
    } catch (error) {
      console.error('Error searching faculty:', error);
    }
  });
}

function displayStudentResults(students) {
  const container = document.getElementById('studentResult');
  
  if (!students || students.length === 0) {
    container.innerHTML = '<p class="no-results">No matching students found</p>';
    return;
  }

  container.innerHTML = students.map(student => `
    <div class="student-card">
      <div class="student-header">
        <div>
          <h3>${student.name}</h3>
          <p class="roll-no">Roll No: ${student.roll_no}</p>
        </div>
        <div class="cgpa-badge">${student.cgpa}</div>
      </div>
      <div class="student-details">
        <div class="detail-row">
          <span class="label">Department:</span>
          <span>${student.department}</span>
        </div>
        <div class="detail-row">
          <span class="label">Semester:</span>
          <span>${student.semester}</span>
        </div>
        <div class="detail-row">
          <span class="label">Overall Attendance:</span>
          <span class="attendance-${student.attendance.overall >= 75 ? 'good' : 'warning'}">${student.attendance.overall}%</span>
        </div>
        <div class="detail-row">
          <span class="label">Fee Status:</span>
          <span class="fee-${student.fee_status.toLowerCase()}">${student.fee_status}${student.fee_status === 'Pending' ? ' (₹' + student.fee_amount + ')' : ''}</span>
        </div>
        <div class="detail-row">
          <span class="label">Hostel:</span>
          <span>${student.hostel}</span>
        </div>
        <div class="attendance-breakdown">
          <p><strong>Subject-wise Attendance:</strong></p>
          ${Object.entries(student.attendance).filter(([k]) => k !== 'overall').map(([subject, percent]) => 
            `<p class="subject-attendance">• ${subject}: ${percent}%</p>`
          ).join('')}
        </div>
      </div>
    </div>
  `).join('');
}

function displayFacultyResults(faculty) {
  const container = document.getElementById('facultyResult');
  
  if (!faculty || faculty.length === 0) {
    container.innerHTML = '<p class="no-results">No matching faculty found</p>';
    return;
  }

  container.innerHTML = faculty.map(member => `
    <div class="faculty-card">
      <div class="faculty-header">
        <div>
          <h3>${member.name}</h3>
          <p class="designation">${member.designation}</p>
        </div>
      </div>
      <div class="faculty-details">
        <div class="detail-row">
          <span class="label">Subject:</span>
          <span>${member.subject}</span>
        </div>
        <div class="detail-row">
          <span class="label">Expertise:</span>
          <span>${member.expertise}</span>
        </div>
        <div class="detail-row">
          <span class="label">Availability:</span>
          <span>${member.availability}</span>
        </div>
      </div>
    </div>
  `).join('');
}

scrollToChat?.addEventListener('click', () => {
  document.querySelector('.assistant-panel')?.scrollIntoView({ behavior: 'smooth' });
});

addMessage('Welcome! Ask me about college timetable, attendance, notices, fees, or faculty.', 'assistant');
loadCollegeData();
