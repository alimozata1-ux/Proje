# Hybrid .LIB Database Engine (Go)

Bu proje JSON verisini REST API ile alır, type-safe Go struct'ına parse eder, XML'e serialize eder ve zlib ile sıkıştırıp 10 shard `.LIB` dosyasına dağıtır.

## Özellikler

- JSON ➜ Go struct ➜ XML ➜ zlib veri hattı
- Hash tabanlı 10 shard (`shard_0.LIB` ... `shard_9.LIB`)
- 64-bit header (magic, version, index offset)
- WAL benzeri güvenli yazma (intent log)
- LRU cache
- Compaction (dosya reorganizasyonu)
- RWMutex ile eşzamanlı erişim
- HTML + Vanilla JS dashboard

## Çalıştırma

```bash
go mod tidy
go run .
```

Sonra tarayıcıdan: `http://localhost:8080`

## API

- `POST /api/put` JSON kayıt ekleme
- `GET /api/get?key=...` XML okuma
- `DELETE /api/delete?key=...` silme
- `POST /api/compact` compaction
- `GET /api/stats` shard metrikleri
- `GET /api/header?shard=0` header bilgisi
