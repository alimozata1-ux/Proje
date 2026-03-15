const STORAGE_KEY = "cloud-files-v1";
const THEME_KEY = "cloud-theme";
const ESTIMATED_STORAGE_LIMIT_BYTES = 5 * 1024 * 1024;

const fileInput = document.getElementById("fileInput");
const searchInput = document.getElementById("searchInput");
const sortSelect = document.getElementById("sortSelect");
const typeFilter = document.getElementById("typeFilter");
const fileList = document.getElementById("fileList");
const emptyState = document.getElementById("emptyState");
const fileItemTemplate = document.getElementById("fileItemTemplate");
const totalCount = document.getElementById("totalCount");
const totalSize = document.getElementById("totalSize");
const favoriteCount = document.getElementById("favoriteCount");
const lastUpload = document.getElementById("lastUpload");
const clearAll = document.getElementById("clearAll");
const themeToggle = document.getElementById("themeToggle");
const dropZone = document.getElementById("dropZone");
const exportData = document.getElementById("exportData");
const importTrigger = document.getElementById("importTrigger");
const importInput = document.getElementById("importInput");
const quotaText = document.getElementById("quotaText");
const quotaBar = document.getElementById("quotaBar");

const dockServerStatus = document.getElementById("dockServerStatus");
const dockTotalSize = document.getElementById("dockTotalSize");
const dockUptime = document.getElementById("dockUptime");
const dockOpenFiles = document.getElementById("dockOpenFiles");
const dockOpenServer = document.getElementById("dockOpenServer");
const dockQuickTheme = document.getElementById("dockQuickTheme");
const dockSettings = document.getElementById("dockSettings");
const dockExport = document.getElementById("dockExport");
const dockSettingsPanel = document.getElementById("dockSettingsPanel");
const compactModeToggle = document.getElementById("compactModeToggle");
const softGlassToggle = document.getElementById("softGlassToggle");

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
wireDock();
initServerStats();

fileInput.addEventListener("change", async (event) => {
  await handleFiles(event.target.files);
  fileInput.value = "";
});

searchInput.addEventListener("input", render);
sortSelect.addEventListener("change", render);
typeFilter.addEventListener("change", render);

exportData.addEventListener("click", handleExport);
importTrigger.addEventListener("click", () => importInput.click());
importInput.addEventListener("change", handleImport);

clearAll.addEventListener("click", () => {
  if (!files.length) return;
  if (confirm("Tüm dosyalar silinsin mi?")) {
    files = [];
    persist();
    render();
    updateServerStats();
  }
});

themeToggle.addEventListener("click", toggleTheme);

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
      type: file.type || "other/unknown",
      size: file.size,
      uploadedAt: new Date().toISOString(),
      dataUrl: fileDataUrl,
      favorite: false,
    });
  }
  persist();
  render();
  updateServerStats();
}

function render() {
  const q = searchInput.value.trim().toLowerCase();
  const selectedType = typeFilter.value;
  const sortedAndFiltered = [...files]
    .filter((file) => file.name.toLowerCase().includes(q))
    .filter((file) => matchesType(file.type, selectedType))
    .sort(sortBySelectedRule);

  fileList.innerHTML = "";

  for (const file of sortedAndFiltered) {
    const item = fileItemTemplate.content.cloneNode(true);
    item.querySelector(".file-name").textContent = `${file.favorite ? "⭐ " : ""}${file.name}`;
    item.querySelector(".file-meta").textContent = `${prettySize(file.size)} • ${new Date(file.uploadedAt).toLocaleString("tr-TR")}`;

    const previewWrap = item.querySelector(".preview-wrap");
    const previewImage = item.querySelector(".file-preview");
    if (file.type.startsWith("image/")) {
      previewWrap.hidden = false;
      previewImage.src = file.dataUrl;
    }

    const favoriteBtn = item.querySelector(".favorite-btn");
    favoriteBtn.classList.toggle("active", Boolean(file.favorite));
    favoriteBtn.textContent = file.favorite ? "⭐ Favori" : "☆ Favori";

    favoriteBtn.addEventListener("click", () => {
      files = files.map((f) => (f.id === file.id ? { ...f, favorite: !f.favorite } : f));
      persist();
      render();
      updateServerStats();
    });

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

  const totalBytes = files.reduce((acc, file) => acc + file.size, 0);

  emptyState.style.display = sortedAndFiltered.length ? "none" : "block";
  totalCount.textContent = String(files.length);
  totalSize.textContent = prettySize(totalBytes);
  dockTotalSize.textContent = prettySize(totalBytes);
  favoriteCount.textContent = String(files.filter((file) => file.favorite).length);
  lastUpload.textContent = files[0] ? new Date(files[0].uploadedAt).toLocaleString("tr-TR") : "-";

  updateQuotaMeter();
}

function sortBySelectedRule(a, b) {
  const rule = sortSelect.value;
  if (rule === "oldest") return new Date(a.uploadedAt) - new Date(b.uploadedAt);
  if (rule === "nameAsc") return a.name.localeCompare(b.name, "tr");
  if (rule === "nameDesc") return b.name.localeCompare(a.name, "tr");
  if (rule === "sizeAsc") return a.size - b.size;
  if (rule === "sizeDesc") return b.size - a.size;
  return new Date(b.uploadedAt) - new Date(a.uploadedAt);
}

function matchesType(mimeType, selectedType) {
  if (selectedType === "all") return true;
  if (selectedType === "other") {
    return !["image", "video", "audio", "application"].some((prefix) => mimeType.startsWith(`${prefix}/`));
  }
  return mimeType.startsWith(`${selectedType}/`);
}

function loadFiles() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return parsed.map((f) => ({ ...f, favorite: Boolean(f.favorite), type: f.type || "other/unknown" }));
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

function toggleTheme() {
  document.body.classList.toggle("dark");
  localStorage.setItem(THEME_KEY, document.body.classList.contains("dark") ? "dark" : "light");
  themeToggle.textContent = document.body.classList.contains("dark") ? "☀️ Gündüz Modu" : "🌙 Gece Modu";
}

function wireTabs() {
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => setActiveTab(btn.dataset.tab || "filesPanel"));
  });
}

