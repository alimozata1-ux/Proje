# C++ Windows Saat + CPU + RAM Widget

Bu proje, Win32 API ile yazılmış masaüstü widget uygulamasıdır.

## Özellikler

- Canlı saat (1 sn güncelleme)
- Tarih (gg.aa.yyyy formatında)
- CPU kullanım yüzdesi
- RAM kullanım bilgisi (GB + yüzde)
- Kırmızı `X` kapatma tuşu
- Başlangıçta yaklaşık `%75` şeffaflık
- `Renk` butonuyla arka plan rengini değiştirme
- `+` / `-` butonlarıyla şeffaflık seviyesini artırıp azaltma
- `Sabit` / `Normal` butonuyla her zaman üstte (topmost) modunu açma-kapama
- Pencereyi sürükleyerek taşıma
- Konum, arka plan rengi, şeffaflık ve pin durumu ayarlarını `widget_settings.ini` dosyasına otomatik kaydetme

## Derleme (Windows)

### MinGW + CMake

```bash
cmake -S . -B build -G "MinGW Makefiles"
cmake --build build
```

Çıktı: `build/SystemWidget.exe`

### Visual Studio ile

```bash
cmake -S . -B build
cmake --build build --config Release
```

Çıktı: `build/Release/SystemWidget.exe`

## Not

Bu uygulama Win32 API kullandığı için Linux/macOS ortamında çalıştırılamaz; Windows üzerinde derlenip çalıştırılmalıdır.
