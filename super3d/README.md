# Super3D

Super3D, Python + Pygame ile yazılmış modüler bir **3D grafik kütüphanesidir**.

## Özellikler

- Hazır 3D şekiller: `Cube`, `Pyramid`, `Sphere`, `Cylinder`, `Cone`, `Torus`
- Şekillerde `vertices`, `edges`, `faces` yapısı
- Varsayılan olarak **çizgi yerine içi dolu (solid)** polygon çizimi
- İstenirse kenar çizgilerini açma: `Renderer(draw_edges=True)`
- X, Y, Z ekseninde döndürme + otomatik açısal hız (`angular_velocity`)
- Şekil ölçekleme (`set_scale`) ve taşıma (`translate`)
- Şekilleri farklı açılarla yerleştirme: `set_rotation_deg(...)`
- Basit doku modları: `flat`, `checker`, `stripe`, `noise` (`set_texture`)
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
- `ucak_oyunu.py`: şehir bombalama temalı uçak oyunu (uçaksavar savunmalı).
- `liman_savunma.py`: limanı koruma oyunu (2 namlulu 360° uçaksavar, mouse hedefleme, dış 3D kamera).
- `araba_oyunu.py`: 3D araba oyunu (şerit değiştir, engellerden kaç).

### Tank Oyunu Kontrolleri
- `W/S`: ileri/geri
- `A/D`: gövdeyi döndür
- `Fare`: kuleyi nişana döndür
- `SPACE`: ateş
- `ESC`: çıkış

- `P`: oyunu duraklat/devam

### Ekstra Oynanış Özellikleri
- Mini-harita (minimap) eklendi.
- Skor sistemi eklendi.
- Gece-gündüz benzeri dinamik ortam rengi eklendi.
- Hız buff point (mavi) eklendi: kısa süreli hareket hız artışı verir.


### Tank Oyunu Güncellemeleri
- Harita ciddi şekilde büyütüldü (daha geniş savaş alanı + engeller).
- Silahlarda menzil sistemi eklendi (mermiler menzil bitince kaybolur).
- Tank modeli M4 Sherman esintili çok parçalı yapıda geliştirildi.

## GPU Test Uygulaması
`gpu_test.py` ekran kartı/performans denemesi için eklendi.

```bash
python gpu_test.py
```

Kontroller:
- `+`: yeni şekil dalgası ekle
- `-`: şekil azalt
- `R`: sahneyi sıfırla
- `W/A/S/D`, `Q/E`, `←/→`: kamera hareketi
- `ESC`: çıkış

### Tank Oyunu Yeni Özellikler
- Gerçek orman hissi veren map (ağaç + kaya yerleşimi).
- Silahlarda reload süresi (ateş aralığı bekleme).
- HUD üzerinde oyuncu/düşman can barı.
- Harita içinde can doldurma pointleri (cooldown ile tekrar aktif olur).


## Açı ve Doku Kullanımı

```python
from super3d import Cube

k = Cube(size=2, color=(220, 120, 90))
k.set_rotation_deg(30, 45, 10)  # derece
k.set_texture("checker", strength=0.2)
```


## Uçak Oyunu

```bash
python ucak_oyunu.py
```

Amaç: Şehirdeki binaları bombalayarak yok etmek. Düşman uçak yok, fakat şehirlerde uçaksavarlar var. Kamera uçağa bağlıdır ve sabit bir ofsetten (cockpit/chase-benzeri) izler.

Kontroller:
- `A/D`: sağa-sola dön
- `W/S`: hızlan-yavaşla
- `Q/E`: yüksel-alçal
- `SPACE`: bomba bırak
- `P`: duraklat
- `ESC`: çıkış

- Uçak ve şehir modelleri detaylandırıldı (çok parçalı model + bina taban/gövde/çatı).

- Bombalarda patlama alanı (splash damage) vardır; yakın binalar ve uçaksavarlar hasar alır.


## Liman Savunma Oyunu

```bash
python liman_savunma.py
```

Amaç: Limanı gelen uçaklardan korumak. Biz 2 namlulu bir uçaksavarız.

Özellikler:
- Gövde 360 derece döner (`yaw`)
- Namlular yukarı-aşağı döner (`pitch`)
- Mouse ile hedefleme
- Sol tık ile ateş
- Uçaksavarın dışından 3D kamera (arkadan takip)
- Kontrollü uçak spawn (max aktif uçak sınırı + zamanla kademeli zorluk)

Kontroller:
- `Mouse`: hedefleme
- `Sol Tık`: ateş
- `ESC`: çıkış


## Araba Oyunu

```bash
python araba_oyunu.py
```

Amaç: Yoldaki engellerden kaçıp mümkün olduğunca skor toplamak.

Kontroller:
- `A/D` veya `←/→`: şerit değiştir
- `ESC`: çıkış

## GTA Tarzı Oyun

```bash
python gta_oyunu.py
```

Özellikler:
- Silah sistemi (tabanca/rifle, şarjör + reload)
- Arabaya binme/sürüş sistemi
- Şehir binaları ve yollar
- Gezen/saldıran NPC sistemi
- Akıllı telefon arayüzü (harita/görev/kontak)

Kontroller:
- `W/A/S/D`: hareket
- `Mouse`: kamera nişan
- `Sol Tık`: ateş
- `R`: reload
- `1/2`: silah değiştir
- `E`: araca bin/in
- `TAB`: telefon
- `P`: duraklat
- `ESC`: çıkış

## BF 109 Orman Saldırısı

```bash
python bf109_orman_saldiri.py
```

Amaç: BF 109 ile büyük ormandaki düşman üssünü yok etmek.

Özellikler:
- Uçakta 2 makineli tüfek
- Uçakta bomba sistemi
- Düşman üssünde 4 adet AA gun
- Büyük orman haritası

Kontroller:
- `A/D`: dön
- `W/S`: hız artır/azalt
- `Q/E`: yüksel/alçal
- `Sol Tık`: makineli tüfek ateşi
- `SPACE`: bomba bırak
- `P`: duraklat
- `ESC`: çıkış
