@echo off
setlocal

REM Neon Browser .exe build script (Windows + Qt6 required)
if "%~1"=="" (
  set BUILD_DIR=build
) else (
  set BUILD_DIR=%~1
)

echo [1/3] Configuring CMake...
cmake -S . -B %BUILD_DIR% -G "Ninja"
if errorlevel 1 goto :fail

echo [2/3] Building...
cmake --build %BUILD_DIR% --config Release
if errorlevel 1 goto :fail

echo [3/3] Installing executable...
cmake --install %BUILD_DIR% --config Release --prefix %BUILD_DIR%\dist
if errorlevel 1 goto :fail

echo.
echo EXE hazir: %BUILD_DIR%\dist\neon_browser.exe
goto :eof

:fail
echo.
echo Build failed.
exit /b 1
