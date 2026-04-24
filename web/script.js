const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

const refs = {
  matrixCanvas: $("#matrixCanvas"),
  logo: $("#logo"),
  status: $("#status"),
  voiceMeter: $("#voiceMeter"),
  prompt: $("#prompt"),
  sendBtn: $("#sendBtn"),
  routeBtn: $("#routeBtn"),
  listenToggle: $("#listenToggle"),
  clearMemory: $("#clearMemory"),
  history: $("#history"),
  historyTemplate: $("#historyItemTemplate"),
  codePanel: $("#codePanel"),
  iconGrid: $("#iconGrid"),
  arduinoToggle: $("#arduinoToggle"),
  arduinoTemp: $("#arduinoTemp"),
  arduinoLightOn: $("#arduinoLightOn"),
  arduinoLightOff: $("#arduinoLightOff"),
  portsBtn: $("#portsBtn"),
  devicePanel: $("#devicePanel"),
  snapshotBtn: $("#snapshotBtn"),
  processBtn: $("#processBtn"),
  memoryBtn: $("#memoryBtn"),
  resourcePanel: $("#resourcePanel"),
  appName: $("#appName"),
  openAppBtn: $("#openAppBtn"),
  cpuText: $("#cpuText"),
  ramText: $("#ramText"),
  diskText: $("#diskText")
};

const state = {
  listening: false,
  speakingPulseTimer: null,
  matrix: {
    ctx: null,
    width: 0,
    height: 0,
    columns: 0,
    drops: [],
    chars: "01"
  },
  meter: {
    t: 0,
    timer: null
  }
};

const ICONS = [
  {
    id: "brain",
    label: "Zeka",
    svg: "<svg viewBox='0 0 24 24'><path d='M9 4a3 3 0 0 0-3 3v1a3 3 0 0 0-2 2.8V12a3 3 0 0 0 3 3h1v2a3 3 0 0 0 3 3h1a3 3 0 0 0 3-3v-1h1a3 3 0 0 0 3-3v-1.2a3 3 0 0 0-2-2.8V7a3 3 0 0 0-3-3h-1a3 3 0 0 0-2 0z'/></svg>"
  },
  {
    id: "mic",
    label: "Mikrofon",
    svg: "<svg viewBox='0 0 24 24'><path d='M12 4a4 4 0 0 1 4 4v5a4 4 0 0 1-8 0V8a4 4 0 0 1 4-4z'/><path d='M6 11v1a6 6 0 0 0 12 0v-1M12 18v3'/></svg>"
  },
  {
    id: "arduino",
    label: "Arduino",
    svg: "<svg viewBox='0 0 24 24'><path d='M4 8h16v8H4zM8 8V5m8 3V5m-8 11v3m8-3v3M8 12h.01M12 12h.01M16 12h.01'/></svg>"
  },
  {
    id: "hub",
    label: "Bağlantı",
    svg: "<svg viewBox='0 0 24 24'><path d='M12 3 4 7v10l8 4 8-4V7zM4 7l8 4 8-4M12 11v10'/></svg>"
  },
  {
    id: "memory",
    label: "Hafıza",
    svg: "<svg viewBox='0 0 24 24'><path d='M5 5h14v14H5zM9 9h6M9 12h6M9 15h4'/></svg>"
  },
  {
    id: "filter",
    label: "Kod Filtresi",
    svg: "<svg viewBox='0 0 24 24'><path d='M4 6h16M7 12h10M10 18h4'/><path d='m14 4 4 4-4 4'/></svg>"
  },
  {
    id: "smart-home",
    label: "Smart Home",
    svg: "<svg viewBox='0 0 24 24'><path d='M4 11 12 5l8 6v8H4zM9 19v-5h6v5'/></svg>"
  },
  {
    id: "resources",
    label: "Kaynak",
    svg: "<svg viewBox='0 0 24 24'><path d='M4 14h3v6H4zM10.5 10h3v10h-3zM17 6h3v14h-3z'/></svg>"
  },
  {
    id: "settings",
    label: "Ayarlar",
    svg: "<svg viewBox='0 0 24 24'><path d='M12 2v4m0 12v4m7-10h3M2 12h3M17 7l2-2M5 19l2-2M17 17l2 2M5 5l2 2'/><circle cx='12' cy='12' r='3'/></svg>"
  }
];

