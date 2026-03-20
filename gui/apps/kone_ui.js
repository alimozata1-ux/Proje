function renderTopbar(title) {
  return `
    <div class="topbar">
      <strong>${title}</strong>
      <span id="clock"></span>
    </div>
  `;
}

function renderBottomBar() {
  return `
    <div class="bottombar">
      <button class="nav-btn">◀</button>
      <button class="nav-btn">●</button>
      <button class="nav-btn">▢</button>
    </div>
  `;
}

function mountClock() {
  const tick = () => {
    const el = document.getElementById('clock');
    if (el) el.textContent = new Date().toLocaleTimeString('tr-TR');
  };
  tick();
  setInterval(tick, 1000);
}

function listToCards(items, mapFn) {
  return items.map(mapFn).join('');
}

function mountAppShell(title, sidebarHtml, panelHtml) {
  document.body.innerHTML = `
    <div class="app-shell">
      ${renderTopbar(title)}
      <div class="main">
        <aside class="sidebar">${sidebarHtml}</aside>
        <section class="panel">${panelHtml}</section>
      </div>
      ${renderBottomBar()}
    </div>
  `;
  mountClock();
}
