const canvas = document.getElementById("matrixCanvas");
const ctx = canvas.getContext("2d");

const logo = document.getElementById("logo");
const statusText = document.getElementById("statusText");
const healthText = document.getElementById("healthText");
const visualizer = document.getElementById("visualizer");
const chatLog = document.getElementById("chatLog");
const promptInput = document.getElementById("promptInput");
const sendBtn = document.getElementById("sendBtn");
const listenBtn = document.getElementById("listenBtn");
const arduinoBtn = document.getElementById("arduinoBtn");
const systemBtn = document.getElementById("systemBtn");
const deviceBtn = document.getElementById("deviceBtn");
const memoryBtn = document.getElementById("memoryBtn");
const exportBtn = document.getElementById("exportBtn");
const guideBtn = document.getElementById("guideBtn");
const codeBox = document.getElementById("codeBox");
const deviceInfo = document.getElementById("deviceInfo");

let listening = true;
const bars = [];

function setStatus(value) {
  statusText.textContent = value;
}

function toggleLogo(active) {
  logo.classList.toggle("talking", active);
}

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  row.textContent = text;
  chatLog.appendChild(row);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function initVisualizer() {
  for (let i = 0; i < 80; i++) {
    const bar = document.createElement("div");
    bar.className = "bar";
    visualizer.appendChild(bar);
    bars.push(bar);
  }
}

function runVisualizer() {
  bars.forEach((bar, i) => {
    const h = 8 + Math.abs(Math.sin(Date.now() / 250 + i * 0.22)) * 64;
    bar.style.height = `${h}px`;
  });
  requestAnimationFrame(runVisualizer);
}

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

const chars = "01BILADER";
let drops = [];

function initMatrix() {
  const columns = Math.max(20, Math.floor(window.innerWidth / 16));
  drops = new Array(columns).fill(1);
}

function drawMatrix() {
  ctx.fillStyle = "rgba(5,5,5,0.16)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#00ff41";
  ctx.font = "15px monospace";

  for (let i = 0; i < drops.length; i++) {
    const ch = chars[Math.floor(Math.random() * chars.length)];
    const x = i * 16;
    const y = drops[i] * 16;
    ctx.fillText(ch, x, y);

    if (y > canvas.height && Math.random() > 0.975) {
      drops[i] = 0;
    }
    drops[i] += 1;
  }
}

function showCodeBlocks(blocks) {
  if (!Array.isArray(blocks) || blocks.length === 0) {
    codeBox.classList.add("hidden");
    codeBox.textContent = "";
    return;
  }
  codeBox.classList.remove("hidden");
  codeBox.textContent = blocks.join("\n\n----\n\n");
}

async function askBilader(text) {
  addMessage("user", text);
  setStatus("DÜŞÜNÜYOR...");
  toggleLogo(true);

  try {
    const res = await window.pywebview.api.ask(text);
    addMessage("assistant", res.answer || "Cevap yok.");
    showCodeBlocks(res.code_blocks || []);
    setStatus(res.source === "local" ? "YEREL MOD CEVABI" : "BAĞLANTI TAMAMLANDI, BİLADER.");
  } catch (err) {
    setStatus("BAĞLANTI HATASI");
    addMessage("assistant", `Hata: ${err}`);
  } finally {
    toggleLogo(false);
  }
}

async function refreshHealth() {
  try {
    const h = await window.pywebview.api.get_health();
    const stt = h.stt ? "OK" : "YOK";
    const tts = h.tts ? "OK" : "YOK";
    const gem = h.gemini ? "OK" : "YOK";
    healthText.textContent = `STT: ${stt} | TTS: ${tts} | Gemini: ${gem}`;
  } catch (_) {
    healthText.textContent = "STT: - | TTS: - | Gemini: -";
  }
}

async function refreshDevices() {
  try {
    const d = await window.pywebview.api.list_devices();
    const usb = d.usb?.length ? d.usb.join(", ") : "yok";
    const bt = d.bluetooth?.length ? d.bluetooth.join(", ") : "yok";
    deviceInfo.innerHTML = `<strong>USB:</strong> ${usb}<br/><strong>Bluetooth:</strong> ${bt}`;
  } catch (_) {
    deviceInfo.innerHTML = "USB: -<br/>Bluetooth: -";
  }
}

sendBtn.addEventListener("click", () => {
  const text = promptInput.value.trim();
  if (!text) return;
  promptInput.value = "";
  askBilader(text);
});

promptInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendBtn.click();
});

listenBtn.addEventListener("click", async () => {
  listening = !listening;
  const res = await window.pywebview.api.set_listening(listening);
  listening = !!res.listening;
  listenBtn.textContent = `Dinleme: ${listening ? "Açık" : "Kapalı"}`;
  setStatus(listening ? "DİNLİYOR..." : "DİNLEME DURDU");
});

arduinoBtn.addEventListener("click", async () => {
  const res = await window.pywebview.api.toggle_arduino();
  addMessage("assistant", res.message);
  const moduleArduino = document.querySelectorAll(".module")[2];
  if (moduleArduino) moduleArduino.classList.toggle("active", !!res.connected);
});

systemBtn.addEventListener("click", async () => {
  const s = await window.pywebview.api.get_system_status();
  addMessage("assistant", `CPU %${s.cpu.toFixed(1)} | RAM %${s.ram_percent.toFixed(1)} | Disk %${s.disk_percent.toFixed(1)}`);
});

deviceBtn.addEventListener("click", refreshDevices);

memoryBtn.addEventListener("click", async () => {
  const res = await window.pywebview.api.clear_memory();
  addMessage("assistant", res.message || "Hafıza temizlendi.");
});

exportBtn.addEventListener("click", async () => {
  const bundle = await window.pywebview.api.export_memory(300);
  const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `bilader-memory-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  addMessage("assistant", "Hafıza JSON olarak dışa aktarıldı.");
});

guideBtn.addEventListener("click", async () => {
  const pb = await window.pywebview.api.get_playbook();
  const core = Object.entries(pb.core || {}).slice(0, 8);
  const text = core
    .map(([k, v]) => `• ${k}: ${v.description}`)
    .join("\\n");
  addMessage("assistant", `Komut rehberi:\\n${text}`);
});

window.BiladerUI = {
  receivePythonEvent(event) {
    if (!event || !event.type) return;
    if (event.type === "assistant_response") {
      const p = event.payload || {};
      addMessage("assistant", p.answer || "");
      showCodeBlocks(p.code_blocks || []);
    }
  }
};

window.addEventListener("resize", () => {
  resizeCanvas();
  initMatrix();
});

function boot() {
  initVisualizer();
  runVisualizer();

  resizeCanvas();
  initMatrix();
  setInterval(drawMatrix, 55);

  refreshHealth();
  refreshDevices();
  setInterval(refreshHealth, 10000);
  setInterval(refreshDevices, 8000);

  addMessage("assistant", "Hazırım bilader. Komut ver veya sohbeti başlat.");
}

boot();
