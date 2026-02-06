# MCU Architecture Designer & Emulator (Windows / C++17)

Bu proje, tamamen yazılım tabanlı bir mikrodenetleyici (MCU) iç mimarisi modelleme ve emülasyon uygulamasıdır.

## Mimari Plan (Ön Tasarım)

Aşağıdaki yapı ile **GUI** ve **emülasyon mantığı** ayrılmıştır:

1. **Donanım Soyutlama Katmanı**
   - `ALU`: ADD/SUB gibi aritmetik işlemler
   - `RAM`: En fazla 128 KB veri belleği
   - `ROM`: Program belleği (flash)
   - `Bus`: Data / Address / Control bus durumları
   - `Pins`: GPIO pinleri, yön ve durum
   - `Clock`: Saat çevrimi, reset/power durumu

2. **CPU Katmanı**
   - `CPU`: Register file, PC, instruction decoder, fetch→decode→execute
   - Temel komut kümesi: `LOAD, STORE, ADD, SUB, JMP, JZ, NOP, HALT`

3. **MCU Kompozisyonu**
   - `MCU`: CPU + bellek + bus + pin + clock + basit periferler (timer, interrupt controller, UART durum yapısı)

4. **Kod Yükleme Katmanı**
   - `Loader`: `.bin` ve basit Intel HEX (`.hex`) okuma
   - ROM’a başlangıç adresiyle yükleme
   - Boyut/adres sınır kontrolü

5. **Emülasyon Orkestrasyonu**
   - `Emulator`: Run / Step / Pause / Reset kontrolü
   - Clock cycle takibi

6. **GUI Katmanı (WinAPI)**
   - `GUI`: Sade teknik arayüz
   - Blok diyagram çizimi (GDI)
   - Run/Step/Pause/Reset butonları
   - Register, PC, aktif komut, RAM ve pin durumu canlı izleme

## Komut Kodlaması (4-byte sabit)

Her komut 4 byte olarak yorumlanır:

- `byte0`: opcode
- `byte1`: operand A (çoğunlukla register index)
- `byte2`: operand B (register index veya adres üst byte)
- `byte3`: operand C (imm veya adres alt byte)

Adres: `((byte2 << 8) | byte3)`

Opcode tablosu:
- `0x00` NOP
- `0x10` LOAD  `R[a] <- RAM[addr]`
- `0x11` STORE `RAM[addr] <- R[a]`
- `0x20` ADD   `R[a] <- R[a] + R[b]`
- `0x21` SUB   `R[a] <- R[a] - R[b]`
- `0x30` JMP   `PC <- addr`
- `0x31` JZ    `if ZF then PC <- addr`
- `0xFF` HALT

## Derleme (Windows MinGW)

`build_exe.bat` tek komutla exe üretir.

> Not: WinAPI GUI uygulaması olduğu için `-mwindows` ve statik link seçenekleri kullanılmıştır.

## Çalıştırma

1. `build_exe.bat`
2. `build\mcu_emulator.exe`
3. GUI'den `Load BIN` veya `Load HEX` ile program yükleyin.
4. Başlangıç adresini `Start Addr` alanına hex olarak girin (örn: `0x0000`).
5. `Run`, `Step`, `Pause`, `Reset` ile emülasyonu yönetin.

## Notlar

- Bu proje **gerçek PCB/çip üretimi yapmaz**.
- Tamamen eğitim/analiz amaçlı yazılım emülasyonudur.
- Kod okunabilir ve öğretici olacak şekilde yorumlanmıştır.


## EXE olusturma sorunu icin hizli cozum ("exe yapamiyorum")

En sik nedenler:
- `g++.exe` PATH'te degil
- MSYS2'nin `ucrt64`/`mingw64` ortami yerine farkli shell kullaniliyor
- MinGW yerine MSVC arac zinciri acik

### Onerilen kurulum (MSYS2)
1. MSYS2 kurun: `https://www.msys2.org/`
2. "MSYS2 MinGW 64-bit" terminalini acin.
3. Paketleri yukleyin:
   - `pacman -S --needed mingw-w64-x86_64-toolchain`
4. `C:\msys64\mingw64\bin` yolunu Windows PATH'e ekleyin.
5. Yeni CMD/PowerShell acip proje klasorunde `build_exe.bat` calistirin.

### Beklenen cikti
- `build\mcu_emulator.exe` dosyasi olusur.
- Script, derleyici yolunu ve varsa DLL bagimlilik ozetini ekrana yazar.

### Not
- Bu script **MinGW g++** icindir.
- Linux/WSL icinde dogrudan Windows `.exe` uretebilmek icin ayrica cross-compiler (ornegin `x86_64-w64-mingw32-g++`) gerekir.
