# Proton Language Interpreter (Python)

Proton, kısa ve sembolik komutlara sahip; shell, async/thread, Python uyumluluğu ve sandbox modu hedefleyen deneysel bir dildir.

## Özellikler
- Line-based **tokenizer** (`proton/lexer.py`)
- AST üreten **parser** (`proton/parser.py`)
- Modüler **interpreter/runtime** (`proton/interpreter.py`)
- Genişletilebilir **komut registry** (`proton/registry.py` + `proton/builtins.py`)
- **Plugin** desteği (`proton/plugins.py`, `plugins/*.py`)
- **REPL** desteği (`proton/cli.py`)
- **Sandbox** güvenlik modu (`proton/sandbox.py`)
- Thread (`T->`, `bg>`) ve async await (`await>`) desteği

## Dosya Yapısı

```text
proton/
  ast_nodes.py
  lexer.py
  parser.py
  registry.py
  sandbox.py
  builtins.py
  plugins.py
  interpreter.py
  cli.py
examples/
  hello.pt
  async_thread.pt
plugins/
  example_plugin.py
```

## Kurulum ve Çalıştırma

```bash
python -m proton.cli examples/hello.pt
python -m proton.cli examples/async_thread.pt
python -m proton.cli               # REPL
python -m proton.cli --sandbox examples/hello.pt
```

## Proton Sözdizimi

```proton
x:10
@ "Merhaba"

f->
    @ "Selam"
    => 1

#mod math as m
sh: "echo test"
T-> f
await> __import__("asyncio").sleep(0, result=1)
```

## Komut Sistemi

`proton/builtins.py`, aşağıdaki komut ailelerini registry'ye kaydeder:

- Temel: `@ ! : => ? type> len>`
- Matematik: `+: -: *: /: ^: %: abs> round>`
- Kontrol/Fonksiyon: `if: elif: else: for: while: break> cont> f-> T-> bg> every> async-> await>`
- Dosya: `mk> del> dir> r< w> append> copy> move> size> perm>`
- Sistem: `sh: sh> sh! sys: kill> proc?> cpu?> ram?> disk?> env>`
- Ağ: `ping> get> post> port?> ip?> dns?>`
- Güvenlik: `hash> enc> dec> rand> uuid> sandbox> scan> firewall> sign> verify> vault>`
- Zaman: `now> wait> t: timer> date>`
- Python: `#mod py: pip> venv>`
- Veri: `push> pop> sort> map> filter> reduce> json> csv> stream> pipe> chunk> compress> decompress> index>`
- DB: `db.connect> db.query> db.insert> db.update> db.delete> db.close>`
- Web/AI/Donanım/Dağıtık/Meta/Geliştirici komutları da registry içinde yer alır.

Not: Harici servis/kitaplık gerektiren komutların bir bölümü "stub" (genişletilebilir yer tutucu) olarak işaretlenmiştir.

## Plugin Yazımı

`plugins/example_plugin.py` gibi bir dosyada:

```python
def register(registry):
    registry.register("my.cmd>", lambda args, ctx: print(args))
```

Interpreter `--plugin-dir` ile bu dosyaları otomatik yükler.

## Mimari Genişletme
- Yeni komut eklemek için `register_builtin_commands` içine handler ekleyin.
- Parser'da yeni söz dizimi kuralı için `ProtonParser._parse_statement` fonksiyonunu genişletin.
- Sandbox politikasını `SandboxPolicy` ile sıkılaştırın.
