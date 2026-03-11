# Pixel2D Engine (Python)

Bu proje, **pixel tarzı 2D oyunlar** üretmek için hazırlanmış mini bir oyun motoru iskeletidir.

## Özellikler
- Grid tabanlı map sistemi
- Map boyutu ayarlama (`resize`)
- Map çevresine sınır ekleme (`add_border`)
- Nesne sistemi (`GameObject`)
- Bileşen mimarisi (component-based)
- Hazır kodlar / prefab'lar:
  - Araba (`create_car`) – sürüş + çarpışma + hareket
  - Ağaç (`create_tree`)
  - Duvar (`create_wall`)
  - Drone düşman (`create_enemy_drone`)
- Hazır şehir map üretici (`create_city_map`)

## Kurulum
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Demo çalıştırma
```bash
python examples/demo_game.py
```

## Kütüphane Kullanımı

```python
from pixel_engine import PixelEngine, create_car, create_city_map

engine = PixelEngine(width=800, height=480, title="Benim Oyunum")
map_data = create_city_map(width_tiles=50, height_tiles=30, tile_size=16)
engine.set_map(map_data)
engine.add_object(create_car(40, 40))
engine.run()
```

## Özel Nesne Tasarlama Örneği

```python
from pixel_engine import GameObject, MovementComponent

fireball = GameObject("fireball", x=100, y=100, width=8, height=8, color=(255,120,20))
fireball.velocity_x = 180
fireball.add_component(MovementComponent())
```

## Dosya Yapısı
- `pixel_engine/engine.py`: Oyun döngüsü, çizim, event, kamera
- `pixel_engine/map_system.py`: Tile map, boyutlandırma, sınır, çarpışma tile
- `pixel_engine/objects.py`: Oyun nesnesi modeli
- `pixel_engine/components.py`: Hazır bileşenler
- `pixel_engine/prefabs.py`: Hazır nesneler
- `pixel_engine/builders.py`: Hazır map üreticileri
- `examples/demo_game.py`: Çalışan örnek
