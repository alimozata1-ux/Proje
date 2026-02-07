# C++ Saat + CPU + RAM Widget (Windows)

Bu proje Windows için hazırlanmış, küçük bir **masaüstü widget** uygulamasıdır.

## Özellikler
- Anlık tarih/saat
- CPU kullanım yüzdesi
- RAM kullanım yüzdesi ve MB bilgisi
- Sağ üstte kırmızı `X` kapatma tuşu
- Pencere opaklığı yaklaşık `%75`
- Arka plan rengini `WIDGET_BG_COLOR` ile değiştirme
- Tek zip içinde **Win32 (x86) + Win64 (x64)** kaynak paket üretme

## Arka plan rengi değiştirme
Örnek:

```powershell
set WIDGET_BG_COLOR=#0F172A
system_widget.exe
```

## Derleme (Windows)
MSVC ile:

```powershell
cmake -S . -B build
cmake --build build --config Release
```

Alternatif hızlı komut:

```powershell
build_win64.bat
```

## Ortak ZIP paketi (Win32 + Win64)
Linux/CI ortamında:

```bash
./scripts/package_win64.sh
```

Çıktı (lokal üretilir):
- `dist/system_widget_windows_x86_x64.zip`

Zip içeriği:
- `windows/win32/...` (kaynak kod)
- `windows/win64/...` (kaynak kod)

## GitHub notu
- GitHub repo içinde binary/zip takip etmiyoruz.
- Bu yüzden `dist/*.zip` dosyaları `.gitignore` ile dışarıda tutulur.
- Paket, **ikili dosya içermeyen kaynak dağıtımı** olarak hazırlanır.
- Derlenmiş `.exe` dosyalarını GitHub Releases üzerinde ayrıca paylaşabilirsiniz.

## Not
- Bu sürüm Win32 API kullanır (`GetSystemTimes`, `GlobalMemoryStatusEx`, GDI çizimi).
- Linux'ta çalıştırıldığında bilgilendirici mesajla çıkar; asıl hedef Windows çalıştırmasıdır.
