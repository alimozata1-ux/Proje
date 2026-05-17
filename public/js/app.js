// State
let currentUser = null;
let currentPage = 'home';

// Categories
const categories = ['Tümü', 'Web', 'Mobil', 'Oyun', 'Yapay Zeka', 'Masaüstü', 'API', 'Diğer'];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
  if (!e.target.closest('.profile-dropdown') && !e.target.closest('.dropdown-menu')) {
    closeDropdown();
  }
});

// Auth check
async function checkAuth() {
  try {
    const res = await fetch('/api/me');
    if (res.ok) {
      const data = await res.json();
      currentUser = data.user;
      updateNavbar(true);
    } else {
      updateNavbar(false);
    }
  } catch {
    updateNavbar(false);
  }
  navigate('home');
}

// Update navbar based on auth state
function updateNavbar(loggedIn) {
  const authDiv = document.getElementById('navAuth');
  const profileDiv = document.getElementById('navProfile');
  const newProjectLink = document.getElementById('newProjectLink');

  if (loggedIn && currentUser) {
    authDiv.style.display = 'none';
    profileDiv.style.display = 'block';
    newProjectLink.style.display = 'flex';
    document.getElementById('navUsername').textContent = currentUser.username;
    const avatarEl = document.getElementById('navAvatar');
    if (currentUser.avatar) {
      avatarEl.innerHTML = `<img src="${currentUser.avatar}" alt="avatar">`;
    } else {
      avatarEl.innerHTML = `<i class="fas fa-user"></i>`;
    }
  } else {
    authDiv.style.display = 'flex';
    profileDiv.style.display = 'none';
    newProjectLink.style.display = 'none';
  }
}

// Navigation
function navigate(page, data) {
  currentPage = page;
  const main = document.getElementById('mainContent');
  main.innerHTML = '';
  main.className = 'main-content page-enter';

  // Update active nav link
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.toggle('active', link.dataset.page === page);
  });

  switch (page) {
    case 'home': renderHome(); break;
    case 'explore': renderExplore(); break;
    case 'login': renderLogin(); break;
    case 'register': renderRegister(); break;
    case 'profile': renderProfile(); break;
    case 'settings': renderSettings(); break;
    case 'new-project': renderNewProject(); break;
    case 'my-projects': renderMyProjects(); break;
    case 'user': renderUserProfile(data); break;
    default: renderHome();
  }
}

// Toggle profile dropdown
function toggleProfileMenu() {
  const dropdown = document.getElementById('profileDropdown');
  dropdown.classList.toggle('show');
}

function closeDropdown() {
  const dropdown = document.getElementById('profileDropdown');
  if (dropdown) dropdown.classList.remove('show');
}

// Toast notification
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
  toast.innerHTML = `<i class="fas ${icon}"></i> ${message}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Search handler
function handleSearch(e) {
  if (e.key === 'Enter') {
    const query = e.target.value.trim();
    if (query) {
      navigate('explore');
      setTimeout(() => {
        document.getElementById('searchInput').value = query;
        loadProjects(query);
      }, 100);
    }
  }
}

// ==================== PAGE RENDERERS ====================

// HOME PAGE
function renderHome() {
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div class="hero">
      <h1>Projelerinizi Paylaşın & Keşfedin</h1>
      <p>Yaratıcı projelerinizi paylaşın, başkalarının çalışmalarını keşfedin ve ilham alın. Topluluğa katılın!</p>
      <div class="hero-actions">
        ${currentUser
          ? `<button class="btn btn-primary btn-lg" onclick="navigate('new-project')"><i class="fas fa-plus"></i> Proje Paylaş</button>
             <button class="btn btn-outline btn-lg" onclick="navigate('explore')"><i class="fas fa-compass"></i> Keşfet</button>`
          : `<button class="btn btn-primary btn-lg" onclick="navigate('register')"><i class="fas fa-user-plus"></i> Hemen Başla</button>
             <button class="btn btn-outline btn-lg" onclick="navigate('explore')"><i class="fas fa-compass"></i> Projeleri Keşfet</button>`
        }
      </div>
    </div>
    <div class="section-header">
      <h2>Son Projeler</h2>
      <button class="btn btn-ghost" onclick="navigate('explore')">Tümünü Gör <i class="fas fa-arrow-right"></i></button>
    </div>
    <div class="project-grid" id="homeProjects">
      <div class="empty-state"><div class="spinner" style="border-color: var(--primary); border-top-color: transparent; width: 32px; height: 32px;"></div></div>
    </div>
  `;
  loadHomeProjects();
}

