@echo off
setlocal

if not exist build mkdir build

echo [1/2] Compiling...
g++ -std=c++17 -O2 -s -static -static-libgcc -static-libstdc++ -mwindows ^
    main.cpp mcu.cpp cpu.cpp alu.cpp ram.cpp rom.cpp bus.cpp pins.cpp clock.cpp emulator.cpp loader.cpp gui.cpp ^
    -lole32 -lcomdlg32 -lgdi32 -o build\mcu_emulator.exe
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo [2/2] Done: build\mcu_emulator.exe
exit /b 0
