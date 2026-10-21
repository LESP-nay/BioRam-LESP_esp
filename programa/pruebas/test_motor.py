"""El motor en Python tiene que dar los mismos números que el BioRAM original.

Las referencias de pruebas/referencias/*.tsv se calcularon con el motor Java
real (gov.sandia.bioram), con los escenarios de referencias/escenarios_*.json.
"""
import json
import math
from pathlib import Path

import pytest

from bioram import modelo, motor

AQUI = Path(__file__).resolve().parent
CUESTIONARIOS = AQUI.parent / 'bioram' / 'cuestionarios'
REFERENCIAS = AQUI / 'referencias'
TIPOS = ['bioseguridad', 'bioproteccion']


def cargar_referencia(tipo):
    """[(escenario, título del perfil, puntaje)] como lo calculó el motor Java."""
    filas = []
    for linea in (REFERENCIAS / f'{tipo}.tsv').read_text(encoding='utf-8').splitlines():
        escenario, titulo, valor = linea.split('\t')
        filas.append((escenario, titulo, float(valor)))
    return filas


@pytest.mark.parametrize('tipo', TIPOS)
def test_coincide_con_el_motor_java(tipo):
    cuestionario = modelo.cargar(CUESTIONARIOS / f'{tipo}.raml')
    escenarios = json.loads((REFERENCIAS / f'escenarios_{tipo}.json').read_text(encoding='utf-8'))
    por_titulo = {p.titulo: uuid for uuid, p in cuestionario.perfiles.items()}

    referencia = cargar_referencia(tipo)
    assert referencia, 'faltan los valores de referencia'

    for escenario, titulo, esperado in referencia:
        obtenido = motor.resultados(cuestionario, escenarios[escenario])[por_titulo[titulo]]
        assert obtenido == pytest.approx(esperado, abs=1e-10), (
            f'{tipo} / {escenario} / {titulo}: se esperaba {esperado}, salió {obtenido}')


@pytest.mark.parametrize('tipo', TIPOS)
def test_el_cuestionario_tiene_105_preguntas_en_un_solo_bloque(tipo):
    cuestionario = modelo.cargar(CUESTIONARIOS / f'{tipo}.raml')
    assert len(cuestionario.preguntas) == 105
    assert len(cuestionario.preguntas_en_orden()) == 105
    assert cuestionario.graficas and all(g.fondo for g in cuestionario.graficas)


def test_bioproteccion_trae_las_plantillas_de_agentes():
    cuestionario = modelo.cargar(CUESTIONARIOS / 'bioproteccion.raml')
    assert len(cuestionario.plantillas) == 80
    assert 'Bacillus anthracis' in cuestionario.plantillas


def test_division_entre_cero_da_infinito_como_en_java():
    assert motor._dividir(1.0, 0.0) == math.inf
    assert motor._dividir(-1.0, 0.0) == -math.inf
    assert math.isnan(motor._dividir(0.0, 0.0))


def test_raiz_de_negativo_no_es_un_numero_como_en_java():
    assert math.isnan(motor._potencia(-4.0, 0.5))
    assert motor._potencia(4.0, 0.5) == 2.0


def test_los_80_agentes_del_cuestionario_dan_los_mismos_puntajes():
    """Datos reales, no sintéticos: cada agente que trae el cuestionario."""
    cuestionario = modelo.incluido('bioproteccion')
    por_titulo = {p.titulo: uuid for uuid, p in cuestionario.perfiles.items()}
    filas = [l.split('\t') for l in
             (REFERENCIAS / 'agentes_bioproteccion.tsv').read_text(encoding='utf-8').splitlines()]
    assert len(filas) == 640

    for agente, titulo, esperado in filas:
        respuestas = cuestionario.plantillas[agente]
        obtenido = motor.resultados(cuestionario, respuestas)[por_titulo[titulo]]
        assert obtenido == pytest.approx(float(esperado), abs=1e-10), f'{agente} / {titulo}'
