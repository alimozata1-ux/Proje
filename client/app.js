const root = document.documentElement;
const THEME_KEY = 'theme';
const KEYS = {
  TOKEN: 'token',
  USER: 'user',
  MUTED_ROOMS: 'mutedRooms'
};

const state = {
  runtimeConfig: null,
  socket: null,
  mode: 'login',
  token: null,
  user: null,
  activeConversationId: null,
  conversations: [],
  messages: [],
  unreadByRoom: {},
  typingTimer: null,
  selectedFile: null,
  authSubmitting: false,
  mutedRooms: {},
  presenceByRoom: {}
};


function getRuntimeConfig() {
  const cfg = window.GOBLINCHAT_CONFIG || {};
  const apiBase = (cfg.API_BASE || '').trim();
  const socketUrl = (cfg.SOCKET_URL || apiBase || '').trim();

  return {
    apiBase,
    socketUrl
  };
}

function buildApiUrl(path) {
  const { apiBase } = getRuntimeConfig();
  if (!apiBase) return path;
  return `${apiBase}${path}`;
}

function getSocketTarget() {
  const { socketUrl } = getRuntimeConfig();
  return socketUrl || undefined;
}


function qs(selector) {
  return document.querySelector(selector);
}

function qid(id) {
  return document.getElementById(id);
}

function toJSONSafe(value, fallback = null) {
  try {
    return JSON.parse(value);
  } catch {
    return fallback;
  }
}

function getSavedTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === 'light' || stored === 'dark') return stored;

  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  return prefersDark ? 'dark' : 'light';
}

function setThemeButtonVisual(theme) {
  const button = qid('themeToggle');
  if (!button) return;
  button.textContent = theme === 'dark' ? '☀️' : '🌙';
  button.title = theme === 'dark' ? 'Aydınlık moda geç' : 'Karanlık moda geç';
}

function applyTheme(theme) {
  root.setAttribute('data-theme', theme);
  setThemeButtonVisual(theme);
}

