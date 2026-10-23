# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Guardar el reporte: PDF, HTML y CSV.

El PDF lo arma Qt a partir del mismo HTML del reporte, así que no hace falta
ningún programa extra ni una impresora instalada.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QMarginsF
from PySide6.QtGui import QPageLayout, QPageSize, QPdfWriter, QTextDocument
from PySide6.QtWidgets import QFileDialog, QMessageBox

from .. import reporte
from ..datos import Almacen


# Lo que Windows no admite en un nombre de archivo. El nombre de una cepa puede
# traer cualquiera de estos (por ejemplo «Influenza A/H1N1» o «BSL-3: sala 2») y
# entonces el diálogo de guardar lo rechaza o guarda con otro nombre.
_PROHIBIDOS_EN_ARCHIVO = '<>:"/\\|?*'
_LARGO_MAXIMO = 80


def nombre_de_archivo_seguro(nombre: str, extension: str = '') -> str:
    """Convierte un nombre cualquiera en uno que Windows acepte."""
    limpio = ''.join('-' if c in _PROHIBIDOS_EN_ARCHIVO or ord(c) < 0x20 else c
                     for c in str(nombre or ''))
    limpio = ' '.join(limpio.split()).strip(' .')      # Windows no quiere punto final
    if len(limpio) > _LARGO_MAXIMO:
        limpio = limpio[:_LARGO_MAXIMO].rstrip()
    return (limpio or 'sin nombre') + extension


def imagenes_de(panel_resultados) -> list[bytes]:
    """Dibuja las gráficas tal como se ven y las devuelve como PNG.

    Al doble de la resolución de la pantalla: en el PDF se imprimen, y una
    captura al tamaño de la ventana sale con los bordes y las letras dentadas.
    """
    imagenes = []
    for lienzo in getattr(panel_resultados, 'lienzos', []):
        mapa = lienzo.imagen(escala=2.0) if hasattr(lienzo, 'imagen') else lienzo.grab()
        datos = QByteArray()
        memoria = QBuffer(datos)
        memoria.open(QBuffer.WriteOnly)
        mapa.save(memoria, 'PNG')
        imagenes.append(bytes(datos))
    return imagenes


def _a_pdf(html: str, ruta: Path):
    documento = QTextDocument()
    documento.setHtml(html)
    escritor = QPdfWriter(str(ruta))
    escritor.setPageLayout(QPageLayout(QPageSize(QPageSize.A4), QPageLayout.Portrait,
                                       QMarginsF(14, 14, 14, 14), QPageLayout.Millimeter))
    escritor.setTitle(ruta.stem)
    # Sin tocar el tamaño del documento: si se fija, Qt mete todo el reporte en
    # una sola página kilométrica en vez de partirlo en hojas.
    documento.print_(escritor)


FILTROS = 'PDF (*.pdf);;Página web (*.html);;Hoja de cálculo (*.csv)'


def guardar_reporte(padre, almacen: Almacen, evaluacion_id: int, imagenes=None):
    """Pregunta dónde guardar y en qué formato, y lo guarda."""
    evaluacion = almacen.evaluacion(evaluacion_id)
    cepa = almacen.cepa(evaluacion.cepa_id)
    sugerido = nombre_de_archivo_seguro(f'{cepa.nombre} - {evaluacion.tipo}', '.pdf')
    ruta, filtro = QFileDialog.getSaveFileName(padre, 'Guardar el reporte', sugerido, FILTROS)
    if not ruta:
        return
    ruta = Path(ruta)
    if not ruta.suffix:
        ruta = ruta.with_suffix({'PDF (*.pdf)': '.pdf',
                                 'Página web (*.html)': '.html',
                                 'Hoja de cálculo (*.csv)': '.csv'}.get(filtro, '.pdf'))
    try:
        if ruta.suffix.lower() == '.csv':
            ruta.write_text(reporte.csv_de_evaluacion(almacen, evaluacion_id),
                            encoding='utf-8-sig')   # para que Excel lea los acentos
        else:
            html = reporte.html_de_evaluacion(almacen, evaluacion_id, imagenes)
            if ruta.suffix.lower() == '.html':
                ruta.write_text(html, encoding='utf-8')
            else:
                _a_pdf(html, ruta)
    except OSError as e:
        QMessageBox.warning(padre, 'Guardar el reporte', f'No se pudo guardar:\n{e}')
        return
    QMessageBox.information(padre, 'Reporte guardado', f'Guardado en:\n{ruta}')


def guardar_resumen_de_area(padre, almacen: Almacen, area_id: int):
    area = almacen.area(area_id)
    sugerido = nombre_de_archivo_seguro(f'Resumen {area.nombre}', '.pdf')
    ruta, filtro = QFileDialog.getSaveFileName(
        padre, 'Guardar el resumen del área', sugerido,
        'PDF (*.pdf);;Página web (*.html)')
    if not ruta:
        return
    ruta = Path(ruta)
    if not ruta.suffix:
        ruta = ruta.with_suffix('.html' if 'html' in filtro else '.pdf')
    try:
        html = reporte.html_de_area(almacen, area_id)
        if ruta.suffix.lower() == '.html':
            ruta.write_text(html, encoding='utf-8')
        else:
            _a_pdf(html, ruta)
    except OSError as e:
        QMessageBox.warning(padre, 'Guardar el resumen', f'No se pudo guardar:\n{e}')
        return
    QMessageBox.information(padre, 'Resumen guardado', f'Guardado en:\n{ruta}')
