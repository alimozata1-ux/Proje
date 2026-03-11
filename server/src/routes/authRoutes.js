const express = require('express');
const bcrypt = require('bcrypt');

const User = require('../models/User');
const { inviteGuard } = require('../middleware/inviteGuard');
const { signToken } = require('../utils/token');

const router = express.Router();

/**
 * KAYIT
 * body: { username, password, inviteCode }
 */
router.post('/register', inviteGuard, async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ message: 'Kullanici adi ve sifre zorunludur.' });
    }

    const existingUser = await User.findOne({ username }).lean();
    if (existingUser) {
      return res.status(409).json({ message: 'Bu kullanici adi zaten kullaniliyor.' });
    }

    const passwordHash = await bcrypt.hash(password, 12);

    const user = await User.create({
      username,
      passwordHash
    });

    const token = signToken(user);

    return res.status(201).json({
      message: 'Kayit basarili',
      token,
      user: { id: user._id, username: user.username }
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: 'Sunucu hatasi' });
  }
});

/**
 * GIRIS
 * body: { username, password }
 */
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ message: 'Kullanici adi ve sifre zorunludur.' });
    }

    const user = await User.findOne({ username });
    if (!user) {
      return res.status(401).json({ message: 'Kullanici adi veya sifre hatali.' });
    }

    const ok = await bcrypt.compare(password, user.passwordHash);
    if (!ok) {
      return res.status(401).json({ message: 'Kullanici adi veya sifre hatali.' });
    }

    const token = signToken(user);

    return res.status(200).json({
      message: 'Giris basarili',
      token,
      user: { id: user._id, username: user.username }
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: 'Sunucu hatasi' });
  }
});

module.exports = router;
