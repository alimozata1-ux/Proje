<?php
declare(strict_types=1);
?>
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Mohittin Abi B.A.Z.A.R</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <div id="wallpaper" class="wallpaper wallpaper--preset-a"></div>

    <header class="hero">
      <div class="hero__overlay"></div>
      <div class="hero__content">
        <p class="hero__badge">ATÖLYE PAYLAŞIM MERKEZİ</p>
        <h1>Mohittin Abi B.A.Z.A.R</h1>
        <p class="hero__subtitle">PHP altyapılı paylaşım sitesi (Netlify için statik+harici PHP API mimarisiyle uyumlu).</p>
        <div class="hero__meta">
          <span>Admin: alimozata1@gmail.com</span>
          <span id="coverLabel">Kapak: Dijital Atölye Neon</span>
          <span>Mod: PHP + JSON Storage</span>
        </div>
      </div>
    </header>

    <main class="layout">
      <section class="workspace">
        <div class="toolbar">
          <div class="tab-row">
            <button class="tab is-active" data-tab="schematics">Arduino Şemaları</button>
            <button class="tab" data-tab="codes">Kodlar</button>
            <button class="tab" data-tab="apps">Uygulamalar</button>
            <button class="tab" data-tab="announcements">Önceden Haber Verme</button>
          </div>

          <label class="inline-field">
            <span>Ara</span>
            <input id="searchInput" type="search" placeholder="Başlık veya içerik ara" />
          </label>
        </div>

        <section class="panel panel--content">
          <div class="content-header">
            <div>
              <h2 id="activeTabTitle">Arduino Şemaları</h2>
              <p id="activeTabDescription" class="muted">Bağlantı planları ve pin dizilimleri.</p>
            </div>
            <div class="content-header__stats">
              <span id="countTotal">Toplam: 0</span>
              <span id="countShown">Gösterilen: 0</span>
            </div>
          </div>
          <div id="cardsContainer" class="cards"></div>
        </section>
      </section>

      <aside class="panel panel--admin">
        <h2>Admin Paneli</h2>
        <p class="muted">Özel kodla admin girişi (PHP session).</p>

        <div id="authCard" class="stack">
          <label>E-posta</label>
          <input id="emailInput" type="email" placeholder="ornek@mail.com" />

          <label>Kod</label>
          <input id="codeInput" type="text" maxlength="6" placeholder="6 haneli kod" />

          <div class="row">
            <button id="sendCodeBtn" class="btn">Kod Gönder</button>
            <button id="loginBtn" class="btn btn--secondary">Giriş</button>
          </div>
          <p id="authStatus" class="status"></p>
        </div>

        <form id="postForm" class="stack hidden">
          <label>Sekme</label>
          <select id="postTab">
            <option value="schematics">Arduino Şemaları</option>
            <option value="codes">Kodlar</option>
            <option value="apps">Uygulamalar</option>
            <option value="announcements">Önceden Haber Verme</option>
          </select>

          <label>Başlık</label>
          <input id="postTitle" type="text" required />

          <label>Özet</label>
          <input id="postSummary" type="text" />

          <label>İçerik</label>
          <textarea id="postContent" rows="6" required></textarea>

          <label>Kod</label>
          <textarea id="postCode" rows="5"></textarea>

          <label>Görsel URL</label>
          <input id="postImage" type="url" />

          <label>Etiketler (virgül)</label>
          <input id="postTags" type="text" />

          <div class="row">
            <label class="check-field"><input id="postPinned" type="checkbox" /> <span>Sabit</span></label>
            <label class="check-field"><input id="postNotify" type="checkbox" checked /> <span>Bildirim</span></label>
          </div>

          <fieldset>
            <legend>Yayın Türü</legend>
            <label class="check-field"><input type="radio" name="postType" value="normal" checked /> <span>Normal</span></label>
            <label class="check-field"><input type="radio" name="postType" value="scheduled" /> <span>Zamanlı</span></label>
          </fieldset>

          <label>Zamanlama</label>
          <input id="postSchedule" type="datetime-local" />

          <div class="row">
            <button type="submit" class="btn">Yayınla</button>
            <button id="logoutBtn" type="button" class="btn btn--ghost">Çıkış</button>
          </div>
          <p id="postStatus" class="status"></p>
        </form>
      </aside>
    </main>

    <template id="cardTemplate">
      <article class="card">
        <header class="card__header">
          <h3 class="card__title"></h3>
          <div class="badges">
            <span class="badge badge--pinned hidden">Sabit</span>
            <span class="badge badge--scheduled hidden">Zamanlı</span>
          </div>
        </header>
        <p class="card__summary"></p>
        <p class="card__content"></p>
        <pre class="card__code hidden"></pre>
        <img class="card__image hidden" alt="Görsel" />
        <footer class="card__footer">
          <div class="tags"></div>
          <small class="card__date"></small>
        </footer>
      </article>
    </template>

    <script>window.API_BASE = './api';</script>
    <script src="app.js"></script>
  </body>
</html>
