# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""El almacén guarda lo que el programa original perdía."""
import pytest

from bioram import modelo
from bioram.datos import Almacen, Respuesta


@pytest.fixture
def alm(tmp_path):
    with Almacen(tmp_path / 'prueba.db') as a:
        yield a


def test_area_cepa_evaluacion(alm):
    area = alm.crear_area('Bacteriología', responsable='QFB Pérez')
    cepa = alm.crear_cepa(area, 'Mycobacterium tuberculosis')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')

    assert [a.nombre for a in alm.areas()] == ['Bacteriología']
    assert [c.nombre for c in alm.cepas(area)] == ['Mycobacterium tuberculosis']
    assert alm.evaluacion(eva).tipo == 'bioseguridad'


def test_una_cepa_lleva_las_dos_evaluaciones(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.crear_evaluacion(cepa, 'bioproteccion')
    assert {e.tipo for e in alm.evaluaciones(cepa)} == {'bioseguridad', 'bioproteccion'}


def test_se_guarda_que_una_respuesta_es_aproximada(alm):
    """Lo que el BioRAM original mostraba pero no guardaba."""
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.guardar_respuestas(eva, {'p1': Respuesta(4.0, aproximada=True),
                                 'p2': Respuesta(2.0)})

    guardadas = alm.respuestas(eva)
    assert guardadas['p1'].aproximada is True
    assert guardadas['p2'].aproximada is False
    assert alm.puntajes(eva) == {'p1': 4.0, 'p2': 2.0}


def test_guardar_dos_veces_actualiza_en_vez_de_duplicar(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.guardar_respuestas(eva, {'p1': 1.0})
    alm.guardar_respuestas(eva, {'p1': 3.0})
    assert alm.puntajes(eva) == {'p1': 3.0}


def test_historial_y_restauracion(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.guardar_respuestas(eva, {'p1': 1.0})
    v1 = alm.guardar_version(eva, autor='Pérez', nota='primera revisión')

    alm.guardar_respuestas(eva, {'p1': 4.0})
    assert alm.puntajes(eva) == {'p1': 4.0}

    assert [v.nota for v in alm.versiones(eva)] == ['primera revisión']
    alm.restaurar_version(v1)
    assert alm.puntajes(eva) == {'p1': 1.0}


def test_copiar_respuestas_de_otra_evaluacion(alm):
    area = alm.crear_area('A')
    a = alm.crear_evaluacion(alm.crear_cepa(area, 'cepa 1'), 'bioseguridad')
    alm.guardar_respuestas(a, {'p1': 2.0, 'p2': 4.0})
    b = alm.crear_evaluacion(alm.crear_cepa(area, 'cepa 2'), 'bioseguridad', copiar_de=a)
    assert alm.puntajes(b) == {'p1': 2.0, 'p2': 4.0}


def test_no_se_copian_respuestas_entre_tipos_distintos(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    a = alm.crear_evaluacion(cepa, 'bioseguridad')
    with pytest.raises(ValueError):
        alm.crear_evaluacion(cepa, 'bioproteccion', copiar_de=a)


def test_borrar_un_area_se_lleva_sus_cepas_y_evaluaciones(alm):
    area = alm.crear_area('A')
    cepa = alm.crear_cepa(area, 'cepa')
    alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.borrar_area(area)
    assert alm.areas() == [] and alm.cepas() == [] and alm.evaluaciones() == []


def test_tipo_invalido(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    with pytest.raises(ValueError):
        alm.crear_evaluacion(cepa, 'quimica')


def test_el_archivo_se_vuelve_a_abrir(tmp_path):
    ruta = tmp_path / 'lab.db'
    with Almacen(ruta) as a:
        eva = a.crear_evaluacion(a.crear_cepa(a.crear_area('A'), 'cepa'), 'bioseguridad')
        a.guardar_respuestas(eva, {'p1': 3.0})
    with Almacen(ruta) as a:
        assert a.puntajes(1) == {'p1': 3.0}


def test_resumen_para_la_pantalla_principal(alm):
    area = alm.crear_area('Bacteriología')
    cepa = alm.crear_cepa(area, 'M. tuberculosis')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.guardar_respuestas(eva, {f'p{i}': 1.0 for i in range(10)})

    fila = alm.resumen()[0]
    assert fila['area'] == 'Bacteriología'
    assert fila['cepa'] == 'M. tuberculosis'
    assert fila['respondidas'] == 10


def test_las_plantillas_de_agentes_se_pueden_guardar(alm):
    cuestionario = modelo.incluido('bioproteccion')
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    eva = alm.crear_evaluacion(cepa, 'bioproteccion')
    alm.guardar_respuestas(eva, cuestionario.plantillas['Bacillus anthracis'])
    assert len(alm.puntajes(eva)) == len(cuestionario.plantillas['Bacillus anthracis'])