async function loadHomeProjects() {
  try {
    const res = await fetch('/api/projects');
    const data = await res.json();
    const container = document.getElementById('homeProjects');
    if (!container) return;
    if (data.projects.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <i class="fas fa-folder-open"></i>
          <h3>Henüz proje yok</h3>
          <p>İlk projeyi paylaşan siz olun!</p>
          ${currentUser ? `<button class="btn btn-primary" onclick="navigate('new-project')"><i class="fas fa-plus"></i> Proje Ekle</button>` : ''}
        </div>`;
    } else {
      container.innerHTML = data.projects.slice(0, 6).map(renderProjectCard).join('');
    }
  } catch {
    document.getElementById('homeProjects').innerHTML = '<div class="empty-state">Projeler yüklenirken hata oluştu.</div>';
  }
}

// EXPLORE PAGE
function renderExplore() {
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div class="explore-header">
      <h1><i class="fas fa-compass"></i> Projeleri Keşfet</h1>
      <p>Tüm kategorilerdeki projeleri keşfedin</p>
    </div>
    <div class="category-filter" id="categoryFilter">
      ${categories.map((c, i) => `<button class="category-btn ${i === 0 ? 'active' : ''}" onclick="filterCategory('${c}', this)">${c}</button>`).join('')}
    </div>
    <div class="project-grid" id="exploreProjects">
      <div class="empty-state"><div class="spinner" style="border-color: var(--primary); border-top-color: transparent; width: 32px; height: 32px;"></div></div>
    </div>
  `;
  loadProjects();
}

let currentCategory = 'Tümü';

function filterCategory(category, btn) {
  currentCategory = category;
  document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  loadProjects();
}

async function loadProjects(searchQuery) {
  const container = document.getElementById('exploreProjects');
  if (!container) return;

  const params = new URLSearchParams();
  if (searchQuery) params.set('search', searchQuery);
  if (currentCategory && currentCategory !== 'Tümü') params.set('category', currentCategory);

  try {
    const res = await fetch(`/api/projects?${params}`);
    const data = await res.json();
    if (data.projects.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <i class="fas fa-search"></i>
          <h3>Proje bulunamadı</h3>
          <p>Farklı bir arama veya kategori deneyin.</p>
        </div>`;
    } else {
      container.innerHTML = data.projects.map(renderProjectCard).join('');
    }
  } catch {
    container.innerHTML = '<div class="empty-state">Projeler yüklenirken hata oluştu.</div>';
  }
}

// Project card renderer
function renderProjectCard(project) {
  const imageHtml = project.image
    ? `<img src="${project.image}" alt="${escapeHtml(project.title)}">`
    : `<i class="fas fa-code"></i>`;

  const avatarHtml = project.user_avatar
    ? `<img src="${project.user_avatar}" alt="avatar">`
    : project.username.charAt(0).toUpperCase();

  return `
    <div class="project-card" onclick="${project.link ? `window.open('${escapeHtml(project.link)}', '_blank')` : ''}">
      <div class="project-card-image">${imageHtml}</div>
      <div class="project-card-body">
        <h3>${escapeHtml(project.title)}</h3>
        <p>${escapeHtml(project.description || 'Açıklama yok')}</p>
        <div class="project-card-meta">
          <div class="project-card-author" onclick="event.stopPropagation(); navigate('user', ${project.user_id})">
            <div class="author-avatar">${avatarHtml}</div>
            <span>${escapeHtml(project.username)}</span>
          </div>
          <span class="project-card-category">${escapeHtml(project.category)}</span>
        </div>
      </div>
    </div>
  `;
}

// LOGIN PAGE
function renderLogin() {
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div class="auth-page">
      <div class="auth-card">
        <div class="auth-icon"><i class="fas fa-sign-in-alt"></i></div>
        <h1>Giriş Yap</h1>
        <p class="auth-subtitle">Hesabınıza giriş yapın</p>
        <form onsubmit="handleLogin(event)">
          <div class="form-group">
            <label>E-posta</label>
            <div class="input-icon">
              <i class="fas fa-envelope"></i>
              <input type="email" id="loginEmail" placeholder="ornek@mail.com" required>
            </div>
          </div>
          <div class="form-group">
            <label>Şifre</label>
            <div class="input-icon">
              <i class="fas fa-lock"></i>
              <input type="password" id="loginPassword" placeholder="••••••••" required>
            </div>
          </div>
          <button type="submit" class="btn btn-primary btn-lg" style="width:100%" id="loginBtn">
            Giriş Yap
          </button>
        </form>
        <div class="auth-footer">
          Hesabınız yok mu? <a href="#" onclick="navigate('register')">Kayıt Olun</a>
        </div>
      </div>
    </div>
  `;
}

async function handleLogin(e) {
  e.preventDefault();
  const btn = document.getElementById('loginBtn');
  btn.innerHTML = '<span class="spinner"></span> Giriş yapılıyor...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value
      })
    });
    const data = await res.json();
    if (res.ok) {
      currentUser = data.user;
      updateNavbar(true);
      showToast('Başarıyla giriş yapıldı!', 'success');
      navigate('home');
    } else {
      showToast(data.error || 'Giriş başarısız', 'error');
      btn.innerHTML = 'Giriş Yap';
      btn.disabled = false;
    }
  } catch {
    showToast('Bağlantı hatası', 'error');
    btn.innerHTML = 'Giriş Yap';
    btn.disabled = false;
  }
}

