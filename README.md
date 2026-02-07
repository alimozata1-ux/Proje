# CustomTkinter Sistem Widget

Windows 7 stiline yakın başlık çubuğu olan, %75 şeffaf, sabitlenebilir/sürüklenebilir masaüstü sistem widget'ı.

## Özellikler

- `CustomTkinter` arayüz
- `%75` şeffaflık
- AERO benzeri blur efekti (Windows'ta destek varsa)
- Windows 7 stili butonlar:
  - `✕` kapat
  - `✎` düzenle / arkaplan rengini değiştir
  - `📌` sabitle / `📍` serbest bırak
- Özel kart alanları:
  - Tarih & Saat
  - CPU
  - RAM
  - GPU
  - SSD

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install customtkinter psutil
# opsiyonel GPU detayları için
pip install gputil
```

## Çalıştırma

```bash
python widget_app.py
```

## Notlar

- `GPUtil` kurulu değilse GPU alanında "GPU bilgisi alınamadı" yazar.
- `nvidia-smi` varsa Windows üzerinde GPU fallback bilgisi alınmaya çalışılır.
