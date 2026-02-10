@echo off
setlocal

REM Windows için system-monitor.exe derleme scripti
REM Kullanım:
REM   1) Go kurulu olmalı: https://go.dev/dl/
REM   2) Bu klasörde terminal açıp: build.bat

where go >nul 2>nul
if errorlevel 1 (
  echo [HATA] Go bulunamadi. Once Go kurun: https://go.dev/dl/
  exit /b 1
)

echo [1/3] Go surumu:
go version
if errorlevel 1 (
  echo [HATA] go version calistirilamadi.
  exit /b 1
)

echo [2/3] Bagimliliklar indiriliyor (go mod tidy)...
go mod tidy
if errorlevel 1 (
  echo [HATA] Bagimliliklar indirilemedi. Ag/proxy ayarlarinizi kontrol edin.
  exit /b 1
)

echo [3/3] system-monitor.exe derleniyor...
go build -o system-monitor.exe .
if errorlevel 1 (
  echo [HATA] Derleme basarisiz.
  exit /b 1
)

echo [BASARILI] system-monitor.exe olusturuldu.
endlocal
