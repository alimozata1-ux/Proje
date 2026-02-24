# Proje Paylaşım Sitesi

Bu uygulama, projeleri vitrin şeklinde gösteren ve admin panelinden dosya yüklemeye izin veren bir Python web sitesidir.

## Özellikler
- Paylaştığın görsele benzer cam (glass) tarzı arayüz.
- Proje kartları ve indirme butonları.
- Admin girişi (varsayılan şifre: `İazemy68`).
- Admin panelinden dosya yükleme ve proje oluşturma.
- Özel Python veritabanı katmanı: `projectdb`.
- Harici framework bağımlılığı yok.

## Çalıştırma
```bash
python app.py
```

Sunucu varsayılan olarak `http://localhost:8000` adresinde çalışır.

## Admin
- Giriş adresi: `/admin`
- Şifreyi değiştirmek için ortam değişkeni kullanabilirsiniz:
```bash
export ADMIN_PASSWORD='yeni-sifre'
```

## Özel Veritabanı Kütüphanesi
`projectdb/client.py` içindeki `ProjectDatabase` sınıfı:
- tablo oluşturur,
- proje ekler,
- projeleri listeler,
- indirme sayısını arttırır.