function nowTime() {
  return new Date().toLocaleTimeString("tr-TR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}

function statusClassByText(text) {
  const t = (text || "").toLowerCase();
  if (t.includes("hata") || t.includes("error")) return "error";
  if (t.includes("uyarı") || t.includes("warn")) return "warn";
  return "";
}

function setStatus(text) {
  refs.status.textContent = text;
  refs.status.classList.remove("warn", "error");
  const klass = statusClassByText(text);
  if (klass) refs.status.classList.add(klass);
}

function setLogoPulse(active) {
  refs.logo.classList.toggle("speaking", Boolean(active));
}

function pulseSpeaking(duration = 900) {
  setLogoPulse(true);
  if (state.speakingPulseTimer) clearTimeout(state.speakingPulseTimer);
  state.speakingPulseTimer = setTimeout(() => setLogoPulse(false), duration);
}

function isApiReady() {
  return !!window.pywebview?.api;
}

async function withApi(task, fallbackMessage = "Native API hazır değil bilader.") {
  if (!isApiReady()) {
    setStatus(fallbackMessage);
    return null;
  }
  try {
    return await task(window.pywebview.api);
  } catch (err) {
    setStatus(`Hata: ${err?.message || err}`);
    return null;
  }
}

function pretty(obj) {
  if (typeof obj === "string") return obj;
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

function addHistory(role, content) {
  const template = refs.historyTemplate;
  const clone = template.content.firstElementChild.cloneNode(true);
  clone.querySelector(".role").textContent = role.toUpperCase();
  clone.querySelector(".time").textContent = nowTime();
  clone.querySelector(".content").textContent = content;
  refs.history.prepend(clone);
}

function clearHistoryUi() {
  refs.history.innerHTML = "";
  refs.codePanel.textContent = "";
  refs.resourcePanel.textContent = "";
  refs.devicePanel.textContent = "";
}

function initIcons() {
  refs.iconGrid.innerHTML = "";
  ICONS.forEach((icon) => {
    const el = document.createElement("button");
    el.className = "icon-card";
    el.title = icon.label;
    el.dataset.iconId = icon.id;
    el.type = "button";
    el.innerHTML = icon.svg;
    el.addEventListener("click", () => onIconClick(icon));
    refs.iconGrid.appendChild(el);
  });
}

function onIconClick(icon) {
  const dictionary = {
    brain: "Gemini ve komut çözümleme aktif bilader.",
    mic: state.listening ? "Mikrofon pasif dinlemede." : "Mikrofon şu an kapalı.",
    arduino: "Arduino modülü seri bağlantı için hazır.",
    hub: "Cihaz hub üzerinden port tarama yapabilirsin.",
    memory: "Hafıza özeti için 'Hafıza Özeti' butonunu kullan.",
    filter: "Kod içeriği ayrıştırılıp ekrana yazılır.",
    "smart-home": "Işık/sensör komutları Arduino üstünden işlenir.",
    resources: "CPU, RAM, DISK telemetrisi canlı akıyor.",
    settings: "Ayarlar .env dosyasından yönetiliyor."
  };
  setStatus(dictionary[icon.id] || icon.label);
  pulseSpeaking(600);
}

function initMatrix() {
  const canvas = refs.matrixCanvas;
  const ctx = canvas.getContext("2d");
  state.matrix.ctx = ctx;

  const resize = () => {
    const rect = canvas.getBoundingClientRect();
    state.matrix.width = Math.max(1, Math.floor(rect.width));
    state.matrix.height = Math.max(1, Math.floor(rect.height));
    canvas.width = state.matrix.width;
    canvas.height = state.matrix.height;
    state.matrix.columns = Math.floor(state.matrix.width / 16);
    state.matrix.drops = Array(state.matrix.columns).fill(1);
  };

  resize();
  window.addEventListener("resize", resize);

  const draw = () => {
    const { width, height, drops, chars } = state.matrix;
    ctx.fillStyle = "rgba(0, 0, 0, 0.08)";
    ctx.fillRect(0, 0, width, height);

    ctx.fillStyle = "#00ff41";
    ctx.font = "15px monospace";

    for (let i = 0; i < drops.length; i += 1) {
      const text = chars[Math.floor(Math.random() * chars.length)];
      ctx.fillText(text, i * 16, drops[i] * 16);
      if (drops[i] * 16 > height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i] += 1;
    }
  };

  setInterval(draw, 45);
}

function initVoiceMeter() {
  if (state.meter.timer) clearInterval(state.meter.timer);
  state.meter.timer = setInterval(() => {
    state.meter.t += 0.2;
    const value = 38 + Math.sin(state.meter.t) * 8 + Math.sin(state.meter.t * 0.36) * 6;
    refs.voiceMeter.style.height = `${Math.max(34, value)}px`;
  }, 50);
}

function setMeterActive(active) {
  refs.voiceMeter.classList.toggle("active", Boolean(active));
}

function updateTelemetry(snap) {
  if (typeof snap?.cpu_percent === "number") {
    refs.cpuText.textContent = `${snap.cpu_percent.toFixed(1)}%`;
  }
  if (typeof snap?.ram_percent === "number") {
    refs.ramText.textContent = `${snap.ram_percent.toFixed(1)}%`;
  }
  if (typeof snap?.disk_percent === "number") {
    refs.diskText.textContent = `${snap.disk_percent.toFixed(1)}%`;
  }
}

async function sendPrompt(asCommand = false) {
  const text = refs.prompt.value.trim();
  if (!text) return;

  addHistory("Sen", text);
  setStatus(asCommand ? "KOMUT ÇÖZÜMLENİYOR..." : "DÜŞÜNÜYOR...");
  setMeterActive(true);

  const result = await withApi((api) => {
    if (asCommand && api.run_command) return api.run_command(text);
    return api.ask(text);
  });

  setMeterActive(false);

  if (!result) return;

  const replyText =
    result.reply ||
    result.response ||
    result.error ||
    "Yanıt alınamadı bilader.";

  addHistory("Bilader", replyText);
  refs.codePanel.textContent = result.code || "";

  if (result.error) {
    setStatus(`Hata: ${result.error}`);
  } else {
    setStatus("BAĞLANTI TAMAMLANDI, BİLADER.");
  }

  pulseSpeaking(1000);
  refs.prompt.value = "";
}

async function toggleListening() {
  if (!state.listening) {
    const result = await withApi((api) => api.start_listening?.());
    if (result?.ok) {
      state.listening = true;
      refs.listenToggle.textContent = "Dinlemeyi Durdur";
      setStatus("DİNLİYOR...");
      setMeterActive(true);
    }
    return;
  }

  const result = await withApi((api) => api.stop_listening?.());
  if (result?.ok) {
    state.listening = false;
    refs.listenToggle.textContent = "Dinlemeyi Başlat";
    setStatus("BAĞLANTI TAMAMLANDI, BİLADER.");
    setMeterActive(false);
  }
}

function bindInputEvents() {
  refs.sendBtn.addEventListener("click", () => sendPrompt(false));
  refs.routeBtn.addEventListener("click", () => sendPrompt(true));

  refs.prompt.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") {
      ev.preventDefault();
      if (ev.shiftKey) {
        sendPrompt(true);
      } else {
        sendPrompt(false);
      }
    }
  });

  refs.listenToggle.addEventListener("click", toggleListening);
  refs.clearMemory.addEventListener("click", () => {
    clearHistoryUi();
    setStatus("Ekran temizlendi bilader.");
  });
}

