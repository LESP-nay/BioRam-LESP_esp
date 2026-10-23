# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Dónde guarda el programa el trabajo del laboratorio.

Esto importa sobre todo cuando el programa corre como ejecutable. Al dar doble
clic a un `.exe`, o al abrirlo desde un acceso directo o desde la barra de
tareas, la carpeta de trabajo del proceso puede ser cualquiera: si el archivo
de datos se guardara «donde esté parado el programa», acabaría en
C:\\Windows\\System32 o fallaría por falta de permiso, y el laboratorio no
encontraría su trabajo.

La regla, en orden:

1. La ruta que se indique al abrir el programa, si se indica alguna.
2. **Junto al programa**, si ahí se puede escribir. Es el modo portátil: la
   carpeta entera se copia a una memoria USB y el trabajo viaja dentro, que es
   como el laboratorio ya usa la versión en Java.
3. Si no se puede escribir junto al programa (porque está instalado en
   «Archivos de programa», por ejemplo), en los **Documentos** del usuario,
   dentro de una carpeta «BioRAM LESP».

Fuera del ejecutable —en desarrollo y en las pruebas— se conserva el
comportamiento de siempre: «bioram.db» en la carpeta de trabajo.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

NOMBRE = 'bioram.db'
CARPETA = 'BioRAM LESP'


def empaquetado() -> bool:
    """¿Está corriendo como ejecutable y no desde el código fuente?"""
    return getattr(sys, 'frozen', False)


def carpeta_del_programa() -> Path:
    """La carpeta donde vive el ejecutable, o la del código si no lo está."""
    if empaquetado():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _se_puede_escribir(carpeta: Path) -> bool:
    prueba = carpeta / '.bioram-prueba-de-escritura'
    try:
        prueba.touch()
        prueba.unlink()
        return True
    except OSError:
        return False


def carpeta_de_documentos() -> Path:
    """Los Documentos del usuario, o lo más parecido en este sistema."""
    if os.name == 'nt':
        perfil = os.environ.get('USERPROFILE')
        if perfil:
            documentos = Path(perfil) / 'Documents'
            if documentos.is_dir():
                return documentos
            # Windows en español, si la carpeta no está redirigida
            españoles = Path(perfil) / 'Documentos'
            if españoles.is_dir():
                return españoles
            return Path(perfil)
    casa = Path.home()
    for nombre in ('Documents', 'Documentos'):
        if (casa / nombre).is_dir():
            return casa / nombre
    return casa


def archivo_de_datos(indicado=None) -> Path:
    """La ruta del archivo de datos que debe usar el programa."""
    if indicado:
        return Path(indicado)
    if not empaquetado():
        return Path(NOMBRE)

    junto = carpeta_del_programa()
    if (junto / NOMBRE).is_file() or _se_puede_escribir(junto):
        return junto / NOMBRE

    destino = carpeta_de_documentos() / CARPETA
    try:
        destino.mkdir(parents=True, exist_ok=True)
    except OSError:
        return junto / NOMBRE      # que falle con un mensaje claro al abrir
    return destino / NOMBRE


def donde_estan_los_cuestionarios() -> Path:
    """La carpeta de los .raml, que PyInstaller copia junto al programa."""
    base = getattr(sys, '_MEIPASS', None)
    if base:
        return Path(base) / 'bioram' / 'cuestionarios'
    return Path(__file__).resolve().parent / 'cuestionarios'
