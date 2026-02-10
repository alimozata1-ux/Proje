# MCU Emulator Architecture Plan

## 1) Hedef
Bu proje; kullanıcıya kendi MCU benzeri sistemi tasarlama, kod yükleme ve çevresel birimleri (LED, Button, Screen, ADC/DAC) emüle etme imkanı verir.

## 2) Katmanlar

1. **Core Emulation Layer (GUI'den bağımsız)**
   - `cpu`: instruction set, register dosyası, çok çekirdek
   - `ram`: 1 MB segmentli RAM
   - `bus`: 16-bit/32-bit veri yolu
   - `timer`: tick ve interrupt
   - `emulator`: fetch/decode/execute döngüsü, step/run/pause/reset
2. **I/O and Peripheral Layer**
   - `pins`, `led`, `button`, `screen`, `adc`, `dac`, `peripheral`
3. **Program Loading Layer**
   - `loader`: `.bin`, `.hex`, basit C benzeri yükleme
4. **Presentation Layer**
   - `gui`: GUI entegrasyon noktaları (şu an eğitim amaçlı stub)

## 3) Veri Akışı
- Loader programı RAM'e yazar.
- CPU çekirdekleri Bus aracılığıyla RAM/IO alanına erişir.
- Emulator her adımda instruction fetch eder, decode/execute yapar.
- Timer belirli tick aralıklarında interrupt request üretir.
- Peripheral'lar pin değerleri ve bellek map'i üzerinden senkronize olur.

## 4) Bellek Segmentleri (1 MB)
- `data` : global initialized data
- `bss`  : global uninitialized data
- `heap` : dinamik alan
- `stack`: çağrı yığını (üst adresten aşağı)

## 5) Genişletilebilirlik
- Tüm çevresel birimler `peripheral.Device` arayüzünü uygular.
- Yeni bir bileşen, bus/ram/pin altyapısına dokunmadan eklenebilir.
- GUI katmanı emulator core’a interface üzerinden bağlanır.