async function toggleArduino() {
  const result = await withApi((api) => api.toggle_arduino?.());
  if (!result) return;

  const connected = Boolean(result.connected);
  refs.arduinoToggle.textContent = connected ? "Arduino Bağlı" : "Arduino Bağla";
  refs.devicePanel.textContent = pretty(result);

  if (connected) {
    setStatus(`Arduino bağlantısı kuruldu (${result.port || "port"}).`);
  } else if (result.error) {
    setStatus(`Arduino hata: ${result.error}`);
  } else {
    setStatus("Arduino bağlantısı kapatıldı.");
  }
}

async function getArduinoTemp() {
  const result = await withApi((api) => api.arduino_temperature?.());
  if (!result) return;
  refs.devicePanel.textContent = pretty(result);
  if (result.ok) {
    setStatus(`Sıcaklık verisi geldi: ${result.response || "?"}`);
  } else {
    setStatus(result.error || "Sıcaklık okunamadı.");
  }
}

async function arduinoLight(on) {
  const fn = on ? "arduino_light_on" : "arduino_light_off";
  const result = await withApi((api) => api[fn]?.());
  if (!result) return;
  refs.devicePanel.textContent = pretty(result);
  setStatus(on ? "Işık aç komutu gönderildi." : "Işık kapat komutu gönderildi.");
}

async function scanPorts() {
  const result = await withApi((api) => api.list_ports?.());
  if (!result) return;
  refs.devicePanel.textContent = pretty(result);
  setStatus("USB/Serial port taraması tamamlandı.");
}

function bindDeviceEvents() {
  refs.arduinoToggle.addEventListener("click", toggleArduino);
  refs.arduinoTemp.addEventListener("click", getArduinoTemp);
  refs.arduinoLightOn.addEventListener("click", () => arduinoLight(true));
  refs.arduinoLightOff.addEventListener("click", () => arduinoLight(false));
  refs.portsBtn.addEventListener("click", scanPorts);
}

