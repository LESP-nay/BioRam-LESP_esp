#!/usr/bin/env python3
"""Cambia "centro" por "instalación" en las tablas de traducción.

La traducción publicada de Sandia dice "centro" para facility. En México se usa
"instalación", que es femenino, así que el cambio arrastra los determinantes (el
centro -> la instalación), las preposiciones contraídas (del, al) y los
adjetivos que acompañan al sustantivo (centro receptor -> instalación
receptora).

El script imprime cada texto que modifica para revisarlo. Es idempotente: si ya
se aplicó, no encuentra nada que cambiar.

Uso:
  python termino_instalacion.py biosafety_es.json biosecurity_es.json
"""
import json
import re
import sys

# Adjetivos que aparecen justo después del sustantivo y hay que concordar.
ADJETIVOS = {'receptor': 'receptora', 'encubierto': 'encubierta'}

REGLAS = [
    # Determinantes y contracciones, respetando mayúscula inicial.
    (r'\bEl centro\b', 'La instalación'),
    (r'\bel centro\b', 'la instalación'),
    (r'\bEste centro\b', 'Esta instalación'),
    (r'\beste centro\b', 'esta instalación'),
    (r'\bEse centro\b', 'Esa instalación'),
    (r'\bese centro\b', 'esa instalación'),
    (r'\bun centro\b', 'una instalación'),
    (r'\bUn centro\b', 'Una instalación'),
    (r'\bdel centro\b', 'de la instalación'),
    (r'\bDel centro\b', 'De la instalación'),
    (r'\bal centro\b', 'a la instalación'),
    (r'\bAl centro\b', 'A la instalación'),
    (r'\blos centros\b', 'las instalaciones'),
    (r'\bLos centros\b', 'Las instalaciones'),
    (r'\bcentros\b', 'instalaciones'),
    (r'\bCentros\b', 'Instalaciones'),
    (r'\bcentro\b', 'instalación'),
    (r'\bCentro\b', 'Instalación'),
]


def convertir(texto):
    for patron, reemplazo in REGLAS:
        texto = re.sub(patron, reemplazo, texto)
    for masculino, femenino in ADJETIVOS.items():
        texto = re.sub(rf'\b(instalaci(?:ón|ones)) {masculino}\b', rf'\1 {femenino}', texto)
    return texto


def main(rutas):
    total = 0
    for ruta in rutas:
        with open(ruta, encoding='utf-8') as f:
            tabla = json.load(f)
        cambios = 0
        for entrada in tabla:
            nuevo = convertir(entrada['es'])
            if nuevo != entrada['es']:
                print(f'--- {ruta}\n  antes: {entrada["es"][:160]}\n  ahora: {nuevo[:160]}')
                entrada['es'] = nuevo
                cambios += 1
        if cambios:
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(tabla, f, ensure_ascii=False, indent=1)
        print(f'{ruta}: {cambios} textos modificados')
        total += cambios
    print(f'total: {total}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
