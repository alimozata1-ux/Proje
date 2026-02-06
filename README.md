# Neon Browser (C++)

Qt6 + WebEngine ile yazılmış neon temalı örnek bir tarayıcı.

## Özellikler
- Sekmeli tarayıcı (yeni sekme / kapatma)
- Geri / ileri / yenile / adres çubuğu
- **Araç çubuğu + adres çubuğu + sekme çubuğu için %75 saydamlık (varsayılan)**
- Neon renk seçimi (ayarlar menüsü)
- Arka plan görselini değiştirme (ayarlar menüsü)
- Ayarların kalıcı kaydı (`QSettings`)

## Linux/macOS Derleme
```bash
cmake -S . -B build
cmake --build build
./build/neon_browser
```

## Windows'ta `.exe` Üretme
> Qt6 (Widgets + WebEngine), CMake ve Ninja kurulu olmalıdır.

### Yöntem 1: GitHub Actions ile hazır `.exe` (önerilen)
1. Repoda **Actions** sekmesine girin.
2. **Build Windows EXE** iş akışını seçin.
3. **Run workflow** deyin.
4. Bittiğinde artifact olarak `neon-browser-windows` indirin.
5. ZIP içinden `neon_browser.exe` dosyasını çalıştırın.

Bu iş akışı Qt runtime dosyalarını (`windeployqt`) da paketler.

### Yöntem 2: Lokal Windows build script
```bat
build_exe.bat
```
Çıktı:
- `build\dist\neon_browser.exe`

### Yöntem 3: Manuel
```bat
cmake -S . -B build -G "Ninja"
cmake --build build --config Release
cmake --install build --config Release --prefix build\dist
windeployqt build\dist\neon_browser.exe
```
