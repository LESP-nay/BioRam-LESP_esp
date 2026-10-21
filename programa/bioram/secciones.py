"""Las dos secciones de cada cuestionario: el agente y las instalaciones.

Las 105 preguntas se contestan de corrido, pero vienen de dos bloques distintos:
unas describen el **agente biológico** con el que se trabaja, y otras las
**instalaciones del laboratorio** y cómo se trabaja en ellas. La diferencia
importa al leer los resultados: lo del agente es lo que hay, y lo de las
instalaciones es sobre lo que el laboratorio puede actuar.

El reparto no es una interpretación nuestra: el modelo inglés de BioRAM 4.0.5
divide cada cuestionario justo así, en un módulo «Facility» y otro «Agent».
Aquí se repite ese corte por categoría de primer nivel, y las pruebas
comprueban que los totales coinciden con los del modelo original
(bioseguridad 52 y 53; bioprotección 46 y 59).
"""
from __future__ import annotations

from .modelo import Categoria, Cuestionario, Nodo, Pregunta

AGENTE = 'agente'
INSTALACION = 'instalacion'

NOMBRE = {AGENTE: 'Agente biológico',
          INSTALACION: 'Instalaciones del laboratorio'}
EXPLICACION = {
    AGENTE: 'Lo que el agente es: cómo infecta, qué tan grave es y qué '
            'consecuencias trae. No cambia con lo que haga el laboratorio.',
    INSTALACION: 'Lo que hace y tiene el laboratorio: procedimientos, equipo, '
                 'controles y medidas. Es donde el laboratorio puede actuar.',
}
ORDEN = (AGENTE, INSTALACION)

# Categoría de primer nivel -> sección. Las claves son los identificadores, que
# no cambian aunque se corrija el texto de un título.
CATEGORIAS = {
    'bioseguridad': {
        '119a2737-d88a-4c3b-839a-1ea0ea30fdc1': AGENTE,       # Probabilidad de infección
        '286f7ffe-a250-42bd-a2b9-0ff2f33bb2dc': AGENTE,       # Categoría principal: Consecuencias
        '4692804d-7854-41fe-ada8-fbe7dba2731f': INSTALACION,  # Probabilidad de exposición
        '6b831782-0568-44f4-93b5-996213621993': INSTALACION,  # Categoría principal: Mitigaciones
    },
    'bioproteccion': {
        # «Agente potencial» contiene «Probabilidad de robo de la instalación»:
        # son las preguntas del centro (perímetro, accesos, personal, transporte).
        '585cc747-5fde-47f5-bb5e-ca52ed733a46': INSTALACION,
        '7b3eaec5-460f-4ee5-bcb5-bd4ab9303cfa': AGENTE,       # Puede usarse como arma
        '8aaa2697-5268-4040-b542-1fb43d38a8ce': AGENTE,       # Consecuencias de un ataque
    },
}


def _preguntas_de(categoria: Categoria):
    for hijo in categoria.hijos:
        if isinstance(hijo, Pregunta):
            yield hijo.uuid
        else:
            yield from _preguntas_de(hijo)


def por_pregunta(cuestionario: Cuestionario, tipo: str) -> dict[str, str]:
    """Identificador de pregunta -> sección a la que pertenece."""
    reparto = CATEGORIAS[tipo]
    resultado = {}
    for hijo in cuestionario.raiz.hijos:
        if isinstance(hijo, Categoria) and hijo.uuid in reparto:
            for uuid in _preguntas_de(hijo):
                resultado[uuid] = reparto[hijo.uuid]
    return resultado


def avance(cuestionario: Cuestionario, tipo: str,
           respuestas) -> dict[str, tuple[int, int]]:
    """Por sección, cuántas preguntas se contestaron de cuántas."""
    secciones = por_pregunta(cuestionario, tipo)
    cuenta = {s: [0, 0] for s in ORDEN}
    for uuid, seccion in secciones.items():
        cuenta[seccion][1] += 1
        if uuid in respuestas:
            cuenta[seccion][0] += 1
    return {s: tuple(v) for s, v in cuenta.items()}


def _preguntas_del_perfil(nodo: Nodo, perfiles, vistos=None):
    """Preguntas de las que depende un resultado, siguiendo las referencias."""
    vistos = set() if vistos is None else vistos
    if nodo.tipo == 'ResultQuestion' and nodo.pregunta_uuid:
        yield nodo.pregunta_uuid
    if nodo.tipo == 'ResultReference' and nodo.perfil_uuid:
        if nodo.perfil_uuid not in vistos:
            vistos.add(nodo.perfil_uuid)
            otro = perfiles.get(nodo.perfil_uuid)
            if otro is not None:
                yield from _preguntas_del_perfil(otro.raiz, perfiles, vistos)
    for hijo in nodo.hijos:
        yield from _preguntas_del_perfil(hijo, perfiles, vistos)


def de_que_depende(cuestionario: Cuestionario, tipo: str, perfil) -> set[str]:
    """Secciones de las que depende un perfil de resultados."""
    secciones = por_pregunta(cuestionario, tipo)
    usadas = {secciones[u] for u in _preguntas_del_perfil(perfil.raiz, cuestionario.perfiles)
              if u in secciones}
    return usadas


def resumen_de_dependencia(secciones: set[str]) -> str:
    """Frase corta para explicar de qué depende un resultado."""
    if secciones == {AGENTE}:
        return 'Depende solo del agente biológico'
    if secciones == {INSTALACION}:
        return 'Depende solo de las instalaciones del laboratorio'
    if not secciones:
        return 'No depende de ninguna pregunta'
    return 'Depende del agente y de las instalaciones'