// REGISTER PAGE
function renderRegister() {
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div class="auth-page">
      <div class="auth-card">
        <div class="auth-icon"><i class="fas fa-user-plus"></i></div>
        <h1>Kayıt Ol</h1>
        <p class="auth-subtitle">Yeni hesap oluşturun</p>
        <form onsubmit="handleRegister(event)">
          <div class="form-group">
            <label>Ad Soyad</label>
            <div class="input-icon">
              <i class="fas fa-user"></i>
              <input type="text" id="regFullname" placeholder="Ad Soyad">
            </div>
          </div>
          <div class="form-group">
            <label>Kullanıcı Adı</label>
            <div class="input-icon">
              <i class="fas fa-at"></i>
              <input type="text" id="regUsername" placeholder="kullaniciadi" required>
            </div>
          </div>
          <div class="form-group">
            <label>E-posta</label>
            <div class="input-icon">
              <i class="fas fa-envelope"></i>
              <input type="email" id="regEmail" placeholder="ornek@mail.com" required>
            </div>
          </div>
          <div class="form-group">
            <label>Şifre</label>
            <div class="input-icon">
              <i class="fas fa-lock"></i>
              <input type="password" id="regPassword" placeholder="En az 6 karakter" minlength="6" required>
            </div>
          </div>
          <button type="submit" class="btn btn-primary btn-lg" style="width:100%" id="registerBtn">
            Kayıt Ol
          </button>
        </form>
        <div class="auth-footer">
          Zaten hesabınız var mı? <a href="#" onclick="navigate('login')">Giriş Yapın</a>
        </div>
      </div>
    </div>
  `;
}

async function handleRegister(e) {
  e.preventDefault();
  const btn = document.getElementById('registerBtn');
  btn.innerHTML = '<span class="spinner"></span> Kayıt olunuyor...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fullname: document.getElementById('regFullname').value,
        username: document.getElementById('regUsername').value,
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value
      })
    });
    const data = await res.json();
    if (res.ok) {
      currentUser = data.user;
      updateNavbar(true);
      showToast('Hesabınız oluşturuldu!', 'success');
      navigate('home');
    } else {
      showToast(data.error || 'Kayıt başarısız', 'error');
      btn.innerHTML = 'Kayıt Ol';
      btn.disabled = false;
    }
  } catch {
    showToast('Bağlantı hatası', 'error');
    btn.innerHTML = 'Kayıt Ol';
    btn.disabled = false;
  }
}

// PROFILE PAGE
function renderProfile() {
  if (!currentUser) {
    navigate('login');
    return;
  }
  const main = document.getElementById('mainContent');
  const avatarHtml = currentUser.avatar
    ? `<img src="${currentUser.avatar}" alt="avatar">`
    : `<i class="fas fa-user"></i>`;

  main.innerHTML = `
    <div class="profile-page">
      <div class="profile-header">
        <div class="profile-avatar" id="profileAvatarMain">
          ${avatarHtml}
          <label class="profile-avatar-upload" for="avatarUpload">
            <i class="fas fa-camera"></i> Değiştir
          </label>
          <input type="file" id="avatarUpload" accept="image/*" onchange="uploadAvatar(event)" style="display:none">
        </div>
        <h2>${escapeHtml(currentUser.fullname || currentUser.username)}</h2>
        <p class="profile-username">@${escapeHtml(currentUser.username)}</p>
        ${currentUser.bio ? `<p class="profile-bio">${escapeHtml(currentUser.bio)}</p>` : '<p class="profile-bio" style="color: var(--text-muted);">Henüz bir biyografi eklenmemiş</p>'}
        <div class="profile-stats" id="profileStats">
          <div class="profile-stat">
            <div class="stat-number" id="projectCount">-</div>
            <div class="stat-label">Proje</div>
          </div>
          <div class="profile-stat">
            <div class="stat-number">${new Date(currentUser.created_at).toLocaleDateString('tr-TR', { month: 'short', year: 'numeric' })}</div>
            <div class="stat-label">Katılım</div>
          </div>
        </div>
      </div>
      <div class="section-header">
        <h2>Projelerim</h2>
        <button class="btn btn-primary btn-sm" onclick="navigate('new-project')"><i class="fas fa-plus"></i> Yeni Proje</button>
      </div>
      <div class="project-grid" id="profileProjects">
        <div class="empty-state"><div class="spinner" style="border-color: var(--primary); border-top-color: transparent; width: 32px; height: 32px;"></div></div>
      </div>
    </div>
  `;
  loadProfileProjects();
}

async function loadProfileProjects() {
  try {
    const res = await fetch(`/api/projects?user_id=${currentUser.id}`);
    const data = await res.json();
    const container = document.getElementById('profileProjects');
    const countEl = document.getElementById('projectCount');
    if (!container) return;
    if (countEl) countEl.textContent = data.projects.length;
    if (data.projects.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <i class="fas fa-folder-open"></i>
          <h3>Henüz projeniz yok</h3>
          <p>İlk projenizi paylaşın!</p>
          <button class="btn btn-primary" onclick="navigate('new-project')"><i class="fas fa-plus"></i> Proje Ekle</button>
        </div>`;
    } else {
      container.innerHTML = data.projects.map(p => renderProjectCard(p) + `
        <div style="position:absolute;top:8px;right:8px;">
        </div>
      `).join('');
    }
  } catch {
    document.getElementById('profileProjects').innerHTML = '<div class="empty-state">Projeler yüklenirken hata oluştu.</div>';
  }
}

