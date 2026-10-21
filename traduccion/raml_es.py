#!/usr/bin/env python3
"""Herramienta de traducción al español de los modelos BioRAM (.raml).

Un .raml es un zip con model.xml (el perfil) y media/ (imágenes). Esta
herramienta solo reemplaza textos visibles; no toca UUID, pesos, fórmulas ni
la estructura, por lo que el modelo traducido calcula exactamente igual que el
original en inglés.

Uso:
  python raml_es.py extraer   Biosafety.raml   traduccion/biosafety_es.json
  python raml_es.py construir Biosafety.raml   traduccion/biosafety_es.json  Biosafety_es.raml
  python raml_es.py verificar Biosafety.raml   Biosafety_es.raml

La tabla JSON es la fuente de la traducción: una entrada por texto con su ID
estable, el original en inglés ("en") y la traducción ("es").
"""
import json
import sys
import zipfile
import xml.etree.ElementTree as ET

# Etiquetas cuyo texto ve el usuario en la aplicación.
TEXT_TAGS = ('title', 'detailText', 'chartTitle', 'legendTitle', 'frontHTML')


def read_model(raml_path):
    with zipfile.ZipFile(raml_path) as z:
        return ET.fromstring(z.read('model.xml'))


def iter_texts(root):
    """Devuelve (id, elemento) para cada texto traducible, en orden de documento.

    El ID es la ruta por índices desde la raíz, prefijada con el UUID más
    cercano (pregunta, categoría o perfil de resultados) para poder leerla. Es
    estable mientras no cambie la estructura del modelo inglés. La ruta completa
    es necesaria porque hay UUID repetidos entre módulos.
    """
    out = []

    def walk(elem, anchor, rel):
        uuid = elem.findtext('uuid')
        if uuid:
            anchor = uuid
        for i, child in enumerate(elem):
            path = f'{rel}/{i}' if rel else str(i)
            if child.tag in TEXT_TAGS:
                if child.text and child.text.strip():
                    out.append((f'{anchor}:{path}:{child.tag}', child))
            else:
                walk(child, anchor, path)

    walk(root, 'root', '')
    keys = [k for k, _ in out]
    assert len(set(keys)) == len(keys), 'IDs duplicados'
    return out


def extraer(raml_path, json_path):
    root = read_model(raml_path)
    entries = [{'id': key, 'en': elem.text, 'es': ''} for key, elem in iter_texts(root)]
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
    print(f'{len(entries)} textos extraídos a {json_path}')


def construir(raml_path, json_path, out_path):
    with open(json_path, encoding='utf-8') as f:
        table = {e['id']: e for e in json.load(f)}
    with zipfile.ZipFile(raml_path) as z:
        root = ET.fromstring(z.read('model.xml'))
        texts = iter_texts(root)
        errors = []
        for key, elem in texts:
            entry = table.get(key)
            if entry is None:
                errors.append(f'falta en la tabla: {key}')
            elif entry['en'] != elem.text:
                errors.append(f'el inglés cambió (re-extraer): {key}')
            elif not entry['es'].strip():
                errors.append(f'sin traducir: {key}')
            else:
                elem.text = entry['es']
        extra = set(table) - {k for k, _ in texts}
        errors += [f'ID desconocido en la tabla: {k}' for k in sorted(extra)]
        if errors:
            print('\n'.join(errors[:50]))
            sys.exit(f'{len(errors)} errores; no se generó {out_path}')
        xml = ET.tostring(root, encoding='UTF-8', xml_declaration=True)
        with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as out:
            for info in z.infolist():
                data = xml if info.filename == 'model.xml' else z.read(info.filename)
                out.writestr(info, data)
    print(f'{len(texts)} textos traducidos -> {out_path}')


def verificar(en_path, es_path):
    """Comprueba que el modelo traducido es idéntico al original salvo los textos."""
    a, b = read_model(en_path), read_model(es_path)
    ea, eb = list(a.iter()), list(b.iter())
    if len(ea) != len(eb):
        sys.exit(f'distinto número de elementos: {len(ea)} vs {len(eb)}')
    translated = {id(e) for _, e in iter_texts(b)}
    diffs = 0
    for x, y in zip(ea, eb):
        if x.tag != y.tag or x.attrib != y.attrib:
            diffs += 1
        elif id(y) not in translated and (x.text or '').strip() != (y.text or '').strip():
            diffs += 1
            print(f'difiere <{x.tag}>: {x.text!r} -> {y.text!r}')
    with zipfile.ZipFile(en_path) as za, zipfile.ZipFile(es_path) as zb:
        for name in za.namelist():
            if name != 'model.xml' and za.read(name) != zb.read(name):
                diffs += 1
                print(f'archivo distinto: {name}')
    if diffs:
        sys.exit(f'{diffs} diferencias fuera de los textos')
    print(f'OK: estructura, UUID, pesos e imágenes idénticos ({len(ea)} elementos)')


if __name__ == '__main__':
    cmds = {'extraer': extraer, 'construir': construir, 'verificar': verificar}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](*sys.argv[2:])
