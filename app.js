const API_BASE = window.API_BASE || './api';

const TABS = {
  schematics: { title: 'Arduino Şemaları', description: 'Bağlantı planları ve pin dizilimleri.' },
  codes: { title: 'Kodlar', description: 'Arduino kod örnekleri.' },
  apps: { title: 'Uygulamalar', description: 'Araçlar ve uygulama dosyaları.' },
  announcements: { title: 'Önceden Haber Verme', description: 'Planlanan içerikler ve duyurular.' },
};

const state = {
  activeTab: 'schematics',
  posts: { schematics: [], codes: [], apps: [], announcements: [] },
  isAdmin: false,
  search: '',
};

const refs = {
  tabButtons: Array.from(document.querySelectorAll('.tab')),
  searchInput: document.getElementById('searchInput'),
  activeTabTitle: document.getElementById('activeTabTitle'),
  activeTabDescription: document.getElementById('activeTabDescription'),
  countTotal: document.getElementById('countTotal'),
  countShown: document.getElementById('countShown'),
  cardsContainer: document.getElementById('cardsContainer'),
  cardTemplate: document.getElementById('cardTemplate'),

  authCard: document.getElementById('authCard'),
  emailInput: document.getElementById('emailInput'),
  codeInput: document.getElementById('codeInput'),
  sendCodeBtn: document.getElementById('sendCodeBtn'),
  loginBtn: document.getElementById('loginBtn'),
  authStatus: document.getElementById('authStatus'),

  postForm: document.getElementById('postForm'),
  postTab: document.getElementById('postTab'),
  postTitle: document.getElementById('postTitle'),
  postSummary: document.getElementById('postSummary'),
  postContent: document.getElementById('postContent'),
  postCode: document.getElementById('postCode'),
  postImage: document.getElementById('postImage'),
  postTags: document.getElementById('postTags'),
  postPinned: document.getElementById('postPinned'),
  postNotify: document.getElementById('postNotify'),
  postSchedule: document.getElementById('postSchedule'),
  postStatus: document.getElementById('postStatus'),
  logoutBtn: document.getElementById('logoutBtn'),
};

function status(node, msg, type = '') {
  node.textContent = msg;
  node.className = `status ${type}`.trim();
}

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const data = await res.json().catch(() => ({ ok: false, message: 'JSON parse hatası' }));
  if (!res.ok || data.ok === false) {
    throw new Error(data.message || 'İstek başarısız');
  }
  return data;
}

function parseTags(raw) {
  return raw
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
    .slice(0, 20);
}

function currentPostType() {
  const selected = document.querySelector('input[name="postType"]:checked');
  return selected ? selected.value : 'normal';
}

function updateAdminUI() {
  refs.authCard.classList.toggle('hidden', state.isAdmin);
  refs.postForm.classList.toggle('hidden', !state.isAdmin);
}

function updateHeader() {
  refs.activeTabTitle.textContent = TABS[state.activeTab].title;
  refs.activeTabDescription.textContent = TABS[state.activeTab].description;
}

function getVisiblePosts() {
  const list = state.posts[state.activeTab] || [];
  if (!state.search.trim()) return list;

  const q = state.search.toLocaleLowerCase('tr');
  return list.filter((p) => {
    const src = `${p.title || ''} ${p.summary || ''} ${p.content || ''} ${(p.tags || []).join(' ')}`;
    return src.toLocaleLowerCase('tr').includes(q);
  });
}

