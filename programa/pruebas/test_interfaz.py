"""La ventana no debe perder ni una respuesta por el camino.

Qt se dibuja sin pantalla (QT_QPA_PLATFORM=offscreen), así que estas pruebas
corren en cualquier servidor.
"""
import os

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication            # noqa: E402

from bioram import modelo                              # noqa: E402
from bioram.datos import Respuesta                     # noqa: E402
from bioram.interfaz.captura import PanelCaptura, opciones_de   # noqa: E402


@pytest.fixture(scope='module')
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize('tipo', modelo.TIPOS)
def test_se_muestran_todas_las_preguntas(app, tipo):
    panel = PanelCaptura(modelo.incluido(tipo))
    assert len(panel.filas) == 105


def test_se_muestran_todas_las_respuestas_guardadas(app):
    """Incluidas las de valor intermedio, que no figuran en los criterios."""
    cuestionario = modelo.incluido('bioproteccion')
    plantilla = cuestionario.plantillas['Bacillus anthracis']
    panel = PanelCaptura(cuestionario)
    panel.mostrar({u: Respuesta(v) for u, v in plantilla.items()})

    mostradas = {u: f._valor() for u, f in panel.filas.items() if f._valor() is not None}
    assert mostradas == plantilla, 'la pantalla perdió respuestas'
    assert f'{len(plantilla)}' in panel.avance.text()


def test_los_valores_intermedios_existen_de_verdad():
    """Si esto falla, la prueba de arriba dejó de comprobar lo que importa."""
    cuestionario = modelo.incluido('bioproteccion')
    plantilla = cuestionario.plantillas['Bacillus anthracis']
    intermedios = [v for u, v in plantilla.items()
                   if v not in [o for o, _ in opciones_de(cuestionario.preguntas[u])]]
    assert intermedios, 'ya no hay valores fuera de los criterios'


def test_las_opciones_salen_de_los_criterios(app):
    cuestionario = modelo.incluido('bioseguridad')
    pregunta = cuestionario.preguntas_en_orden()[0]
    opciones = opciones_de(pregunta)
    assert opciones, 'la primera pregunta debería traer criterios'
    assert all(isinstance(v, float) and texto for v, texto in opciones)


def test_marcar_aproximada_se_refleja(app):
    cuestionario = modelo.incluido('bioseguridad')
    panel = PanelCaptura(cuestionario)
    pregunta = cuestionario.preguntas_en_orden()[0]
    panel.mostrar({pregunta.uuid: Respuesta(4.0, aproximada=True)})
    assert panel.filas[pregunta.uuid].aproximada.isChecked()
