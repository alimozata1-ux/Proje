# KONE OS Tasarım Dokümanı

## 1. Üçlü Kernel Mimarisi

### X Kernel (Core)
- Scheduler: zamanlayıcı tik tabanlı round-robin iskeleti
- Memory: erken aşama bump allocator (`xk_kmalloc`)
- Process/Thread: process model başlangıç noktası
- Syscall: kullanıcı alanı API kapısı için başlangıç kancası
- Panic: sistem durdurma ve hata raporlama
- Shared memory: `shm_create/open/destroy`
- Plugin system: runtime kayıt altyapısı
- Audio: temel beep arayüzü
- AI Command: komut yorumlayıcı iskeleti

### Y Kernel (I/O)
- HAL başlangıcı
- Klavye/mouse/touch simülasyon driver başlangıçları
- Disk I/O başlangıç katmanı

### Z Kernel (GUI)
- Framebuffer abstraction
- Window manager: create/move/resize/minimize/maximize/close/focus
- Layered renderer/compositor frame döngüsü
- Tema sistemi (açık/koyu)
- Çoklu masaüstü yöneticisi başlangıcı
- Bildirim merkezi başlangıcı
- Debug panel başlangıcı
- Android-benzeri taskbar + running tasks modeli

## 2. Kernel İletişimi

- IPC: ring-buffer message queue (`ipc_send`, `ipc_recv`)
- Event System: giriş ve pencere olayları için hafif event kuyruğu
- Shared memory: modüller arası veri paylaşımı için named region modeli

## 3. Güvenlik

- Permission sistemi (`security_register_app`, `security_grant`, `security_check`)
- Sandbox profilleri (app başına memory/cpu limit tanımı)
- User mode/kernel mode ayrımı için API hazırlığı

## 4. GUI Sistemi

Kernel tarafında GUI çekirdeği başlatma seviyesindedir.
`gui/preview/koneos_preview.html` dosyası, Android-benzeri hedef tablet deneyimini demonstratif olarak gösterir:
- Home Screen
- App Menu
- Dock
- Notification overlay
- Widget host
- Çoklu masaüstü düğmesi
- Tema geçişi
- Debug paneli
- Her temel uygulama için ayrı GUI mock ekranları (`gui/apps/*.html`)
- Browser uygulaması: sekme, geçmiş, yer imi, indirme ve devtools panel mockları
- Game Center: Snake, Reaction Tap, Memory Match mini oyunları

## 5. KFS

KFS, in-memory node tabanlı basit bir dosya sistemi prototipidir:
- Dizin oluşturma (`kfs_mkdir`)
- Dosya oluşturma (`kfs_create`)
- Root mount (`kfs_init`)

Destek hedefi uzantılar: `.txt`, `.cfg`, `.log`, `.bin`, `.app`, `.img`

## 6. KONEC Derleyici

Pipeline:
1. Lexer (`lexer.c`)
2. Parser + AST (`parser.c`)
3. Code generation (MARS bytecode)

Çıktı:
- `.mars32` (M3 header)
- `.mars64` (M6 header)

Örnek syntax:
```c
print(40 + 2);
```

## 7. KONE VM

- Basit CPU emülasyonu: stack tabanlı opcode yürütümü
- RAM, disk, framebuffer modelleyen VM state yapısı
- Debug modu (`--debug`)
- Python referans VM (`vm/konevm_py.py`)

Opcode set:
- `PUSH`
- `ADD`
- `PRINT`
- `HALT`

## 8. Büyük Ölçekli Kod Tabanı Simülasyonu

Aşağıdaki dosyalar, büyük ölçekli bir OS ekosisteminde karşılaşılacak veri kataloglarını simüle eder:
- `kernel/generated/syscall_catalog.c`: 5000+ syscall metadata satırı
- `gui/preview/mock_data.js`: büyük uygulama/veri/log kataloğu
- `gui/apps/mock_app_data.js`: uygulama bazlı yoğun GUI veri seti

Bu sayede hem kod tabanı satır sayısı hem de test verisi yoğunluğu artırılmıştır.

## 9. Build ve Çalıştırma

- `make all`: kernel + host tools
- `make iso`: bootable ISO
- `make run-qemu`: QEMU ile çalıştır
- `make stats`: toplam çekirdek kaynak satırı

## 10. Geliştirme Yol Haritası

1. Paging + gerçek frame allocator
2. Interrupt/IDT + syscall gate
3. KFS disk-backed sürüm
4. GUI theme/parser + compositing
5. App sandbox enforcement (runtime)
6. Mars64 kernel port
7. ARM tablet deneyi
