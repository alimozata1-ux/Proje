const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT || 3000);
const DEEPSEEK_API_URL = process.env.DEEPSEEK_API_URL || 'https://api.deepseek.com/chat/completions';
const MODEL = process.env.DEEPSEEK_MODEL || 'deepseek-chat';

const publicDir = path.join(__dirname, 'public');

const baseSystemPrompt =
  'You are C.O.M.R.A.D.E 7.1, a helpful assistant in a retro command-center UI. Keep answers practical and concise. Avoid harmful, extremist, or hateful propaganda. Maintain a playful retro tone when appropriate.';

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
};

function sendJson(res, status, data) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(data));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
      if (body.length > 1e6) {
        reject(new Error('Payload too large'));
      }
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

async function handleChat(req, res) {
  const apiKey = process.env.DEEPSEEK_API_KEY;
  if (!apiKey) {
    return sendJson(res, 500, { error: 'DEEPSEEK_API_KEY tanımlı değil.' });
  }

  try {
    const rawBody = await readBody(req);
    const { messages = [], mode = 'satire' } = rawBody ? JSON.parse(rawBody) : {};

    const stylePrompt =
      mode === 'serious'
        ? 'Respond in neutral Turkish with professional clarity.'
        : 'Respond in Turkish with a light retro-satire style and "yoldaş" flavor, without political incitement.';

    const payload = {
      model: MODEL,
      messages: [{ role: 'system', content: `${baseSystemPrompt} ${stylePrompt}` }, ...messages],
      temperature: 0.7,
    };

    const deepseekResponse = await fetch(DEEPSEEK_API_URL, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await deepseekResponse.json();
    if (!deepseekResponse.ok) {
      return sendJson(res, 500, { error: data?.error?.message || 'DeepSeek API hatası' });
    }

    const reply = data?.choices?.[0]?.message?.content || 'Yanıt üretilemedi.';
    return sendJson(res, 200, { reply });
  } catch (error) {
    return sendJson(res, 500, { error: error.message || 'Sunucu hatası' });
  }
}

function serveStatic(req, res) {
  const reqPath = req.url === '/' ? '/index.html' : req.url;
  const normalizedPath = path.normalize(reqPath).replace(/^([.][.][/\\])+/, '');
  const filePath = path.join(publicDir, normalizedPath);

  if (!filePath.startsWith(publicDir)) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      return res.end('Not Found');
    }

    const ext = path.extname(filePath).toLowerCase();
    const type = mimeTypes[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': type });
    res.end(content);
  });
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'POST' && req.url === '/api/chat') {
    return handleChat(req, res);
  }

  if (req.method === 'GET') {
    return serveStatic(req, res);
  }

  res.writeHead(405, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('Method Not Allowed');
});

server.listen(PORT, () => {
  console.log(`C.O.M.R.A.D.E 7.1 running on http://localhost:${PORT}`);
});
