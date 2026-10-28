# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Corrige erratas de la traducción oficial de Sandia al español.

Los cuestionarios en español los tradujo Sandia, no este laboratorio, y traen
erratas que se detectaron comparando los 105 pares de preguntas contra el
original en inglés. Algunas no son cosméticas: **niegan la mejor opción**, con
lo que el evaluador no puede contestar correctamente porque el nivel 0 dice lo
mismo que el nivel 4.

Esta herramienta sólo cambia **texto de criterios y de títulos**. No toca
pesos, ni límites, ni la estructura, ni los perfiles de resultados: los
puntajes no se mueven, y `verificar.sh` lo comprueba.

Cada corrección lleva el texto en inglés del que sale, para que se pueda
auditar. Se ejecuta así:

    python3 traduccion/corregir_erratas.py --revisar      # sólo dice qué haría
    python3 traduccion/corregir_erratas.py --aplicar      # lo aplica
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent

# Los cuatro archivos en español que hay que mantener iguales entre sí.
ARCHIVOS = [
    RAIZ / 'historico' / 'java-es' / 'Biosafety_es.raml',
    RAIZ / 'historico' / 'java-es' / 'Biosecurity_es.raml',
    RAIZ / 'programa' / 'bioram' / 'cuestionarios' / 'bioseguridad.raml',
    RAIZ / 'programa' / 'bioram' / 'cuestionarios' / 'bioproteccion.raml',
]


class Errata:
    """Una corrección: qué texto se busca, por qué, y con qué se reemplaza."""

    def __init__(self, clave, gravedad, porque, ingles, viejo, nuevo):
        self.clave = clave
        self.gravedad = gravedad      # 'grave' si impide contestar bien
        self.porque = porque
        self.ingles = ingles          # el texto original, para poder auditarlo
        self.viejo = viejo
        self.nuevo = nuevo


ERRATAS = [
    Errata(
        'mca-nivel-0', 'grave',
        'La mejor opción está negada: el nivel 0 dice lo mismo que el nivel 4, '
        'así que un laboratorio que sí tiene procedimientos no tiene cómo '
        'contestarlo.',
        '0 = Written procedures are in place and implemented to ensure timely and '
        'accurate recording, reporting and auditing of materials subject to MC&A',
        'No existen procedimientos escritos ni implementados para asegurar los '
        'registros oportunos y precisos, los informes',
        'Existen procedimientos escritos e implementados para asegurar los '
        'registros oportunos y precisos, los informes',
    ),
    Errata(
        'secuelas-nivel-1', 'grave',
        'Al nivel 1 le falta el «no»: queda diciendo que las repercusiones leves '
        'impiden funcionar con normalidad, igual que el nivel 4, y la escala '
        'deja de tener sentido.',
        '1 = Mild long-term impacts do not impede the hosts ability to function normally',
        'Tiene repercusiones leves a largo plazo que impiden la capacidad del '
        'hospedador de funcionar con normalidad',
        'Tiene repercusiones leves a largo plazo que no impiden al hospedador '
        'funcionar con normalidad',
    ),
    Errata(
        'morbilidad-moderada', 'importante',
        'La pregunta es de morbilidad (cuántos enferman) y el nivel dice '
        'mortalidad (cuántos mueren). Son cosas distintas y la confusión cambia '
        'lo que el evaluador contesta.',
        '3 = Moderate Morbidity (25% to 75%)',
        'Mortalidad moderada (entre el 25% y el 75%)',
        'Morbilidad moderada (entre el 25% y el 75%)',
    ),
    Errata(
        'morbilidad-baja', 'importante',
        'Igual que la anterior, en el nivel 1 de la misma pregunta.',
        '1 = Low Morbidity (1% to 25%)',
        'Mortalidad baja (entre el 1% y el 25%)',
        'Morbilidad baja (entre el 1% y el 25%)',
    ),
]

TEXTOS = ('title', 'detailText')


def _aplicar_a_arbol(raiz, erratas):
    """Devuelve {clave: cuántas veces se cambió} y modifica el árbol."""
    cuenta = {e.clave: 0 for e in erratas}
    for elem in raiz.iter():
        if elem.tag not in TEXTOS or not elem.text:
            continue
        texto = elem.text
        for e in erratas:
            if e.viejo in texto:
                texto = texto.replace(e.viejo, e.nuevo)
                cuenta[e.clave] += 1
        if texto != elem.text:
            elem.text = texto
    return cuenta


def _reescribir(ruta, raiz):
    """Reescribe el .raml con el model.xml nuevo, dejando el resto intacto."""
    temporal = ruta.with_suffix('.raml.nuevo')
    with zipfile.ZipFile(ruta) as z, \
         zipfile.ZipFile(temporal, 'w', zipfile.ZIP_DEFLATED) as salida:
        for info in z.infolist():
            if info.filename == 'model.xml':
                salida.writestr(info, ET.tostring(raiz, encoding='UTF-8',
                                                  xml_declaration=True))
            else:
                salida.writestr(info, z.read(info.filename))
    shutil.move(temporal, ruta)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    grupo = p.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--revisar', action='store_true',
                       help='sólo informa qué cambiaría, sin tocar nada')
    grupo.add_argument('--aplicar', action='store_true',
                       help='aplica las correcciones a los cuatro archivos')
    args = p.parse_args(argv)

    print(f'{len(ERRATAS)} erratas de la traducción oficial de Sandia\n')
    for e in ERRATAS:
        print(f'  [{e.gravedad}] {e.clave}')
        print(f'      inglés: {e.ingles}')
        print(f'      dice:   {e.viejo}')
        print(f'      debe:   {e.nuevo}')
        print(f'      porqué: {e.porque}\n')

    total = {e.clave: 0 for e in ERRATAS}
    faltan = []
    for ruta in ARCHIVOS:
        if not ruta.exists():
            faltan.append(ruta)
            continue
        with zipfile.ZipFile(ruta) as z:
            raiz = ET.fromstring(z.read('model.xml'))
        cuenta = _aplicar_a_arbol(raiz, ERRATAS)
        hechos = sum(cuenta.values())
        for k, v in cuenta.items():
            total[k] += v
        detalle = ', '.join(f'{k}×{v}' for k, v in cuenta.items() if v)
        print(f'  {ruta.relative_to(RAIZ)}: {hechos} cambios'
              + (f' ({detalle})' if detalle else ' (ya estaba corregido)'))
        if args.aplicar and hechos:
            _reescribir(ruta, raiz)

    if faltan:
        print('\nno se encontraron: ' + ', '.join(str(f) for f in faltan))
    print()
    for e in ERRATAS:
        estado = 'sin encontrar' if total[e.clave] == 0 else f'{total[e.clave]} veces'
        print(f'  {e.clave}: {estado}')
    if args.revisar:
        print('\n(revisión solamente; no se cambió ningún archivo)')
    else:
        print('\nAplicado. Ahora corra las pruebas para confirmar que ningún '
              'puntaje se movió:\n    cd programa && python3 -m pytest -q')
    return 0


if __name__ == '__main__':
    sys.exit(main())
