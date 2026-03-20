# KONE OS

KONE OS, tamamen sıfırdan geliştirilen deneysel bir işletim sistemi ekosistemidir.
Bu depo, tek seferde üretilebilir bir **minimum çalışır temel** (MVP+) sağlar:

- GRUB ile açılabilen freestanding kernel (Mars32) iskeleti
- Üçlü kernel mimarisi (X/Y/Z) modülleri
- IPC mesaj kuyruğu, event hattı ve shared memory
- Permission + sandbox güvenlik altyapısı
- Basit KFS (KONE File System) in-memory uygulaması
- KONEC dili için lexer+parser+AST+codegen (host aracı)
- KONE VM (debug modlu özel sanal makine)
- Plugin, ses ve AI komut sistemi iskeleti
- Android-benzeri tablet GUI önizlemesi (taskbar + pencere yönetimi) (`gui/preview/koneos_preview.html`)

## Dizin Yapısı

- `/boot` Bootloader ve linker script
- `/kernel` X Kernel + güvenlik/plugin/ses/AI sistemleri
- `/drivers` Y Kernel (input, disk, HAL, touch)
- `/gui` Z Kernel (framebuffer, wm, render/compositor, tema, desktop, bildirim, taskbar modeli)
- `/fs` KFS
- `/compiler` KONEC derleyici
- `/vm` KONE VM
- `/apps` Örnek uygulama paketleri
- `/lib` Ortak tipler ve util
- `/gui/preview` HTML ile tablet arayüz prototipi
- `/gui/apps` Her temel uygulama için ayrı, düzgün GUI mock ekranları

## Derleme

```bash
make all
```

### Sadece host araçları

```bash
make host-tools
```

### ISO üretimi

```bash
make iso
```

### Kod satırı istatistiği

```bash
make stats
```

## Çalıştırma

QEMU:

```bash
make run-qemu
```

VirtualBox:

1. `build/koneos.iso` dosyasından yeni VM oluştur
2. `Other/Unknown (32-bit)` seç
3. RAM >= 256MB ver
4. ISO'yu optical drive'a takıp başlat

## KONEC örneği

```bash
./build/bin/konec compiler/examples/hello.kc build/hello.mars32
./build/bin/konevm build/hello.mars32 --debug
python3 vm/konevm_py.py build/hello.mars32 --debug
```

## HTML Arayüz Önizleme

Ana shell: `gui/preview/koneos_preview.html`

Uygulama GUI sayfaları:
- `gui/apps/file_manager.html`
- `gui/apps/settings.html`
- `gui/apps/terminal.html`
- `gui/apps/text_editor.html`
- `gui/apps/media_player.html`
- `gui/apps/calculator.html`
- `gui/apps/system_monitor.html`
- `gui/apps/browser.html`


```bash
xdg-open gui/preview/koneos_preview.html
```

> `mock_data.js` büyük bir demo veri seti içerir; mağaza/liste/log ekranlarını yoğun yükte simüle eder.

## Mimariler

- Mars32: i386 freestanding kernel + `.mars32` bytecode hedefi
- Mars64: toolchain/VM tarafında `.mars64` çıktı desteği (kernel port planlanmıştır)


## Python Tabanlı VM

- Dosya: `vm/konevm_py.py`
- Özellikler: debug modu, stack trace, step limiti

```bash
python3 vm/konevm_py.py build/hello.mars64 --debug --trace-stack
```
