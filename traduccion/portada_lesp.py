# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Pone la portada institucional del laboratorio en los cuestionarios.

La portada original dirige las preguntas de soporte a `sacaske@sandia.gov`, el
buzón de una persona en un laboratorio nacional de Estados Unidos. Quien trabaje
en Nayarit y escriba ahí no va a obtener ayuda útil, así que el contacto pasa a
ser del laboratorio.

Lo que **no** se toca, porque son los avisos del titular de los derechos y
quitarlos no se debe:

  - el crédito a Sandia National Laboratories y el número SAND;
  - el aviso de contratista del Departamento de Energía;
  - el aviso de derecho de autor y el de control de exportaciones;
  - la advertencia de que el modelo no debe ser la única fuente de información
    para decidir sobre riesgos.

Todo eso se conserva, en texto literal, en el pie de la portada.

CÓMO SE USA

    python3 traduccion/portada_lesp.py --revisar
    python3 traduccion/portada_lesp.py --aplicar
    python3 traduccion/portada_lesp.py --aplicar --logo mi_logotipo.png

El logotipo es opcional. Si no se da, la portada queda con el encabezado
tipográfico del laboratorio y conserva la imagen que ya traía. Cuando el
laboratorio tenga su archivo oficial, se vuelve a correr con `--logo` y queda
puesto: conviene un PNG de fondo transparente de unos 510 por 129 puntos, que es
el espacio que el programa reserva.

QUÉ CAMBIAR AQUÍ

Las cuatro constantes de abajo: la cadena de dependencias del laboratorio, su
nombre, el lugar y el correo de contacto.
"""
from __future__ import annotations

import argparse
import html
import pathlib
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

# --------------------------------------------------------------- lo editable
# La cadena de la que depende el laboratorio, de arriba hacia abajo. Sale
# encima de su nombre, en letra chica.
DEPENDENCIAS = (
    'Servicios de Salud de Nayarit (SSN)',
    'Comisión Estatal para la Protección contra Riesgos Sanitarios '
    'de Nayarit (CESPRISNAY)',
)
LABORATORIO = 'Laboratorio Estatal de Salud Pública de Nayarit (LESP Nayarit)'
LUGAR = 'Nayarit, México'
CONTACTO = 'gnc.lespnay@gmail.com'
# ---------------------------------------------------------------------------

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent

# Color del encabezado de cada cuestionario, el mismo que usa el programa nuevo.
CUESTIONARIOS = {
    'bioseguridad': {
        'archivos': [RAIZ / 'historico' / 'java-es' / 'Biosafety_es.raml',
                     RAIZ / 'programa' / 'bioram' / 'cuestionarios' / 'bioseguridad.raml'],
        'titulo': 'Evaluación de riesgos de bioseguridad',
        'subtitulo': 'Modelo de evaluación de riesgos relacionados con la bioseguridad '
                     '(RAM de Bioseguridad)',
        'color': '#02788f',
        'version': 'Versión 1.0 · Septiembre de 2010 · SAND No. 2010-6487',
        'avisos': [
            'Cuestionario, ponderaciones y método: <b>BioRAM</b>, de Sandia National '
            'Laboratories, SAND No. 2010-6487. Traducción oficial al español de Sandia, '
            f'con las erratas corregidas por el {LABORATORIO}.',
            'Sandia es un laboratorio multiprograma operado por Sandia Corporation, una '
            'empresa de Lockheed Martin Company, para el Departamento de Administración '
            'de la Seguridad Nuclear de los Estados Unidos conforme al contrato '
            'DE-AC04-94AL85000.',
        ],
        'advertencia':
            'Este modelo brinda un proceso estructurado y sistemático para realizar '
            'evaluaciones de riesgos relacionados con la bioseguridad en laboratorios; '
            'sin embargo, no debería ser la única fuente de información cuando tome '
            'decisiones relativas al manejo de riesgos.',
    },
    'bioproteccion': {
        'archivos': [RAIZ / 'historico' / 'java-es' / 'Biosecurity_es.raml',
                     RAIZ / 'programa' / 'bioram' / 'cuestionarios' / 'bioproteccion.raml'],
        'titulo': 'Evaluación de riesgos de bioprotección',
        'subtitulo': 'Modelo de riesgos relacionados con la bioprotección 2010 '
                     '(BioRAM 2.0) · también llamada biocustodia',
        'color': '#232858',
        'version': 'Prototipo · 2010',
        'avisos': [
            'Cuestionario, ponderaciones y método: <b>BioRAM</b>, de Sandia National '
            f'Laboratories. Traducción oficial al español de Sandia, con las erratas '
            f'corregidas por el {LABORATORIO}.',
            'Derecho de autor 2007/2009 Sandia Corporation. Conforme los términos del '
            'contrato DE-AC04-94AL85000, se emitió una licencia sin exclusividad con '
            'respecto al uso de este trabajo a favor del Gobierno de los EE. UU. La '
            'exportación de este programa tal vez requiera una licencia del Gobierno de '
            'los Estados Unidos.',
        ],
        'advertencia':
            'Este modelo brinda un proceso estructurado y sistemático para evaluar '
            'riesgos de bioprotección; sin embargo, no debería ser la única fuente de '
            'información cuando tome decisiones relativas al manejo de riesgos.',
    },
}

# El estilo va en el propio HTML porque lo dibujan dos programas distintos: el
# JEditorPane del Java y el QTextBrowser del programa nuevo. Los dos entienden
# poco CSS, así que se usa lo básico y nada de posicionamiento.
PLANTILLA = """<html>
  <head>
    <style type="text/css">
