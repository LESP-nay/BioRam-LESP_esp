"""El reparto en agente / instalaciones tiene que cubrir las 105 preguntas.

Los totales se comparan con los del modelo inglés de BioRAM 4.0.5, que divide
cada cuestionario en un módulo «Facility» y otro «Agent». Si alguien cambia un
cuestionario y el reparto deja de cuadrar, estas pruebas lo detienen.
"""
import pytest

from bioram import modelo, secciones

# Módulo «Facility» y módulo «Agent» del modelo inglés 4.0.5.
TOTALES = {
    'bioseguridad': {secciones.AGENTE: 53, secciones.INSTALACION: 52},
    'bioproteccion': {secciones.AGENTE: 59, secciones.INSTALACION: 46},
}


@pytest.mark.parametrize('tipo', modelo.TIPOS)
def test_todas_las_preguntas_tienen_seccion(tipo):
    cuestionario = modelo.incluido(tipo)
    reparto = secciones.por_pregunta(cuestionario, tipo)
    assert set(reparto) == set(cuestionario.preguntas), 'quedaron preguntas sin sección'


@pytest.mark.parametrize('tipo', modelo.TIPOS)
def test_los_totales_son_los_del_modelo_original(tipo):
    reparto = secciones.por_pregunta(modelo.incluido(tipo), tipo)
    contados = {s: sum(1 for v in reparto.values() if v == s) for s in secciones.ORDEN}
    assert contados == TOTALES[tipo]


@pytest.mark.parametrize('tipo', modelo.TIPOS)
def test_el_avance_se_cuenta_por_separado(tipo):
    cuestionario = modelo.incluido(tipo)
    reparto = secciones.por_pregunta(cuestionario, tipo)
    del_agente = [u for u, s in reparto.items() if s == secciones.AGENTE]

    avance = secciones.avance(cuestionario, tipo, {u: 4.0 for u in del_agente})
    assert avance[secciones.AGENTE][0] == len(del_agente)
    assert avance[secciones.INSTALACION][0] == 0


@pytest.mark.parametrize('tipo', modelo.TIPOS)
def test_la_consecuencia_depende_solo_del_agente(tipo):
    """Es lo que permite decir en la gráfica qué eje puede mover el laboratorio."""
    cuestionario = modelo.incluido(tipo)
    consecuencias = [p for p in cuestionario.perfiles.values()
                     if p.titulo.lower().startswith('consecuencia')]
    assert consecuencias
    for perfil in consecuencias:
        if 'comunidad' in perfil.titulo.lower():
            continue      # esta combina otras, se revisa aparte
        assert secciones.de_que_depende(cuestionario, tipo, perfil) == {secciones.AGENTE}, \
            f'{perfil.titulo} ya no depende solo del agente'


def test_las_probabilidades_mezclan_las_dos_secciones():
    cuestionario = modelo.incluido('bioseguridad')
    perfil = next(p for p in cuestionario.perfiles.values()
                  if p.titulo == 'Probabilidad por inhalación (individuo)')
    assert secciones.de_que_depende(cuestionario, 'bioseguridad', perfil) == \
        {secciones.AGENTE, secciones.INSTALACION}


def test_se_siguen_las_referencias_entre_perfiles():
    """Hay perfiles que no usan preguntas, sino otros perfiles."""
    cuestionario = modelo.incluido('bioseguridad')
    perfil = next(p for p in cuestionario.perfiles.values()
                  if p.titulo == 'Consecuencia de la enfermedad para la comunidad')
    assert secciones.de_que_depende(cuestionario, 'bioseguridad', perfil), \
        'sin seguir las referencias este perfil parecería no depender de nada'
