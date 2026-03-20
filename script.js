const STORAGE_KEY = "cloud-files-v1";
const THEME_KEY = "cloud-theme";
const ESTIMATED_STORAGE_LIMIT_BYTES = 5 * 1024 * 1024;
const NOTES_KEY = "cloud-quick-notes";
const ACTIVITY_KEY = "cloud-activity-log";
const VIEW_PREFS_KEY = "cloud-view-prefs";
const ACCENT_KEY_LIGHT = "cloud-accent-color-light";
const ACCENT_KEY_DARK = "cloud-accent-color-dark";
const CLIENT_ID_KEY = "cloud-client-id";

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
const folderTrigger = document.getElementById("folderTrigger");
const folderInput = document.getElementById("folderInput");
const quotaText = document.getElementById("quotaText");
const quotaBar = document.getElementById("quotaBar");
const quickNotes = document.getElementById("quickNotes");
const activityList = document.getElementById("activityList");
const activityEmpty = document.getElementById("activityEmpty");
const toast = document.getElementById("toast");
const tipText = document.getElementById("tipText");
const newTip = document.getElementById("newTip");
const footerYear = document.getElementById("footerYear");
const scrollTopBtn = document.getElementById("scrollTopBtn");
const selectionInfo = document.getElementById("selectionInfo");
const selectAllVisible = document.getElementById("selectAllVisible");
const clearSelection = document.getElementById("clearSelection");
const bulkFavorite = document.getElementById("bulkFavorite");
const bulkDownload = document.getElementById("bulkDownload");
const bulkDelete = document.getElementById("bulkDelete");

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
const serverEndpoint = document.getElementById("serverEndpoint");
const serverRam = document.getElementById("serverRam");
const serverWifi = document.getElementById("serverWifi");
const serverStorage = document.getElementById("serverStorage");
const serverLastChecked = document.getElementById("serverLastChecked");
const refreshServerStats = document.getElementById("refreshServerStats");

let files = loadFiles();
let favoriteOnlyMode = false;
let activities = loadActivities();
const appStartTime = Date.now();
const clientId = getOrCreateClientId();
let selectedFileIds = new Set();

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
initFinalTouches();

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
  const threshold = Math.round(ESTIMATED_STORAGE_LIMIT_BYTES * 0.8);
  let usage = new Blob([localStorage.getItem(STORAGE_KEY) || ""]).size;
  if (usage <= threshold) {
    showToast("Depolama zaten sağlıklı");
    return;
  }

  const ownFileIdsByOldest = [...files]
    .filter((f) => f.ownerId === clientId)
    .sort((a, b) => new Date(a.uploadedAt) - new Date(b.uploadedAt))
    .map((f) => f.id);

  let removed = 0;
  for (const fileId of ownFileIdsByOldest) {
    if (usage <= threshold) break;
    files = files.filter((f) => f.id !== fileId);
    usage = new Blob([JSON.stringify(files)]).size;
    removed += 1;
  }

  persist();
  render();
  updateServerStats();
  addActivity(`Akıllı temizlik: ${removed} kendi dosyan kaldırıldı`);
  showToast(removed ? `Akıllı temizlik tamamlandı (${removed} dosya)` : "Silinebilir kendi dosyan bulunamadı");
});

exportData.addEventListener("click", handleExport);
importTrigger.addEventListener("click", () => importInput.click());
importInput.addEventListener("change", handleImport);
folderTrigger.addEventListener("click", () => folderInput.click());
folderInput.addEventListener("change", async (event) => {
  const filesFromFolder = Array.from(event.target.files || []);
  if (!filesFromFolder.length) return;
  await handleFiles(filesFromFolder);
  folderInput.value = "";
});
quickNotes.addEventListener("input", () => {
  localStorage.setItem(NOTES_KEY, quickNotes.value);
});

newTip.addEventListener("click", renderTip);

selectAllVisible.addEventListener("click", () => {
  const visibleIds = getVisibleFiles().map((f) => f.id);
  selectedFileIds = new Set(visibleIds);
  render();
  showToast(`${visibleIds.length} dosya seçildi`);
});

clearSelection.addEventListener("click", () => {
  selectedFileIds.clear();
  render();
  showToast("Seçim temizlendi");
});

bulkFavorite.addEventListener("click", () => {
  if (!selectedFileIds.size) {
    showToast("Önce dosya seçmelisin");
    return;
  }
  files = files.map((f) => (selectedFileIds.has(f.id) ? { ...f, favorite: true } : f));
  persist();
  render();
  addActivity(`${selectedFileIds.size} dosya favoriye alındı`);
  showToast("Seçilen dosyalar favoriye alındı");
});

