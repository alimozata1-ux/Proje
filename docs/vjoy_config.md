# vJoy Konfigurasyonu (LCD Projesi Icin)

Bu dokuman, `python_app/lcd_gui.py --vjoy` modunu vJoy + otomasyon araclari ile kullanmak icin hazir ayarlari verir.

## 1) vJoy Device Ayari

vJoyConf uygulamasinda:

- Enable vJoy: **Acik**
- Device Number: **1**
- Buttons: **8** (minimum 4)
- Axes: **Kapali** (LCD metin gonderimi icin gerekmez)
- POV: **Kapali**

> Not: Sadece buton tetiklemek yeterli oldugu icin eksen tanimlamasi zorunlu degildir.

## 2) Projedeki CLI Modunu Dogrulama

Asagidaki komutla dogrudan test edin:

```bash
python python_app/lcd_gui.py --vjoy --port COM3 --text "TEST MESAJI"
```

Beklenen:
- Arduino READY satiri gelir.
- Arduino RESP satiri `OK` olur.

## 3) Buton-Mesaj Esleme Plani

vJoy butonlarini otomasyon aracinda su sekilde komutlara baglayin:

- BTN1 -> `python python_app/lcd_gui.py --vjoy --port COM3 --text "Sistem Hazir"`
- BTN2 -> `python python_app/lcd_gui.py --vjoy --port COM3 --text "Yaris Basladi"`
- BTN3 -> `python python_app/lcd_gui.py --vjoy --port COM3 --text "Pit Stop"`
- BTN4 -> `python python_app/lcd_gui.py --vjoy --port COM3 --text "Yavasla"`
- BTN5 -> `python python_app/lcd_gui.py --vjoy --port COM3 --text "Tur Tamamlandi"`

## 4) UCR (Universal Control Remapper) ile Kurulum

1. UCR'de vJoy Device 1 secin.
2. Her buton icin `Execute Command` (veya benzeri komut calistirma plugini) ekleyin.
3. Komut olarak yukaridaki `python ... --vjoy --port ... --text ...` satirlarini girin.
4. Profil kaydedin ve etkinlestirin.

## 5) Karakter / Uzunluk Kurali

- Metin maksimum **32 karakter** olmalidir.
- En stabil sonuc icin ASCII metin kullanin (Turkce karakter yerine sade karakter).

## 6) Sorun Giderme

- `PermissionError [Errno 13]`: Port baska uygulama tarafindan kullaniliyor olabilir (Arduino IDE Serial Monitor'u kapatin).
- COM port degistiyse komutlardaki `COM3` degerini guncelleyin.
- Hic yazi gelmiyorsa baud rate'in 9600 oldugunu kontrol edin.
