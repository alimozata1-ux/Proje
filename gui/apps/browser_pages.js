window.KONE_BROWSER_PAGES = {
  "kone://home": {
    title: "KONE Home",
    html: `
      <h2>KONE Browser Ana Sayfa</h2>
      <p>Hızlı erişim:</p>
      <ul>
        <li><a href="#" data-link="kone://docs">KONE Docs</a></li>
        <li><a href="#" data-link="kone://store">KONE Store</a></li>
        <li><a href="#" data-link="kone://news">KONE News</a></li>
      </ul>
    `
  },
  "kone://docs": {
    title: "KONE Docs",
    html: `
      <h2>Dokümantasyon</h2>
      <p>Kernel API, KFS ve GUI API dökümanları burada.</p>
      <pre>zk_window_create(title, x, y, w, h)\nipc_send(msg)\nkfs_create(name, data, len)</pre>
    `
  },
  "kone://store": {
    title: "KONE Store",
    html: `
      <h2>Uygulama Mağazası</h2>
      <table class="table">
        <tr><th>Uygulama</th><th>Sürüm</th><th>Durum</th></tr>
        <tr><td>Paint Lite</td><td>1.0</td><td>Yüklenebilir</td></tr>
        <tr><td>KNotes</td><td>2.1</td><td>Yüklü</td></tr>
        <tr><td>Music Box</td><td>0.9</td><td>Güncelleme var</td></tr>
      </table>
    `
  },
  "kone://news": {
    title: "KONE News",
    html: `
      <h2>KONE News</h2>
      <article><h4>KONE OS Build 42</h4><p>Yeni compositor optimizasyonları eklendi.</p></article>
      <article><h4>Browser App Beta</h4><p>Sekmeler, geçmiş ve indirme yöneticisi aktif.</p></article>
    `
  },
  "kone://devtools": {
    title: "DevTools",
    html: `
      <h2>Geliştirici Araçları</h2>
      <div class="log" id="devtools-log">[devtools] hazır...</div>
    `
  }
};