async function uploadAvatar(e) {
  const file = e.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('avatar', file);
  try {
    const res = await fetch('/api/profile/avatar', { method: 'POST', body: formData });
    const data = await res.json();
    if (res.ok) {
      currentUser.avatar = data.avatar;
      updateNavbar(true);
      showToast('Profil fotoğrafı güncellendi!', 'success');
      navigate('profile');
    } else {
      showToast(data.error || 'Yükleme başarısız', 'error');
    }
  } catch {
    showToast('Yükleme hatası', 'error');
  }
}

// SETTINGS PAGE
function renderSettings() {
  if (!currentUser) {
    navigate('login');
    return;
  }
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div class="settings-page">
      <h1 style="font-size: 1.75rem; font-weight: 700; margin-bottom: 24px;"><i class="fas fa-cog"></i> Ayarlar</h1>
      <div class="settings-card">
        <h2>Profil Bilgileri</h2>
        <form onsubmit="handleUpdateProfile(event)">
          <div class="form-group">
            <label>Ad Soyad</label>
            <input type="text" id="settingsFullname" value="${escapeHtml(currentUser.fullname || '')}" placeholder="Ad Soyad">
          </div>
          <div class="form-group">
            <label>Biyografi</label>
            <textarea id="settingsBio" placeholder="Kendinizden bahsedin...">${escapeHtml(currentUser.bio || '')}</textarea>
          </div>
          <button type="submit" class="btn btn-primary" id="saveProfileBtn">
            <i class="fas fa-save"></i> Kaydet
          </button>
        </form>
      </div>
      <div class="settings-card">
        <h2>Hesap Bilgileri</h2>
        <div class="form-group">
          <label>Kullanıcı Adı</label>
          <input type="text" value="${escapeHtml(currentUser.username)}" disabled style="background: var(--bg);">
        </div>
        <div class="form-group">
          <label>E-posta</label>
          <input type="email" value="${escapeHtml(currentUser.email)}" disabled style="background: var(--bg);">
        </div>
      </div>
    </div>
  `;
}

async function handleUpdateProfile(e) {
  e.preventDefault();
  const btn = document.getElementById('saveProfileBtn');
  btn.innerHTML = '<span class="spinner"></span> Kaydediliyor...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fullname: document.getElementById('settingsFullname').value,
        bio: document.getElementById('settingsBio').value
      })
    });
    const data = await res.json();
    if (res.ok) {
      currentUser = data.user;
      updateNavbar(true);
      showToast('Profil güncellendi!', 'success');
    } else {
      showToast(data.error || 'Güncelleme başarısız', 'error');
    }
  } catch {
    showToast('Bağlantı hatası', 'error');
  }
  btn.innerHTML = '<i class="fas fa-save"></i> Kaydet';
  btn.disabled = false;
}

// NEW PROJECT PAGE
function renderNewProject() {
  if (!currentUser) {
    navigate('login');
    showToast('Proje eklemek için giriş yapın', 'error');
    return;
  }
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div class="new-project-page">
      <div class="form-card">
        <h1><i class="fas fa-plus-circle"></i> Yeni Proje</h1>
        <form onsubmit="handleNewProject(event)">
          <div class="form-group">
            <label>Proje Başlığı *</label>
            <input type="text" id="projectTitle" placeholder="Projenizin adı" required>
          </div>
          <div class="form-group">
            <label>Açıklama</label>
            <textarea id="projectDesc" placeholder="Projeniz hakkında kısa bir açıklama yazın..."></textarea>
          </div>
          <div class="form-group">
            <label>Kategori</label>
            <select id="projectCategory">
              ${categories.filter(c => c !== 'Tümü').map(c => `<option value="${c}">${c}</option>`).join('')}
            </select>
          </div>
          <div class="form-group">
            <label>Proje Linki</label>
            <div class="input-icon">
              <i class="fas fa-link"></i>
              <input type="url" id="projectLink" placeholder="https://github.com/...">
            </div>
          </div>
          <div class="form-group">
            <label>Görsel</label>
            <div class="file-upload" onclick="document.getElementById('projectImage').click()">
              <i class="fas fa-cloud-upload-alt"></i>
              <p>Görsel yüklemek için tıklayın</p>
              <input type="file" id="projectImage" accept="image/*" onchange="previewImage(event)">
            </div>
            <div class="file-preview" id="imagePreview"></div>
          </div>
          <button type="submit" class="btn btn-primary btn-lg" style="width:100%" id="newProjectBtn">
            <i class="fas fa-share"></i> Projeyi Paylaş
          </button>
        </form>
      </div>
    </div>
  `;
}

