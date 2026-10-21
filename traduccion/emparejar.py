"""Emparejamiento uno a uno entre las preguntas de dos modelos en inglés.

Hace falta porque la traducción publicada de bioseguridad corresponde a una
versión anterior del modelo, con otros UUID y otro orden. Muchas preguntas
comparten el mismo texto de detalle (todas las vías de infección lo comparten),
así que emparejar por texto, de una en una, colapsaría preguntas distintas en la
misma traducción. Un emparejamiento uno a uno lo impide: cada pregunta del
modelo vigente recibe exactamente una pregunta del modelo antiguo.

El costo es la distancia de texto entre los pares; se resuelve con el método
húngaro, que da el emparejamiento de costo total mínimo.
"""
import difflib
import re


def norm(texto):
    return re.sub(r'\s+', ' ', texto.replace('\xa0', ' ')).strip().lower()


def similitud(a, b):
    """Parecido entre dos preguntas (título, detalle); el título pesa más."""
    titulo = difflib.SequenceMatcher(None, norm(a[0]), norm(b[0])).ratio()
    detalle = difflib.SequenceMatcher(None, norm(a[1]), norm(b[1])).ratio()
    return 0.75 * titulo + 0.25 * detalle


def hungaro(costo):
    """Asignación de costo mínimo (algoritmo húngaro, O(n^3)).

    costo es una matriz n x n. Devuelve una lista donde el elemento i es la
    columna asignada a la fila i.
    """
    n = len(costo)
    INF = float('inf')
    u = [0.0] * (n + 1)
    v = [0.0] * (n + 1)
    p = [0] * (n + 1)   # p[j] = fila asignada a la columna j
    way = [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = 0
            for j in range(1, n + 1):
                if used[j]:
                    continue
                cur = costo[i0 - 1][j - 1] - u[i0] - v[j]
                if cur < minv[j]:
                    minv[j] = cur
                    way[j] = j0
                if minv[j] < delta:
                    delta = minv[j]
                    j1 = j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    asignacion = [0] * n
    for j in range(1, n + 1):
        asignacion[p[j] - 1] = j - 1
    return asignacion


def emparejar(nuevas, antiguas):
    """Devuelve [(indice_nueva, indice_antigua, similitud)] uno a uno."""
    if len(nuevas) != len(antiguas):
        raise ValueError(f'distinto número de preguntas: {len(nuevas)} vs {len(antiguas)}')
    sim = [[similitud(a, b) for b in antiguas] for a in nuevas]
    costo = [[1.0 - s for s in fila] for fila in sim]
    asignacion = hungaro(costo)
    return [(i, j, sim[i][j]) for i, j in enumerate(asignacion)]
