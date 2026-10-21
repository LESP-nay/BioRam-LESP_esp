@echo off
rem Inicia BioRAM en espanol sin usar los .exe, por si el antivirus los bloquea.
rem Sin argumento abre Bioseguridad; para Bioproteccion:  BioRAM.bat Biosecurity_es.raml
setlocal
set "JAR=%~dp0bioram-4.0.5-es-java-actual.jar"
set "MODELO=%~1"
if "%MODELO%"=="" set "MODELO=Biosafety_es.raml"
where javaw >nul 2>nul
if errorlevel 1 (
  echo No se encontro Java en este equipo.
  echo Instale Java 8 o una version posterior desde https://adoptium.net
  pause
  exit /b 1
)
start "BioRAM" javaw -jar "%JAR%" "%~dp0%MODELO%"
