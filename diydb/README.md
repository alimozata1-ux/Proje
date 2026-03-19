# diydb

`diydb`, GoblinPackege için özelleştirilebilen, dosya tabanlı ve yerel-first çalışan bir Python veri tabanı kütüphanesidir.

## Özellikler

- JSON dosyasına atomik kayıt
- Şema/alan doğrulama
- Unique alan + index desteği
- Query builder (filtre, sıralama, limit/offset)
- Transaction (rollback ile)
- Hook sistemi
- Backup / restore
- Migration kayıt ve çalıştırma

## Hızlı başlangıç

```python
from diydb import Field, open_db, query

db = open_db("./goblin.db.json")

db.create_table(
    "files",
    [
        Field("name", str, required=True),
        Field("size", int, required=True),
        Field("owner", str, required=True),
    ],
    primary_key="id",
    if_not_exists=True,
)

db.insert("files", {"name": "a.txt", "size": 123, "owner": "u1"})

def only_u1():
    return query().where_eq("owner", "u1").order("size", desc=True)

rows = db.find("files", only_u1())
print(rows)
```
