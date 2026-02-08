const root = document.documentElement;
const webFrame = document.getElementById("webFrame");
const urlInput = document.getElementById("urlInput");
const goBtn = document.getElementById("goBtn");
const neonColor = document.getElementById("neonColor");
const intensity = document.getElementById("intensity");
const favoriteList = document.getElementById("favoriteList");

const favorites = [];

function navigate() {
  const raw = urlInput.value.trim();
  if (!raw) return;

  const normalized = raw.startsWith("http") ? raw : `https://${raw}`;
  webFrame.src = normalized;
}

function updateGlow() {
  const neon = neonColor.value;
  const glowStrength = Number(intensity.value);

  root.style.setProperty("--neon", neon);
  root.style.setProperty(
    "--glow",
    `0 0 ${Math.max(3, Math.floor(glowStrength / 12))}px ${neon}, 0 0 ${Math.floor(
      glowStrength / 3
    )}px color-mix(in srgb, ${neon}, transparent 35%)`
  );
}

function renderFavorites() {
  favoriteList.innerHTML = "";
  favorites.forEach((item) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.textContent = item;
    btn.addEventListener("click", () => {
      urlInput.value = item;
      navigate();
    });
    li.appendChild(btn);
    favoriteList.appendChild(li);
  });
}

goBtn.addEventListener("click", navigate);
urlInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") navigate();
});

neonColor.addEventListener("input", updateGlow);
intensity.addEventListener("input", updateGlow);

document.getElementById("refreshBtn").addEventListener("click", () => {
  webFrame.src = webFrame.src;
});

document.getElementById("backBtn").addEventListener("click", () => {
  window.alert("Demo arayüzünde geri geçmişi iframe kısıtı nedeniyle sınırlı.");
});

document.getElementById("forwardBtn").addEventListener("click", () => {
  window.alert("Demo arayüzünde ileri geçmişi iframe kısıtı nedeniyle sınırlı.");
});

document.getElementById("focusBtn").addEventListener("click", () => {
  document.body.classList.toggle("focus-mode");
});

document.getElementById("splitBtn").addEventListener("click", () => {
  document.body.classList.toggle("split-mode");
});

document.getElementById("saveFavorite").addEventListener("click", () => {
  const val = urlInput.value.trim();
  if (!val) return;
  if (!favorites.includes(val)) favorites.push(val);
  renderFavorites();
});

document.getElementById("clearFavorite").addEventListener("click", () => {
  favorites.length = 0;
  renderFavorites();
});

updateGlow();
navigate();
