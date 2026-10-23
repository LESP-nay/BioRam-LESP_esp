# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Diagnostica por qué el texto de un PDF se puede copiar o no.

Un reporte que se imprime bien pero cuyo texto no se puede copiar ni buscar
sirve de poco en un expediente: no se puede citar, ni indexar, ni comprobar
años después. En Linux esto se resolvió eligiendo una tipografía con
codificación sana (Arial o su equivalente libre); en Windows hay que
comprobarlo, porque Qt empotra las tipografías de otra manera.

El programa genera un PDF de prueba y reporta:

  - qué tipografías ve Qt y si están las que el reporte pide;
  - qué tipografías quedaron empotradas en el PDF, con qué codificación, y
    sobre todo si cada una trae su tabla ToUnicode, que es la que permite que
    un lector sepa qué letra es cada dibujo;
  - si el texto se puede extraer, cuando hay con qué extraerlo.

    python3 empaquetar/diagnostico_pdf.py [salida.pdf]
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BUSCADAS = ('Arial', 'Liberation Sans', 'Helvetica')
MUESTRA = 'Mycobacterium tuberculosis'


def tipografias_que_ve_qt():
    from PySide6.QtGui import QFontDatabase
    familias = QFontDatabase.families()
    print(f'Qt ve {len(familias)} tipografías.')
    for buscada in BUSCADAS:
        hay = [f for f in familias if buscada.lower() in f.lower()]
        print(f'  {buscada:<18} {"sí: " + ", ".join(hay[:3]) if hay else "NO ESTÁ"}')
    return familias


def _objetos(datos: bytes):
    """Los objetos del PDF, descomprimidos cuando se puede."""
    for cuerpo in re.findall(rb'\d+ 0 obj(.*?)endobj', datos, re.S):
        yield cuerpo
    for flujo in re.findall(rb'stream\r?\n(.*?)endstream', datos, re.S):
        try:
            yield zlib.decompress(flujo)
        except zlib.error:
            pass


def tipografias_dentro_del_pdf(ruta: Path):
    datos = ruta.read_bytes()
    fuentes = {}
    for cuerpo in _objetos(datos):
        if b'/Type' not in cuerpo or b'/Font' not in cuerpo:
            continue
        nombre = re.search(rb'/BaseFont\s*/([^\s/>\]]+)', cuerpo)
        if not nombre:
            continue
        codificacion = re.search(rb'/Encoding\s*/?([^\s/>\]]+)', cuerpo)
        fuentes[nombre.group(1).decode('latin-1')] = {
            'codificacion': codificacion.group(1).decode('latin-1') if codificacion else '(ninguna)',
            'tiene_tounicode': b'/ToUnicode' in cuerpo,
        }
    print(f'\nEl PDF empotra {len(fuentes)} tipografía(s):')
    sin_mapa = 0
    for nombre, datos_fuente in sorted(fuentes.items()):
        mapa = 'sí' if datos_fuente['tiene_tounicode'] else 'NO'
        sin_mapa += not datos_fuente['tiene_tounicode']
        print(f'  {nombre:<40} codificación {datos_fuente["codificacion"]:<16} ToUnicode: {mapa}')
    if sin_mapa:
        print(f'\n  ATENCIÓN: {sin_mapa} tipografía(s) sin tabla ToUnicode. Sin esa')
        print('  tabla el lector dibuja bien las letras pero no sabe cuáles son,')
        print('  así que el texto no se puede copiar ni buscar.')
    return fuentes


def se_puede_extraer(ruta: Path):
    if not shutil.which('pdftotext'):
        print('\nNo hay pdftotext aquí, así que no se puede comprobar la extracción.')
        return None
    salida = subprocess.run(['pdftotext', str(ruta), '-'],
                            capture_output=True, text=True).stdout
    limpio = salida.replace('\f', '').strip()
    print(f'\npdftotext saca {len(limpio)} caracteres de texto '
          f'(sin contar los saltos de página).')
    if MUESTRA in salida:
        print(f'  «{MUESTRA}» aparece: el texto SÍ se puede copiar.')
        return True
    print(f'  «{MUESTRA}» NO aparece: el texto no se puede copiar.')
    if limpio:
        print(f'  Lo que sí sacó, al principio: {limpio[:120]!r}')
    return False


def main():
    destino = Path(sys.argv[1] if len(sys.argv) > 1 else 'diagnostico.pdf')

    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([sys.argv[0]])

    print(f'Plataforma de Qt: {os.environ.get("QT_QPA_PLATFORM", "(la del sistema)")}')
    print(f'Sistema: {sys.platform}\n')
    tipografias_que_ve_qt()

    from bioram import reporte
    from bioram.datos import Almacen, Respuesta
    from bioram.interfaz.salidas import _a_pdf

    almacen = Almacen(destino.parent / 'diagnostico.db')
    area = almacen.crear_area('Bacteriología')
    cepa = almacen.crear_cepa(area, MUESTRA)
    evaluacion = almacen.crear_evaluacion(cepa, 'bioseguridad')
    almacen.guardar_respuestas(evaluacion, {'p1': Respuesta(3.0)})
    _a_pdf(reporte.html_de_evaluacion(almacen, evaluacion), destino)
    almacen.cerrar()

    print(f'\nPDF generado: {destino} ({destino.stat().st_size} bytes)')
    tipografias_dentro_del_pdf(destino)
    se_puede_extraer(destino)
    return 0


if __name__ == '__main__':
    sys.exit(main())
