# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Arranque de la ventana.

    python -m bioram.interfaz.app [archivo de datos]

Aquí se instala el gancho que atrapa cualquier error no previsto y lo muestra en
un cuadro. Hace falta porque en el ejecutable de Windows no hay consola: sin él,
un error se perdía sin que el usuario se enterara de nada.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from ..datos import Almacen, ArchivoDeDatosInvalido
from . import estilo
from .ventana import Ventana

POR_OMISION = 'bioram.db'


def _mostrar_error_no_previsto(tipo, valor, rastro):
    """Muestra en un cuadro cualquier error que nadie atrapó."""
    detalle = ''.join(traceback.format_exception(tipo, valor, rastro))
    sys.stderr.write(detalle)
    cuadro = QMessageBox()
    cuadro.setIcon(QMessageBox.Critical)
    cuadro.setWindowTitle('Ocurrió un error')
    cuadro.setText(
        'El programa encontró un problema que no esperaba.\n\n'
        f'{tipo.__name__}: {valor}\n\n'
        'Su trabajo guardado hasta ahora no se perdió: está en el archivo de '
        'datos. Si el problema se repite, mande el detalle de abajo a quien dio '
        'soporte al programa.')
    cuadro.setDetailedText(detalle)
    cuadro.exec()


def main(argv=None):
    argv = sys.argv if argv is None else argv
    ruta = Path(argv[1]) if len(argv) > 1 else Path(POR_OMISION)

    app = QApplication(argv[:1])
    app.setApplicationName('BioRAM LESP')
    estilo.aplicar(app)
    sys.excepthook = _mostrar_error_no_previsto

    try:
        almacen = Almacen(ruta)
    except ArchivoDeDatosInvalido as e:
        QMessageBox.critical(None, 'No se pudo abrir el archivo de datos', str(e))
        return 1

    ventana = Ventana(almacen)
    ventana.show()
    codigo = app.exec()
    almacen.cerrar()
    return codigo


if __name__ == '__main__':
    sys.exit(main())
