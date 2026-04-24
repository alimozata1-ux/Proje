const statsEl = document.getElementById("stats");
const resultEl = document.getElementById("result");

async function refreshStats() {
  const res = await fetch("/api/stats");
  const data = await res.json();
  const maxFile = Math.max(...data.map(s => s.file_size), 1);

  statsEl.innerHTML = data.map(s => {
    const pct = (s.file_size / maxFile) * 100;
    const ratio = (s.compression_ratio * 100).toFixed(1);
    return `
      <div class="row">
        <strong>Shard ${s.shard_id}</strong> | Kayıt: ${s.record_count} | Dosya: ${s.file_size} bytes | Sıkıştırma: ${ratio}%
        <div class="bar"><div style="width:${pct}%"></div></div>
      </div>`;
  }).join("");
}

document.getElementById("sendBtn").onclick = async () => {
  try {
    const payload = JSON.parse(document.getElementById("jsonInput").value);
    const res = await fetch("/api/put", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    const text = await res.text();
    resultEl.textContent = text;
    await refreshStats();
  } catch (e) {
    resultEl.textContent = e.message;
  }
};

document.getElementById("getBtn").onclick = async () => {
  const key = document.getElementById("getKey").value;
  const res = await fetch(`/api/get?key=${encodeURIComponent(key)}`);
  resultEl.textContent = await res.text();
};

document.getElementById("compactBtn").onclick = async () => {
  const res = await fetch("/api/compact", {method: "POST"});
  document.getElementById("maintenanceResult").textContent = await res.text();
  await refreshStats();
};

setInterval(refreshStats, 3000);
refreshStats();
