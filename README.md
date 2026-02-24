# Proje Paylaşım Sitesi (HTML + Python)

Bu uygulama, **HTML/CSS tabanlı** bir proje vitrin sitesidir. Backend tarafında Python ile admin giriş, dosya yükleme ve SQLite kayıtları yönetilir.

## Özellikler
- Vista/glass görünüme benzer arayüz.
- Ayrı HTML dosyaları (`templates/*.html`).
- Admin giriş (`/admin`) ve dosya yükleme paneli (`/admin/panel`).
- Varsayılan admin şifresi: `İazemy68`.
- Özel veritabanı katmanı: `projectdb`.

## Çalıştırma
```bash
python app.py
```

Sunucu: `http://localhost:8000`

## Şifre Değiştirme
```bash
export ADMIN_PASSWORD='yeni-sifre'
python app.py
```

## Dizin Yapısı
- `templates/`: HTML sayfaları
- `static/style.css`: arayüz stilleri
- `projectdb/`: özel Python veritabanı kütüphanesi
- `uploads/`: admin panelinden yüklenen dosyalar