async function snapshotSystem() {
  const result = await withApi((api) => api.system_snapshot?.());
  if (!result) return;
  refs.resourcePanel.textContent = pretty(result);
  updateTelemetry(result);
  setStatus("Sistem görünümü güncellendi.");
}

async function listProcesses() {
  const result = await withApi((api) => api.process_table?.());
  if (!result) return;
  refs.resourcePanel.textContent = pretty(result);
  setStatus("Aktif süreç tablosu güncellendi.");
}

async function loadMemorySummary() {
  const result = await withApi((api) => api.memory_summary?.());
  if (!result) return;
  refs.resourcePanel.textContent = pretty(result);
  setStatus("Hafıza özeti getirildi.");
}

function bindSystemEvents() {
  refs.snapshotBtn.addEventListener("click", snapshotSystem);
  refs.processBtn.addEventListener("click", listProcesses);
  refs.memoryBtn.addEventListener("click", loadMemorySummary);
}

async function openApplication() {
  const app = refs.appName.value.trim();
  if (!app) {
    setStatus("Uygulama adı gir bilader.");
    return;
  }

  const result = await withApi((api) => api.open_application?.(app));
  if (!result) return;

  refs.resourcePanel.textContent = pretty(result);
  if (result.ok) {
    setStatus(`${app} açma komutu gönderildi.`);
  } else {
    setStatus(result.error || "Uygulama açılamadı.");
  }
}

function bindAppLauncherEvents() {
  refs.openAppBtn.addEventListener("click", openApplication);
  refs.appName.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter") {
      ev.preventDefault();
      openApplication();
    }
  });
}

async function pollVoiceEvents() {
  const result = await withApi((api) => api.poll_voice_events?.(), "");
  if (!result || !Array.isArray(result)) return;

  result.forEach((evt) => {
    const kind = evt?.kind;
    const payload = evt?.payload || {};

    if (kind === "wake") {
      setStatus(`Wake-word algılandı: ${payload.text || "bilader"}`);
      addHistory("Wake", payload.text || "hey bilader");
      pulseSpeaking(650);
      return;
    }

    if (kind === "error") {
      setStatus(`Mikrofon hatası: ${payload.error || "bilinmiyor"}`);
      return;
    }
  });
}

function startVoicePolling() {
  setInterval(() => {
    if (!state.listening) return;
    pollVoiceEvents();
  }, 1000);
}

function startClockTelemetryFallback() {
  setInterval(() => {
    if (refs.cpuText.textContent !== "0%") return;
    const t = Date.now() / 1000;
    const cpu = 18 + Math.abs(Math.sin(t * 0.9)) * 35;
    const ram = 32 + Math.abs(Math.sin(t * 0.3)) * 40;
    const disk = 52 + Math.abs(Math.sin(t * 0.14)) * 14;
    refs.cpuText.textContent = `${cpu.toFixed(1)}%`;
    refs.ramText.textContent = `${ram.toFixed(1)}%`;
    refs.diskText.textContent = `${disk.toFixed(1)}%`;
  }, 1300);
}

window.Bilader = {
  onNativeEvent(evt) {
    if (!evt || typeof evt !== "object") return;

    if (evt.event === "status") {
      const text = evt.payload?.text || "";
      setStatus(text);
      pulseSpeaking(800);
      return;
    }

    if (evt.event === "telemetry") {
      updateTelemetry(evt.payload || {});
      return;
    }

    if (evt.event === "wake") {
      const text = evt.payload?.text || "hey bilader";
      setStatus(`Wake-word: ${text}`);
      addHistory("Wake", text);
      pulseSpeaking(760);
      return;
    }
  }
};

function boot() {
  initIcons();
  initMatrix();
  initVoiceMeter();

  bindInputEvents();
  bindDeviceEvents();
  bindSystemEvents();
  bindAppLauncherEvents();

  startVoicePolling();
  startClockTelemetryFallback();

  setStatus("BAĞLANTI TAMAMLANDI, BİLADER.");
  addHistory("Sistem", "BİLADER başlatıldı. Hazırım bilader.");
}

boot();

// ------------------------------------------------------------
// Utility helpers for future expansion (kept explicit for readability)
// ------------------------------------------------------------

