# Super3D

Super3D, Python + Pygame ile yazılmış modüler bir **3D wireframe grafik kütüphanesidir**.

## Özellikler

- Hazır 3D şekiller: `Cube`, `Pyramid`, `Sphere`, `Cylinder`, `Cone`, `Torus`
- Her şekil için `vertices` ve `edges` verisi
- X, Y, Z ekseninde döndürme + otomatik açısal hız (`angular_velocity`)
- Şekil ölçekleme (`set_scale`) ve taşıma (`translate`)
- Perspektif projeksiyon + kamera yaw/pitch
- Pygame tabanlı gerçek zamanlı çizim
- Grid/eksen çizimi ve uzaklığa göre çizim sıralaması
- Sahne yönetimi için `Sahne` sınıfı

## Kurulum

```bash
pip install -r requirements.txt
pip install -e .
```

## Hızlı Kullanım

```python
from super3d import Kamera, Renderer, Cube

kamera = Kamera(position=(0, 0, -10), fov=600)
renderer = Renderer(size=(1000, 700))
kup = Cube(size=2, position=(0, 0, 8), color=(255, 120, 120))
kup.angular_velocity = (0.8, 1.1, 0.4)

renderer.run([kup], kamera)
```

## Kamera Kontrolleri (varsayılan)

- `W/S`: ileri/geri
- `A/D`: sol/sağ
- `Q/E`: yukarı/aşağı
- `←/→`: yaw
- `↑/↓`: pitch

## Örnek

Kök dizindeki `ornek.py` dosyası tüm şekilleri aynı sahnede döndürür ve kamera kontrollerini gösterir.
