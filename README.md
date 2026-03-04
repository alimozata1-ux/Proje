# GoblinChat

GoblinChat, Node.js + Express + Socket.io + MongoDB tabanli davet kodlu grup sohbet uygulamasidir.

## Ozellikler
- Kayit: kullanici adi + sifre + davet kodu (`İAZEMY68`)
- 5 yanlis davet kodunda IP 15 dakika gecici engel
- Sifreler `bcrypt` ile hashlenir
- Gercek zamanli mesajlasma (Socket.io)
- Mesaj kaliciligi (MongoDB)
- Sohbet odalari: birden fazla oda olusturma ve secme
- Dosya gonderme: yuklenen dosyalar `/uploads` altinda servis edilir
- Mesajlarda arama kutusu
- Yaziyor gostergesi (typing indicator)
- Kullanici kendi mesajlarini silebilir
- Arayuz: sohbet sitesi benzeri modern layout + aydinlik/karanlik tema
- Giris/Kayit ve Sohbet ekranlari ayridir (`/` ve `/chat.html`)

## Klasor yapisi
- `/server` -> backend kodlari
- `/client` -> frontend dosyalari
- `package.json` -> bagimliliklar

## Kurulum
```bash
npm install
cp .env.example .env
# .env icinde MONGODB_URI ve JWT_SECRET degerlerini doldurun
npm run dev
```

Varsayilan adres: `http://localhost:3000`

## Render notu
Render HTTPS'i platform seviyesinde saglar. Uygulama `trust proxy` ile buna uygun calisir.
