# Python Fotoğraflar Uygulaması+

Bu proje, Flask ile geliştirilmiş daha kapsamlı bir fotoğraf yönetim uygulamasıdır.

## Özellikler

- Fotoğraf yükleme (`png`, `jpg`, `jpeg`, `gif`, `webp`)
- Galeri listeleme
- Arama, uzantı filtresi ve sıralama
- Favori işaretleme / kaldırma
- Fotoğraf silme
- Fotoğraf detay sayfası
- JSON API: `GET /api/photos`
- 8 MB dosya yükleme sınırı
- `uploads/photos.json` ile metadata saklama

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

Sonra tarayıcıda `http://localhost:5000` adresini aç.

## API Örneği

```bash
curl http://localhost:5000/api/photos
```

## Notlar

- Üretim ortamında `app.secret_key` değeri değiştirilmeli.
- Uygulama ilk çalıştığında `uploads/photos.json` dosyası otomatik oluşturulur.
