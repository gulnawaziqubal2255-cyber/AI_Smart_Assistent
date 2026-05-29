const chatWindow = document.getElementById('chatWindow');
const queryForm = document.getElementById('queryForm');
const queryInput = document.getElementById('queryInput');
const heroStats = document.getElementById('heroStats');
const dashboardGrid = document.getElementById('dashboardGrid');
const scrollToChat = document.getElementById('scrollToChat');

function addMessage(text, role) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function loadCollegeData() {
  try {
    const response = await fetch('/api/college-data');
    const data = await response.json();
    renderHeroStats(data.stats);
    renderDashboardCards(data);
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

async function sendQuery(message) {
  addMessage(message, 'user');
  try {
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: message, role: 'student' })
    });
    const data = await response.json();
    addMessage(data.answer, 'assistant');
  } catch (error) {
    addMessage('Unable to contact the backend. Please start the server and try again.', 'assistant');
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
