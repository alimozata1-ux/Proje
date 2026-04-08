const CHANNEL_HANDLE = "@Mohittin_Abi_Yazılım-t6v";
const API_URL = `https://yt.lemnoslife.com/noKey/channels?part=statistics&forHandle=${encodeURIComponent(CHANNEL_HANDLE)}`;

const countEl = document.getElementById("subscriberCount");
const statusEl = document.getElementById("statusMessage");
const refreshBtn = document.getElementById("refreshBtn");

const numberFormatter = new Intl.NumberFormat("tr-TR");

async function loadSubscriberCount() {
  statusEl.classList.remove("error");
  statusEl.textContent = "Güncel abone sayısı alınıyor...";

  try {
    const response = await fetch(API_URL, { cache: "no-store" });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const count = data?.items?.[0]?.statistics?.subscriberCount;

    if (!count) {
      throw new Error("Abone sayısı bulunamadı.");
    }

    const formattedCount = numberFormatter.format(Number(count));
    countEl.textContent = formattedCount;

    const now = new Date();
    const timeText = now.toLocaleTimeString("tr-TR", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
    statusEl.textContent = `Son güncelleme: ${timeText}`;
  } catch (error) {
    countEl.textContent = "--";
    statusEl.classList.add("error");
    statusEl.textContent = `Veri alınamadı (${error.message}).`;
  }
}

refreshBtn.addEventListener("click", loadSubscriberCount);
loadSubscriberCount();

setInterval(loadSubscriberCount, 30_000);
