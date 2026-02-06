@echo off
setlocal EnableExtensions

REM ------------------------------------------------------------
REM MCU Emulator - Windows EXE Build Script (MinGW g++)
REM ------------------------------------------------------------

set "APP_NAME=mcu_emulator.exe"
set "OUT_DIR=build"
set "OUT_EXE=%OUT_DIR%\%APP_NAME%"

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

REM 1) Compiler detection (prefer g++.exe from PATH)
where g++.exe >nul 2>nul
if errorlevel 1 (
    echo [ERROR] g++.exe PATH icinde bulunamadi.
    echo.
    echo Lutfen su adimlardan birini uygulayin:
    echo   1) MSYS2 MinGW64 kurun ve PATH'e ekleyin:
    echo      C:\msys64\mingw64\bin
    echo   2) Sonra yeni bir terminal acip bu dosyayi tekrar calistirin.
    echo.
    exit /b 1
)

for /f "delims=" %%G in ('where g++.exe') do (
    set "CXX=%%G"
    goto :compiler_found
)

:compiler_found

echo [INFO] Compiler: %CXX%
"%CXX%" --version | more +0

REM 2) Build flags
set "CXXFLAGS=-std=c++17 -O2 -Wall -Wextra -pedantic -s -mwindows -static -static-libgcc -static-libstdc++"
set "SOURCES=main.cpp mcu.cpp cpu.cpp alu.cpp ram.cpp rom.cpp bus.cpp pins.cpp clock.cpp emulator.cpp loader.cpp gui.cpp"
set "LDFLAGS=-lcomdlg32 -lgdi32 -luser32 -lkernel32 -lole32 -luuid -lwinmm -lws2_32"

echo.
echo [1/2] Building %OUT_EXE% ...
"%CXX%" %CXXFLAGS% %SOURCES% %LDFLAGS% -o "%OUT_EXE%"
if errorlevel 1 (
    echo.
    echo [ERROR] Build basarisiz.
    echo [TIP] MinGW yerine MSVC cl.exe ile derlemeye calisiyorsaniz bu script calismaz.
    exit /b 1
)

echo [2/2] Build tamamlandi: %OUT_EXE%

REM 3) Optional dependency check (if objdump exists)
where objdump.exe >nul 2>nul
if not errorlevel 1 (
    echo.
    echo [INFO] Runtime dependency kontrolu (objdump):
    objdump -p "%OUT_EXE%" | findstr /i "DLL Name"
)

echo.
echo [OK] Bitti.
exit /b 0
