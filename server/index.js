/**
 * Ana sunucu dosyasi
 * - Express REST API (kayit/giris/sohbetler/upload)
 * - Socket.io ile gercek zamanli grup sohbet
 * - MongoDB ile kalici veri saklama
 */
require('dotenv').config();

const path = require('path');
const http = require('http');
const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const { Server } = require('socket.io');

const { connectDatabase } = require('./src/config/db');
const authRoutes = require('./src/routes/authRoutes');
const chatRoutes = require('./src/routes/chatRoutes');
const User = require('./src/models/User');
const Message = require('./src/models/Message');
const Conversation = require('./src/models/Conversation');

const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'CHANGE_ME_FOR_PRODUCTION';

const app = express();
const server = http.createServer(app);

app.set('trust proxy', 1);
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.join(__dirname, '..', 'client')));

app.use('/api/auth', authRoutes);
app.use('/api/chat', chatRoutes);

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'client', 'index.html'));
});

const io = new Server(server, {
  cors: { origin: '*' }
});

io.use(async (socket, next) => {
  try {
    const token = socket.handshake.auth?.token;
    if (!token) return next(new Error('Token eksik'));

    const payload = jwt.verify(token, JWT_SECRET);
    const user = await User.findById(payload.userId).lean();
    if (!user) return next(new Error('Kullanici bulunamadi'));

    socket.user = { id: user._id.toString(), username: user.username };
    next();
  } catch (err) {
    next(new Error('Socket kimlik dogrulama basarisiz'));
  }
});


function emitPresence(ioServer, conversationId) {
  if (!conversationId) return;
  const roomName = `conversation:${conversationId}`;
  const room = ioServer.sockets.adapter.rooms.get(roomName);
  const count = room ? room.size : 0;

  ioServer.to(roomName).emit('chat:presence', {
    conversationId,
    onlineCount: count
  });
}

io.on('connection', (socket) => {
  socket.on('chat:join', async ({ conversationId }) => {
    if (!conversationId) return;

    const roomName = `conversation:${conversationId}`;
    for (const room of socket.rooms) {
      if (room.startsWith('conversation:')) {
        const previousConversationId = room.replace('conversation:', '');
        socket.leave(room);
        emitPresence(io, previousConversationId);
      }
    }
    socket.join(roomName);
    emitPresence(io, conversationId);

    const history = await Message.find({ conversationId }).sort({ createdAt: -1 }).limit(100).lean();
    socket.emit('chat:history', history.reverse());

    socket.to(roomName).emit('chat:user-joined', {
      username: socket.user.username,
      message: `${socket.user.username} sohbete katildi.`
    });
  });

  // Yaziyor gostergesi
  socket.on('chat:typing', ({ conversationId, isTyping }) => {
    if (!conversationId) return;
    socket.to(`conversation:${conversationId}`).emit('chat:typing', {
      conversationId,
      username: socket.user.username,
      isTyping: Boolean(isTyping)
    });
  });

  socket.on('chat:send', async (payload) => {
    const conversationId = payload?.conversationId;
    const text = typeof payload?.text === 'string' ? payload.text.trim() : '';
    const fileUrl = payload?.fileUrl || null;
    const fileName = payload?.fileName || null;
    const fileType = payload?.fileType || null;

    if (!conversationId) return;
    if (!text && !fileUrl) return;

    const messageDoc = await Message.create({
      conversationId,
      userId: socket.user.id,
      username: socket.user.username,
      text,
      fileUrl,
      fileName,
      fileType
    });

    io.to(`conversation:${conversationId}`).emit('chat:new-message', {
      _id: messageDoc._id,
      conversationId: messageDoc.conversationId,
      userId: messageDoc.userId,
      username: messageDoc.username,
      text: messageDoc.text,
      fileUrl: messageDoc.fileUrl,
      fileName: messageDoc.fileName,
      fileType: messageDoc.fileType,
      createdAt: messageDoc.createdAt
    });
  });


  // Kendi mesajini duzenleme
  socket.on('chat:edit', async ({ conversationId, messageId, text }) => {
    if (!conversationId || !messageId) return;

    const nextText = typeof text === 'string' ? text.trim() : '';
    if (!nextText) {
      socket.emit('chat:error', { message: 'Mesaj bos olamaz.' });
      return;
    }

    const updated = await Message.findOneAndUpdate(
      {
        _id: messageId,
        conversationId,
        userId: socket.user.id
      },
      {
        $set: { text: nextText }
      },
      { new: true }
    ).lean();

    if (!updated) {
      socket.emit('chat:error', { message: 'Mesaj duzenlenemedi veya yetkiniz yok.' });
      return;
    }

    io.to(`conversation:${conversationId}`).emit('chat:edited', {
      conversationId,
      messageId,
      text: updated.text,
      updatedAt: updated.updatedAt
    });
  });

  // Kendi mesajini silme
  socket.on('chat:delete', async ({ conversationId, messageId }) => {
    if (!conversationId || !messageId) return;

    const deleted = await Message.findOneAndDelete({
      _id: messageId,
      conversationId,
      userId: socket.user.id
    }).lean();

    if (!deleted) {
      socket.emit('chat:error', { message: 'Mesaj silinemedi veya yetkiniz yok.' });
      return;
    }

    io.to(`conversation:${conversationId}`).emit('chat:deleted', {
      conversationId,
      messageId
    });
  });

  socket.on('disconnect', () => {
    for (const room of socket.rooms) {
      if (room.startsWith('conversation:')) {
        const conversationId = room.replace('conversation:', '');
        socket.to(room).emit('chat:user-left', {
          username: socket.user.username,
          message: `${socket.user.username} sohbetten ayrildi.`
        });
        emitPresence(io, conversationId);
      }
    }
  });
});

(async () => {
  await connectDatabase();

  await Conversation.findOneAndUpdate(
    { name: 'Genel Sohbet' },
    { name: 'Genel Sohbet' },
    { upsert: true, new: true, setDefaultsOnInsert: true }
  );

  server.listen(PORT, () => {
    console.log(`Sunucu ${PORT} portunda calisiyor`);
  });
})();
