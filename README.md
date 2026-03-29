# Arduino LCD Ekran Python Kontrolcusu

Bu proje ile bilgisayardaki Python uygulamasindan yazdiginiz metin, seri port uzerinden Arduino'ya gider ve 16x2 I2C LCD ekranda gosterilir.

## Klasor Yapisi

- `arduino_app/lcd_controller.ino`: Arduino kodu (LCD'ye yazdirma + seri haberlesme)
- `python_app/lcd_gui.py`: Python GUI uygulamasi (metin gonderme)

## Donanim Gereksinimi

- Arduino Uno/Nano (veya uyumlu kart)
- 16x2 I2C LCD (genelde adres `0x27`)
- Jumper kablo

## Baglanti (Arduino Uno)

- LCD VCC -> 5V
- LCD GND -> GND
- LCD SDA -> A4
- LCD SCL -> A5

> Not: Bazi kartlarda SDA/SCL pinleri farkli olabilir.

## Arduino Kurulumu

1. Arduino IDE'de `arduino_app/lcd_controller.ino` dosyasini acin.
2. Gerekirse `LiquidCrystal_I2C` kutuphanesini kurun.
3. Kodu karta yukleyin.
4. Baud rate: `9600`.

## Python Kurulumu

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pyserial
python python_app/lcd_gui.py
```

## Uygulama Inputlari (Girilecek Degerler)

Python uygulamasinda 2 ana input vardir:

1. **COM Port**
   - Ornek: `COM3` (Windows), `/dev/ttyUSB0` (Linux), `/dev/tty.usbserial-xxxx` (macOS)
2. **LCD Mesaji** (maksimum 32 karakter)
   - Ornek 1: `Merhaba Dunya`
   - Ornek 2: `Sicaklik: 24C Nem: 40%`
   - Ornek 3: `Satir1-16karakterSatir2-16karakter`

## Serial Uzerinden Giden Veri Formati

- Python -> Arduino: `mesaj\n`
- Arduino -> Python:
  - Acilista: `LCD_READY`
  - Yazim basariliysa: `OK`

## Kullanim

1. Python uygulamasini acin.
2. `COM Port` secin ve **Baglan** butonuna basin.
3. Metni yazin ve **LCD'ye Gonder** butonuna basin.
4. Metin LCD'de 16+16 karakter olarak 2 satira bolunerek gorunur.

## Olası Sorunlar

- Port listede yoksa USB kabloyu kontrol edin, **Yenile** butonuna basin.
- LCD bossa I2C adresiniz `0x27` degil olabilir (`0x3F` deneyin).
- Karakter sorunu varsa sadece temel ASCII ile test edin.
- **PermissionError: [Errno 13]** alirsaniz:
  - Arduino IDE/Serial Monitor kapali olsun (portu kilitlemesin).
  - Linux: `sudo usermod -a -G dialout $USER` calistirin.
  - Oturumu kapatip acin, sonra tekrar deneyin.


## vJoy Uyumlu Kullanim

Detayli vJoy konfig adimlari icin: `docs/vjoy_config.md`


Eger metni baska bir uygulamadan (vJoy ile birlikte kullandiginiz bir otomasyon/script akisi gibi) gonderecekseniz, GUI acmadan su sekilde tek komutla gonderebilirsiniz:

```bash
python python_app/lcd_gui.py --vjoy --port COM3 --text "Merhaba LCD"
```

Bu modda:
- `--port` ve `--text` zorunludur.
- Metin 32 karaktere kisilir.
- Sadece ASCII uyumlu veri gondermeniz onerilir.
