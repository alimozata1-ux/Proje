# Modern Browser (WPF + WebView2)

Bu proje, **C# + WPF + Microsoft WebView2** ile geliştirilmiş sekmeli modern bir masaüstü tarayıcı örneğidir.

## 1) Gereksinimler

Windows üzerinde aşağıdakiler kurulu olmalıdır:

- **.NET 8 SDK**
- **WebView2 Runtime (Evergreen)**

Kontrol:

```powershell
dotnet --info
```

WebView2 Runtime kontrolü (örnek):

- Denetim Masası > Programlar kısmında `Microsoft Edge WebView2 Runtime` görünmeli.

## 2) Derleme (Build)

Proje klasöründe:

```powershell
dotnet restore
dotnet build -c Release
```

## 3) Çalıştırma (Run)

Debug modda çalıştırmak için:

```powershell
dotnet run -c Debug
```

Alternatif olarak Visual Studio ile:

1. `Proje.csproj` dosyasını aç
2. Build Configuration: `Debug` veya `Release`
3. `F5` ile çalıştır

## 4) Yayın Alma (Publish)

Tek klasör publish (framework-dependent):

```powershell
dotnet publish -c Release -r win-x64 --self-contained false
```

Çıktı klasörü:

```text
bin\Release\net8.0-windows\win-x64\publish\
```

## 5) Sık Karşılaşılan Sorunlar

### `dotnet: command not found`

.NET SDK kurulu değildir ya da PATH'e eklenmemiştir.

### WebView2 başlatma hatası

WebView2 Runtime eksik olabilir. Runtime'ı yükleyip tekrar deneyin.

### WPF sadece Windows'ta çalışır

`TargetFramework=net8.0-windows` olduğu için Linux/macOS üzerinde bu uygulama derlenip çalıştırılamaz.
