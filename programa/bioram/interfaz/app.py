"""Arranque de la ventana.

    python -m bioram.interfaz.app [archivo de datos]
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ..datos import Almacen
from . import estilo
from .ventana import Ventana

POR_OMISION = 'bioram.db'


def main(argv=None):
    argv = sys.argv if argv is None else argv
    ruta = Path(argv[1]) if len(argv) > 1 else Path(POR_OMISION)

    app = QApplication(argv[:1])
    app.setApplicationName('BioRAM LESP')
    estilo.aplicar(app)
    almacen = Almacen(ruta)
    ventana = Ventana(almacen)
    ventana.show()
    codigo = app.exec()
    almacen.cerrar()
    return codigo


if __name__ == '__main__':
    sys.exit(main())
