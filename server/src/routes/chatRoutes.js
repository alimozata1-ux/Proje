const express = require('express');
const path = require('path');
const fs = require('fs');
const multer = require('multer');

const Message = require('../models/Message');
const Conversation = require('../models/Conversation');
const { authMiddleware } = require('../middleware/authMiddleware');

const router = express.Router();

const uploadDir = path.join(__dirname, '..', '..', 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, uploadDir),
  filename: (_req, file, cb) => {
    const ext = path.extname(file.originalname);
    const safeBase = path.basename(file.originalname, ext).replace(/[^a-zA-Z0-9-_]/g, '_');
    cb(null, `${Date.now()}-${safeBase}${ext}`);
  }
});

const upload = multer({
  storage,
  limits: { fileSize: 8 * 1024 * 1024 }
});

router.get('/conversations', authMiddleware, async (_req, res) => {
  try {
    const conversations = await Conversation.find({}).sort({ createdAt: 1 }).lean();
    return res.status(200).json(conversations);
  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: 'Sohbetler alinamadi' });
  }
});

router.post('/conversations', authMiddleware, async (req, res) => {
  try {
    const name = (req.body.name || '').trim();
    if (!name) return res.status(400).json({ message: 'Sohbet adi zorunludur.' });

    const created = await Conversation.create({ name });
    return res.status(201).json(created);
  } catch (err) {
    if (err.code === 11000) {
      return res.status(409).json({ message: 'Bu sohbet zaten var.' });
    }
    console.error(err);
    return res.status(500).json({ message: 'Sohbet olusturulamadi' });
  }
});

router.get('/messages/:conversationId', authMiddleware, async (req, res) => {
  try {
    const { conversationId } = req.params;
    const messages = await Message.find({ conversationId }).sort({ createdAt: -1 }).limit(100).lean();
    return res.status(200).json(messages.reverse());
  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: 'Mesajlar alinamadi' });
  }
});

router.post('/upload', authMiddleware, upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: 'Dosya bulunamadi' });
  }

  return res.status(201).json({
    fileUrl: `/uploads/${req.file.filename}`,
    fileName: req.file.originalname,
    fileType: req.file.mimetype
  });
});

module.exports = router;
