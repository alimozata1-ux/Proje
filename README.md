# LİB-BAG

Hibrit veri depolama motoru:
- 10 shard (`node_0..9.lib/.bag`)
- `.LIB`: XML metadata + zlib sıkıştırma
- `.BAG`: yüksek kapasiteli binary blok depolama (64-bit offset)

## Dosya Formatı

Header (22 bayt, little-endian):
- Magic Number (4B)
- Version (2B)
- Entry Count (8B)
- Last Offset (8B)

### `.BAG` kayıt düzeni
- key_len (uint16)
- key bytes
- type_code (uint8)
- payload_len (uint64)
- payload
- crc32 (uint32)

### `.LIB` kayıt düzeni
- compressed_len (uint32)
- zlib(compressed XML record)

## Build

```bash
go build -o libbag-engine ./engine.go
```

## Çalıştırma

```bash
export LIBBAG_DATA_DIR=./data
./libbag-engine
```

Sunucu varsayılan olarak `http://127.0.0.1:8080` üzerinde açılır.

## API

### Veri Yazma
`POST /api/put`

```json
{
  "key": "user:1:photo",
  "data_type": "binary",
  "data": "..."
}
```

### İstatistik
`GET /api/stats`

Dashboard `index.html` + `app.js` ile bu endpoint'i kullanır.

## Python Araçları

Corruption kontrolü:

```bash
python3 tools.py inspect ./data/node_0.bag
```

Yük testi:

```bash
python3 tools.py stress --url http://127.0.0.1:8080 --count 5000
```
