const $ = (s) => document.querySelector(s);

const refs = {
  logo: $("#logo"),
  status: $("#status"),
  history: $("#history"),
  prompt: $("#prompt"),
  sendBtn: $("#sendBtn"),
  voiceBtn: $("#voiceBtn"),
  refreshHistoryBtn: $("#refreshHistoryBtn"),
  snapshotBtn: $("#snapshotBtn"),
  arduinoBtn: $("#arduinoBtn"),
  tempBtn: $("#tempBtn"),
  sidePanel: $("#sidePanel"),
  codePanel: $("#codePanel"),
  itemTpl: $("#itemTpl")
};

function setStatus(text) {
  refs.status.textContent = text;
}

function pulseLogo() {
  refs.logo.classList.add("speaking");
  setTimeout(() => refs.logo.classList.remove("speaking"), 700);
}

function apiReady() {
  return !!window.pywebview?.api;
}

async function callApi(fn) {
  if (!apiReady()) {
    setStatus("Native API hazır değil.");
    return null;
  }
  try {
    return await fn(window.pywebview.api);
  } catch (err) {
    setStatus(`Hata: ${err?.message || err}`);
    return null;
  }
}

function addItem(role, content, createdAt = "") {
  const el = refs.itemTpl.content.firstElementChild.cloneNode(true);
  el.querySelector(".role").textContent = role;
  el.querySelector(".time").textContent = createdAt || new Date().toLocaleTimeString("tr-TR");
  el.querySelector(".content").textContent = content;
  refs.history.appendChild(el);
  refs.history.scrollTop = refs.history.scrollHeight;
}

function clearHistoryUI() {
  refs.history.innerHTML = "";
}

async function loadHistory() {
  const rows = await callApi((api) => api.get_history?.(80));
  if (!rows) return;

  clearHistoryUI();
  rows.forEach((r) => addItem(r.role, r.content, r.created_at));
}

async function sendPrompt(text) {
  if (!text.trim()) return;

  addItem("user", text);
  refs.prompt.value = "";
  setStatus("DÜŞÜNÜYOR...");

  const result = await callApi((api) => api.ask(text));
  if (!result) return;

  const reply = result.reply || result.error || "Yanıt yok.";
  addItem("assistant", reply);
  refs.codePanel.textContent = result.code || "";

  pulseLogo();
  setStatus(result.error ? `Hata: ${result.error}` : "BAĞLANTI TAMAMLANDI, BİLADER.");
}

async function listenAndSend() {
  setStatus("DİNLİYOR...");
  const heard = await callApi((api) => api.listen_once?.());
  if (!heard) return;

  if (!heard.ok) {
    setStatus(heard.error || "Ses alınamadı.");
    return;
  }

  refs.prompt.value = heard.text;
  await sendPrompt(heard.text);
}

async function getSystemSnapshot() {
  const result = await callApi((api) => api.system_snapshot?.());
  if (!result) return;
  refs.sidePanel.textContent = JSON.stringify(result, null, 2);
  setStatus("Sistem bilgisi güncellendi.");
}

async function toggleArduino() {
  const result = await callApi((api) => api.toggle_arduino?.());
  if (!result) return;
  refs.sidePanel.textContent = JSON.stringify(result, null, 2);
  setStatus(result.error || "Arduino durumu güncellendi.");
}

async function readTemperature() {
  const result = await callApi((api) => api.arduino_temperature?.());
  if (!result) return;
  refs.sidePanel.textContent = JSON.stringify(result, null, 2);
  setStatus(result.error || "Sıcaklık isteği gönderildi.");
}

window.Bilader = {
  onNativeEvent(evt) {
    if (!evt) return;
    if (evt.event === "status") {
      setStatus(evt.payload?.text || "");
      pulseLogo();
    }
  }
};

refs.sendBtn.addEventListener("click", () => sendPrompt(refs.prompt.value));
refs.prompt.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendPrompt(refs.prompt.value);
  }
});
refs.voiceBtn.addEventListener("click", listenAndSend);
refs.refreshHistoryBtn.addEventListener("click", loadHistory);
refs.snapshotBtn.addEventListener("click", getSystemSnapshot);
refs.arduinoBtn.addEventListener("click", toggleArduino);
refs.tempBtn.addEventListener("click", readTemperature);

loadHistory();
