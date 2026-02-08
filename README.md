# Windows 7 Benzeri Python Simülatör

Bu proje, **Python + PySide6** ile hazırlanmış basit bir Windows 7 görünümlü masaüstü simülatörüdür.

## Özellikler
- Windows 7 tarzı mavi masaüstü + görev çubuğu
- Başlat menüsü (QMenu)
- Masaüstü ikonları (Belgeler / Resimler / Tarayıcı)
- Hızlı erişim butonları
- Saat + tarih alanı

## İkon Paketi
İkonlar için **qtawesome** paketi kullanıldı. Bu paket Font Awesome ikonlarını Python Qt uygulamalarında kolayca kullanmayı sağlıyor.

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
