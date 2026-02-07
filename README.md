# CustomTkinter Sistem Widget

Windows 7 / AERO görünümüne yakın, %75 şeffaf, masaüstüne özel sistem widget'ı.

## Özellikler

- `CustomTkinter` arayüz
- `%75` şeffaflık
- AERO benzeri blur/acrylic efekt denemesi (Windows)
- Daha belirgin (kalın) yazılar ve kompakt kart alanları
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
- **Sadece masaüstü odaktayken görünür** (Windows'ta `Progman/WorkerW` kontrolü)

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

- `GPUtil` kurulu değilse GPU için `nvidia-smi` fallback denenir.
- Destek yoksa GPU alanında `GPU bilgisi yok` yazısı gösterilir.
- AERO efekt API'leri Windows sürümüne göre değişebileceği için bazı sistemlerde etkisiz kalabilir.
