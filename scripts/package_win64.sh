#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
PKG_ROOT="$ROOT_DIR/package"
PKG_DIR="$PKG_ROOT/windows"
ZIP_PATH="$DIST_DIR/system_widget_windows_x86_x64.zip"

rm -rf "$PKG_DIR"
mkdir -p "$PKG_DIR/win32" "$PKG_DIR/win64"

# Sadece kaynak paket: ikili dosya (.exe) eklenmez.
for arch in win32 win64; do
  cp "$ROOT_DIR/README.md" "$PKG_DIR/$arch/README.md"
  cp "$ROOT_DIR/CMakeLists.txt" "$PKG_DIR/$arch/CMakeLists.txt"
  mkdir -p "$PKG_DIR/$arch/src"
  cp "$ROOT_DIR/src/main.cpp" "$PKG_DIR/$arch/src/main.cpp"

  cat > "$PKG_DIR/$arch/BUILD_STATUS.txt" <<'TXT'
Bu paket kaynak-kod odaklidir; ikili dosya (.exe) bilerek eklenmez.
GitHub'da binary kısıtları nedeniyle sadece kaynaklar dağıtılır.

Windows'ta derlemek için:
  cmake -S . -B build
  cmake --build build --config Release

Çıktı:
  build/Release/system_widget.exe
TXT
done

cat > "$PKG_DIR/README_PACKAGE.txt" <<'TXT'
Bu paket hem Win32 (x86) hem Win64 (x64) sürümlerinin kaynak kodunu aynı zip içinde sunar.
- windows/win32
- windows/win64

Her klasörde:
- Kaynak kod (src/main.cpp)
- CMake dosyası
- BUILD_STATUS.txt

Not: İkili dosya (.exe) bu pakete dahil edilmez.
TXT

mkdir -p "$DIST_DIR"
(
  cd "$PKG_ROOT"
  zip -r "$ZIP_PATH" windows >/dev/null
)

echo "Created: $ZIP_PATH"
