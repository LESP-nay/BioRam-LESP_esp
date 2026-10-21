@echo off
rem Inicia BioRAM en espanol sin usar el .exe, por si el antivirus lo bloquea.
setlocal
set "JAR=%~dp0bioram-4.0.5-es-java-actual.jar"
where javaw >nul 2>nul
if errorlevel 1 (
  echo No se encontro Java en este equipo.
  echo Instale Java 8 o una version posterior desde https://adoptium.net
  pause
  exit /b 1
)
start "BioRAM" javaw -jar "%JAR%"
