# BABAMIC 🎤

BABAMIC, Python + Tkinter ile yazılmış gerçek zamanlı mikrofon efekt uygulamasıdır.

## Özellikler
- Klasik **Tkinter GUI**
- Canlı efekt seçimi
- Mikrofon / hoparlör cihaz seçimi
- Peak / RMS seviye göstergesi
- Preset butonları
- 10 efekt modu:
  - Ses artırma
  - Cinnet modu
  - Cin modu
  - Mini P.E.K.K.A
  - MC köylü
  - Yüksek bass
  - Adam Kalın ses
  - Kız sesi
  - Veled sesi
  - Cızırtılı Mod

## Kurulum
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma
```bash
python babamic.py
```

## Kullanım
1. Uygulama açıldığında efekt seç.
2. Input ve output ses cihazını seç.
3. Sample rate / block size ayarla.
4. Başlat butonuna bas.
5. Sağ paneldeki sliderlar ile karakteri anlık değiştir.
6. Durdur ile akışı kapat.

## Notlar
- Linux sistemlerde PortAudio paketleri gerekebilir.
- Gecikme yüksekse block size değerini küçült (`512`, `256` gibi).
