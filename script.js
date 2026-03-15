const STORAGE_KEY = "cloud-files-v1";
const THEME_KEY = "cloud-theme";
const ESTIMATED_STORAGE_LIMIT_BYTES = 5 * 1024 * 1024;
const NOTES_KEY = "cloud-quick-notes";
const ACTIVITY_KEY = "cloud-activity-log";
const VIEW_PREFS_KEY = "cloud-view-prefs";
const ACCENT_KEY_LIGHT = "cloud-accent-color-light";
const ACCENT_KEY_DARK = "cloud-accent-color-dark";

const fileInput = document.getElementById("fileInput");
const searchInput = document.getElementById("searchInput");
const sortSelect = document.getElementById("sortSelect");
const typeFilter = document.getElementById("typeFilter");
const fileList = document.getElementById("fileList");
const emptyState = document.getElementById("emptyState");
const quickAccess = document.getElementById("quickAccess");
const quickAccessEmpty = document.getElementById("quickAccessEmpty");
const fileItemTemplate = document.getElementById("fileItemTemplate");
const totalCount = document.getElementById("totalCount");
const totalSize = document.getElementById("totalSize");
const favoriteCount = document.getElementById("favoriteCount");
const lastUpload = document.getElementById("lastUpload");
const storageHealth = document.getElementById("storageHealth");
const clearAll = document.getElementById("clearAll");
const favoriteOnlyToggle = document.getElementById("favoriteOnlyToggle");
const resetFilters = document.getElementById("resetFilters");
const smartCleanup = document.getElementById("smartCleanup");
const themeToggle = document.getElementById("themeToggle");
const dropZone = document.getElementById("dropZone");
const exportData = document.getElementById("exportData");
const importTrigger = document.getElementById("importTrigger");
const importInput = document.getElementById("importInput");
const quotaText = document.getElementById("quotaText");
const quotaBar = document.getElementById("quotaBar");
const quickNotes = document.getElementById("quickNotes");
const activityList = document.getElementById("activityList");
const activityEmpty = document.getElementById("activityEmpty");
const toast = document.getElementById("toast");
const tipText = document.getElementById("tipText");
const newTip = document.getElementById("newTip");

const dockServerStatus = document.getElementById("dockServerStatus");
const dockTotalSize = document.getElementById("dockTotalSize");
const dockFileCount = document.getElementById("dockFileCount");
const dockUptime = document.getElementById("dockUptime");
const dockRam = document.getElementById("dockRam");
const dockWifi = document.getElementById("dockWifi");
const dockOpenFiles = document.getElementById("dockOpenFiles");
const dockOpenServer = document.getElementById("dockOpenServer");
const dockQuickTheme = document.getElementById("dockQuickTheme");
const dockSettings = document.getElementById("dockSettings");
const dockExport = document.getElementById("dockExport");
const dockSettingsPanel = document.getElementById("dockSettingsPanel");
const compactModeToggle = document.getElementById("compactModeToggle");
const softGlassToggle = document.getElementById("softGlassToggle");
const accentColorPicker = document.getElementById("accentColorPicker");
const resetAccent = document.getElementById("resetAccent");

const tabButtons = Array.from(document.querySelectorAll(".tab-btn"));
const tabPanels = Array.from(document.querySelectorAll(".tab-panel"));

const serverStatus = document.getElementById("serverStatus");
const serverLatency = document.getElementById("serverLatency");
const uptime = document.getElementById("uptime");
const storageUsage = document.getElementById("storageUsage");
const ramUsage = document.getElementById("ramUsage");
const wifiUsage = document.getElementById("wifiUsage");
const browserName = document.getElementById("browserName");
const onlineStatus = document.getElementById("onlineStatus");
const refreshServerStats = document.getElementById("refreshServerStats");

let files = loadFiles();
let favoriteOnlyMode = false;
let activities = loadActivities();
const appStartTime = Date.now();

applySavedTheme();
applyAccentTheme();
render();
wireTabs();
wireDock();
wireShortcuts();
loadQuickNotes();
loadViewPrefs();
renderActivity();
initServerStats();
renderTip();

