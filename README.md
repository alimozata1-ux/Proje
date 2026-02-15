# Neon Browser (Go)

Golang ile yazılmış, GUI tabanlı bir masaüstü tarayıcı örneği.

## Özellikler
- WebView tabanlı gezinme (geri, ileri, yenile, adres çubuğu)
- Araç çubuğunda yaklaşık **%75 şeffaf** görünüm (ayarlar ile değiştirilebilir)
- Araç çubuğu altında **neon çizgi**
- Neon çizgi rengini ayarlardan değiştirme
- Detaylı ayarlar:
  - Ana sayfa
  - Arama motoru deseni
  - Araç çubuğu şeffaflığı
  - Zoom oranı
  - Durum çubuğu görünürlüğü
  - JavaScript/dev modu bayrakları
  - Son sayfayı açma
  - İndirme klasörü
- Son URL'yi hatırlama (opsiyonel)

## Çalıştırma (Windows)
```bat
build_windows.bat
```

Üretilen dosya: `NeonBrowser.exe`

## Geliştirme
```bash
go mod tidy
go run .
```

> Not: Uygulamanın tam GUI sürümü Windows hedefi içindir (`main_windows.go`).
