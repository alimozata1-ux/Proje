@echo off
setlocal

REM Windows için system-monitor.exe derleme scripti
REM Kullanım:
REM   1) Go kurulu olmalı: https://go.dev/dl/
REM   2) Bu klasörde terminal açıp: build.bat
REM
REM Not:
REM   - Bu script doğrudan Windows .exe üretir.
REM   - Varsayılan hedef: windows/amd64

set "TARGET_OS=windows"
set "TARGET_ARCH=amd64"
set "OUTPUT=system-monitor.exe"

where go >nul 2>nul
if errorlevel 1 (
  echo [HATA] Go bulunamadi. Once Go kurun: https://go.dev/dl/
  exit /b 1
)

echo [1/4] Go surumu:
go version
if errorlevel 1 (
  echo [HATA] go version calistirilamadi.
  exit /b 1
)

echo [2/4] Mod bilgisi kontrol ediliyor...
if not exist go.mod (
  echo [HATA] go.mod bulunamadi. Komutu proje klasorunde calistirin.
  exit /b 1
)

echo [3/4] Bagimliliklar indirilmeye calisiliyor (opsiyonel)...
go mod download
if errorlevel 1 (
  echo [UYARI] Bagimlilik indirme adimi basarisiz. Derleme yine de denenecek.
)

echo [4/4] %OUTPUT% derleniyor ^(%TARGET_OS%/%TARGET_ARCH%^)...
set "GOOS=%TARGET_OS%"
set "GOARCH=%TARGET_ARCH%"
set "CGO_ENABLED=0"
go build -o %OUTPUT% .
if errorlevel 1 (
  echo [HATA] Derleme basarisiz.
  echo [IPUCU] Ag/proxy engeli varsa once bagimliliklari indirebildiginiz bir ortamda tekrar deneyin.
  exit /b 1
)

echo [BASARILI] %OUTPUT% olusturuldu.
endlocal
