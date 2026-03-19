# Python Sistem İzleyici (CLI + HTML GUI)

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
```

> `psutil` kurulu değilse uygulama Linux üzerinde `/proc` fallback ile çalışmaya devam eder.

## GUI Çalıştırma

```bash
python3 dashboard_server.py --host 127.0.0.1 --port 8080
```

Tarayıcı:
```text
http://127.0.0.1:8080
```

## CLI Çalıştırma

```bash
python3 system_monitor.py
python3 system_monitor.py --json
python3 system_monitor.py --watch 5
```

## Notlar

- SVG ikonlar `web/static/icons/` altında tutulur ve GUI’de kullanılır.
- GUI kartlarında şeffaf cam (glassmorphism) efekti vardır.
- Disk türü Linux üzerinde `/sys/class/block` ile tespit edilir.
