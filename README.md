# Go MCU Emulator (Educational Starter)

Bu proje, modüler bir MCU emülatörü için başlangıç iskeletidir.

## 1) Mimari Plan
Detaylar için: `ARCHITECTURE.md`

## 2) Dosya Yapısı

```text
.
├── main.go
├── cpu/cpu.go
├── ram/ram.go
├── bus/bus.go
├── pins/pins.go
├── led/led.go
├── button/button.go
├── screen/screen.go
├── adc/adc.go
├── dac/dac.go
├── timer/timer.go
├── loader/loader.go
├── emulator/emulator.go
├── gui/gui.go
└── peripheral/peripheral.go
```

## 3) Adım Adım Bileşenler
1. `ram`: 1 MB segmentli bellek
2. `bus`: 16/32-bit bus erişimi
3. `cpu`: instruction decode ve core state
4. `emulator`: fetch/decode/execute, step/run/pause/reset, debug noktaları
5. `peripheral` + `led/button/screen/adc/dac`: IO birimleri
6. `loader`: `.bin`, `.hex`, pseudo `.c` yükleme
7. `gui`: core'dan ayrı tutulan sunum katmanı (şu an stub)
8. `main.go`: tüm parçaları birleştiren örnek uygulama

## 4) Çalıştırma

```bash
go run .
```

Program dosyasıyla:

```bash
go run . ./program.hex
```

## 5) Windows EXE Derleme

Windows `.exe` almak için:

```bat
build_windows.bat
```

Özel çıktı adıyla:

```bat
build_windows.bat mcu_emulator.exe
```

## 6) Not
Bu sürüm eğitim amaçlıdır; instruction formatı ve pseudo-C yükleyici sade tutulmuştur.
