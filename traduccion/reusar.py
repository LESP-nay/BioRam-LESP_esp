#!/usr/bin/env python3
"""Rellena la tabla de traducción reutilizando un .raml en español ya existente.

Las traducciones al español publicadas por Sandia (BiosecurityRAM_es.raml y
BiosafetyRAM_es.raml) se reutilizan tal cual: son las preguntas oficiales. Esta
herramienta solo las traslada al modelo inglés vigente y normaliza el formato,
que quedó con artefactos de la conversión desde MS Word (espacios dobles,
espacios duros, líneas en blanco entre opciones y numeración "(N)" en los
títulos que el modelo inglés no tiene).

Uso (desde traduccion/):
  python reusar.py biosecurity_es.json fuente/BiosecurityRAM_es.raml
"""
import json
import re
import sys

import raml_es

# Etiquetas de perfiles de resultados y de gráficas, que la traducción
# publicada dejó en inglés.
ETIQUETAS = {
    'Facility': 'Instalación',
    'Agent': 'Agente',
    'Risk to Humans': 'Riesgo para los seres humanos',
    'Risk to Animals': 'Riesgo para los animales',
    'Consequence': 'Consecuencia',
    'Likelihood': 'Probabilidad',
    'Adversary With Access': 'Adversario con acceso',
    'Adversary Without Access': 'Adversario sin acceso',
    'Agent Potential - Risk to Human From Adversary With Access':
        'Potencial del agente: riesgo para los seres humanos por un adversario con acceso',
    'Agent Potential - Risk to Human From Adversary Without Access':
        'Potencial del agente: riesgo para los seres humanos por un adversario sin acceso',
    'Agent Potential - Risk to Animals From Adversary With Access':
        'Potencial del agente: riesgo para los animales por un adversario con acceso',
    'Agent Potential - Risk to Animals From Adversary Without Access':
        'Potencial del agente: riesgo para los animales por un adversario sin acceso',
    'Consequence - Risk to Human From Adversary With Access':
        'Consecuencia: riesgo para los seres humanos por un adversario con acceso',
    'Consequence - Risk to Human From Adversary Without Access':
        'Consecuencia: riesgo para los seres humanos por un adversario sin acceso',
    'Consequence - Risk to Animals From Adversary With Access':
        'Consecuencia: riesgo para los animales por un adversario con acceso',
    'Consequence - Risk to Animals From Adversary Without Access':
        'Consecuencia: riesgo para los animales por un adversario sin acceso',
}


# En dos opciones el modelo original en inglés viene truncado y el traductor lo
# marcó con una nota en inglés. La nota se conserva, pero en español.
NOTA_INCOMPLETA = re.compile(r'[\(\[]\s*incomplete sentence\s*[\)\]]\.?')


def normalizar(texto):
    texto = texto.replace('\xa0', ' ').replace('‑', '-')
    texto = NOTA_INCOMPLETA.sub('(frase incompleta en el modelo original)', texto)
    lineas = []
    for linea in texto.split('\n'):
        linea = re.sub(r' {2,}', ' ', linea).strip()
        # "4  = ..." -> "4 = ..."
        linea = re.sub(r'^(\d) *=', r'\1 =', linea)
        if linea:
            lineas.append(linea)
    texto = '\n'.join(lineas)
    # La numeración "(17) ¿Qué tipo..." no existe en el modelo inglés.
    return re.sub(r'^\(\d+\)\s*', '', texto)


def main(json_path, old_raml):
    with open(json_path, encoding='utf-8') as f:
        table = json.load(f)
    old = {k: e.text for k, e in raml_es.iter_texts(raml_es.read_model(old_raml))}
    rellenos = pendientes = 0
    for entry in table:
        if entry['es'].strip():
            continue
        es = old.get(entry['id'])
        if es is None or es.strip() == entry['en'].strip():
            es = ETIQUETAS.get(entry['en'].strip())
        if es is None:
            pendientes += 1
            continue
        entry['es'] = normalizar(es)
        rellenos += 1
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(table, f, ensure_ascii=False, indent=1)
    print(f'{rellenos} rellenos, {pendientes} pendientes de traducir, '
          f'{sum(1 for e in table if e["es"].strip())}/{len(table)} completos')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
