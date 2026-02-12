# myos

Eğitsel amaçlı x86 (32-bit) bare-metal OS.

## Öne Çıkanlar
- Bootloader + protected mode
- Paging/MMU (ilk 4MB identity map)
- Ring3 kullanıcı modu + int 0x80 syscall
- Timer tabanlı preemptive scheduler
- PS/2 klavye sürücüsü (IRQ1)
- Kernel heap allocator
- Seri port logger
- Basit komut kabuğu (shell)
- Tanılama (diagnostics) modülü
- In-memory RAM filesystem (RAMFS) + shell file commands
- Text-mode GUI demo (VGA üzerinde taskbar + pencere sistemi)
- Bliss tarzı duvar kağıdı (gökyüzü + yeşil tepe)
- Masaüstü ikon sistemi (ekle/sil/listele)
- Text-mode web browser (sekme/geçmiş/yer imi, built-in sayfalar)
- Ayarlar sistemi (duvar kağıdı/bulut/taskbar modu)
- Bildirim merkezi (taskbar unread sayacı)
- Sürücü bulucu/kurucu (driver manager)
- Sistem uygulamaları (terminal/files/settings/browser/notifications/drivers/calculator/notepad/thispc/monitor/display/desktop/xox/tetris/snake/pong)
- Feature Hub (900 eğitimsel özellik kaydı)
- Hybrid kernel modu (monolithic + servis karmasi)

## Derleme
```bash
make
```

## Çalıştırma
```bash
make run
```

## Not
Bu proje öğretici sadelik için minimal ve anlaşılır bırakılmıştır.

## Dosya Sistemi Komutları
- `ls`, `touch NAME`, `rm NAME`, `cat NAME`, `write NAME TEXT`, `append NAME TEXT`, `run NAME`

## GUI Komutu
- `gui` komutu VGA text mode üzerinde pencere/masaüstü demo ekranı çizer.

## Varsayılan Özel EXE-Dosya
- RAMFS başlangıçta `superx323` isimli executable benzeri dosya oluşturur.
- Shell içinde `run superx323` komutu ile içeriği çalıştırma simülasyonu yapılır.

## Pencere Sistemi Komutları
- `gui`: taskbar + demo pencereleri çizer
- `winlist`: açık pencereleri listeler
- `winopen TITLE`: yeni pencere açar
- `winfocus ID`: pencereyi öne getirir
- `winclose ID`: pencereyi kapatır

## İkon Sistemi Komutları
- `iconlist`: ikonları listeler
- `iconadd NAME`: masaüstüne ikon ekler
- `icondel ID`: ikon siler

## Tarayıcı Komutları
- `browser home`
- `browser open URL`
- `browser back` / `browser forward`
- `browser tabs` / `browser tab ID` / `browser close ID`
- `browser bm URL` / `browser bms`

> Not: Bu sürüm eğitim amaçlı text-mode tarayıcıdır; TCP/IP ağı olmadığı için built-in sayfaları render eder.

## Ayarlar Komutları
- `settings show`
- `settings wallpaper 0|1`
- `settings clouds 0|1`
- `settings taskbar 0|1`

## Bildirim Komutları
- `notif add TEXT`
- `notif list`
- `notif readall`
- `notif clear`

## Driver Komutları
- `driver list`
- `driver find TEXT`
- `driver install NAME`
- `driver uninstall NAME`
- `driver info NAME`
- `driver installed`

## Sistem Uygulamaları Komutları
- `apps`
- `app open NAME` (örn: `app open terminal`, `app open browser`, `app open calculator`, `app open notepad`, `app open thispc`, `app open monitor`, `app open display`, `app open desktop`, `app open xox`, `app open tetris`, `app open snake`, `app open pong`)
- Kısayollar: `calc`, `note`, `thispc`, `monitor`, `display`, `desktop`, `xox`, `tetris`, `snake`, `pong`

## Feature Hub Komutları
- `features`
- `feature count`
- `feature run feature_0001`

## Görüntü Ayarları
- `settings show`
- `settings desktop 0|1`
- `settings brightness N` (0..100)
- `settings theme 0|1`

## Oyunlar
- `xox` (Tic-Tac-Toe)
- `tetris`
- `snake`
- `pong`

## Kernel Modu Komutları
- `kernelmode` / `kernelmode show`
- `kernelmode set hybrid`
- `kernelmode set monolithic`
- `kernelmode services`
