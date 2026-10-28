# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Repone la referencia de puntuación que la traducción de Sandia perdió.

EL PROBLEMA

El cuestionario de bioseguridad en español se tradujo de la revisión inglesa
que viene dentro de «historico/sandia/Java source.zip» (models/Biosafety/Biosafety.raml, 2014),
con la que comparte los 105 identificadores de pregunta. Contra esa revisión el
español es idéntico en todo —mismo orden, misma jerarquía, mismos pesos, mismos
límites, mismos criterios, las mismas 50 categorías— salvo en **un** nodo: al
perfil «Probabilidad por ingestión (individuo)» le falta una referencia.

El inglés de 2014 tiene, en la categoría «Exposición por contacto»
(cef76a48-db4c-4b3b-b84a-010a6ae70e01, peso 0.86, sin normalizar sus hijos):

    <ResultQuestion>
        <questionUUID>8e15e478-850c-4136-b1b0-5f6ef7d00265</questionUUID>
        <rawWeight>0.13</rawWeight>
    </ResultQuestion>
    <ResultQuestion>
        <questionUUID>bb9a10c8-f39f-4736-b20e-bb792be503a6</questionUUID>
        <rawWeight>0.41</rawWeight>
    </ResultQuestion>

y el español sólo tiene la segunda. La pregunta que falta es «¿Todos los agentes
biológicos de este laboratorio figuran en los inventarios?».

Falta en las cuatro variantes españolas, incluida la oficial de Sandia, así que
la pérdida ocurrió en su traducción, no en el trabajo de este laboratorio.

EL EFECTO

Como esa categoría no normaliza los pesos de sus hijos, quitar un sumando de
0.13 baja el resultado. Medido sobre 3.000 escenarios al azar:

    Probabilidad por ingestión (individuo)         77.4% de los escenarios,
                                                   −0.19 de 4 en promedio
                                                   (−16%), hasta −0.91
    Probabilidad de transmisión secundaria (hum.)  10.7%, −0.06, hasta −0.21

Todas las diferencias van en la misma dirección: el español puntúa más bajo.
Un sesgo sistemático así no se promedia con más datos, corre toda la serie.

LA COMPROBACIÓN

La herramienta no se conforma con escribir el nodo: después de reponerlo
recalcula los 19 perfiles del español y del inglés de 2014 sobre un juego de
escenarios y **exige que la diferencia sea exactamente cero**. Si no lo es,
deshace el cambio. O sea que la corrección se valida contra el original del que
se tradujo, no contra nuestro criterio.

CÓMO SE USA

    python3 traduccion/reponer_referencia.py --revisar
    python3 traduccion/reponer_referencia.py --aplicar
