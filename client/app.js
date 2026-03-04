const root = document.documentElement;
const THEME_KEY = 'theme';

function applyTheme(theme) {
  root.setAttribute('data-theme', theme);
  const toggle = document.getElementById('themeToggle');
  if (toggle) toggle.textContent = theme === 'dark' ? '☀️ Aydınlık' : '🌙 Karanlık';
}

function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) || 'light';
  applyTheme(saved);

  const toggle = document.getElementById('themeToggle');
  if (!toggle) return;

  toggle.addEventListener('click', () => {
    const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function initAuthPage() {
  const authForm = document.getElementById('authForm');
  if (!authForm) return;

  const authMessage = document.getElementById('authMessage');
  const inviteWrap = document.getElementById('inviteWrap');
  const authSubmit = document.getElementById('authSubmit');
  const tabLogin = document.getElementById('tabLogin');
  const tabRegister = document.getElementById('tabRegister');

  let mode = 'login';

  function setMode(nextMode) {
    mode = nextMode;
    const isRegister = mode === 'register';
    tabLogin.classList.toggle('active', !isRegister);
    tabRegister.classList.toggle('active', isRegister);
    inviteWrap.classList.toggle('hidden', !isRegister);
    authSubmit.textContent = isRegister ? 'Kayıt Ol' : 'Giriş Yap';
    authMessage.textContent = '';
  }

  tabLogin.addEventListener('click', () => setMode('login'));
  tabRegister.addEventListener('click', () => setMode('register'));

  authForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const inviteCode = document.getElementById('inviteCode').value.trim();

    const endpoint = mode === 'register' ? '/api/auth/register' : '/api/auth/login';
    const payload = mode === 'register' ? { username, password, inviteCode } : { username, password };

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || 'İşlem başarısız');

      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      window.location.href = '/chat.html';
    } catch (err) {
      authMessage.textContent = err.message;
    }
  });

  setMode('login');
}

