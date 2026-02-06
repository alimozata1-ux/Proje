# Neon Browser (C++)

Qt6 + WebEngine ile yazılmış neon temalı örnek bir tarayıcı.

## Özellikler
- Sekmeli tarayıcı (yeni sekme / kapatma)
- Geri / ileri / yenile / adres çubuğu
- **Araç çubuğu + adres çubuğu + sekme çubuğu için %75 saydamlık (varsayılan)**
- Neon renk seçimi (ayarlar menüsü)
- Arka plan görselini değiştirme (ayarlar menüsü)
- Ayarların kalıcı kaydı (`QSettings`)

## Derleme
```bash
cmake -S . -B build
cmake --build build
```

## Çalıştırma
```bash
./build/neon_browser
```
