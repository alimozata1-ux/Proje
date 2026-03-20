# BABAMIC 🎤

Python ile yazılmış gerçek zamanlı mikrofon efekt uygulaması.

## Özellikler
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

## Kullanım
Efektleri listele:
```bash
python babamic.py --list
```

Uygulamayı belirli efektle başlat:
```bash
python babamic.py --effect "Kız sesi"
```

Varsayılan efekt `Ses artırma`.

## Not
- Mikrofon girişin ve hoparlör çıkışın açık olmalı.
- Gecikmeyi azaltmak için `--blocksize 512` veya `--blocksize 256` deneyebilirsin.