function setActiveTab(tabId) {
  tabButtons.forEach((b) => b.classList.toggle("active", b.dataset.tab === tabId));
  tabPanels.forEach((panel) => panel.classList.toggle("active", panel.id === tabId));
}

function wireDock() {
  dockOpenFiles.addEventListener("click", () => setActiveTab("filesPanel"));
  dockOpenServer.addEventListener("click", () => setActiveTab("serverPanel"));
  dockQuickTheme.addEventListener("click", toggleTheme);
  dockSettings.addEventListener("click", () => {
    dockSettingsPanel.hidden = !dockSettingsPanel.hidden;
  });
  dockExport.addEventListener("click", handleExport);

  compactModeToggle.addEventListener("change", () => {
    document.body.classList.toggle("compact", compactModeToggle.checked);
  });

  softGlassToggle.addEventListener("change", () => {
    document.body.classList.toggle("no-glass", !softGlassToggle.checked);
  });
}

function initServerStats() {
  browserName.textContent = navigator.userAgent;
  updateServerStats();
  setInterval(() => {
    const elapsedSeconds = Math.floor((Date.now() - appStartTime) / 1000);
    const formatted = formatDuration(elapsedSeconds);
    uptime.textContent = formatted;
    dockUptime.textContent = formatted;
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
      dockServerStatus.textContent = "Aktif";
    } else {
      serverStatus.textContent = `Hata (${response.status})`;
      serverLatency.textContent = `${duration} ms`;
      dockServerStatus.textContent = "Hata";
    }
  } catch {
    serverStatus.textContent = "Bağlantı Yok";
    serverLatency.textContent = "-";
    dockServerStatus.textContent = "Çevrimdışı";
  }
}

function updateQuotaMeter() {
  const usage = new Blob([localStorage.getItem(STORAGE_KEY) || ""]).size;
  const percentage = Math.min(100, Math.round((usage / ESTIMATED_STORAGE_LIMIT_BYTES) * 100));
  quotaBar.style.width = `${percentage}%`;
  quotaText.textContent = `Kullanım: %${percentage} (${prettySize(usage)} / ~${prettySize(ESTIMATED_STORAGE_LIMIT_BYTES)})`;
}

function handleExport() {
  const payload = {
    exportedAt: new Date().toISOString(),
    fileCount: files.length,
    files,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `cloud-files-backup-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

async function handleImport(event) {
  const importFile = event.target.files?.[0];
  if (!importFile) return;

  try {
    const text = await importFile.text();
    const parsed = JSON.parse(text);
    if (!Array.isArray(parsed.files)) {
      throw new Error("Yedek formatı geçersiz");
    }

    const normalized = parsed.files
      .filter((f) => f && typeof f === "object" && f.name && f.dataUrl)
      .map((f) => ({
        id: typeof f.id === "string" ? f.id : crypto.randomUUID(),
        name: String(f.name),
        type: String(f.type || "other/unknown"),
        size: Number(f.size || 0),
        uploadedAt: f.uploadedAt || new Date().toISOString(),
        dataUrl: String(f.dataUrl),
        favorite: Boolean(f.favorite),
      }));

    files = normalized;
    persist();
    render();
    updateServerStats();
    alert("Yedek başarıyla içe aktarıldı.");
  } catch {
    alert("Yedek okunamadı. Lütfen geçerli bir JSON dosyası seç.");
  } finally {
    importInput.value = "";
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