function initThemeSystem() {
  const current = getSavedTheme();
  applyTheme(current);

  const toggle = qid('themeToggle');
  if (!toggle) return;

  toggle.addEventListener('click', () => {
    const active = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = active === 'dark' ? 'light' : 'dark';
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

function formatTime(dateValue) {
  const date = new Date(dateValue || Date.now());
  return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}

function formatDate(dateValue) {
  const date = new Date(dateValue || Date.now());
  return date.toLocaleDateString('tr-TR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

async function fetchJSON(url, options = {}) {
  const headers = {
    ...(options.headers || {})
  };

  let response;
  try {
    response = await fetch(url, {
      ...options,
      headers
    });
  } catch (error) {
    throw new Error(
      'Sunucuya ulasilamadi. Backend URL ayarini (API_BASE/SOCKET_URL) ve ag baglantisini kontrol edin.'
    );
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.message || `İstek başarısız. (HTTP ${response.status})`);
  }

  return data;
}

async function authFetch(path, options = {}) {
  return fetchJSON(buildApiUrl(path), {
    ...options,
    headers: {
      Authorization: `Bearer ${state.token}`,
      ...(options.headers || {})
    }
  });
}

function setAuthMessage(message = '') {
  const box = qid('authMessage');
  if (!box) return;
  box.textContent = message;
}


function normalizeErrorText(message) {
  if (!message) return 'İstek başarısız. Lütfen tekrar deneyin.';

  return String(message)
    .replaceAll('başarırız', 'başarısız')
    .replaceAll('basaririz', 'basarisiz');
}

function setAuthSubmitting(isSubmitting) {
  state.authSubmitting = isSubmitting;

  const submit = qid('authSubmit');
  if (!submit) return;

  submit.disabled = isSubmitting;
  if (isSubmitting) {
    submit.dataset.originalText = submit.textContent;
    submit.textContent = 'İşleniyor...';
  } else if (submit.dataset.originalText) {
    submit.textContent = submit.dataset.originalText;
  }
}


function setAuthMode(nextMode) {
  state.mode = nextMode;

  const tabLogin = qid('tabLogin');
  const tabRegister = qid('tabRegister');
  const inviteWrap = qid('inviteWrap');
  const submit = qid('authSubmit');

  if (!tabLogin || !tabRegister || !inviteWrap || !submit) return;

  const register = nextMode === 'register';
  tabLogin.classList.toggle('active', !register);
  tabRegister.classList.toggle('active', register);
  tabLogin.setAttribute('aria-selected', String(!register));
  tabRegister.setAttribute('aria-selected', String(register));
  inviteWrap.classList.toggle('hidden', !register);
  submit.textContent = register ? 'Kayıt Ol' : 'Giriş Yap';
  setAuthMessage('');
}

async function onAuthSubmit(event) {
  event.preventDefault();
  if (state.authSubmitting) return;

  const username = qid('username')?.value.trim() || '';
  const password = qid('password')?.value || '';
  const inviteCode = qid('inviteCode')?.value.trim() || '';

  const isRegister = state.mode === 'register';

  const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login';
  const payload = isRegister ? { username, password, inviteCode } : { username, password };

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 12000);

  try {
    setAuthSubmitting(true);
    setAuthMessage('');

    const data = await fetchJSON(buildApiUrl(endpoint), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });

    localStorage.setItem(KEYS.TOKEN, data.token);
    localStorage.setItem(KEYS.USER, JSON.stringify(data.user));

    window.location.href = '/chat.html';
  } catch (error) {
    if (error.name === 'AbortError') {
      setAuthMessage('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.');
    } else {
      setAuthMessage(normalizeErrorText(error.message));
    }
  } finally {
    clearTimeout(timeoutId);
    setAuthSubmitting(false);
  }
}

function initAuthPage() {
  const authForm = qid('authForm');
  if (!authForm) return;

  const tabLogin = qid('tabLogin');
  const tabRegister = qid('tabRegister');

  tabLogin?.addEventListener('click', () => setAuthMode('login'));
  tabRegister?.addEventListener('click', () => setAuthMode('register'));

  authForm.addEventListener('submit', onAuthSubmit);

  setAuthMode('login');
}

function getUser() {
  const raw = localStorage.getItem(KEYS.USER);
  return toJSONSafe(raw);
}

function mutedRoomsStorageKey() {
  const userId = state.user?.id || 'guest';
  return `${KEYS.MUTED_ROOMS}:${userId}`;
}

function loadMutedRooms() {
  const raw = localStorage.getItem(mutedRoomsStorageKey());
  state.mutedRooms = toJSONSafe(raw, {}) || {};
}

function saveMutedRooms() {
  localStorage.setItem(mutedRoomsStorageKey(), JSON.stringify(state.mutedRooms));
}

function isRoomMuted(conversationId) {
  return Boolean(state.mutedRooms[conversationId]);
}

function toggleRoomMute(conversationId) {
  if (!conversationId) return;

  if (isRoomMuted(conversationId)) {
    delete state.mutedRooms[conversationId];
  } else {
    state.mutedRooms[conversationId] = true;
  }

  saveMutedRooms();
  renderConversations();
  updateMuteButtonText();
}

function updateMuteButtonText() {
  const btn = qid('toggleMuteRoomBtn');
  if (!btn || !state.activeConversationId) return;
  btn.textContent = isRoomMuted(state.activeConversationId) ? 'Sessizi Kaldır' : 'Odayı Sessize Al';
}

function setPresenceText(conversationId) {
  const el = qid('presenceIndicator');
  if (!el) return;
  const count = state.presenceByRoom[conversationId] || 0;
  el.textContent = `${count} kişi çevrimiçi`;
}

function ensureChatSession() {
  state.token = localStorage.getItem(KEYS.TOKEN);
  state.user = getUser();

  if (!state.token || !state.user) {
    window.location.href = '/';
    return false;
  }

  return true;
}

function updateUserVisuals() {
  const welcome = qid('welcomeText');
  const avatar = qid('avatarInitial');

  if (welcome) {
    welcome.textContent = state.user?.username ? `Hoş geldin, ${state.user.username}` : '';
  }

  if (avatar) {
    avatar.textContent = state.user?.username?.[0]?.toUpperCase() || 'G';
  }
}

function roomBadgeText() {
  const total = state.conversations.length;
  return `${total} oda`;
}

function updateRoomBadge() {
  const badge = qid('roomCountBadge');
  if (!badge) return;
  badge.textContent = roomBadgeText();
}

function getConversationUnread(conversationId) {
  return state.unreadByRoom[conversationId] || 0;
}

function incrementUnread(conversationId) {
  if (!conversationId) return;
  state.unreadByRoom[conversationId] = getConversationUnread(conversationId) + 1;
}

function resetUnread(conversationId) {
  if (!conversationId) return;
  state.unreadByRoom[conversationId] = 0;
}

function conversationButtonHTML(conversation, unreadCount) {
  const muted = isRoomMuted(conversation._id);
  const unread = unreadCount > 0 && !muted ? `<span class="unread-dot" title="${unreadCount} yeni mesaj"></span>` : '';
  const mutedLabel = muted ? '🔕' : '';

  return `
    <span class="${muted ? 'room-muted' : ''}">${escapeHtml(conversation.name)}</span>
    <span class="room-meta">${mutedLabel} ${unread}</span>
  `;
}

function renderConversations() {
  const list = qid('conversationList');
  if (!list) return;

  list.innerHTML = '';

  state.conversations.forEach((conversation) => {
    const li = document.createElement('li');
    const button = document.createElement('button');

    button.type = 'button';
    button.classList.toggle('active', state.activeConversationId === conversation._id);
    button.innerHTML = conversationButtonHTML(conversation, getConversationUnread(conversation._id));

    button.addEventListener('click', () => {
      if (state.activeConversationId === conversation._id) return;

      state.activeConversationId = conversation._id;
      resetUnread(conversation._id);
      qid('currentConversationName').textContent = conversation.name;
      clearTypingIndicator();
      setPresenceText(conversation._id);
      renderConversations();
      updateMuteButtonText();
      loadConversationHistory(conversation._id);
      emitJoinRoom(conversation._id);
    });

    li.appendChild(button);
    list.appendChild(li);
  });

  updateRoomBadge();
}

function setEmptyStateVisibility() {
  const empty = qid('emptyState');
  if (!empty) return;
  empty.classList.toggle('hidden', state.messages.length > 0);
}

function filteredMessages() {
  const query = (qid('messageSearchInput')?.value || '').trim().toLowerCase();
  if (!query) return state.messages;

  return state.messages.filter((message) => {
    const searchable = `${message.username || ''} ${message.text || ''} ${message.fileName || ''}`.toLowerCase();
    return searchable.includes(query);
  });
}

function messageIsMine(message) {
  if (!message || message.system) return false;
  if (message.userId && state.user?.id) {
    return String(message.userId) === String(state.user.id);
  }
  return message.username === state.user?.username;
}

function createDeleteButton(message) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'delete-btn';
  button.textContent = 'Sil';

  button.addEventListener('click', () => {
    if (!state.activeConversationId) return;
    state.socket?.emit('chat:delete', {
      conversationId: state.activeConversationId,
      messageId: message._id
    });
  });

  return button;
}

function createEditButton(message) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'edit-btn';
  button.textContent = 'Düzenle';

  button.addEventListener('click', () => {
    const nextText = prompt('Yeni mesaj metni:', message.text || '');
    if (nextText === null) return;

    const trimmed = nextText.trim();
    if (!trimmed) {
      addSystemMessage('Mesaj boş olamaz.');
      return;
    }

    state.socket?.emit('chat:edit', {
      conversationId: state.activeConversationId,
      messageId: message._id,
      text: trimmed
    });
  });

  return button;
}