bulkDownload.addEventListener("click", () => {
  const selected = files.filter((f) => selectedFileIds.has(f.id));
  if (!selected.length) {
    showToast("Önce dosya seçmelisin");
    return;
  }
  for (const file of selected) {
    const a = document.createElement("a");
    a.href = file.dataUrl;
    a.download = file.name;
    a.click();
  }
  addActivity(`${selected.length} dosya toplu indirildi`);
  showToast("Toplu indirme başlatıldı");
});

bulkDelete.addEventListener("click", () => {
  const selected = files.filter((f) => selectedFileIds.has(f.id));
  const ownSelected = selected.filter((f) => f.ownerId === clientId);
  if (!ownSelected.length) {
    showToast("Silmek için sana ait dosya seçmelisin");
    return;
  }
  if (!confirm(`${ownSelected.length} seçili dosya silinsin mi?`)) return;
  const ownIds = new Set(ownSelected.map((f) => f.id));
  files = files.filter((f) => !ownIds.has(f.id));
  for (const id of ownIds) selectedFileIds.delete(id);
  persist();
  render();
  updateServerStats();
  addActivity(`${ownSelected.length} dosya toplu silindi`);
  showToast("Seçili dosyalar silindi");
});

scrollTopBtn.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});

window.addEventListener("scroll", () => {
  const shouldShow = window.scrollY > 280;
  scrollTopBtn.hidden = !shouldShow;
});