body {{ font-family: Arial,Helvetica,sans-serif; color: #1b2435; }}
.institucion {{ text-align: center; font-size: 9.5pt; color: #5a6478;
                margin: 0; }}
.laboratorio {{ text-align: center; font-size: 15pt; font-weight: bold;
                color: {color}; padding-top: 4px; }}
.lugar {{ text-align: center; font-size: 10pt; color: #5a6478;
          padding-bottom: 14px; }}
.titulo {{ text-align: center; font-size: 21pt; color: {color};
           padding-top: 14px; padding-bottom: 2px; }}
.subtitulo {{ text-align: center; font-size: 10.5pt; font-style: italic;
              color: #4a5568; }}
.version {{ text-align: center; font-size: 9.5pt; color: #5a6478;
            padding-top: 6px; padding-bottom: 14px; }}
.contacto {{ text-align: center; font-size: 10.5pt; padding-top: 10px;
             padding-bottom: 10px; }}
.advertencia {{ text-align: center; font-size: 10pt; color: #8a5a00;
                padding-top: 10px; padding-bottom: 10px; }}
.credito {{ text-align: center; font-size: 8.5pt; color: #5a6478;
            padding-top: 14px; }}
    </style>
  </head>
  <body>
{encabezado}
    <p class="titulo">{titulo}</p>
    <p class="subtitulo">{subtitulo}</p>
    <p class="version">{version}</p>

    <p class="contacto">Dudas, comentarios o sugerencias sobre esta versión
    en español:<br /><b>{contacto}</b></p>

    <p class="advertencia">{advertencia}</p>

    <hr />
{creditos}
  </body>
</html>
"""


def _encabezado() -> str:
    partes = []
    for dependencia in DEPENDENCIAS:
        partes.append(f'    <p class="institucion">{html.escape(dependencia)}</p>')
    partes.append(f'    <p class="laboratorio">{html.escape(LABORATORIO)}</p>')
    if LUGAR:
        partes.append(f'    <p class="lugar">{html.escape(LUGAR)}</p>')
    return '\n'.join(partes)


def portada(cuestionario: dict) -> str:
    creditos = '\n'.join(f'    <p class="credito">{a}</p>' for a in cuestionario['avisos'])
    return PLANTILLA.format(
        color=cuestionario['color'],
        encabezado=_encabezado(),
        titulo=html.escape(cuestionario['titulo']),
        subtitulo=html.escape(cuestionario['subtitulo']),
        version=html.escape(cuestionario['version']),
        contacto=html.escape(CONTACTO),
        advertencia=html.escape(cuestionario['advertencia']),
        creditos=creditos)


def _poner(ruta: pathlib.Path, nuevo_html: str, logo: pathlib.Path | None,
           aplicar: bool) -> str:
    with zipfile.ZipFile(ruta) as z:
        raiz = ET.fromstring(z.read('model.xml'))
        nombres = z.namelist()
    info = raiz.find('ModelInformation')
    if info is None:
        return 'no tiene ModelInformation'

    elem = info.find('frontHTML')
    if elem is None:
        elem = ET.SubElement(info, 'frontHTML')
    antes_html = elem.text or ''
    elem.text = nuevo_html

    camino_logo = info.findtext('frontImagePath') or ''
    nota_logo = f'conserva la imagen que ya traía ({camino_logo or "ninguna"})'
    if logo is not None:
        destino = 'media/logotipo_lesp.png'
        elem_img = info.find('frontImagePath')
        if elem_img is None:
            elem_img = ET.SubElement(info, 'frontImagePath')
        elem_img.text = destino
        nota_logo = f'logotipo puesto en {destino}'

    if not aplicar:
        return ('cambiaría la portada'
                + (' (ya estaba puesta)' if antes_html == nuevo_html else '')
                + f'; {nota_logo}')

    temporal = ruta.with_suffix('.raml.nuevo')
    with zipfile.ZipFile(ruta) as z, \
         zipfile.ZipFile(temporal, 'w', zipfile.ZIP_DEFLATED) as salida:
        for i in z.infolist():
            if i.filename == 'model.xml':
                salida.writestr(i, ET.tostring(raiz, encoding='UTF-8',
                                               xml_declaration=True))
            elif i.filename == 'media/logotipo_lesp.png' and logo is not None:
                continue      # se vuelve a escribir abajo
            else:
                salida.writestr(i, z.read(i.filename))
        if logo is not None:
            salida.writestr('media/logotipo_lesp.png', logo.read_bytes())
    shutil.move(temporal, ruta)
    return f'portada puesta; {nota_logo}'


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    grupo = p.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--revisar', action='store_true', help='sólo dice qué haría')
    grupo.add_argument('--aplicar', action='store_true', help='escribe los archivos')
    p.add_argument('--logo', type=pathlib.Path,
                   help='PNG del logotipo del laboratorio (unos 510x129)')
    p.add_argument('--mostrar', action='store_true',
                   help='imprimir el HTML de la portada y salir')
    args = p.parse_args(argv)

    if args.logo is not None and not args.logo.is_file():
        sys.exit(f'no existe el archivo del logotipo: {args.logo}')

    print(f'Contacto de soporte: {CONTACTO}')
    for dependencia in DEPENDENCIAS:
        print(f'  {dependencia}')
    print(f'  {LABORATORIO}')
    print(f'Logotipo: {args.logo if args.logo else "no se cambia"}\n')

    for clave, cuestionario in CUESTIONARIOS.items():
        nuevo = portada(cuestionario)
        if args.mostrar:
            print('=' * 70); print(clave); print(nuevo); continue
        for ruta in cuestionario['archivos']:
            if not ruta.exists():
                print(f'  {ruta.relative_to(RAIZ)}: no existe'); continue
            resultado = _poner(ruta, nuevo, args.logo, args.aplicar)
            print(f'  {ruta.relative_to(RAIZ)}: {resultado}')

    if args.revisar and not args.mostrar:
        print('\n(revisión solamente; no se cambió ningún archivo)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