fileInput.addEventListener("change", async (event) => {
  await handleFiles(event.target.files);
  fileInput.value = "";
});

searchInput.addEventListener("input", () => { render(); saveViewPrefs(); });
sortSelect.addEventListener("change", () => { render(); saveViewPrefs(); });
typeFilter.addEventListener("change", () => { render(); saveViewPrefs(); });
favoriteOnlyToggle.addEventListener("click", () => {
  favoriteOnlyMode = !favoriteOnlyMode;
  favoriteOnlyToggle.textContent = favoriteOnlyMode ? "⭐ Favoriler Açık" : "⭐ Sadece Favoriler";
  render();
  saveViewPrefs();
});
resetFilters.addEventListener("click", () => {
  searchInput.value = "";
  sortSelect.value = "newest";
  typeFilter.value = "all";
  favoriteOnlyMode = false;
  favoriteOnlyToggle.textContent = "⭐ Sadece Favoriler";
  render();
  saveViewPrefs();
  showToast("Filtreler sıfırlandı");
});
smartCleanup.addEventListener("click", () => {
  const before = files.length;
  const threshold = Math.round(ESTIMATED_STORAGE_LIMIT_BYTES * 0.8);
  let usage = new Blob([localStorage.getItem(STORAGE_KEY) || ""]).size;
  if (usage <= threshold) {
    showToast("Depolama zaten sağlıklı");
    return;
  }
  files = [...files].sort((a, b) => new Date(a.uploadedAt) - new Date(b.uploadedAt));
  while (files.length && usage > threshold) {
    files.shift();
    usage = new Blob([JSON.stringify(files)]).size;
  }
  files = files.sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt));
  persist();
  render();
  updateServerStats();
  const removed = before - files.length;
  addActivity(`Akıllı temizlik: ${removed} dosya kaldırıldı`);
  showToast(`Akıllı temizlik tamamlandı (${removed} dosya)`);
});

exportData.addEventListener("click", handleExport);
importTrigger.addEventListener("click", () => importInput.click());
importInput.addEventListener("change", handleImport);
quickNotes.addEventListener("input", () => {
  localStorage.setItem(NOTES_KEY, quickNotes.value);
});

newTip.addEventListener("click", renderTip);

clearAll.addEventListener("click", () => {
  if (!files.length) return;
  if (confirm("Tüm dosyalar silinsin mi?")) {
    files = [];
    persist();
    render();
    updateServerStats();
    addActivity("Tüm dosyalar temizlendi");
    showToast("Tüm dosyalar silindi");
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
if (navigator.connection) {
  navigator.connection.addEventListener("change", updateDeviceStats);
}
refreshServerStats.addEventListener("click", updateServerStats);

async function handleFiles(fileListObj) {
  const incoming = Array.from(fileListObj);
  let added = 0;
  let skipped = 0;
  for (const file of incoming) {
    const duplicate = files.some((f) => f.name === file.name && f.size === file.size);
    if (duplicate) {
      skipped += 1;
      continue;
    }
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
    added += 1;
  }
  persist();
  render();
  updateServerStats();
  if (added) {
    addActivity(`${added} dosya yüklendi`);
    showToast(`${added} dosya yüklendi`);
  }
  if (skipped) {
    addActivity(`${skipped} yinelenen dosya atlandı`);
    showToast(`${skipped} yinelenen dosya atlandı`);
  }
}

function render() {
  const q = searchInput.value.trim().toLowerCase();
  const selectedType = typeFilter.value;
  const sortedAndFiltered = [...files]
    .filter((file) => file.name.toLowerCase().includes(q))
    .filter((file) => matchesType(file.type, selectedType))
    .filter((file) => (favoriteOnlyMode ? file.favorite : true))
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
      addActivity(`Favori güncellendi: ${file.name}`);
      showToast("Favori durumu güncellendi");
    });

    item.querySelector(".copy-name-btn").addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(file.name);
        addActivity(`Dosya adı kopyalandı: ${file.name}`);
        showToast("Dosya adı kopyalandı");
      } catch {
        showToast("Kopyalama desteklenmiyor");
      }
    });

    item.querySelector(".download-btn").addEventListener("click", () => {
      const a = document.createElement("a");
      a.href = file.dataUrl;
      a.download = file.name;
      a.click();
      addActivity(`Dosya indirildi: ${file.name}`);
    });

    item.querySelector(".delete-btn").addEventListener("click", () => {
      files = files.filter((f) => f.id !== file.id);
      persist();
      render();
      updateServerStats();
      addActivity(`Dosya silindi: ${file.name}`);
      showToast("Dosya silindi");
    });

    fileList.appendChild(item);
  }

  const totalBytes = files.reduce((acc, file) => acc + file.size, 0);

  emptyState.style.display = sortedAndFiltered.length ? "none" : "block";
  totalCount.textContent = String(files.length);
  totalSize.textContent = prettySize(totalBytes);
  dockTotalSize.textContent = prettySize(totalBytes);
  favoriteCount.textContent = String(files.filter((file) => file.favorite).length);
  dockFileCount.textContent = `${files.length} dosya`;
  lastUpload.textContent = files[0] ? new Date(files[0].uploadedAt).toLocaleString("tr-TR") : "-";

  updateQuotaMeter();
  updateStorageHealth();
  renderQuickAccess();
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