function previewImage(e) {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (ev) => {
      document.getElementById('imagePreview').innerHTML = `<img src="${ev.target.result}" alt="preview">`;
    };
    reader.readAsDataURL(file);
  }
}

async function handleNewProject(e) {
  e.preventDefault();
  const btn = document.getElementById('newProjectBtn');
  btn.innerHTML = '<span class="spinner"></span> Paylaşılıyor...';
  btn.disabled = true;

  const formData = new FormData();
  formData.append('title', document.getElementById('projectTitle').value);
  formData.append('description', document.getElementById('projectDesc').value);
  formData.append('category', document.getElementById('projectCategory').value);
  formData.append('link', document.getElementById('projectLink').value);
  const imageFile = document.getElementById('projectImage').files[0];
  if (imageFile) formData.append('image', imageFile);

  try {
    const res = await fetch('/api/projects', { method: 'POST', body: formData });
    const data = await res.json();
    if (res.ok) {
      showToast('Proje başarıyla paylaşıldı!', 'success');
      navigate('home');
    } else {
      showToast(data.error || 'Proje eklenemedi', 'error');
      btn.innerHTML = '<i class="fas fa-share"></i> Projeyi Paylaş';
      btn.disabled = false;
    }
  } catch {
    showToast('Bağlantı hatası', 'error');
    btn.innerHTML = '<i class="fas fa-share"></i> Projeyi Paylaş';
    btn.disabled = false;
  }
}

// MY PROJECTS PAGE
function renderMyProjects() {
  if (!currentUser) {
    navigate('login');
    return;
  }
  const main = document.getElementById('mainContent');
  main.innerHTML = `
    <div class="section-header">
      <h2><i class="fas fa-folder"></i> Projelerim</h2>
      <button class="btn btn-primary btn-sm" onclick="navigate('new-project')"><i class="fas fa-plus"></i> Yeni Proje</button>
    </div>
    <div class="project-grid" id="myProjectsList">
      <div class="empty-state"><div class="spinner" style="border-color: var(--primary); border-top-color: transparent; width: 32px; height: 32px;"></div></div>
    </div>
  `;
  loadMyProjects();
}

