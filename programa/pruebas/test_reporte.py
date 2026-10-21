"""El reporte tiene que llevar todo lo que el laboratorio necesita entregar."""
import csv
import io
import shutil
import subprocess

import pytest

from bioram import modelo, reporte
from bioram.datos import Almacen, Respuesta


@pytest.fixture
def lab(tmp_path):
    alm = Almacen(tmp_path / 'lab.db')
    area = alm.crear_area('Bacteriología', responsable='QFB Pérez')
    cepa = alm.crear_cepa(area, 'Mycobacterium tuberculosis')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad', responsables='QFB Pérez',
                               procedimiento='Cultivo y tipificación')
    cuestionario = modelo.incluido('bioseguridad')
    preguntas = cuestionario.preguntas_en_orden()
    alm.guardar_respuestas(eva, {p.uuid: Respuesta(4.0) for p in preguntas[:60]})
    alm.guardar_respuestas(eva, {preguntas[0].uuid: Respuesta(4.0, aproximada=True)})
    yield alm, area, cepa, eva
    alm.cerrar()


def test_el_reporte_lleva_los_datos_de_la_evaluacion(lab):
    alm, _, _, eva = lab
    html = reporte.html_de_evaluacion(alm, eva)
    for esperado in ('Mycobacterium tuberculosis', 'Bacteriología', 'QFB Pérez',
                     'Cultivo y tipificación', 'Agente biológico',
                     'Instalaciones del laboratorio', 'Resultados'):
        assert esperado in html, f'falta «{esperado}» en el reporte'


def test_avisa_cuando_faltan_preguntas(lab):
    alm, _, _, eva = lab
    html = reporte.html_de_evaluacion(alm, eva)
    assert 'Faltan 45 preguntas' in html
    assert 'cuentan como cero' in html


def test_marca_las_respuestas_estimadas(lab):
    alm, _, _, eva = lab
    assert '(estimación)' in reporte.html_de_evaluacion(alm, eva)


def test_el_reporte_incluye_las_graficas_cuando_se_le_pasan(lab):
    alm, _, _, eva = lab
    html = reporte.html_de_evaluacion(alm, eva, imagenes=[b'\x89PNG falsa', b''])
    assert 'data:image/png;base64,' in html
    assert 'Gráficas de riesgo' in html


def test_el_csv_trae_una_fila_por_pregunta_y_los_resultados(lab):
    alm, _, _, eva = lab
    filas = list(csv.reader(io.StringIO(reporte.csv_de_evaluacion(alm, eva))))
    encabezado = filas[0]
    assert encabezado[:4] == ['área', 'cepa', 'evaluación', 'sección']

    preguntas = [f for f in filas[1:] if len(f) == len(encabezado) and f[4].isdigit()]
    assert len(preguntas) == 105
    contestadas = [f for f in preguntas if f[6]]
    assert len(contestadas) == 60
    assert any(f[7] == 'sí' for f in preguntas), 'no se marcó la estimación'
    assert any(fila and fila[0] == 'resultado' for fila in filas), 'faltan los resultados'


def test_el_resumen_del_area_compara_las_cepas(lab):
    alm, area, _, _ = lab
    otra = alm.crear_cepa(area, 'Salmonella spp.')
    alm.crear_evaluacion(otra, 'bioseguridad')
    html = reporte.html_de_area(alm, area)
    assert 'Mycobacterium tuberculosis' in html and 'Salmonella spp.' in html
    assert 'comparación entre cepas' in html


@pytest.mark.skipif(not shutil.which('pdftotext'), reason='falta pdftotext')
def test_el_pdf_se_pagina_y_su_texto_se_puede_copiar(lab, tmp_path):
    """Si el PDF no se puede copiar ni buscar, no sirve para un expediente."""
    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    pytest.importorskip('PySide6')
    from PySide6.QtWidgets import QApplication
    from bioram.interfaz.salidas import _a_pdf

    QApplication.instance() or QApplication([])
    alm, _, _, eva = lab
    destino = tmp_path / 'reporte.pdf'
    _a_pdf(reporte.html_de_evaluacion(alm, eva), destino)

    assert destino.stat().st_size > 10_000
    texto = subprocess.run(['pdftotext', str(destino), '-'], capture_output=True,
                           text=True, check=True).stdout
    assert 'Mycobacterium tuberculosis' in texto
    assert 'Bacteriología' in texto
    assert texto.count('\f') >= 3, 'el reporte debería ocupar varias páginas'
