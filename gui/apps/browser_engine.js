(function(){
  const state = {
    tabs: [
      { id: 1, url: 'kone://home', title: 'KONE Home' }
    ],
    activeTab: 1,
    history: [],
    bookmarks: [
      { title: 'KONE Home', url: 'kone://home' },
      { title: 'KONE Docs', url: 'kone://docs' },
      { title: 'KONE Store', url: 'kone://store' }
    ],
    downloads: []
  };

  function byId(id){ return document.getElementById(id); }
  function activeTab(){ return state.tabs.find(t=>t.id===state.activeTab); }

  function renderTabs() {
    const root = byId('tabs');
    root.innerHTML = state.tabs.map(t =>
      `<button class="badge" data-tab="${t.id}" style="margin-right:6px;${t.id===state.activeTab?'border-color:#5da8ff':''}">${t.title}</button>`
    ).join('') + '<button class="button" id="new-tab">+ Yeni Sekme</button>';

    root.querySelectorAll('[data-tab]').forEach(btn => {
      btn.onclick = () => {
        state.activeTab = Number(btn.getAttribute('data-tab'));
        renderAll();
      };
    });

    byId('new-tab').onclick = () => {
      const nextId = Math.max(...state.tabs.map(t=>t.id)) + 1;
      state.tabs.push({ id: nextId, url: 'kone://home', title: 'Yeni Sekme' });
      state.activeTab = nextId;
      renderAll();
    };
  }

  function openUrl(url, pushHistory = true) {
    const page = window.KONE_BROWSER_PAGES[url] || {
      title: '404',
      html: `<h2>Sayfa bulunamadı</h2><p>${url}</p>`
    };

    const tab = activeTab();
    tab.url = url;
    tab.title = page.title;

    byId('address').value = url;
    byId('page').innerHTML = page.html;

    if (pushHistory) {
      state.history.unshift({
        at: new Date().toLocaleTimeString('tr-TR'),
        title: page.title,
        url
      });
      if (state.history.length > 200) state.history.pop();
    }

    byId('page').querySelectorAll('[data-link]').forEach(link => {
      link.onclick = (e) => {
        e.preventDefault();
        openUrl(link.getAttribute('data-link'));
      };
    });

    renderTabs();
    renderSidebar();
  }

  function renderSidebar() {
    byId('history').innerHTML = state.history.slice(0, 25).map(h =>
      `<div class="card"><small>${h.at}</small><br><a href="#" data-href="${h.url}">${h.title}</a></div>`
    ).join('');

    byId('bookmarks').innerHTML = state.bookmarks.map(b =>
      `<div class="card"><a href="#" data-bm="${b.url}">${b.title}</a></div>`
    ).join('');

    byId('downloads').innerHTML = state.downloads.length
      ? state.downloads.map(d => `<div class="card">${d.name} - ${d.progress}%</div>`).join('')
      : '<div class="card">İndirme yok</div>';

    byId('history').querySelectorAll('[data-href]').forEach(a => {
      a.onclick = (e) => { e.preventDefault(); openUrl(a.getAttribute('data-href'), false); };
    });
    byId('bookmarks').querySelectorAll('[data-bm]').forEach(a => {
      a.onclick = (e) => { e.preventDefault(); openUrl(a.getAttribute('data-bm')); };
    });
  }

  function fakeDownload() {
    const id = state.downloads.length + 1;
    const item = { name: `package_${id}.app`, progress: 0 };
    state.downloads.unshift(item);
    const timer = setInterval(() => {
      item.progress += 10;
      renderSidebar();
      if (item.progress >= 100) clearInterval(timer);
    }, 200);
  }

  function renderAll() {
    renderTabs();
    openUrl(activeTab().url, false);
  }

  window.KoneBrowser = {
    init() {
      byId('go').onclick = () => openUrl(byId('address').value.trim() || 'kone://home');
      byId('address').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') byId('go').click();
      });
      byId('add-bookmark').onclick = () => {
        const t = activeTab();
        state.bookmarks.unshift({ title: t.title, url: t.url });
        renderSidebar();
      };
      byId('fake-download').onclick = fakeDownload;
      byId('open-devtools').onclick = () => openUrl('kone://devtools');
      renderAll();
    }
  };
})();
