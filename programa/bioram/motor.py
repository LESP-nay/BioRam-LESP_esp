"""El cálculo de los resultados de BioRAM.

Reproduce exactamente el motor del programa original en Java
(classes/model/ResultObject.java y cada ResultMathOp*.java), incluidos sus
casos raros: la división no protege contra el cero, una resta con un número de
hijos distinto de dos se convierte en suma, y una multiplicación sin hijos vale
cero. Se respetan porque los modelos oficiales se diseñaron sobre ese
comportamiento y cambiarlo cambiaría los resultados de una evaluación.

La prueba de que coincide está en pruebas/test_motor.py: compara contra 540
valores calculados con el motor Java real.
"""
from __future__ import annotations

import math

from .modelo import Cuestionario, Nodo

# Igual que ResultMathOpExponent: al sumar puntajes casi nulos a veces sale un
# negativo minúsculo en vez de cero, y elevarlo a 0.5 daría "no es un número".
EPSILON = 1e-6


def _dividir(a: float, b: float) -> float:
    """División con la semántica de Java: entre cero da infinito, no un error."""
    if b == 0.0:
        if a == 0.0 or math.isnan(a):
            return math.nan
        signo = math.copysign(1.0, a) * math.copysign(1.0, b)
        return math.copysign(math.inf, signo)
    return a / b


def _potencia(base: float, exponente: float) -> float:
    """Potencia con la semántica de Math.pow: la raíz de un negativo no es un número."""
    try:
        resultado = math.pow(base, exponente)
    except (ValueError, OverflowError):
        return math.nan
    return resultado


def puntaje(nodo: Nodo, respuestas: dict[str, float],
            perfiles: dict[str, 'object'] | None = None) -> float:
    """Puntaje de un nodo del árbol de resultados."""
    tipo = nodo.tipo

    if tipo == 'ResultQuestion':
        return respuestas.get(nodo.pregunta_uuid, 0.0) * nodo.peso

    if tipo == 'ResultMathOpConstant':
        return nodo.constante * nodo.peso

    if tipo == 'ResultReference':
        otro = (perfiles or {}).get(nodo.perfil_uuid)
        if otro is None:
            return 0.0
        return nodo.peso * puntaje(otro.raiz, respuestas, perfiles)

    hijos = [puntaje(h, respuestas, perfiles) for h in nodo.hijos]

    if tipo == 'ResultMathOpSubtract' and len(hijos) == 2:
        return (hijos[0] - hijos[1]) * nodo.peso

    if tipo == 'ResultMathOpDivide' and len(hijos) == 2:
        return _dividir(hijos[0], hijos[1]) * nodo.peso

    if tipo == 'ResultMathOpMultiply':
        if not hijos:
            return 0.0
        producto = 1.0
        for h in hijos:
            producto *= h
        return producto * nodo.peso

    if tipo in ('ResultMathOpMin', 'ResultMathOpMax'):
        if not hijos:
            return 0.0
        extremo = min(hijos) if tipo.endswith('Min') else max(hijos)
        return extremo * nodo.peso

    if tipo == 'ResultMathOpExponent':
        suma = sum(hijos)
        if -EPSILON < suma < 0:
            suma = 0.0
        return _potencia(suma, nodo.exponente) * nodo.peso

    # ResultTitle, ResultCategory, ResultMathOpAdd y una resta o división con
    # un número de hijos distinto de dos: suma ponderada.
    return sum(hijos) * nodo.peso


def resultados(cuestionario: Cuestionario,
               respuestas: dict[str, float]) -> dict[str, float]:
    """Puntaje de cada perfil de resultados, por su identificador."""
    return {uuid: puntaje(perfil.raiz, respuestas, cuestionario.perfiles)
            for uuid, perfil in cuestionario.perfiles.items()}


def puntos_de_grafica(cuestionario: Cuestionario,
                      respuestas: dict[str, float]) -> list[list[tuple]]:
    """Para cada gráfica, sus puntos como (leyenda, x, y)."""
    puntajes = resultados(cuestionario, respuestas)
    return [[(p.leyenda, puntajes.get(p.perfil_x, 0.0), puntajes.get(p.perfil_y, 0.0))
             for p in grafica.puntos]
            for grafica in cuestionario.graficas]
