# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Dejar que Qt trabaje sin abrir ventanas, sin quedarse sin tipografías.

Hace falta en dos lugares: cuando la línea de comandos arma un PDF, y cuando
corren las pruebas. En ninguno de los dos hay pantalla, pero Qt necesita de
todos modos una aplicación viva para medir las letras.

La manera de lograrlo NO es la misma en todos los sistemas, y confundirlas
cuesta caro. En Linux la plataforma «offscreen» es lo correcto: dibuja en
memoria y encuentra las tipografías del sistema por fontconfig. En Windows esa
misma plataforma deja a Qt viendo CERO tipografías, así que el PDF sale con
sus páginas y su tamaño pero sin una sola letra que se pueda copiar o buscar
—inservible para un expediente—. En Windows la plataforma nativa dibuja fuera
de pantalla igual de bien y sí trae el catálogo completo del sistema, así que
ahí lo correcto es no tocar nada.
"""
from __future__ import annotations

import os
import sys


def plataforma_sin_ventana() -> str:
    """Prepara la plataforma de Qt y devuelve cuál quedó."""
    if not sys.platform.startswith('win'):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    return os.environ.get('QT_QPA_PLATFORM', '(la nativa del sistema)')
