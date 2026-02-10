@echo off
setlocal

REM Windows icin .exe derleme scripti
REM Kullanim:
REM   build_windows.bat
REM   build_windows.bat my_emulator.exe

set OUTPUT=emulator.exe
if not "%~1"=="" set OUTPUT=%~1

echo [INFO] Building %OUTPUT% ...
go build -o %OUTPUT% .
if errorlevel 1 (
  echo [ERROR] Build failed.
  exit /b 1
)

echo [OK] Build completed: %OUTPUT%
exit /b 0