function renderQuickAccess() {
  const favorites = files.filter((f) => f.favorite).slice(0, 8);
  quickAccess.innerHTML = "";
  for (const file of favorites) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "quick-chip";
    btn.textContent = file.name;
    btn.title = file.name;
    btn.addEventListener("click", () => {
      const a = document.createElement("a");
      a.href = file.dataUrl;
      a.download = file.name;
      a.click();
      addActivity(`Hızlı erişimden indirildi: ${file.name}`);
      showToast("Hızlı erişim indirildi");
    });
    quickAccess.appendChild(btn);
  }
  quickAccessEmpty.style.display = favorites.length ? "none" : "block";
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
  applyAccentTheme();
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

  accentColorPicker.addEventListener("input", () => {
    const color = accentColorPicker.value;
    applyAccentColor(color);
    const key = document.body.classList.contains("dark") ? ACCENT_KEY_DARK : ACCENT_KEY_LIGHT;
    localStorage.setItem(key, color);
  });

  resetAccent.addEventListener("click", () => {
    const key = document.body.classList.contains("dark") ? ACCENT_KEY_DARK : ACCENT_KEY_LIGHT;
    localStorage.removeItem(key);
    applyAccentTheme();
    showToast("Bu mod için tema rengi sıfırlandı");
  });
}


function initServerStats() {
  browserName.textContent = navigator.userAgent;
  updateServerStats();
  updateDeviceStats();
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
  updateDeviceStats();
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
  addActivity("Yedek dışa aktarıldı");
  showToast("Yedek dışa aktarıldı");
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
    addActivity("Yedek içe aktarıldı");
    showToast("Yedek içe aktarıldı");
  } catch {
    alert("Yedek okunamadı. Lütfen geçerli bir JSON dosyası seç.");
  } finally {
    importInput.value = "";
  }
}

function updateDeviceStats() {
  const ramText = navigator.deviceMemory ? `${navigator.deviceMemory} GB (tarayıcı bildirimi)` : "Desteklenmiyor";
  ramUsage.textContent = ramText;
  dockRam.textContent = `RAM: ${navigator.deviceMemory ? `${navigator.deviceMemory}GB` : "-"}`;

  const connection = navigator.connection;
  if (connection) {
    const wifiText = `${connection.effectiveType || "?"} • ${connection.downlink || "?"} Mbps • ${connection.rtt || "?"} ms`;
    wifiUsage.textContent = wifiText;
    dockWifi.textContent = `${connection.downlink || "?"}Mbps`;
  } else {
    wifiUsage.textContent = navigator.onLine ? "Ağ API desteklenmiyor (çevrimiçi)" : "Çevrimdışı";
    dockWifi.textContent = navigator.onLine ? "Online" : "Offline";
  }
}

