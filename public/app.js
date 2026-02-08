const bootWindow = document.getElementById('bootWindow');
const chatWindow = document.getElementById('chatWindow');
const bootProgress = document.getElementById('bootProgress');
const messagesEl = document.getElementById('messages');
const chatForm = document.getElementById('chatForm');
const promptInput = document.getElementById('promptInput');
const modeSelect = document.getElementById('modeSelect');
const statusText = document.getElementById('statusText');
const newChatBtn = document.getElementById('newChatBtn');
const aboutBtn = document.getElementById('aboutBtn');
const aboutDialog = document.getElementById('aboutDialog');
const closeAboutBtn = document.getElementById('closeAboutBtn');
const fullscreenBtn = document.getElementById('fullscreenBtn');
const exportBtn = document.getElementById('exportBtn');
const clockText = document.getElementById('clockText');

let conversation = [];

function addMessage(role, text) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.textContent = `${role === 'user' ? 'Siz' : 'C.O.M.R.A.D.E'}: ${text}`;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function resetChat() {
  conversation = [];
  messagesEl.innerHTML = '';
  addMessage('assistant', 'C.O.M.R.A.D.E 7.1 online. Emirlerinizi bekliyorum.');
}

function runBoot() {
  let progress = 0;
  const interval = setInterval(() => {
    progress += 8;
    bootProgress.style.width = `${Math.min(progress, 100)}%`;

    if (progress >= 100) {
      clearInterval(interval);
      bootWindow.classList.add('hidden');
      chatWindow.classList.remove('hidden');
      resetChat();
    }
  }, 120);
}

async function toggleFullscreen() {
  const appWindow = document.getElementById('chatWindow');
  try {
    if (!document.fullscreenElement) {
      await document.documentElement.requestFullscreen();
      appWindow.classList.add('fullscreen');
      fullscreenBtn.textContent = '🗗';
      fullscreenBtn.title = 'Pencereden çık';
    } else {
      await document.exitFullscreen();
      appWindow.classList.remove('fullscreen');
      fullscreenBtn.textContent = '▢';
      fullscreenBtn.title = 'Tam ekran';
    }
  } catch (error) {
    addMessage('assistant', `Tam ekran işlemi başarısız oldu: ${error.message}`);
  }
}

function exportConversation() {
  const lines = conversation.map((item) => `${item.role.toUpperCase()}: ${item.content}`);
  const text = [`C.O.M.R.A.D.E 7.1 STATE REPORT`, `Generated: ${new Date().toISOString()}`, '', ...lines].join('\n');
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'state_report.txt';
  a.click();
  URL.revokeObjectURL(url);
}

function startClock() {
  const updateClock = () => {
    const now = new Date();
    clockText.textContent = now.toLocaleTimeString('tr-TR', { hour12: false });
  };
  updateClock();
  setInterval(updateClock, 1000);
}

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = promptInput.value.trim();
  if (!prompt) return;

  addMessage('user', prompt);
  conversation.push({ role: 'user', content: prompt });
  promptInput.value = '';
  statusText.textContent = 'Moskova’ya bağlanılıyor...';

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: conversation,
        mode: modeSelect.value,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Bilinmeyen hata');
    }

    const answer = data.reply;
    conversation.push({ role: 'assistant', content: answer });
    addMessage('assistant', answer);
    statusText.textContent = 'Online';
  } catch (error) {
    addMessage('assistant', `Bağlantı kesildi. Hattı yeniden kurun, yoldaş. (${error.message})`);
    statusText.textContent = 'Offline';
  }
});

newChatBtn.addEventListener('click', resetChat);
aboutBtn.addEventListener('click', () => aboutDialog.showModal());
closeAboutBtn.addEventListener('click', () => aboutDialog.close());
fullscreenBtn.addEventListener('click', toggleFullscreen);
exportBtn.addEventListener('click', exportConversation);

document.addEventListener('fullscreenchange', () => {
  if (!document.fullscreenElement) {
    const appWindow = document.getElementById('chatWindow');
    appWindow.classList.remove('fullscreen');
    fullscreenBtn.textContent = '▢';
    fullscreenBtn.title = 'Tam ekran';
  }
});

runBoot();
startClock();
