@echo off
setlocal

REM MSVC environment kontrolü
where cl >nul 2>nul
if errorlevel 1 (
    echo [HATA] cl bulunamadi. Lutfen "Developer Command Prompt for VS" acin.
    exit /b 1
)

set SRC=main.cpp mcu.cpp cpu.cpp alu.cpp ram.cpp rom.cpp bus.cpp pins.cpp clock.cpp peripheral.cpp led.cpp button.cpp screen.cpp timer.cpp emulator.cpp loader.cpp gui.cpp
set OUT=MCUEmulator.exe

echo [INFO] Derleme basliyor...
cl /std:c++17 /EHsc /W4 /nologo %SRC% /Fe:%OUT% user32.lib gdi32.lib comdlg32.lib
if errorlevel 1 (
    echo [HATA] Derleme basarisiz.
    exit /b 1
)

echo [OK] Derleme tamamlandi: %OUT%
endlocal