function initChatPage() {
  const conversationList = document.getElementById('conversationList');
  if (!conversationList) return;

  const logoutBtn = document.getElementById('logoutBtn');
  const welcomeText = document.getElementById('welcomeText');
  const newConversationForm = document.getElementById('newConversationForm');
  const newConversationInput = document.getElementById('newConversationInput');
  const currentConversationName = document.getElementById('currentConversationName');
  const messagesEl = document.getElementById('messages');
  const typingIndicator = document.getElementById('typingIndicator');
  const messageSearchInput = document.getElementById('messageSearchInput');
  const messageForm = document.getElementById('messageForm');
  const messageInput = document.getElementById('messageInput');
  const fileInput = document.getElementById('fileInput');

  const token = localStorage.getItem('token');
  const rawUser = localStorage.getItem('user');
  if (!token || !rawUser) {
    window.location.href = '/';
    return;
  }

  const currentUser = JSON.parse(rawUser);
  welcomeText.textContent = `Hoş geldin, ${currentUser.username}`;

  let socket;
  let conversations = [];
  let activeConversationId = null;
  let currentMessages = [];
  let typingTimeout;

  async function api(path, options = {}) {
    const response = await fetch(path, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(options.headers || {})
      }
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'İstek başarısız');
    return data;
  }

  function formatTime(value) {
    return new Date(value || Date.now()).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
  }

  function renderMessages() {
    const query = messageSearchInput.value.trim().toLowerCase();
    const filtered = currentMessages.filter((message) => {
      if (!query) return true;
      return `${message.username || ''} ${message.text || ''} ${message.fileName || ''}`.toLowerCase().includes(query);
    });

    messagesEl.innerHTML = '';

    filtered.forEach((message) => {
      const li = document.createElement('li');
      li.classList.add('message-item');
      li.dataset.messageId = message._id || '';

      if (message.system) {
        li.classList.add('system');
        li.textContent = message.text;
      } else {
        const isSelf = message.userId === currentUser.id || message.username === currentUser.username;
        li.classList.add(isSelf ? 'self' : 'other');

        const textHtml = message.text ? `<div>${escapeHtml(message.text)}</div>` : '';
        const fileHtml = message.fileUrl
          ? `<a class="file-link" href="${escapeHtml(message.fileUrl)}" target="_blank" rel="noopener noreferrer">📎 ${escapeHtml(message.fileName || 'Dosya')}</a>`
          : '';
        const deleteHtml = isSelf && message._id ? '<button class="delete-btn" type="button">Sil</button>' : '';

        li.innerHTML = `<strong>${escapeHtml(message.username || 'Kullanıcı')}</strong>${textHtml}${fileHtml}<span class="meta">${formatTime(message.createdAt)}</span>${deleteHtml}`;

        const deleteBtn = li.querySelector('.delete-btn');
        if (deleteBtn) {
          deleteBtn.addEventListener('click', () => {
            socket.emit('chat:delete', {
              conversationId: activeConversationId,
              messageId: message._id
            });
          });
        }
      }

      messagesEl.appendChild(li);
    });

    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addSystemMessage(text) {
    currentMessages.push({ system: true, text, createdAt: Date.now() });
    renderMessages();
  }

  function renderConversations() {
    conversationList.innerHTML = '';

    conversations.forEach((conversation) => {
      const li = document.createElement('li');
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = conversation.name;
      btn.classList.toggle('active', conversation._id === activeConversationId);

      btn.addEventListener('click', () => {
        activeConversationId = conversation._id;
        currentConversationName.textContent = conversation.name;
        currentMessages = [];
        typingIndicator.textContent = '';
        renderConversations();
        renderMessages();
        socket.emit('chat:join', { conversationId: activeConversationId });
      });

      li.appendChild(btn);
      conversationList.appendChild(li);
    });
  }

  async function uploadSelectedFile() {
    if (!fileInput.files.length) return null;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const response = await fetch('/api/chat/upload', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Dosya yüklenemedi');
    fileInput.value = '';
    return data;
  }

  async function loadConversations() {
    conversations = await api('/api/chat/conversations');
    renderConversations();

    if (conversations.length) {
      activeConversationId = conversations[0]._id;
      currentConversationName.textContent = conversations[0].name;
      renderConversations();
      socket.emit('chat:join', { conversationId: activeConversationId });
    }
  }

  socket = io({ auth: { token } });

  socket.on('chat:history', (messages) => {
    currentMessages = messages;
    renderMessages();
  });

  socket.on('chat:new-message', (message) => {
    if (message.conversationId !== activeConversationId) return;
    currentMessages.push(message);
    typingIndicator.textContent = '';
    renderMessages();
  });

  socket.on('chat:deleted', ({ conversationId, messageId }) => {
    if (conversationId !== activeConversationId) return;
    currentMessages = currentMessages.filter((message) => message._id !== messageId);
    renderMessages();
  });

  socket.on('chat:typing', ({ conversationId, username, isTyping }) => {
    if (conversationId !== activeConversationId) return;
    typingIndicator.textContent = isTyping ? `${username} yazıyor...` : '';
  });

  socket.on('chat:user-joined', ({ message }) => addSystemMessage(message));
  socket.on('chat:user-left', ({ message }) => addSystemMessage(message));
  socket.on('chat:error', ({ message }) => addSystemMessage(message));

  loadConversations();

  messageSearchInput.addEventListener('input', renderMessages);

  newConversationForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const name = newConversationInput.value.trim();
    if (!name) return;

    try {
      const created = await api('/api/chat/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
      });
      conversations.push(created);
      newConversationInput.value = '';
      renderConversations();
    } catch (err) {
      addSystemMessage(err.message);
    }
  });

  messageInput.addEventListener('input', () => {
    if (!activeConversationId) return;
    socket.emit('chat:typing', { conversationId: activeConversationId, isTyping: true });

    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
      socket.emit('chat:typing', { conversationId: activeConversationId, isTyping: false });
    }, 900);
  });

  messageForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!activeConversationId) return;

    const text = messageInput.value.trim();

    try {
      const uploaded = await uploadSelectedFile();
      if (!text && !uploaded) return;

      socket.emit('chat:send', {
        conversationId: activeConversationId,
        text,
        fileUrl: uploaded?.fileUrl,
        fileName: uploaded?.fileName,
        fileType: uploaded?.fileType
      });

      socket.emit('chat:typing', { conversationId: activeConversationId, isTyping: false });
      messageInput.value = '';
    } catch (err) {
      addSystemMessage(err.message);
    }
  });

  logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    socket.disconnect();
    window.location.href = '/';
  });
}

initTheme();
initAuthPage();
initChatPage();