function renderMessageContent(li, message) {
  if (message.system) {
    li.classList.add('system');
    li.textContent = message.text;
    return;
  }

  const mine = messageIsMine(message);
  li.classList.add(mine ? 'self' : 'other');

  const sender = document.createElement('strong');
  sender.textContent = message.username || 'Kullanıcı';
  li.appendChild(sender);

  if (message.text) {
    const text = document.createElement('div');
    text.textContent = message.text;
    li.appendChild(text);
  }

  if (message.fileUrl) {
    const link = document.createElement('a');
    link.className = 'file-link';
    link.href = message.fileUrl;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = `📎 ${message.fileName || 'Dosya'}`;
    li.appendChild(link);
  }

  const meta = document.createElement('span');
  meta.className = 'meta';
  const editedTag = message.edited ? ' • düzenlendi' : '';
  meta.textContent = `${formatDate(message.createdAt)} • ${formatTime(message.createdAt)}${editedTag}`;
  li.appendChild(meta);

  if (mine && message._id) {
    const actions = document.createElement('div');
    actions.className = 'message-actions';
    actions.appendChild(createEditButton(message));
    actions.appendChild(createDeleteButton(message));
    li.appendChild(actions);
  }
}

function renderMessages() {
  const messagesEl = qid('messages');
  if (!messagesEl) return;

  messagesEl.innerHTML = '';

  filteredMessages().forEach((message) => {
    const li = document.createElement('li');
    li.classList.add('message-item');
    li.dataset.messageId = message._id || '';

    renderMessageContent(li, message);
    messagesEl.appendChild(li);
  });

  messagesEl.scrollTop = messagesEl.scrollHeight;
  setEmptyStateVisibility();
}

