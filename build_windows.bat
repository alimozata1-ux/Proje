@echo off
setlocal

echo [1/3] Go mod dependencies indiriliyor...
go mod tidy
if errorlevel 1 goto :error

echo [2/3] Windows EXE derleniyor...
set GOOS=windows
set GOARCH=amd64
go build -ldflags="-H windowsgui" -o NeonBrowser.exe .
if errorlevel 1 goto :error

echo [3/3] Tamamlandi: NeonBrowser.exe
exit /b 0

:error
echo Derleme sirasinda hata olustu.
exit /b 1