async function loadMyProjects() {
  try {
    const res = await fetch(`/api/projects?user_id=${currentUser.id}`);
    const data = await res.json();
    const container = document.getElementById('myProjectsList');
    if (!container) return;
    if (data.projects.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <i class="fas fa-folder-open"></i>
          <h3>Henüz projeniz yok</h3>
          <p>İlk projenizi paylaşın!</p>
          <button class="btn btn-primary" onclick="navigate('new-project')"><i class="fas fa-plus"></i> Proje Ekle</button>
        </div>`;
    } else {
      container.innerHTML = data.projects.map(p => {
        const card = renderProjectCard(p);
        return card.replace('</div>\n    </div>\n  ', `
          <div style="padding: 0 20px 16px; text-align: right;">
            <button class="btn btn-danger btn-sm" onclick="event.stopPropagation(); deleteProject(${p.id})">
              <i class="fas fa-trash"></i> Sil
            </button>
          </div>
        </div>\n    </div>\n  `);
      }).join('');
    }
  } catch {
    document.getElementById('myProjectsList').innerHTML = '<div class="empty-state">Projeler yüklenirken hata oluştu.</div>';
  }
}

async function deleteProject(id) {
  if (!confirm('Bu projeyi silmek istediğinizden emin misiniz?')) return;
  try {
    const res = await fetch(`/api/projects/${id}`, { method: 'DELETE' });
    if (res.ok) {
      showToast('Proje silindi', 'success');
      renderMyProjects();
    } else {
      showToast('Silme başarısız', 'error');
    }
  } catch {
    showToast('Bağlantı hatası', 'error');
  }
}

// USER PROFILE PAGE (public)
async function renderUserProfile(userId) {
  const main = document.getElementById('mainContent');
  main.innerHTML = '<div class="empty-state"><div class="spinner" style="border-color: var(--primary); border-top-color: transparent; width: 32px; height: 32px;"></div></div>';

  try {
    const res = await fetch(`/api/users/${userId}`);
    const data = await res.json();
    if (!res.ok) {
      main.innerHTML = '<div class="empty-state"><h3>Kullanıcı bulunamadı</h3></div>';
      return;
    }

    const user = data.user;
    const projects = data.projects;
    const avatarHtml = user.avatar
      ? `<img src="${user.avatar}" alt="avatar">`
      : `<i class="fas fa-user"></i>`;

    main.innerHTML = `
      <div class="user-profile-page">
        <div class="profile-header">
          <div class="profile-avatar">${avatarHtml}</div>
          <h2>${escapeHtml(user.fullname || user.username)}</h2>
          <p class="profile-username">@${escapeHtml(user.username)}</p>
          ${user.bio ? `<p class="profile-bio">${escapeHtml(user.bio)}</p>` : ''}
          <div class="profile-stats">
            <div class="profile-stat">
              <div class="stat-number">${projects.length}</div>
              <div class="stat-label">Proje</div>
            </div>
            <div class="profile-stat">
              <div class="stat-number">${new Date(user.created_at).toLocaleDateString('tr-TR', { month: 'short', year: 'numeric' })}</div>
              <div class="stat-label">Katılım</div>
            </div>
          </div>
        </div>
        <div class="section-header">
          <h2>${escapeHtml(user.username)} Projeleri</h2>
        </div>
        <div class="project-grid">
          ${projects.length > 0
            ? projects.map(p => renderProjectCard({ ...p, username: user.username, user_avatar: user.avatar })).join('')
            : '<div class="empty-state" style="grid-column: 1 / -1;"><i class="fas fa-folder-open"></i><h3>Henüz proje yok</h3></div>'
          }
        </div>
      </div>
    `;
  } catch {
    main.innerHTML = '<div class="empty-state"><h3>Bir hata oluştu</h3></div>';
  }
}

// LOGOUT
async function logout() {
  try {
    await fetch('/api/logout', { method: 'POST' });
  } catch { /* ignore */ }
  currentUser = null;
  updateNavbar(false);
  showToast('Çıkış yapıldı', 'success');
  navigate('home');
}

// Utility
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
