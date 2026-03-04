# GoblinChat

GoblinChat, Node.js + Express + Socket.io + MongoDB tabanli davet kodlu grup sohbet uygulamasidir.

## Ozellikler
- Kayit: kullanici adi + sifre + davet kodu (`İAZEMY68`)
- 5 yanlis davet kodunda IP 15 dakika gecici engel
- Sifreler `bcrypt` ile hashlenir
- Gercek zamanli mesajlasma (Socket.io)
- Mesaj kaliciligi (MongoDB)
- Sohbetler bolumu: birden fazla sohbet odasi olusturma ve secme
- Dosya gonderme: yuklenen dosyalar `/uploads` altinda servis edilir
- Arayuz: sade tasarim + aydinlik/karanlik tema secenegi
- Giris/Kayit ve Sohbetler sayfasi birbirinden ayridir (`/` ve `/chat.html`)
- Yeni: mesajlarda arama kutusu
- Yeni: yaziyor gostergesi (typing indicator)
- Yeni: kullanici kendi mesajlarini silebilir

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
