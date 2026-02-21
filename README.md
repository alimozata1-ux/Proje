# Python Fotoğraflar Uygulaması+

Bu proje artık iki arayüz sunar:
- Flask ile web arayüzü
- Tkinter ile masaüstü GUI arayüzü

## Özellikler

- Fotoğraf yükleme (`png`, `jpg`, `jpeg`, `gif`, `webp`)
- Galeri listeleme
- Arama, uzantı filtresi ve sıralama
- Favori işaretleme / kaldırma
- Fotoğraf silme
- Fotoğraf detay sayfası (web)
- JSON API: `GET /api/photos` (web)
- Masaüstü GUI: tablo görünümü, istatistik, önizleme, favori/silme işlemleri
- 8 MB web yükleme sınırı
- `uploads/photos.json` ile metadata saklama

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Web Arayüzünü Çalıştırma

```bash
python app.py
```

Tarayıcıda `http://localhost:5000` adresini aç.

## Masaüstü GUI Çalıştırma

```bash
python gui_app.py
```

## API Örneği

```bash
curl http://localhost:5000/api/photos
```

## Notlar

- Üretim ortamında `app.secret_key` değeri değiştirilmeli.
- Uygulama ilk çalıştığında `uploads/photos.json` dosyası otomatik oluşturulur.
- GUI önizleme için Pillow kullanır; önizleme yüklenemezse uygulama çalışmaya devam eder.