clearAll.addEventListener("click", () => {
  const ownCount = files.filter((f) => f.ownerId === clientId).length;
  if (!ownCount) return;
  if (confirm("Sadece sana ait tüm dosyalar silinsin mi?")) {
    files = files.filter((f) => f.ownerId !== clientId);
    persist();
    render();
    updateServerStats();
    addActivity("Kullanıcı kendi tüm dosyalarını temizledi");
    showToast(`${ownCount} dosya silindi (yalnızca sana ait)`);
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
  const dt = event.dataTransfer;
  if (!dt) return;

  const fromEntries = await extractDroppedFiles(dt);
  if (fromEntries.length) {
    await handleFiles(fromEntries);
    return;
  }

  const dropped = dt.files;
  if (!dropped?.length) return;
  await handleFiles(dropped);
});

window.addEventListener("online", () => { updateServerStats(); updateDockClientStats(); });
window.addEventListener("offline", () => { updateServerStats(); updateDockClientStats(); });
if (navigator.connection) {
  navigator.connection.addEventListener("change", updateDockClientStats);
}
refreshServerStats.addEventListener("click", updateServerStats);


async function extractDroppedFiles(dataTransfer) {
  const items = Array.from(dataTransfer.items || []);
  if (!items.length) return [];

  const collected = [];
  for (const item of items) {
    const entry = item.webkitGetAsEntry ? item.webkitGetAsEntry() : null;
    if (!entry) continue;
    await walkEntry(entry, collected);
  }
  return collected;
}

async function walkEntry(entry, collected) {
  if (entry.isFile) {
    await new Promise((resolve) => {
      entry.file((file) => {
        collected.push(file);
        resolve();
      }, () => resolve());
    });
    return;
  }

  if (!entry.isDirectory) return;
  const reader = entry.createReader();
  while (true) {
    const entries = await new Promise((resolve) => reader.readEntries(resolve));
    if (!entries.length) break;
    for (const child of entries) {
      await walkEntry(child, collected);
    }
  }
}

async function handleFiles(fileListObj) {
  const incoming = Array.from(fileListObj);
  let added = 0;
  let skipped = 0;
  for (const file of incoming) {
    const incomingName = file.webkitRelativePath || file.name;
    const duplicate = files.some((f) => f.name === incomingName && f.size === file.size);
    if (duplicate) {
      skipped += 1;
      continue;
    }
    const fileDataUrl = await readAsDataURL(file);
    files.unshift({
      id: crypto.randomUUID(),
      name: incomingName,
      type: file.type || "other/unknown",
      size: file.size,
      uploadedAt: new Date().toISOString(),
      dataUrl: fileDataUrl,
      favorite: false,
      ownerId: clientId,
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

function getVisibleFiles() {
  const q = searchInput.value.trim().toLowerCase();
  const selectedType = typeFilter.value;
  return [...files]
    .filter((file) => file.name.toLowerCase().includes(q))
    .filter((file) => matchesType(file.type, selectedType))
    .filter((file) => (favoriteOnlyMode ? file.favorite : true))
    .sort(sortBySelectedRule);
}

function render() {
  const sortedAndFiltered = getVisibleFiles();
  selectedFileIds = new Set([...selectedFileIds].filter((id) => files.some((f) => f.id === id)));

  fileList.innerHTML = "";

  for (const file of sortedAndFiltered) {
    const item = fileItemTemplate.content.cloneNode(true);
    const listItem = item.querySelector(".file-item");
    const fileSelect = item.querySelector(".file-select");
    fileSelect.checked = selectedFileIds.has(file.id);
    fileSelect.addEventListener("change", () => {
      if (fileSelect.checked) selectedFileIds.add(file.id);
      else selectedFileIds.delete(file.id);
      listItem.classList.toggle("selected", fileSelect.checked);
      updateSelectionInfo();
    });
    listItem.classList.toggle("selected", fileSelect.checked);

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

    item.querySelector(".rename-btn").addEventListener("click", () => {
      if (file.ownerId !== clientId) {
        showToast("Sadece kendi dosyanı yeniden adlandırabilirsin");
        return;
      }
      const nextName = prompt("Yeni dosya adı", file.name);
      if (!nextName || !nextName.trim()) return;
      files = files.map((f) => (f.id === file.id ? { ...f, name: nextName.trim() } : f));
      persist();
      render();
      addActivity(`Dosya yeniden adlandırıldı: ${file.name} -> ${nextName.trim()}`);
      showToast("Dosya adı güncellendi");
    });

    const deleteBtn = item.querySelector(".delete-btn");
    const isOwnedByCurrentUser = file.ownerId === clientId;
    deleteBtn.disabled = !isOwnedByCurrentUser;
    if (!isOwnedByCurrentUser) {
      deleteBtn.title = "Sadece dosyanın sahibi silebilir";
    }

    deleteBtn.addEventListener("click", () => {
      if (!isOwnedByCurrentUser) {
        showToast("Bu dosya sana ait değil, silemezsin");
        return;
      }
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
  updateSelectionInfo();
}

function updateSelectionInfo() {
  if (!selectionInfo) return;
  const total = selectedFileIds.size;
  const own = files.filter((f) => selectedFileIds.has(f.id) && f.ownerId === clientId).length;
  selectionInfo.textContent = `Seçili: ${total} (silinebilir: ${own})`;
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
    return parsed.map((f) => ({ ...f, favorite: Boolean(f.favorite), type: f.type || "other/unknown", ownerId: f.ownerId || clientId }));
  } catch {
    return [];
  }
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(files));
}

function getOrCreateClientId() {
  const existing = localStorage.getItem(CLIENT_ID_KEY);
  if (existing) return existing;
  const generated = crypto.randomUUID();
  localStorage.setItem(CLIENT_ID_KEY, generated);
  return generated;
}

function updateDockClientStats() {
  dockRam.textContent = `RAM: ${navigator.deviceMemory ? `${navigator.deviceMemory}GB` : "-"}`;
  const connection = navigator.connection;
  if (connection && connection.downlink) {
    dockWifi.textContent = `${connection.downlink}Mbps`;
  } else {
    dockWifi.textContent = navigator.onLine ? "Online" : "Offline";
  }
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
  serverEndpoint.textContent = window.location.origin;
  updateDockClientStats();
  updateServerStats();
  setInterval(() => {
    const elapsedSeconds = Math.floor((Date.now() - appStartTime) / 1000);
    const formatted = formatDuration(elapsedSeconds);
    dockUptime.textContent = formatted;
  }, 1000);
}

async function updateServerStats() {
  await measureLatency();
  serverLastChecked.textContent = new Date().toLocaleTimeString("tr-TR");
}

async function measureLatency() {
  const start = performance.now();
  try {
    const response = await fetch(window.location.href, { method: "HEAD", cache: "no-store" });
    const duration = Math.round(performance.now() - start);
    const serverRamHeader = response.headers.get("x-server-ram");
    const serverWifiHeader = response.headers.get("x-server-wifi");
    const serverStorageHeader = response.headers.get("x-server-storage");
    const serverStorageUsed = response.headers.get("x-server-storage-used");
    const serverStorageTotal = response.headers.get("x-server-storage-total");

    serverRam.textContent = serverRamHeader || "Sunucu verisi yok";
    serverWifi.textContent = serverWifiHeader || "Sunucu verisi yok";
    serverStorage.textContent = serverStorageHeader || ((serverStorageUsed && serverStorageTotal) ? `${serverStorageUsed} / ${serverStorageTotal}` : "Sunucu verisi yok");

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
    serverRam.textContent = "-";
    serverWifi.textContent = "-";
    serverStorage.textContent = "-";
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
        ownerId: clientId,
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
  // body.dark içindeki CSS değişkenlerini gerçekten override etmek için
  // rengi doğrudan body üzerine de yazıyoruz.
  document.documentElement.style.setProperty("--accent", color);
  document.documentElement.style.setProperty("--accent-soft", hexToRgba(color, 0.2));
  document.body.style.setProperty("--accent", color);
  document.body.style.setProperty("--accent-soft", hexToRgba(color, 0.2));
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

function initFinalTouches() {
  footerYear.textContent = String(new Date().getFullYear());
  setTimeout(() => {
    showToast("İpucu: Ctrl/Cmd + K ile hızlı arama");
  }, 700);
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
