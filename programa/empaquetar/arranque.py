# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Punto de entrada del ejecutable.

Hace falta este archivo intermedio porque bioram/interfaz/app.py usa importes
relativos («from .. import ubicacion») y por eso no se puede ejecutar como
programa principal: hay que importarlo como parte del paquete.
"""
import sys

from bioram.interfaz.app import main

if __name__ == '__main__':
    sys.exit(main())
