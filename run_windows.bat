@echo off
setlocal

REM EXE'yi calistirir ve cikista pencereyi acik tutar.
set EXE_NAME=emulator.exe
if not "%~1"=="" set EXE_NAME=%~1

if not exist "%EXE_NAME%" (
  echo [ERROR] "%EXE_NAME%" bulunamadi.
  echo [INFO] Once build_windows.bat komutunu calistirin.
  pause
  exit /b 1
)

echo [INFO] Running %EXE_NAME% ...
set MCU_WAIT_ON_EXIT=1
"%EXE_NAME%"
set EXIT_CODE=%ERRORLEVEL%

echo.
echo [INFO] Program exit code: %EXIT_CODE%
pause
exit /b %EXIT_CODE%
