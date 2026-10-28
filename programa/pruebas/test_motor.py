# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
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


def test_maximo_y_minimo_contagian_el_no_es_un_numero_como_en_java():
    """Math.max y Math.min de Java contagian el NaN; max() y min() de Python no.

    Comprobado ejecutando Java: Math.max(nan, 1) y Math.max(1, nan) dan los dos
    NaN, mientras que en Python max(nan, 1.0) da nan pero max(1.0, nan) da 1.0.
    Sin esto, un modelo que produce NaN daría un número en lugar de NaN.
    """
    nan = math.nan
    assert math.isnan(motor._extremo([nan, 1.0], mayor=True))
    assert math.isnan(motor._extremo([1.0, nan], mayor=True))
    assert math.isnan(motor._extremo([nan, 1.0], mayor=False))
    assert math.isnan(motor._extremo([1.0, nan], mayor=False))
    assert motor._extremo([1.0, 3.0, 2.0], mayor=True) == 3.0
    assert motor._extremo([1.0, 3.0, 2.0], mayor=False) == 1.0


def test_el_cero_firmado_sale_como_en_java():
    """Math.max devuelve +0.0 y Math.min devuelve -0.0, sin importar el orden.

    En Python el resultado depende de cuál va primero. El signo del cero importa
    porque cambia el signo del infinito si después se divide entre él.
    """
    for valores in ([-0.0, 0.0], [0.0, -0.0]):
        assert math.copysign(1.0, motor._extremo(valores, mayor=True)) == 1.0
        assert math.copysign(1.0, motor._extremo(valores, mayor=False)) == -1.0


# El modelo inglés vigente de bioseguridad sí llega a producir «no es un número»;
# los dos cuestionarios en español no (comprobado sobre 40.016 escenarios cada
# uno). Por eso la prueba de ese camino usa el modelo inglés de Sandia, que está
# en historico/sandia/: si sólo se distribuye la carpeta programa/, se omite.
BIOSAFETY_EN = AQUI.parent.parent / 'historico' / 'sandia' / 'Biosafety.raml'


def test_los_valores_no_finitos_coinciden_con_el_motor_java():
    """228 valores del modelo inglés, 16 de ellos «no es un número»."""
    if not BIOSAFETY_EN.exists():
        pytest.skip(f'no está {BIOSAFETY_EN}, el modelo inglés de Sandia')

    cuestionario = modelo.cargar(BIOSAFETY_EN)
    escenarios = json.loads(
        (REFERENCIAS / 'escenarios_nan_biosafety_en.json').read_text(encoding='utf-8'))
    por_titulo = {p.titulo: uuid for uuid, p in cuestionario.perfiles.items()}

    filas = [l.split('\t') for l in
             (REFERENCIAS / 'nan_biosafety_en.tsv').read_text(encoding='utf-8').splitlines()]
    assert len(filas) == 228
    no_finitos = 0

    for escenario, titulo, texto_java in filas:
        obtenido = motor.resultados(cuestionario, escenarios[escenario])[por_titulo[titulo]]
        if 'nan' in texto_java.lower():
            no_finitos += 1
            assert math.isnan(obtenido), (
                f'{escenario} / {titulo}: Java da «no es un número» y salió {obtenido}')
        elif 'infinity' in texto_java.lower():
            no_finitos += 1
            esperado = math.inf if not texto_java.startswith('-') else -math.inf
            assert obtenido == esperado
        else:
            assert obtenido == pytest.approx(float(texto_java), abs=1e-10), (
                f'{escenario} / {titulo}: se esperaba {texto_java}, salió {obtenido}')

    assert no_finitos == 16, 'la referencia debe ejercitar el camino del NaN'


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
