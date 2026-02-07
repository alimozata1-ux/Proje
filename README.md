# C++ Saat + CPU + RAM Widget (Windows)

Bu proje Windows için hazırlanmış, küçük bir **masaüstü widget** uygulamasıdır.

## Özellikler
- Anlık tarih/saat
- CPU kullanım yüzdesi
- RAM kullanım yüzdesi ve MB bilgisi
- Sağ üstte kırmızı `X` kapatma tuşu
- Pencere opaklığı yaklaşık `%75`
- Arka plan rengini `WIDGET_BG_COLOR` ile değiştirme

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

Çıktı:
- `build/Release/system_widget.exe`

## Not
- Bu sürüm Win32 API kullanır (`GetSystemTimes`, `GlobalMemoryStatusEx`, GDI çizimi).
- Linux'ta derlenirse uygulama bilgilendirici bir mesajla çıkar; asıl hedef Windows çalıştırmasıdır.
