# Super3D

Super3D, Python + Pygame ile yazılmış modüler bir **3D grafik kütüphanesidir**.

## Özellikler

- Hazır 3D şekiller: `Cube`, `Pyramid`, `Sphere`, `Cylinder`, `Cone`, `Torus`
- Şekillerde `vertices`, `edges`, `faces` yapısı
- Varsayılan olarak **çizgi yerine içi dolu (solid)** polygon çizimi
- İstenirse kenar çizgilerini açma: `Renderer(draw_edges=True)`
- X, Y, Z ekseninde döndürme + otomatik açısal hız (`angular_velocity`)
- Şekil ölçekleme (`set_scale`) ve taşıma (`translate`)
- Perspektif projeksiyon + kamera yaw/pitch
- Grid/eksen çizimi ve sahne yönetimi (`Sahne`)
- Özel şekil tasarlama: `Sekil3D.ozel_sekil(...)`

## Kurulum

```bash
pip install -r requirements.txt
pip install -e .
```

## Hızlı Kullanım

```python
from super3d import Kamera, Renderer, Cube

kamera = Kamera(position=(0, 0, -10), fov=600)
renderer = Renderer(size=(1000, 700), draw_edges=False)
kup = Cube(size=2, position=(0, 0, 8), color=(255, 120, 120))
kup.angular_velocity = (0.8, 1.1, 0.4)

renderer.run([kup], kamera)
```

## Özel Şekil Tasarlama

```python
from super3d import Sekil3D

vertices = [
    (0, 1, 0),
    (-1, -1, -1),
    (1, -1, -1),
    (1, -1, 1),
    (-1, -1, 1),
]
faces = [
    (1, 2, 3, 4),
    (0, 1, 2),
    (0, 2, 3),
    (0, 3, 4),
    (0, 4, 1),
]
sekil = Sekil3D.ozel_sekil(vertices=vertices, faces=faces, color=(180, 120, 255))
```

## Kamera Kontrolleri (varsayılan)

- `W/S`: ileri/geri
- `A/D`: sol/sağ
- `Q/E`: yukarı/aşağı
- `←/→`: yaw
- `↑/↓`: pitch

## Örnekler

- `ornek.py`: tüm temel şekilleri döndürür.
- `tank_oyunu.py`: haritalı, kolaylaştırılmış, M4 Sherman esintili tank modelleri olan oyun.

### Tank Oyunu Kontrolleri
- `W/S`: ileri/geri
- `A/D`: gövdeyi döndür
- `Fare`: kuleyi nişana döndür
- `SPACE`: ateş
- `ESC`: çıkış