function wireShortcuts() {
  window.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      setActiveTab("filesPanel");
      searchInput.focus();
    }
  });
}

function loadActivities() {
  try {
    return JSON.parse(localStorage.getItem(ACTIVITY_KEY) || "[]");
  } catch {
    return [];
  }
}

function addActivity(text) {
  activities.unshift({ text, at: new Date().toISOString() });
  activities = activities.slice(0, 20);
  localStorage.setItem(ACTIVITY_KEY, JSON.stringify(activities));
  renderActivity();
}

function renderActivity() {
  activityList.innerHTML = "";
  for (const item of activities) {
    const li = document.createElement("li");
    li.textContent = `${new Date(item.at).toLocaleTimeString("tr-TR")} • ${item.text}`;
    activityList.appendChild(li);
  }
  activityEmpty.style.display = activities.length ? "none" : "block";
}

function loadQuickNotes() {
  quickNotes.value = localStorage.getItem(NOTES_KEY) || "";
}

let toastTimer;
function showToast(message) {
  toast.textContent = message;
  toast.hidden = false;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
    toast.hidden = true;
  }, 1800);
}

function saveViewPrefs() {
  const prefs = {
    search: searchInput.value,
    sort: sortSelect.value,
    type: typeFilter.value,
    favoriteOnlyMode,
  };
  localStorage.setItem(VIEW_PREFS_KEY, JSON.stringify(prefs));
}

function loadViewPrefs() {
  try {
    const prefs = JSON.parse(localStorage.getItem(VIEW_PREFS_KEY) || "{}");
    searchInput.value = prefs.search || "";
    sortSelect.value = prefs.sort || "newest";
    typeFilter.value = prefs.type || "all";
    favoriteOnlyMode = Boolean(prefs.favoriteOnlyMode);
    favoriteOnlyToggle.textContent = favoriteOnlyMode ? "⭐ Favoriler Açık" : "⭐ Sadece Favoriler";
    render();
  } catch {
    // ignore invalid prefs
  }
}

function updateStorageHealth() {
  const usage = new Blob([localStorage.getItem(STORAGE_KEY) || ""]).size;
  const percentage = Math.round((usage / ESTIMATED_STORAGE_LIMIT_BYTES) * 100);
  if (percentage >= 90) {
    storageHealth.textContent = "Kritik";
  } else if (percentage >= 70) {
    storageHealth.textContent = "Dikkat";
  } else {
    storageHealth.textContent = "İyi";
  }
}

function applyAccentTheme() {
  const isDark = document.body.classList.contains("dark");
  const key = isDark ? ACCENT_KEY_DARK : ACCENT_KEY_LIGHT;
  const fallback = isDark ? "#4a8dff" : "#1f6fff";
  const color = localStorage.getItem(key) || fallback;
  applyAccentColor(color);
  accentColorPicker.value = color;
}

function applyAccentColor(color) {
  document.documentElement.style.setProperty("--accent", color);
  document.documentElement.style.setProperty("--accent-soft", hexToRgba(color, 0.2));
}

function hexToRgba(hex, alpha) {
  const clean = hex.replace("#", "");
  const bigint = parseInt(clean, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function renderTip() {
  const tips = [
    "Kısayol: Ctrl/Cmd + K ile aramaya hızlı odaklan.",
    "Favori dosyaları hızlı erişime eklemek için yıldızla işaretle.",
    "Depolama sağlığı Dikkat/Kritik olduğunda Akıllı Temizlik kullan.",
    "Yedek dışa aktarıp farklı cihazda içe aktararak taşıma yapabilirsin.",
    "Filtreleri sıfırla butonu yoğun listelerde hızlı toparlama sağlar.",
  ];
  const selected = tips[Math.floor(Math.random() * tips.length)];
  tipText.textContent = selected;
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