function renderCards() {
  refs.cardsContainer.innerHTML = '';

  const all = state.posts[state.activeTab] || [];
  const shown = getVisiblePosts();

  refs.countTotal.textContent = `Toplam: ${all.length}`;
  refs.countShown.textContent = `Gösterilen: ${shown.length}`;

  if (shown.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.textContent = 'İçerik bulunamadı.';
    refs.cardsContainer.appendChild(empty);
    return;
  }

  const sorted = [...shown].sort((a, b) => Number(b.pinned) - Number(a.pinned));

  sorted.forEach((post) => {
    const frag = refs.cardTemplate.content.cloneNode(true);

    frag.querySelector('.card__title').textContent = post.title || '';
    frag.querySelector('.card__summary').textContent = post.summary || '';
    frag.querySelector('.card__content').textContent = post.content || '';
    frag.querySelector('.card__date').textContent = `Yayın: ${post.createdAt || ''}`;

    const codeNode = frag.querySelector('.card__code');
    if (post.code?.trim()) {
      codeNode.classList.remove('hidden');
      codeNode.textContent = post.code;
    }

    const imageNode = frag.querySelector('.card__image');
    if (post.image?.trim()) {
      imageNode.classList.remove('hidden');
      imageNode.src = post.image;
    }

    if (post.pinned) frag.querySelector('.badge--pinned').classList.remove('hidden');
    if (post.type === 'scheduled') frag.querySelector('.badge--scheduled').classList.remove('hidden');

    const tagsNode = frag.querySelector('.tags');
    (post.tags || []).forEach((tag) => {
      const span = document.createElement('span');
      span.className = 'tag';
      span.textContent = `#${tag}`;
      tagsNode.appendChild(span);
    });

    refs.cardsContainer.appendChild(frag);
  });
}

function selectTab(tab) {
  state.activeTab = tab;
  refs.tabButtons.forEach((btn) => btn.classList.toggle('is-active', btn.dataset.tab === tab));
  updateHeader();
  renderCards();
}

async function loadPosts() {
  const data = await api('/posts.php');
  state.posts = data.posts;
  state.isAdmin = Boolean(data.isAdmin);
  updateAdminUI();
  updateHeader();
  renderCards();
}

async function sendCode() {
  try {
    const email = refs.emailInput.value.trim();
    const data = await api('/send-code.php', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });

    status(refs.authStatus, `${data.message}. Demo kod: ${data.demoCode}`, 'success');
  } catch (error) {
    status(refs.authStatus, error.message, 'error');
  }
}

async function login() {
  try {
    const email = refs.emailInput.value.trim();
    const code = refs.codeInput.value.trim();

    const data = await api('/login.php', {
      method: 'POST',
      body: JSON.stringify({ email, code }),
    });

    status(refs.authStatus, data.message, 'success');
    state.isAdmin = true;
    updateAdminUI();
  } catch (error) {
    status(refs.authStatus, error.message, 'error');
  }
}

async function logout() {
  try {
    await api('/logout.php', { method: 'POST', body: JSON.stringify({}) });
    state.isAdmin = false;
    updateAdminUI();
    status(refs.postStatus, 'Çıkış yapıldı', 'success');
  } catch (error) {
    status(refs.postStatus, error.message, 'error');
  }
}

async function createPost(event) {
  event.preventDefault();

  const payload = {
    tab: refs.postTab.value,
    title: refs.postTitle.value.trim(),
    summary: refs.postSummary.value.trim(),
    content: refs.postContent.value.trim(),
    code: refs.postCode.value,
    image: refs.postImage.value.trim(),
    tags: parseTags(refs.postTags.value),
    pinned: refs.postPinned.checked,
    notify: refs.postNotify.checked,
    type: currentPostType(),
    scheduledAt: refs.postSchedule.value,
  };

  try {
    const data = await api('/posts.php', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    status(refs.postStatus, data.message, 'success');
    refs.postForm.reset();
    await loadPosts();
    selectTab(payload.tab);
  } catch (error) {
    status(refs.postStatus, error.message, 'error');
  }
}

function bindEvents() {
  refs.tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => selectTab(btn.dataset.tab));
  });

  refs.searchInput.addEventListener('input', () => {
    state.search = refs.searchInput.value;
    renderCards();
  });

  refs.sendCodeBtn.addEventListener('click', sendCode);
  refs.loginBtn.addEventListener('click', login);
  refs.logoutBtn.addEventListener('click', logout);
  refs.postForm.addEventListener('submit', createPost);
}

async function init() {
  bindEvents();
  await loadPosts();
}

init();
