#!/usr/bin/env python3
"""Rellena traduccion/biosafety_es.json reutilizando la traducción publicada.

BiosafetyRAM_es.raml traduce una versión anterior del modelo: tiene otros UUID y
otro orden, así que no se puede mapear por ruta como en bioprotección. El puente
es la plantilla inglesa que acompaña a esa traducción en el código fuente
(util/translatedQuestionMover/modelTemplates/Biosafety.raml), que sí comparte los
175 UUID con el español. Las 105 preguntas de ambos modelos se emparejan una a
una (ver emparejar.py) y de ahí se toma la traducción. Las etiquetas que no son
preguntas vienen del glosario.

Uso:
  python reusar_biosafety.py <plantilla_en.raml>
"""
import json
import re
import sys

import emparejar
import raml_es
from glosario_biosafety import ETIQUETAS
from reusar import normalizar

# Por debajo de este parecido, el par se informa para revisarlo a mano.
UMBRAL_REVISION = 0.80


def preguntas(path):
    """Devuelve [(titulo, detalle, uuid)] de cada pregunta del modelo."""
    return [(q.findtext('title') or '', q.findtext('detailText') or '', q.findtext('uuid'))
            for q in raml_es.read_model(path).iter('QuestionSetQuestion')]


def main(plantilla_en):
    with open('biosafety_es.json', encoding='utf-8') as f:
        table = json.load(f)

    root = raml_es.read_model('../Biosafety.raml')
    padre = {}

    def walk(elem):
        for hijo in elem:
            padre[id(hijo)] = elem
            walk(hijo)

    walk(root)

    # Emparejamiento uno a uno con el modelo antiguo, vía su plantilla inglesa.
    nuevas = list(root.iter('QuestionSetQuestion'))
    antiguas_en = preguntas(plantilla_en)
    es_por_uuid = {u: (t, d) for t, d, u in preguntas('fuente/BiosafetyRAM_es.raml')}
    pares = emparejar.emparejar([(q.findtext('title') or '', q.findtext('detailText') or '')
                                 for q in nuevas],
                                [(t, d) for t, d, _ in antiguas_en])

    traduccion, dudosos = {}, []
    for i, j, sim in pares:
        es_t, es_d = es_por_uuid[antiguas_en[j][2]]
        titulo, detalle = nuevas[i].find('title'), nuevas[i].find('detailText')
        if titulo is not None:
            traduccion[id(titulo)] = es_t
        if detalle is not None:
            traduccion[id(detalle)] = es_d
        if sim < UMBRAL_REVISION:
            dudosos.append((sim, nuevas[i].findtext('title') or '', es_t))

    # La portada se toma de la traducción publicada.
    portada = raml_es.read_model('fuente/BiosafetyRAM_es.raml').findtext('ModelInformation/frontHTML')

    elementos = {k: el for k, el in raml_es.iter_texts(root)}
    rellenos, pendientes = 0, []
    for entry in table:
        if entry['es'].strip():
            continue
        el = elementos[entry['id']]
        if entry['id'].endswith(':frontHTML'):
            es = portada
        elif id(el) in traduccion:
            es = traduccion[id(el)]
        else:
            es = ETIQUETAS.get(el.text.strip())
        if not es:
            pendientes.append((entry['id'], padre[id(el)].tag, el.text[:70]))
            continue
        # La portada es HTML: se copia tal cual, sin normalizar espacios.
        entry['es'] = es if entry['id'].endswith(':frontHTML') else normalizar(es)
        rellenos += 1

    with open('biosafety_es.json', 'w', encoding='utf-8') as f:
        json.dump(table, f, ensure_ascii=False, indent=1)
    completos = sum(1 for e in table if e['es'].strip())
    print(f'{rellenos} rellenos, {completos}/{len(table)} completos')
    for pid, tag, texto in pendientes:
        print(f'  PENDIENTE [{tag}] {texto}')
    for sim, en, es in sorted(dudosos):
        print(f'  REVISAR ({sim:.2f})\n    EN: {normalizar(en)[:150]}\n    ES: {normalizar(es)[:150]}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
