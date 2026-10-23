# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""La ventana no debe perder ni una respuesta por el camino.

Qt se dibuja sin abrir ventanas, así que estas pruebas corren en cualquier
servidor. Cómo se logra eso depende del sistema: ver bioram/sin_pantalla.py.
"""
import pytest

from bioram.sin_pantalla import plataforma_sin_ventana

plataforma_sin_ventana()

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
    assert panel.barra.value() == len(plantilla), 'el avance no cuadra con lo guardado'


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


def test_el_filtro_de_faltantes(app):
    cuestionario = modelo.incluido('bioseguridad')
    panel = PanelCaptura(cuestionario)
    primera = cuestionario.preguntas_en_orden()[0]
    panel.mostrar({primera.uuid: Respuesta(4.0)})

    # isHidden() y no isVisible(): la ventana no está en pantalla durante la prueba.
    panel.grupo.button(1).setChecked(True)      # «Faltan»
    assert panel.filas[primera.uuid].isHidden()
    panel.grupo.button(2).setChecked(True)      # «Contestadas»
    assert not panel.filas[primera.uuid].isHidden()
    assert sum(1 for f in panel.orden if not f.isHidden()) == 1


def test_marcar_aproximada_se_refleja(app):
    cuestionario = modelo.incluido('bioseguridad')
    panel = PanelCaptura(cuestionario)
    pregunta = cuestionario.preguntas_en_orden()[0]
    panel.mostrar({pregunta.uuid: Respuesta(4.0, aproximada=True)})
    assert panel.filas[pregunta.uuid].aproximada.isChecked()
