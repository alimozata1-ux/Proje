# Neon Aero Browser (Python)

Modern görünümlü, neon çizgili ve detaylı ayar paneline sahip örnek bir Python masaüstü tarayıcısı.

## Özellikler

- Araç çubuğu için `%75` varsayılan şeffaflık (ayarlar ekranından değiştirilebilir)
- Aero benzeri yarı saydam görünüm
- Neon çerçeve ve parlama efekti
- Neon çizgi rengini ayarlardan değiştirme
- Detaylı ayarlar:
  - Şeffaflık
  - Neon kalınlığı
  - Neon parlama yoğunluğu
  - Köşe yuvarlaklığı
  - Anasayfa
  - Arama motoru şablonu
- Ayarlar `settings.json` dosyasına kalıcı olarak kaydedilir

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

> Not: `QWebEngineView` kullandığı için sisteminizde grafik ortamı gerekir.
