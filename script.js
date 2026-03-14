const STORAGE_KEY = "cloud-files-v1";
const THEME_KEY = "cloud-theme";

const fileInput = document.getElementById("fileInput");
const searchInput = document.getElementById("searchInput");
const fileList = document.getElementById("fileList");
const emptyState = document.getElementById("emptyState");
const fileItemTemplate = document.getElementById("fileItemTemplate");
const totalCount = document.getElementById("totalCount");
const totalSize = document.getElementById("totalSize");
const lastUpload = document.getElementById("lastUpload");
const clearAll = document.getElementById("clearAll");
const themeToggle = document.getElementById("themeToggle");
const dropZone = document.getElementById("dropZone");

const tabButtons = Array.from(document.querySelectorAll(".tab-btn"));
const tabPanels = Array.from(document.querySelectorAll(".tab-panel"));

const serverStatus = document.getElementById("serverStatus");
const serverLatency = document.getElementById("serverLatency");
const uptime = document.getElementById("uptime");
const storageUsage = document.getElementById("storageUsage");
const browserName = document.getElementById("browserName");
const onlineStatus = document.getElementById("onlineStatus");
const refreshServerStats = document.getElementById("refreshServerStats");

let files = loadFiles();
const appStartTime = Date.now();

applySavedTheme();
render();
wireTabs();
initServerStats();

fileInput.addEventListener("change", async (event) => {
  await handleFiles(event.target.files);
  fileInput.value = "";
});

searchInput.addEventListener("input", render);

clearAll.addEventListener("click", () => {
  if (!files.length) return;
  if (confirm("Tüm dosyalar silinsin mi?")) {
    files = [];
    persist();
    render();
    updateServerStats();
  }
});

themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("dark");
  localStorage.setItem(THEME_KEY, document.body.classList.contains("dark") ? "dark" : "light");
  themeToggle.textContent = document.body.classList.contains("dark") ? "☀️ Gündüz Modu" : "🌙 Gece Modu";
});

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("drag-over");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("drag-over");
  });
});

dropZone.addEventListener("drop", async (event) => {
  const dropped = event.dataTransfer?.files;
  if (!dropped?.length) return;
  await handleFiles(dropped);
});

window.addEventListener("online", updateServerStats);
window.addEventListener("offline", updateServerStats);
refreshServerStats.addEventListener("click", updateServerStats);

async function handleFiles(fileListObj) {
  const incoming = Array.from(fileListObj);
  for (const file of incoming) {
    const fileDataUrl = await readAsDataURL(file);
    files.unshift({
      id: crypto.randomUUID(),
      name: file.name,
      type: file.type || "bilinmeyen",
      size: file.size,
      uploadedAt: new Date().toISOString(),
      dataUrl: fileDataUrl,
    });
  }
  persist();
  render();
  updateServerStats();
}

function render() {
  const q = searchInput.value.trim().toLowerCase();
  const visibleFiles = files.filter((f) => f.name.toLowerCase().includes(q));
  fileList.innerHTML = "";

  for (const file of visibleFiles) {
    const item = fileItemTemplate.content.cloneNode(true);
    item.querySelector(".file-name").textContent = file.name;
    item.querySelector(".file-meta").textContent = `${prettySize(file.size)} • ${new Date(file.uploadedAt).toLocaleString("tr-TR")}`;

    item.querySelector(".download-btn").addEventListener("click", () => {
      const a = document.createElement("a");
      a.href = file.dataUrl;
      a.download = file.name;
      a.click();
    });

    item.querySelector(".delete-btn").addEventListener("click", () => {
      files = files.filter((f) => f.id !== file.id);
      persist();
      render();
      updateServerStats();
    });

    fileList.appendChild(item);
  }

  emptyState.style.display = visibleFiles.length ? "none" : "block";
  totalCount.textContent = String(files.length);
  totalSize.textContent = prettySize(files.reduce((acc, file) => acc + file.size, 0));
  lastUpload.textContent = files[0] ? new Date(files[0].uploadedAt).toLocaleString("tr-TR") : "-";
}

function loadFiles() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(files));
}

function applySavedTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === "dark") {
    document.body.classList.add("dark");
    themeToggle.textContent = "☀️ Gündüz Modu";
  }
}

function wireTabs() {
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabId = btn.dataset.tab;
      tabButtons.forEach((b) => b.classList.toggle("active", b === btn));
      tabPanels.forEach((panel) => panel.classList.toggle("active", panel.id === tabId));
    });
  });
}

function initServerStats() {
  browserName.textContent = navigator.userAgent;
  updateServerStats();
  setInterval(() => {
    const elapsedSeconds = Math.floor((Date.now() - appStartTime) / 1000);
    uptime.textContent = formatDuration(elapsedSeconds);
  }, 1000);
}

async function updateServerStats() {
  onlineStatus.textContent = navigator.onLine ? "Çevrimiçi" : "Çevrimdışı";
  storageUsage.textContent = prettySize(new Blob([localStorage.getItem(STORAGE_KEY) || ""]).size);
  await measureLatency();
}

async function measureLatency() {
  const start = performance.now();
  try {
    const response = await fetch(window.location.href, { method: "HEAD", cache: "no-store" });
    const duration = Math.round(performance.now() - start);
    if (response.ok) {
      serverStatus.textContent = "Aktif";
      serverLatency.textContent = `${duration} ms`;
    } else {
      serverStatus.textContent = `Hata (${response.status})`;
      serverLatency.textContent = `${duration} ms`;
    }
  } catch {
    serverStatus.textContent = "Bağlantı Yok";
    serverLatency.textContent = "-";
  }
}

function formatDuration(totalSeconds) {
  const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
  const minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

function prettySize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error("Dosya okunamadı"));
    reader.readAsDataURL(file);
  });
}