function setTypingIndicator(text = '') {
  const indicator = qid('typingIndicator');
  if (!indicator) return;
  indicator.textContent = text;
}

function clearTypingIndicator() {
  setTypingIndicator('');
}

function addSystemMessage(text) {
  state.messages.push({
    system: true,
    text,
    createdAt: Date.now()
  });
  renderMessages();
}

function appendIncomingMessage(message) {
  if (message.conversationId !== state.activeConversationId) {
    if (!isRoomMuted(message.conversationId)) {
      incrementUnread(message.conversationId);
    }
    renderConversations();
    return;
  }

  state.messages.push(message);
  clearTypingIndicator();
  renderMessages();
}

function replaceMessageList(messages) {
  state.messages = Array.isArray(messages) ? messages : [];
  renderMessages();
}

function removeMessageFromState(messageId) {
  state.messages = state.messages.filter((message) => String(message._id) !== String(messageId));
  renderMessages();
}

function updateSelectedFilePill() {
  const pill = qid('selectedFilePill');
  if (!pill) return;

  if (!state.selectedFile) {
    pill.classList.add('hidden');
    pill.textContent = '';
    return;
  }

  pill.classList.remove('hidden');
  pill.innerHTML = `<span>📎 ${escapeHtml(state.selectedFile.name)}</span><button id="clearFileBtn" class="ghost" type="button">Kaldır</button>`;

  const clearButton = qid('clearFileBtn');
  clearButton?.addEventListener('click', () => {
    state.selectedFile = null;
    const fileInput = qid('fileInput');
    if (fileInput) fileInput.value = '';
    updateSelectedFilePill();
  });
}

async function uploadSelectedFile() {
  if (!state.selectedFile) return null;

  const formData = new FormData();
  formData.append('file', state.selectedFile);

  const result = await authFetch('/api/chat/upload', {
    method: 'POST',
    body: formData
  });

  state.selectedFile = null;
  updateSelectedFilePill();

  return result;
}

function emitJoinRoom(conversationId) {
  if (!state.socket || !conversationId) return;
  state.socket.emit('chat:join', { conversationId });
}

async function loadConversationHistory(conversationId) {
  if (!conversationId) {
    replaceMessageList([]);
    return;
  }

  // Socket history event kullanılacağı için önce boşaltıp join gönderiyoruz.
  replaceMessageList([]);
}

async function loadConversations() {
  const rooms = await authFetch('/api/chat/conversations');
  state.conversations = rooms;

  if (!state.activeConversationId && state.conversations.length > 0) {
    state.activeConversationId = state.conversations[0]._id;
    qid('currentConversationName').textContent = state.conversations[0].name;
  }

  renderConversations();

  if (state.activeConversationId) {
    updateMuteButtonText();
    setPresenceText(state.activeConversationId);
    emitJoinRoom(state.activeConversationId);
  }
}

async function createConversation(name) {
  const created = await authFetch('/api/chat/conversations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name })
  });

  state.conversations.push(created);
  state.unreadByRoom[created._id] = 0;
  renderConversations();
}

function emitTyping(isTyping) {
  if (!state.socket || !state.activeConversationId) return;
  state.socket.emit('chat:typing', {
    conversationId: state.activeConversationId,
    isTyping: Boolean(isTyping)
  });
}

function scheduleTypingOff() {
  clearTimeout(state.typingTimer);
  state.typingTimer = setTimeout(() => emitTyping(false), 900);
}

function autoresizeTextarea(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = `${Math.min(textarea.scrollHeight, 140)}px`;
}

function resetComposer() {
  const input = qid('messageInput');
  if (!input) return;
  input.value = '';
  input.style.height = 'auto';
  emitTyping(false);
}

async function onSendMessage(event) {
  event.preventDefault();

  if (!state.activeConversationId || !state.socket) return;

  const textArea = qid('messageInput');
  const text = textArea?.value.trim() || '';

  try {
    const uploaded = await uploadSelectedFile();
    if (!text && !uploaded) return;

    state.socket.emit('chat:send', {
      conversationId: state.activeConversationId,
      text,
      fileUrl: uploaded?.fileUrl,
      fileName: uploaded?.fileName,
      fileType: uploaded?.fileType
    });

    resetComposer();
  } catch (error) {
    addSystemMessage(error.message);
  }
}

