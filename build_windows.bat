@echo off
setlocal

REM Windows icin .exe derleme scripti
REM Kullanim:
REM   build_windows.bat
REM   build_windows.bat my_emulator.exe
REM   build_windows.bat my_emulator.exe amd64

set OUTPUT=emulator.exe
if not "%~1"=="" set OUTPUT=%~1

set TARGET_ARCH=amd64
if not "%~2"=="" set TARGET_ARCH=%~2

where go >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Go bulunamadi. Lutfen Go 1.21+ kurun ve PATH'e ekleyin.
  pause
  exit /b 1
)

echo [INFO] Building %OUTPUT% for windows/%TARGET_ARCH% ...
set GOOS=windows
set GOARCH=%TARGET_ARCH%
set CGO_ENABLED=0
go build -o %OUTPUT% .
if errorlevel 1 (
  echo [ERROR] Build failed.
  pause
  exit /b 1
)

echo [OK] Build completed: %OUTPUT%
echo [INFO] Cift tiklama ile calistiracaksaniz run_windows.bat kullanin.
exit /b 0