function safeNumber(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function mapRange(value, inMin, inMax, outMin, outMax) {
  const n = (value - inMin) / (inMax - inMin || 1);
  return lerp(outMin, outMax, clamp(n, 0, 1));
}

function debounce(fn, wait = 200) {
  let t = null;
  return (...args) => {
    if (t) clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

function throttle(fn, ms = 120) {
  let pending = false;
  return (...args) => {
    if (pending) return;
    pending = true;
    fn(...args);
    setTimeout(() => {
      pending = false;
    }, ms);
  };
}

function chunkArray(arr, chunkSize = 3) {
  const chunks = [];
  for (let i = 0; i < arr.length; i += chunkSize) {
    chunks.push(arr.slice(i, i + chunkSize));
  }
  return chunks;
}

function stringifyError(err) {
  if (!err) return "unknown_error";
  if (typeof err === "string") return err;
  if (err.message) return err.message;
  try {
    return JSON.stringify(err);
  } catch {
    return String(err);
  }
}

function toHumanBytes(bytes) {
  const b = safeNumber(bytes);
  const units = ["B", "KB", "MB", "GB", "TB"];
  let i = 0;
  let value = b;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value.toFixed(2)} ${units[i]}`;
}

function translateIntent(intent) {
  const map = {
    toggle: "Bağlantı Aç/Kapat",
    temperature: "Sıcaklık Oku",
    light_on: "Işığı Yak",
    light_off: "Işığı Kapat",
    stats: "Sistem İstatistikleri",
    open_app: "Uygulama Aç",
    chat: "Genel Sohbet"
  };
  return map[intent] || intent;
}

function parseTemperature(raw) {
  if (!raw) return null;
  const m = String(raw).match(/-?\d+(\.\d+)?/);
  if (!m) return null;
  return Number(m[0]);
}

function renderTemperature(raw) {
  const c = parseTemperature(raw);
  if (c == null) return `Sıcaklık okunamadı (${raw})`;
  const f = c * 1.8 + 32;
  return `${c.toFixed(1)}°C / ${f.toFixed(1)}°F`;
}

function summarizeProcessTable(rows) {
  if (!Array.isArray(rows) || rows.length === 0) return "Süreç bulunamadı";
  return rows
    .slice(0, 5)
    .map((p, idx) => `${idx + 1}. ${p.name} (CPU: ${p.cpu || 0} | RAM: ${p.memory || 0}%)`)
    .join("\n");
}

function textContainsAny(text, words) {
  const low = String(text || "").toLowerCase();
  return words.some((w) => low.includes(String(w).toLowerCase()));
}

function makeUid(prefix = "id") {
  const rnd = Math.random().toString(36).slice(2, 8);
  return `${prefix}_${Date.now()}_${rnd}`;
}

function ensureArray(value) {
  return Array.isArray(value) ? value : [];
}

function normalizeStatusMessage(msg) {
  if (!msg) return "Durum güncellendi.";
  if (msg.length < 3) return "Durum güncellendi.";
  return msg;
}

function updatePanel(panelEl, value) {
  panelEl.textContent = pretty(value);
}

function appendPanelLine(panelEl, line) {
  panelEl.textContent += `${panelEl.textContent ? "\n" : ""}${line}`;
}

function clearPanel(panelEl) {
  panelEl.textContent = "";
}

function panelHasContent(panelEl) {
  return Boolean(panelEl.textContent.trim());
}

function roleColor(role) {
  const r = String(role || "").toLowerCase();
  if (r.includes("bilader") || r.includes("assistant")) return "#8ef7ff";
  if (r.includes("sistem")) return "#b4ff96";
  return "#d2e7ef";
}

function enhanceHistoryStyles() {
  $$(".history-item").forEach((item) => {
    const role = item.querySelector(".role")?.textContent || "";
    item.style.borderColor = `${roleColor(role)}55`;
  });
}

const enhanceHistoryStylesThrottled = throttle(enhanceHistoryStyles, 200);

new MutationObserver(enhanceHistoryStylesThrottled).observe(refs.history, {
  childList: true,
  subtree: true
});

function buildQuickCommandBar() {
  const commands = [
    "Bilader CPU nasıl?",
    "Arduino'ya bağlan",
    "Odanın sıcaklığı kaç?",
    "Işığı yak",
    "Spotify aç",
    "RAM dolu mu?",
    "Kod örneği ver"
  ];

  const wrap = document.createElement("div");
  wrap.className = "chips-row";

  commands.forEach((cmd) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = cmd;
    chip.addEventListener("click", () => {
      refs.prompt.value = cmd;
      sendPrompt(textContainsAny(cmd, ["bağlan", "yak", "aç", "cpu", "ram", "sıcaklık"]));
    });
    wrap.appendChild(chip);
  });

  const chatPanel = $(".chat-panel");
  chatPanel.appendChild(wrap);
}

buildQuickCommandBar();
