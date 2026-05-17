const express = require('express');
const session = require('express-session');
const crypto = require('crypto');
const Database = require('better-sqlite3');
const bcrypt = require('bcryptjs');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir);

const db = new Database(path.join(__dirname, 'data.db'));
db.pragma('journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    fullname TEXT DEFAULT '',
    bio TEXT DEFAULT '',
    avatar TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    category TEXT DEFAULT 'Genel',
    image TEXT DEFAULT '',
    link TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
  );
`);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.use('/uploads', express.static(uploadsDir));

app.use(session({
  secret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString('hex'),
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 24 * 60 * 60 * 1000 }
}));

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadsDir),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    cb(null, `${Date.now()}-${Math.random().toString(36).slice(2)}${ext}`);
  }
});
const upload = multer({ storage, limits: { fileSize: 5 * 1024 * 1024 } });

function requireAuth(req, res, next) {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Giriş yapmanız gerekiyor' });
  }
  next();
}

// Auth routes
app.post('/api/register', (req, res) => {
  const { username, email, password, fullname } = req.body;
  if (!username || !email || !password) {
    return res.status(400).json({ error: 'Tüm alanları doldurun' });
  }
  const existing = db.prepare('SELECT id FROM users WHERE username = ? OR email = ?').get(username, email);
  if (existing) {
    return res.status(400).json({ error: 'Bu kullanıcı adı veya e-posta zaten kayıtlı' });
  }
  const hash = bcrypt.hashSync(password, 10);
  const result = db.prepare('INSERT INTO users (username, email, password, fullname) VALUES (?, ?, ?, ?)').run(username, email, hash, fullname || '');
  req.session.userId = result.lastInsertRowid;
  res.json({ success: true, user: { id: result.lastInsertRowid, username, email, fullname: fullname || '' } });
});

app.post('/api/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ error: 'E-posta ve şifre gerekli' });
  }
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
  if (!user || !bcrypt.compareSync(password, user.password)) {
    return res.status(401).json({ error: 'Geçersiz e-posta veya şifre' });
  }
  req.session.userId = user.id;
  res.json({ success: true, user: { id: user.id, username: user.username, email: user.email, fullname: user.fullname, bio: user.bio, avatar: user.avatar } });
});

app.post('/api/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});

app.get('/api/me', (req, res) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Giriş yapılmamış' });
  }
  const user = db.prepare('SELECT id, username, email, fullname, bio, avatar, created_at FROM users WHERE id = ?').get(req.session.userId);
  if (!user) return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
  res.json({ user });
});

// Profile routes
app.put('/api/profile', requireAuth, (req, res) => {
  const { fullname, bio } = req.body;
  db.prepare('UPDATE users SET fullname = ?, bio = ? WHERE id = ?').run(fullname || '', bio || '', req.session.userId);
  const user = db.prepare('SELECT id, username, email, fullname, bio, avatar, created_at FROM users WHERE id = ?').get(req.session.userId);
  res.json({ success: true, user });
});

app.post('/api/profile/avatar', requireAuth, upload.single('avatar'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'Dosya yüklenmedi' });
  const avatarPath = `/uploads/${req.file.filename}`;
  db.prepare('UPDATE users SET avatar = ? WHERE id = ?').run(avatarPath, req.session.userId);
  res.json({ success: true, avatar: avatarPath });
});

// Project routes
app.get('/api/projects', (req, res) => {
  const { search, category, user_id } = req.query;
  let query = `SELECT p.*, u.username, u.avatar as user_avatar FROM projects p JOIN users u ON p.user_id = u.id`;
  const conditions = [];
  const params = [];
  if (search) {
    conditions.push('(p.title LIKE ? OR p.description LIKE ?)');
    params.push(`%${search}%`, `%${search}%`);
  }
  if (category && category !== 'Tümü') {
    conditions.push('p.category = ?');
    params.push(category);
  }
  if (user_id) {
    conditions.push('p.user_id = ?');
    params.push(user_id);
  }
  if (conditions.length) query += ' WHERE ' + conditions.join(' AND ');
  query += ' ORDER BY p.created_at DESC';
  const projects = db.prepare(query).all(...params);
  res.json({ projects });
});

app.post('/api/projects', requireAuth, upload.single('image'), (req, res) => {
  const { title, description, category, link } = req.body;
  if (!title) return res.status(400).json({ error: 'Proje başlığı gerekli' });
  const imagePath = req.file ? `/uploads/${req.file.filename}` : '';
  const result = db.prepare('INSERT INTO projects (user_id, title, description, category, image, link) VALUES (?, ?, ?, ?, ?, ?)').run(req.session.userId, title, description || '', category || 'Genel', imagePath, link || '');
  const project = db.prepare('SELECT p.*, u.username, u.avatar as user_avatar FROM projects p JOIN users u ON p.user_id = u.id WHERE p.id = ?').get(result.lastInsertRowid);
  res.json({ success: true, project });
});

app.delete('/api/projects/:id', requireAuth, (req, res) => {
  const project = db.prepare('SELECT * FROM projects WHERE id = ? AND user_id = ?').get(req.params.id, req.session.userId);
  if (!project) return res.status(404).json({ error: 'Proje bulunamadı' });
  db.prepare('DELETE FROM projects WHERE id = ?').run(req.params.id);
  res.json({ success: true });
});

// User profile (public)
app.get('/api/users/:id', (req, res) => {
  const user = db.prepare('SELECT id, username, fullname, bio, avatar, created_at FROM users WHERE id = ?').get(req.params.id);
  if (!user) return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
  const projects = db.prepare('SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC').all(req.params.id);
  res.json({ user, projects });
});

// SPA fallback
app.get('{*path}', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
