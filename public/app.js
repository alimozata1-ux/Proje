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

runBoot();
