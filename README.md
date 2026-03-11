# GoblinChat

GoblinChat, Node.js + Express + Socket.io + MongoDB tabanli davet kodlu grup sohbet uygulamasidir.

## Ozellikler
- Kayit: kullanici adi + sifre + davet kodu
- 5 yanlis davet kodunda IP 15 dakika gecici engel
- Sifreler `bcrypt` ile hashlenir
- Gercek zamanli mesajlasma (Socket.io)
- Mesaj kaliciligi (MongoDB)
- Sohbet odalari: birden fazla oda olusturma ve secme
- Dosya gonderme: yuklenen dosyalar `/uploads` altinda servis edilir
- Mesajlarda arama kutusu
- Yaziyor gostergesi (typing indicator)
- Kullanici kendi mesajlarini silebilir
- **Yeni:** kullanici kendi mesajini duzenleyebilir
- **Yeni:** oda bazli anlik cevrimici kisi sayisi
- **Yeni:** oda sessize alma (mute) ozelligi (istemci tarafi)
- Arayuz: sohbet sitesi benzeri modern layout + aydinlik/karanlik tema
- Giris/Kayit ve Sohbet tek sayfada (`/`) goruntulenir

## Klasor yapisi
- `/server` -> backend kodlari
- `/client` -> frontend dosyalari
- `package.json` -> bagimliliklar
- `netlify.toml` -> Netlify frontend deploy ayarlari
- `Dockerfile` / `docker-compose.yml` -> Docker ile calistirma

## Lokal kurulum
```bash
npm install
cp .env.example .env
# .env icinde MONGODB_URI, JWT_SECRET ve gerekiyorsa INVITE_CODE degerlerini doldurun
npm run dev
```

Varsayilan adres: `http://localhost:3000`

## Docker ile calistirma
### 1) Tek container (harici MongoDB ile)
```bash
docker build -t goblinchat .
docker run --rm -p 3000:3000 \
  -e MONGODB_URI='mongodb://host.docker.internal:27017/goblinchat' \
  -e JWT_SECRET='change-this-secret' \
  -e INVITE_CODE='change-this-invite' \
  goblinchat
```

### 2) Docker Compose (uygulama + MongoDB)
```bash
docker compose up --build
```
Uygulama: `http://localhost:3000`
MongoDB: `mongodb://localhost:27017`

## Netlify icin hazirlama
> Onemli: Netlify Node Socket.io sunucusunu host etmez. Backend'i Render/Railway/Fly.io gibi bir platformda ayri calistirmalisin.

1. Backend'i deploy et (ornek: `https://goblinchat-api.onrender.com`).
2. `client/config.js` dosyasini backend adresine gore guncelle:
   ```js
   window.GOBLINCHAT_CONFIG = {
     API_BASE: 'https://goblinchat-api.onrender.com',
     SOCKET_URL: 'https://goblinchat-api.onrender.com'
   };
   ```
3. Netlify'da yeni site olustur ve bu repoyu bagla.
4. Build ayarlari:
   - Build command: (bos birakilabilir)
   - Publish directory: `client`
5. Deploy et.

## Render notu
Render HTTPS'i platform seviyesinde saglar. Uygulama `trust proxy` ile buna uygun calisir.
