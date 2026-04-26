async function fetchStats() {
  const res = await fetch('/api/stats');
  if (!res.ok) throw new Error('stats endpoint failed');
  return res.json();
}

function render(stats) {
  const totalIO = stats.reduce((a, s) => a + s.io_bytes_per_second, 0);
  const avgComp = stats.length ? stats.reduce((a, s) => a + s.compression_ratio, 0) / stats.length : 1;
  document.getElementById('totalIO').textContent = totalIO.toLocaleString();
  document.getElementById('avgCompression').textContent = avgComp.toFixed(3);

  const rows = document.getElementById('rows');
  rows.innerHTML = '';
  for (const s of stats) {
    const tr = document.createElement('tr');
    const fill = Math.max(0, Math.min(100, s.estimated_fill_pct_bag || 0));
    tr.innerHTML = `
      <td>${s.shard_id}</td>
      <td>${s.lib_entries}</td>
      <td>${s.bag_entries}</td>
      <td>${s.io_bytes_per_second.toLocaleString()}</td>
      <td>${s.compression_ratio.toFixed(3)}</td>
      <td>
        <div class="bar"><span style="width:${fill}%"></span></div>
        <small>${fill.toFixed(1)}%</small>
      </td>
    `;
    rows.appendChild(tr);
  }
}

async function tick() {
  try {
    const data = await fetchStats();
    render(data);
  } catch (e) {
    console.error(e);
  }
}

setInterval(tick, 1000);
tick();
