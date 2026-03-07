# Kivy Mega Browser Suite

Bu proje, Kivy ile yazılmış **modern GUI'li**, çok ekranlı, gelişmiş bir masaüstü tarayıcı örneğidir.

## Öne Çıkanlar

- Sekmeli tarayıcı akışı
- URL + arama kutusu
- Reader-mode içerik çözümleme (`requests` + `BeautifulSoup`)
- Yer imi yönetimi
- İndirme yöneticisi (progress)
- Paket yöneticisi (`pip install/uninstall/list`)
- Detaylı ayarlar menüsü (tema, timeout, adblock, user-agent, vb.)
- Çok sayıda hızlı aksiyon (otomasyon paneli)
- Kalıcı durum dosyası (`browser_state.json`)

> Not: Kullanıcı isteğine uygun olarak kod tabanı 2000+ satırın üstündedir.

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
