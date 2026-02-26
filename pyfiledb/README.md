# PyFileDB - Python Dosya Tabanlı Veritabanı Kütüphanesi

Siteler için dosya sistemi ve dış depolama aygıtına (USB, SD kart, harici disk) veri yazabilen hafif bir Python veritabanı kütüphanesi.

## Özellikler

- **Dosya Tabanlı Depolama**: JSON formatında yerel dosya sistemine veri yazar
- **Dış Depolama Desteği**: USB, SD kart, harici disk gibi aygıtlara doğrudan bağlanır
- **CRUD İşlemleri**: Insert, Select, Update, Delete tam desteği
- **Otomatik Aygıt Tespiti**: Sisteme bağlı dış depolama aygıtlarını otomatik tespit eder
- **Thread-Safe**: Çoklu iş parçacığı güvenli yazma/okuma
- **Yedekleme**: Veritabanını bir depolamadan diğerine yedekleme
- **CLI Uygulaması**: İnteraktif komut satırı arayüzü

## Kurulum

```bash
pip install -e .
```

## Kütüphane Kullanımı

### Dosya Tabanlı Veritabanı

```python
from pyfiledb import Database, FileStorage

# Dosya tabanlı veritabanı oluştur
db = Database.from_file("./veritabanim")

# Tablo oluştur ve veri ekle
kullanicilar = db.table("kullanicilar")
kullanicilar.insert({"ad": "Ali", "email": "ali@site.com", "yas": 25})
kullanicilar.insert({"ad": "Ayşe", "email": "ayse@site.com", "yas": 30})

# Kayıtları sorgula
tum_kayitlar = kullanicilar.find_all()
sonuc = kullanicilar.find({"ad": "Ali"})
genc = kullanicilar.find_where(lambda r: r.get("yas", 0) < 30)

# Güncelle
kullanicilar.update({"ad": "Ali"}, {"yas": 26})

# Sil
kullanicilar.delete({"ad": "Ali"})
```

### Dış Depolama Aygıtına Bağlanma

```python
from pyfiledb import Database, ExternalStorage

# USB/Harici disk'e bağlan
db = Database.from_external("/mnt/usb_disk")

# Artık veriler dış depolama aygıtına yazılır
urunler = db.table("urunler")
urunler.insert({"isim": "Laptop", "fiyat": 15000, "stok": 50})
```

### Bağlantı Yöneticisi

```python
from pyfiledb import ConnectionManager

manager = ConnectionManager()

# Dosyaya bağlan
db_local = manager.connect_file("yerel", "./veri")

# Dış aygıta bağlan
db_usb = manager.connect_external("usb", "/mnt/usb_disk")

# Dış aygıtları otomatik tespit et ve bağlan
manager.auto_connect_external()

# Aktif bağlantıları listele
print(manager.list_connections())
```

### Yedekleme

```python
from pyfiledb import Database, FileStorage

db = Database.from_file("./veritabanim")
# Dış depolamaya yedekle
yedek = FileStorage("/mnt/usb_disk/yedek")
db.backup(yedek)
```

## CLI Uygulaması

### Başlatma

```bash
# Dosya tabanlı
pyfiledb --dosya ./veritabanim

# Dış depolama aygıtına bağlan
pyfiledb --aygit /mnt/usb_disk

# Aygıtları tespit et
pyfiledb --tespit
```

### İnteraktif Komutlar

```
baglan dosya <yol>           Dosya tabanlı veritabanına bağlan
baglan aygit <yol>           Dış depolama aygıtına bağlan
aygitlar                     Dış depolama aygıtlarını tespit et

tablolar                     Mevcut tabloları listele
ekle <tablo> <json>          Tabloya yeni kayıt ekle
listele <tablo>              Tablodaki tüm kayıtları listele
bul <tablo> <json_sorgu>     Tabloda arama yap
guncelle <tablo> <id> <json> Kayıt güncelle
sil <tablo> <id>             Kayıt sil

bilgi                        Depolama bilgilerini göster
istatistik                   Veritabanı istatistikleri
yedekle <hedef_yol>          Veritabanını yedekle
yardim                       Yardım mesajı
cikis                        Uygulamadan çık
```

### Örnek Kullanım

```bash
$ pyfiledb --dosya ./site_veritabani

pyfiledb(local)> ekle kullanicilar {"ad": "Ali", "email": "ali@site.com"}
[OK] Kayıt eklendi. ID: abc-123-def

pyfiledb(local)> listele kullanicilar
'kullanicilar' tablosu (1 kayıt):
  {"_id": "abc-123-def", "ad": "Ali", "email": "ali@site.com", ...}

pyfiledb(local)> yedekle /mnt/usb_disk/yedek
[OK] 1 tablo yedeklendi: /mnt/usb_disk/yedek
```

## Proje Yapısı

```
pyfiledb/
├── pyfiledb/
│   ├── __init__.py      # Paket tanımı ve dışa aktarımlar
│   ├── storage.py       # Depolama arka uçları (FileStorage, ExternalStorage)
│   ├── table.py         # Tablo/Koleksiyon CRUD işlemleri
│   ├── database.py      # Ana veritabanı sınıfı
│   ├── connection.py    # Bağlantı yöneticisi
│   └── app.py           # CLI uygulaması
├── tests/
│   └── test_pyfiledb.py # Testler
├── setup.py
└── README.md
```

## Lisans

MIT
