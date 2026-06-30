@echo off
setlocal

echo Installing dependencies...
pip install -r requirements-build.txt
if errorlevel 1 exit /b 1

echo Building executable...
pyinstaller --noconfirm build.spec
if errorlevel 1 exit /b 1

echo.
echo Done: dist\serch_size.exe
pause
