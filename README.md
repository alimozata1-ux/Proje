# BAG Arşiv Sistemi

Bu proje, ZIP benzeri ama `.bag` uzantılı bir arşiv formatı ve komut satırı araçları sağlar.

## Özellikler

- `.bag` uzantısı ile arşiv oluşturma
- Sonradan şifre ekleme/değiştirme/kaldırma
- Şifreli arşivlerde silme işlemi için parola doğrulama
- Basit kurulum sihirbazı (`setup_wizard.py`)

## Kullanım

### 1) Arşiv oluştur

```bash
python3 bag_tool.py create yedek.bag dosya1.txt klasorA --password 1234
```

### 2) Arşivi aç

```bash
python3 bag_tool.py extract yedek.bag cikti_klasoru
```

### 3) Sonradan şifre koy / değiştir / kaldır

```bash
python3 bag_tool.py set-password yedek.bag --password yeniSifre
python3 bag_tool.py set-password yedek.bag --password ""
```

Etkileşimli kullanım:

```bash
python3 bag_tool.py set-password yedek.bag --ask-password
```

### 4) Arşivi sil

Şifre yoksa direkt silinir:

```bash
python3 bag_tool.py delete yedek.bag
```

Şifre varsa parola gerekir:

```bash
python3 bag_tool.py delete yedek.bag --password 1234
```

## Kurulum sihirbazı

```bash
python3 setup_wizard.py
```

Bu sihirbaz `~/.bag_tool_config.json` dosyasını oluşturur.