"""
from __future__ import annotations

import argparse
import pathlib
import random
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / 'programa'))

# Dónde va la referencia y cuál es.
CATEGORIA = 'cef76a48-db4c-4b3b-b84a-010a6ae70e01'   # «Exposición por contacto»
PREGUNTA = '8e15e478-850c-4136-b1b0-5f6ef7d00265'    # «…figuran en los inventarios?»
PESO = '0.13'
ANTES_DE = 'bb9a10c8-f39f-4736-b20e-bb792be503a6'    # va justo antes de ésta
PERFIL = 'Probabilidad por ingestión (individuo)'

# Sólo bioseguridad: bioprotección no tiene este defecto.
ARCHIVOS = [
    RAIZ / 'historico' / 'java-es' / 'Biosafety_es.raml',
    RAIZ / 'programa' / 'bioram' / 'cuestionarios' / 'bioseguridad.raml',
]

# El original del que se tradujo, para comprobar contra él. Viene dentro de
# «historico/sandia/Java source.zip», que está en la raíz del repositorio.
ZIP_FUENTE = RAIZ / 'historico' / 'sandia' / 'Java source.zip'
DENTRO = 'Java source/BioRAM/models/Biosafety/Biosafety.raml'


def _categorias_afectadas(raiz) -> list[ET.Element]:
    """Las categorías donde debería estar la referencia y no está."""
    faltantes = []
    for cat in raiz.iter('ResultCategory'):
        if cat.findtext('categoryUUID') != CATEGORIA:
            continue
        hijos = cat.find('Children')
        if hijos is None:
            continue
        presentes = [c.findtext('questionUUID') for c in hijos
                     if c.tag == 'ResultQuestion']
        if PREGUNTA not in presentes and ANTES_DE in presentes:
            faltantes.append(cat)
    return faltantes


def _reponer_en(raiz) -> int:
    """Inserta la referencia donde falte. Devuelve cuántas veces."""
    puestas = 0
    for cat in _categorias_afectadas(raiz):
        hijos = cat.find('Children')
        indice = next(i for i, c in enumerate(hijos)
                      if c.tag == 'ResultQuestion'
                      and c.findtext('questionUUID') == ANTES_DE)
        nodo = ET.Element('ResultQuestion')
        ET.SubElement(nodo, 'questionUUID').text = PREGUNTA
        ET.SubElement(nodo, 'rawWeight').text = PESO
        hijos.insert(indice, nodo)
        puestas += 1
    return puestas


def _escribir(ruta: pathlib.Path, raiz):
    temporal = ruta.with_suffix('.raml.nuevo')
    with zipfile.ZipFile(ruta) as z, \
         zipfile.ZipFile(temporal, 'w', zipfile.ZIP_DEFLATED) as salida:
        for i in z.infolist():
            if i.filename == 'model.xml':
                salida.writestr(i, ET.tostring(raiz, encoding='UTF-8',
                                               xml_declaration=True))
            else:
                salida.writestr(i, z.read(i.filename))
    shutil.move(temporal, ruta)


def _original_2014(destino: pathlib.Path) -> pathlib.Path | None:
    """Saca del .zip del código fuente la revisión de la que se tradujo."""
    if not ZIP_FUENTE.exists():
        return None
    with zipfile.ZipFile(ZIP_FUENTE) as z:
        nombres = [n for n in z.namelist()
                   if n.endswith('models/Biosafety/Biosafety.raml')]
        if not nombres:
            return None
        destino.write_bytes(z.read(nombres[0]))
    return destino


def comprobar(ruta_es: pathlib.Path, ruta_en: pathlib.Path, escenarios=400):
    """¿El español da ahora exactamente lo mismo que el inglés de 2014?"""
    from bioram import modelo, motor
    es, en = modelo.cargar(ruta_es), modelo.cargar(ruta_en)
    uuids = [p.uuid for p in es.preguntas_en_orden()]
    comunes = {p.uuid for p in en.preguntas_en_orden()} & set(uuids)
    if len(comunes) != 105:
        return None, f'los dos modelos comparten {len(comunes)} preguntas, no 105'

    rnd = random.Random(20261023)
    peor, comparados = 0.0, 0
    for n in range(escenarios):
        if n == 0:
            r = {u: 0.0 for u in uuids}
        elif n == 1:
            r = {u: 4.0 for u in uuids}
        else:
            r = {u: float(rnd.choice([0, 1, 2, 3, 4])) for u in uuids}
        a, b = motor.resultados(en, r), motor.resultados(es, r)
        for va, vb in zip(a.values(), b.values()):
            comparados += 1
            peor = max(peor, abs(va - vb))
    return (peor, comparados), None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    grupo = p.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--revisar', action='store_true', help='sólo dice qué haría')
    grupo.add_argument('--aplicar', action='store_true', help='repone y comprueba')
    args = p.parse_args(argv)

    print(f'Referencia a reponer en «{PERFIL}»:')
    print(f'  categoría {CATEGORIA}')
    print(f'  pregunta  {PREGUNTA}  con peso {PESO}')
    print(f'  va justo antes de {ANTES_DE}\n')

    pendientes = []
    for ruta in ARCHIVOS:
        if not ruta.exists():
            print(f'  {ruta.relative_to(RAIZ)}: no existe'); continue
        with zipfile.ZipFile(ruta) as z:
            raiz = ET.fromstring(z.read('model.xml'))
        cuantas = len(_categorias_afectadas(raiz))
        if cuantas:
            pendientes.append(ruta)
            print(f'  {ruta.relative_to(RAIZ)}: falta en {cuantas} lugar(es)')
        else:
            print(f'  {ruta.relative_to(RAIZ)}: ya está repuesta')

    if args.revisar:
        print('\n(revisión solamente; no se cambió ningún archivo)')
        return 0
    if not pendientes:
        print('\nNo hay nada que reponer.')
        return 0

    respaldos = {}
    for ruta in pendientes:
        respaldo = ruta.with_suffix('.raml.respaldo')
        shutil.copy2(ruta, respaldo)
        respaldos[ruta] = respaldo
        with zipfile.ZipFile(ruta) as z:
            raiz = ET.fromstring(z.read('model.xml'))
        puestas = _reponer_en(raiz)
        _escribir(ruta, raiz)
        print(f'\n  {ruta.relative_to(RAIZ)}: repuesta ({puestas})')

    # La comprobación: tiene que quedar idéntico al original de 2014.
    print('\nComprobando contra la revisión inglesa de la que se tradujo…')
    temporal = pathlib.Path('/tmp') / 'biosafety_2014_para_comprobar.raml'
    original = _original_2014(temporal)
    if original is None:
        print('  AVISO: no se encontró «historico/sandia/Java source.zip», así que no se pudo '
              'comprobar contra el original. Los archivos quedaron cambiados; '
              f'los respaldos están en {[str(r) for r in respaldos.values()]}')
        return 1

    resultado, error = comprobar(ARCHIVOS[0], original)
    if error:
        print(f'  NO se pudo comprobar: {error}')
        for ruta, respaldo in respaldos.items():
            shutil.move(respaldo, ruta)
        print('  Se deshizo el cambio.')
        return 1

    peor, comparados = resultado
    print(f'  {comparados} valores comparados | diferencia máxima {peor:.12f}')
    if peor > 0.0:
        print('  NO quedó idéntico al original. Se deshace el cambio.')
        for ruta, respaldo in respaldos.items():
            shutil.move(respaldo, ruta)
        return 1

    print('  Idéntico al original: la corrección es correcta.')
    for respaldo in respaldos.values():
        respaldo.unlink()
    print('\nAhora corra las pruebas:  cd programa && python3 -m pytest -q')
    return 0


if __name__ == '__main__':
    sys.exit(main())
