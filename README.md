# Python Sistem İzleyici (CLI + Custom Tkinter GUI)

Bu proje gerçek sistem verilerini izler:
- SSD / HDD / NVMe (M.2 olası) takılı mı
- USB bellek takılı mı
- SD kart takılı mı
- CPU / RAM / GPU kullanım durumu
- Disk okuma/yazma hızları (MB/s)
- Eşik aşımlarında uyarı üretimi

## Kurulum

Tercihen:
```bash
pip install psutil
# Opsiyonel GPU takibi için:
pip install gputil
# SVG ikonları tkinter içinde görüntülemek için opsiyonel:
pip install cairosvg pillow
```

> `psutil` kurulu değilse uygulama Linux üzerinde `/proc` fallback ile çalışmaya devam eder.

## Custom Tkinter GUI Çalıştırma

```bash
python3 tkinter_gui.py
```

## CLI Çalıştırma

```bash
python3 system_monitor.py
python3 system_monitor.py --json
python3 system_monitor.py --watch 5
```

## Notlar

- HTML GUI kaldırıldı; yerine tamamen custom tkinter arayüzü eklendi.
- SVG ikonlar `web/static/icons/` altında tutulur ve tkinter GUI tarafından kullanılır.
- `cairosvg+pillow` yoksa uygulama SVG dosyalarını yine okuyup metin fallback gösterir.
- Disk türü Linux üzerinde `/sys/class/block` ile tespit edilir.
