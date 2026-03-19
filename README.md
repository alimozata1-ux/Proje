# Python Sistem İzleyici (CLI + HTML GUI)

Bu proje gerçek sistem verilerini izler:
- SSD / HDD / NVMe (M.2 olası) takılı mı
- USB bellek takılı mı
- SD kart takılı mı
- CPU / RAM / GPU kullanım durumu
- Disk okuma/yazma hızları (MB/s)
- Eşik aşımlarında uyarı üretimi

## Kurulum

```bash
pip install psutil
# Opsiyonel GPU takibi için:
pip install gputil
```

## CLI Çalıştırma

Tek sefer ölçüm:
```bash
python3 system_monitor.py
```

JSON çıktı:
```bash
python3 system_monitor.py --json
```

Sürekli izleme (her 5 saniye):
```bash
python3 system_monitor.py --watch 5
```

## HTML GUI Çalıştırma

```bash
python3 dashboard_server.py --host 127.0.0.1 --port 8080
```

Ardından tarayıcıdan aç:

```text
http://127.0.0.1:8080
```

GUI özellikleri:
- Gerçek veriler `/api/snapshot` endpoint’inden çekilir.
- Kart tasarımında şeffaf cam (glassmorphism) efekti vardır.
- Paylaştığın PNG’lere uygun olarak hazırlanmış SVG ikonlar kullanılır (`web/static/icons/*.svg`).

## Notlar

- Disk türü tespiti Linux üzerinde `/sys/class/block` üzerinden yapılır.
- NVMe tespiti, cihaz adından yapılır (`nvme*`) ve genellikle M.2 form faktörünü işaret eder.
- GPU bilgisi için önce `nvidia-smi`, yoksa `GPUtil` denenir.
