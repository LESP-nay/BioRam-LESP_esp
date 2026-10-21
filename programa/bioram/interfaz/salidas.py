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


def imagenes_de(panel_resultados) -> list[bytes]:
    """Dibuja las gráficas tal como se ven y las devuelve como PNG."""
    imagenes = []
    for lienzo in getattr(panel_resultados, 'lienzos', []):
        mapa = lienzo.grab()
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
    sugerido = f'{cepa.nombre} - {evaluacion.tipo}.pdf'.replace('/', '-')
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
    sugerido = f'Resumen {area.nombre}.pdf'.replace('/', '-')
    ruta, filtro = QFileDialog.getSaveFileName(
        padre, 'Guardar el resumen del área', sugerido,
        'PDF (*.pdf);;Página web (*.html)')
    if not ruta:
        return
    ruta = Path(ruta)
    if not ruta.suffix:
        ruta = ruta.with_suffix('.html' if 'html' in filtro else '.pdf')
    html = reporte.html_de_area(almacen, area_id)
    try:
        if ruta.suffix.lower() == '.html':
            ruta.write_text(html, encoding='utf-8')
        else:
            _a_pdf(html, ruta)
    except OSError as e:
        QMessageBox.warning(padre, 'Guardar el resumen', f'No se pudo guardar:\n{e}')
        return
    QMessageBox.information(padre, 'Resumen guardado', f'Guardado en:\n{ruta}')
