# Kivy Modern Browser

Daha düzenli ve modern bir GUI hedefiyle yeniden düzenlenmiş Kivy tabanlı masaüstü tarayıcı.

## Özellikler

- Modern ve sade ekran düzeni (kart tabanlı içerik alanı, üst araç çubukları)
- Sekmeli gezinme (yeni sekme, sekme geçişi)
- URL + arama kutusu
- Reader-mode benzeri içerik metinleştirme
- Yer imi yönetimi popup
- İndirme yöneticisi (ilerleme çubuğu)
- Paket yöneticisi (`pip install / uninstall / list`)
- Detaylı ayarlar menüsü (tema, timeout, adblock, user-agent vb.)
- Kalıcı durum dosyası (`browser_state.json`)

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
python app.py
```