function onMessageInput(event) {
  const textarea = event.target;
  autoresizeTextarea(textarea);

  if (!state.activeConversationId) return;
  emitTyping(true);
  scheduleTypingOff();
}

function onMessageInputKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    qid('messageForm')?.requestSubmit();
  }
}

function onGlobalKeydown(event) {
  if (event.key === '/') {
    const search = qid('messageSearchInput');
    if (!search) return;

    const activeTag = document.activeElement?.tagName;
    if (activeTag === 'INPUT' || activeTag === 'TEXTAREA') return;

    event.preventDefault();
    search.focus();
  }
}

function wireSocketEvents() {
  state.socket.on('connect_error', (error) => {
    addSystemMessage(`Bağlantı hatası: ${error.message}`);
  });

  state.socket.on('chat:history', (messages) => {
    replaceMessageList(messages);
    resetUnread(state.activeConversationId);
    renderConversations();
  });

  state.socket.on('chat:new-message', (message) => {
    appendIncomingMessage(message);
  });

  state.socket.on('chat:deleted', ({ conversationId, messageId }) => {
    if (conversationId !== state.activeConversationId) return;
    removeMessageFromState(messageId);
  });

  state.socket.on('chat:edited', ({ conversationId, messageId, text, updatedAt }) => {
    if (conversationId !== state.activeConversationId) return;
    state.messages = state.messages.map((message) =>
      String(message._id) === String(messageId)
        ? { ...message, text, updatedAt, edited: true }
        : message
    );
    renderMessages();
  });

  state.socket.on('chat:presence', ({ conversationId, onlineCount }) => {
    state.presenceByRoom[conversationId] = onlineCount;
    if (conversationId === state.activeConversationId) {
      setPresenceText(conversationId);
    }
  });

  state.socket.on('chat:typing', ({ conversationId, username, isTyping }) => {
    if (conversationId !== state.activeConversationId) return;
    if (!isTyping) {
      clearTypingIndicator();
      return;
    }
    setTypingIndicator(`${username} yazıyor...`);
  });

  state.socket.on('chat:user-joined', ({ message }) => addSystemMessage(message));
  state.socket.on('chat:user-left', ({ message }) => addSystemMessage(message));
  state.socket.on('chat:error', ({ message }) => addSystemMessage(message));
}

function bindChatEvents() {
  qid('logoutBtn')?.addEventListener('click', () => {
    localStorage.removeItem(KEYS.TOKEN);
    localStorage.removeItem(KEYS.USER);

    state.socket?.disconnect();
    window.location.href = '/';
  });

  qid('newConversationForm')?.addEventListener('submit', async (event) => {
    event.preventDefault();

    const input = qid('newConversationInput');
    const name = input?.value.trim() || '';
    if (!name) return;

    try {
      await createConversation(name);
      input.value = '';
    } catch (error) {
      addSystemMessage(error.message);
    }
  });

  qid('messageSearchInput')?.addEventListener('input', () => {
    renderMessages();
  });

  qid('toggleMuteRoomBtn')?.addEventListener('click', () => {
    toggleRoomMute(state.activeConversationId);
  });

  qid('clearSearchBtn')?.addEventListener('click', () => {
    const input = qid('messageSearchInput');
    if (!input) return;
    input.value = '';
    renderMessages();
  });

  qid('fileInput')?.addEventListener('change', (event) => {
    state.selectedFile = event.target.files?.[0] || null;
    updateSelectedFilePill();
  });

  qid('messageInput')?.addEventListener('input', onMessageInput);
  qid('messageInput')?.addEventListener('keydown', onMessageInputKeydown);
  qid('messageForm')?.addEventListener('submit', onSendMessage);

  window.addEventListener('keydown', onGlobalKeydown);
}

async function initChatPage() {
  if (typeof io === 'undefined') {
    addSystemMessage('Socket.io istemcisi yuklenemedi. Backend URL ayarini kontrol et.');
    return;
  }
  const chatRoot = qs('.chat-page');
  if (!chatRoot) return;

  if (!ensureChatSession()) return;

  updateUserVisuals();
  loadMutedRooms();

  state.socket = io(getSocketTarget(), { auth: { token: state.token } });
  wireSocketEvents();
  bindChatEvents();

  try {
    await loadConversations();
  } catch (error) {
    addSystemMessage(error.message);
  }
}

function init() {
  state.runtimeConfig = getRuntimeConfig();
  initThemeSystem();
  initAuthPage();
  initChatPage();
}

init();
