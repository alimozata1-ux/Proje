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

### Yöntem 1: Tek komut (önerilen)
```bat
build_exe.bat
```
Çıktı:
- `build\dist\neon_browser.exe`

### Yöntem 2: Manuel
```bat
cmake -S . -B build -G "Ninja"
cmake --build build --config Release
cmake --install build --config Release --prefix build\dist
```
Çıktı:
- `build\dist\neon_browser.exe`

### Qt DLL / runtime dosyalarını kopyalama
EXE'nin başka makinelerde çalışması için genelde `windeployqt` gerekir:
```bat
windeployqt build\dist\neon_browser.exe
```
