@echo off
echo ========================================================
echo  Compilando Lee y Juega con PyInstaller para Windows
echo ========================================================

REM Asegurar que estamos en el directorio raíz del proyecto
cd /d "%~dp0\.."

REM Ejecutar PyInstaller con ventana completa, icono y recursos
pyinstaller --noconfirm --onedir --windowed ^
    --name "LeeYJuega" ^
    --add-data "lee_y_juega\recursos;recursos" ^
    --hidden-import "PySide6" ^
    --hidden-import "sqlalchemy" ^
    --hidden-import "matplotlib" ^
    --hidden-import "argon2" ^
    --hidden-import "httpx" ^
    --hidden-import "win32crypt" ^
    --hidden-import "win32gui" ^
    --hidden-import "win32process" ^
    run.py

echo.
echo Compilación finalizada. Ejecutable generado en: dist\LeeYJuega\LeeYJuega.exe
echo.
pause
