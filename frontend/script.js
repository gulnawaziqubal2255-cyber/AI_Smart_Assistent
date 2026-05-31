const chatWindow = document.getElementById('chatWindow');
const queryForm = document.getElementById('queryForm');
const queryInput = document.getElementById('queryInput');
const heroStats = document.getElementById('heroStats');
const dashboardGrid = document.getElementById('dashboardGrid');
const scrollToChat = document.getElementById('scrollToChat');
const QUICK_ACTIONS = [
  { label: 'Latest Notices', query: 'Show me the latest notices' },
  { label: 'My Attendance', query: 'What is my attendance percentage?' },
  { label: 'CSE Timetable', query: 'What is the CSE timetable?' },
  { label: 'Hostel Fee Due Date', query: 'When is the hostel fee due?' }
];
const FAQ_ITEMS = [
  'How do I login to the ERP portal?',
  'What is the campus address?',
  'When is semester exam registration?',
  'How can I apply for scholarships?'
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
  if (!message) return;
  queryInput.value = '';
  sendQuery(message);
});

scrollToChat?.addEventListener('click', () => {
  document.querySelector('.assistant-panel')?.scrollIntoView({ behavior: 'smooth' });
});

addMessage('Welcome! Ask me about college timetable, attendance, notices, fees, or faculty.', 'assistant');
loadCollegeData();
