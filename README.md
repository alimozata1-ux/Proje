# Python Sistem Widget

Bu uygulama masaüstünde çalışan, sürüklenebilir/sabitlenebilir bir widget sağlar:

- Saat ve tarih
- CPU kullanım yüzdesi
- RAM kullanım durumu
- SSD (disk) kullanım durumu
- `%75` şeffaf pencere
- Kırmızı `X` kapatma tuşu
- Arkaplan renk değiştirme (`🎨`)
- Sabitleme / sürüklenebilirlik (`📌`)

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install psutil
```

## Çalıştırma

```bash
python widget_app.py
```

## Kontroller

- `X`: Uygulamayı kapatır.
- `📌`: Widget sabitleme durumunu değiştirir.
  - Sabit (`📌`) iken taşınmaz.
  - Serbest (`📍`) iken fare ile sürüklenebilir.
- `🎨`: Arkaplan rengini değiştirir.
