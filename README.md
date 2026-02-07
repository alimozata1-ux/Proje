# HTML Studio (CustomTkinter)

Bu proje, **CustomTkinter arayüzlü** bir HTML editör + canlı önizleme uygulamasıdır.

## Özellikler

- Modern masaüstü arayüz (CustomTkinter)
- HTML dosyasını editörde açma/düzenleme/kaydetme
- Canlı önizleme sunucusu (`/preview`, `/raw`, `/events`)
- Kod değiştiğinde tarayıcı önizlemesinin otomatik yenilenmesi
- Oto kaydet (toggle)
- Tek tıkla yedek alma (`backups/` klasörü)
- Hazır şablonlar (Boş, Kart, Landing)
- Kelime + karakter sayacı
- Koyu/Açık tema değiştirme
- Son kullanılan ayarları `.html_studio_settings.json` dosyasında saklama

## Kurulum

```bash
python3 -m pip install customtkinter
```

## Çalıştırma

```bash
python3 app.py target.html --host 127.0.0.1 --port 8000
```

## Kullanım Akışı

1. Uygulama açıldığında `target.html` editörde yüklenir.
2. **Önizleme Başlat** ile yerel sunucuyu ayağa kaldırın.
3. **Tarayıcıda Aç** ile canlı sayfayı görüntüleyin.
4. Editörde değişiklik yaptıkça oto kaydet aktifse dosya kaydedilir ve önizleme otomatik yenilenir.

## Not

Canlı önizleme için tarayıcı adresi:

- `http://127.0.0.1:8000/preview`
