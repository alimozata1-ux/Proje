# AeroWin7

`aerowin7`, `aerotkinter` üstünde çalışan modüler bir Windows 7 Aero stil GUI kütüphanesidir.

> Not: Bu repoda örneklerin her ortamda açılabilmesi için hafif bir yerel `aerotkinter` uyumluluk katmanı da bulunur.

## Modüller
- `aerowin7/core.py` → `AeroAppWindow`
- `aerowin7/animation.py` → GUI animasyon motoru (`AnimationEngine`)
- `aerowin7/theme.py` → Light / Dark tema paletleri
- `aerowin7/utils.py` → gradient/renk yardımcıları
- `aerowin7/widgets/` → `GlassButton`, `GlassLabel`, `GlassEntry`, `GlassCard`
- `aerotkinter/` → yerel uyumluluk katmanı (fallback)

## Çalıştırma
```bash
python examples/demo.py
# veya
python examples/ornek.py
```

## Kullanım
```python
from aerowin7.core import AeroAppWindow
from aerowin7.widgets import GlassButton
```
