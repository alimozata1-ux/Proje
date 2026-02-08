# C.O.M.R.A.D.E 7.1

Windows 98 temalı, DeepSeek tabanlı retro chat arayüzü.

## Kurulum

```bash
npm install
cp .env.example .env
# .env içine DEEPSEEK_API_KEY gir
npm run dev
```

Sonra `http://localhost:3000` aç.

## Özellikler

- Windows 98 benzeri tema
- Açılış (boot) ekranı
- Serious / Satire mod seçimi
- DeepSeek API üzerinden sohbet

## Not

`DEEPSEEK_API_KEY` olmadan sunucu `/api/chat` çağrısında hata döndürür.
