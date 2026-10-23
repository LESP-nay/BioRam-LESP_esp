@echo off
rem BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Publica de Nayarit.
rem Software libre bajo la Licencia Publica General de GNU v3 o posterior (ver LICENSE).
rem Metodo y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
rem
rem   Arma "BioRAM LESP.exe" en una computadora con Windows.
rem
rem   Hace falta Python 3.11 o posterior, de python.org, marcando
rem   "Add python.exe to PATH" al instalarlo.
rem
rem   Para usarlo: abra esta carpeta en el Explorador y de doble clic a este
rem   archivo. Al terminar, el ejecutable queda en programa\dist\.
setlocal

echo.
echo ============================================================
echo   BioRAM LESP - armado del ejecutable para Windows
echo ============================================================
echo.

cd /d "%~dp0\.."

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: no se encontro Python.
    echo.
    echo   Instalelo desde https://www.python.org/downloads/
    echo   y marque la casilla "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

echo [1/4] Version de Python:
python --version
echo.

echo [2/4] Instalando lo que hace falta ^(PySide6 y PyInstaller^)...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet PySide6 pyinstaller pytest
if errorlevel 1 (
    echo ERROR: no se pudieron instalar las dependencias.
    pause
    exit /b 1
)
echo      listo.
echo.

echo [3/4] Corriendo las pruebas antes de armar nada...
python -m pytest -q
if errorlevel 1 (
    echo.
    echo ERROR: las pruebas no pasaron. No se arma el ejecutable.
    echo        Avise de esto antes de seguir.
    pause
    exit /b 1
)
echo      todas pasaron.
echo.

echo [4/4] Armando el ejecutable. Esto tarda unos minutos...
python -m PyInstaller empaquetar\bioram_lesp.spec --noconfirm
if errorlevel 1 (
    echo ERROR: fallo el armado.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Listo.
echo.
echo   El programa quedo en:
echo       %CD%\dist\BioRAM LESP.exe
echo.
echo   Copielo a donde lo vaya a usar. El archivo de datos
echo   ^(bioram.db^) se crea junto a el la primera vez que se abre.
echo ============================================================
echo.
pause
