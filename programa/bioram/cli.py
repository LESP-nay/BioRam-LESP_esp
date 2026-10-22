# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Línea de comandos de BioRAM LESP.

Es la etapa 1: todavía no hay ventana, pero ya se puede trabajar de verdad y,
sobre todo, comprobar que las cuentas salen bien.

    python -m bioram.cli area nueva "Bacteriología"
    python -m bioram.cli cepa nueva 1 "Mycobacterium tuberculosis"
    python -m bioram.cli evaluacion nueva 1 bioseguridad
    python -m bioram.cli importar 1 evaluacion_vieja.raml
    python -m bioram.cli resultados 1
    python -m bioram.cli exportar 1 evaluacion.raml

El archivo de datos es bioram.db en la carpeta actual, o el que indique --datos.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import datos, intercambio, modelo, motor, reporte
from .datos import Almacen

POR_OMISION = 'bioram.db'


def _tabla(filas, encabezados):
    if not filas:
        return '  (nada todavía)'
    anchos = [max(len(str(f[i])) for f in [encabezados] + filas) for i in range(len(encabezados))]
    linea = lambda f: '  ' + '  '.join(str(v).ljust(a) for v, a in zip(f, anchos))
    return '\n'.join([linea(encabezados), '  ' + '  '.join('-' * a for a in anchos)]
                     + [linea(f) for f in filas])


# --------------------------------------------------------------------- áreas
def cmd_area_nueva(alm, args):
    area_id = alm.crear_area(args.nombre, args.responsable)
    print(f'área {area_id}: {args.nombre}')


def cmd_area_listar(alm, args):
    print(_tabla([(a.id, a.nombre, a.responsable, len(alm.cepas(a.id))) for a in alm.areas()],
                 ('id', 'área', 'responsable', 'cepas')))


# --------------------------------------------------------------------- cepas
def cmd_cepa_nueva(alm, args):
    cepa_id = alm.crear_cepa(args.area, args.nombre, args.agente)
    print(f'cepa {cepa_id}: {args.nombre} (área {args.area})')


def cmd_cepa_listar(alm, args):
    filas = [(c.id, alm.area(c.area_id).nombre, c.nombre, c.agente,
              len(alm.evaluaciones(c.id))) for c in alm.cepas(args.area)]
    print(_tabla(filas, ('id', 'área', 'cepa', 'agente', 'evaluaciones')))


# --------------------------------------------------------------- evaluaciones
def cmd_evaluacion_nueva(alm, args):
    eva_id = alm.crear_evaluacion(args.cepa, args.tipo, responsables=args.responsables,
                                  copiar_de=args.copiar_de)
    cepa = alm.cepa(args.cepa)
    print(f'evaluación {eva_id}: {args.tipo} de {cepa.nombre}')
    if args.plantilla:
        cuestionario = modelo.incluido(args.tipo)
        if args.plantilla not in cuestionario.plantillas:
            sys.exit(f'no existe la plantilla "{args.plantilla}". '
                     f'Vea: python -m bioram.cli plantillas {args.tipo}')
        alm.guardar_respuestas(eva_id, cuestionario.plantillas[args.plantilla])
        print(f'  precargada con la plantilla "{args.plantilla}"')


def cmd_evaluacion_listar(alm, args):
    filas = []
    for f in alm.resumen():
        if f['evaluacion_id'] is None:
            continue
        filas.append((f['evaluacion_id'], f['area'], f['cepa'], f['tipo'],
                      f"{f['respondidas']}/105", f['estado']))
    print(_tabla(filas, ('id', 'área', 'cepa', 'tipo', 'respondidas', 'estado')))


def cmd_plantillas(alm, args):
    nombres = sorted(modelo.incluido(args.tipo).plantillas)
    print('\n'.join(f'  {n}' for n in nombres) or '  (este cuestionario no trae plantillas)')


# ------------------------------------------------------------------ preguntas
def cmd_preguntas(alm, args):
    cuestionario = modelo.incluido(args.tipo)
    for i, p in enumerate(cuestionario.preguntas_en_orden(), 1):
        print(f'{i:3}. {p.titulo}')
        if args.detalle and p.detalle:
            for linea in p.detalle.splitlines():
                print(f'       {linea}')


def cmd_responder(alm, args):
    eva = alm.evaluacion(args.evaluacion)
    preguntas = modelo.incluido(eva.tipo).preguntas_en_orden()
    if not 1 <= args.numero <= len(preguntas):
        sys.exit(f'la pregunta debe ir de 1 a {len(preguntas)}')
    pregunta = preguntas[args.numero - 1]
    # Los límites los define el cuestionario (0 a 4 en los dos). Sin esta
    # comprobación, un 999 entraba en la base y el reporte salía con «nan».
    valor = datos.revisar_valor(args.valor, pregunta)
    respuesta = datos.Respuesta(valor, bool(args.aproximada))
    alm.guardar_respuestas(args.evaluacion, {pregunta.uuid: respuesta})
    marca = '  (estimación)' if args.aproximada else ''
    print(f'{args.numero}. {pregunta.titulo[:70]} -> {valor:g}{marca}')


# ----------------------------------------------------------------- resultados
def cmd_resultados(alm, args):
    eva = alm.evaluacion(args.evaluacion)
    cuestionario = modelo.incluido(eva.tipo)
    respuestas = alm.puntajes(args.evaluacion)
    faltan = len(cuestionario.preguntas) - len(respuestas)
    cepa = alm.cepa(eva.cepa_id)
    area = alm.area(cepa.area_id)

    print(f'{area.nombre} / {cepa.nombre} / {eva.tipo}')
    if faltan:
        print(f'  AVISO: faltan {faltan} preguntas por responder; cuentan como 0')
    print()
    puntajes = motor.resultados(cuestionario, respuestas)
    filas = [(cuestionario.perfiles[u].titulo, f'{v:.4f}') for u, v in puntajes.items()]
    print(_tabla(filas, ('perfil de resultados', 'puntaje')))
    print()
    for grafica, puntos in zip(cuestionario.graficas,
                               motor.puntos_de_grafica(cuestionario, respuestas)):
        print(f'  {grafica.titulo}')
        print(_tabla([(leyenda, f'{x:.4f}', f'{y:.4f}') for leyenda, x, y in puntos],
                     ('punto', grafica.eje_x, grafica.eje_y)))


# --------------------------------------------------------------- intercambio
def cmd_importar(alm, args):
    eva = alm.evaluacion(args.evaluacion)
    cuestionario = modelo.incluido(eva.tipo)
    leido = intercambio.leer_respuestas(args.archivo, cuestionario)
    if not leido:
        sys.exit(f'{args.archivo} no trae conjuntos de respuestas')

    nombre = args.conjunto or next(iter(leido.conjuntos))
    if nombre not in leido.conjuntos:
        sys.exit(f'ese archivo no trae el conjunto "{nombre}". '
                 f'Trae: {", ".join(sorted(leido.conjuntos))}')
    respuestas = leido.conjuntos[nombre]
    alm.guardar_respuestas(args.evaluacion, respuestas)
    print(f'importadas {len(respuestas)} respuestas del conjunto "{nombre}"')
    if leido.desconocidas.get(nombre):
        print(f'  AVISO: {leido.desconocidas[nombre]} respuestas del archivo no '
              'corresponden a ninguna pregunta de este cuestionario y se omitieron')
    if leido.responsables and not eva.responsables:
        alm.actualizar_evaluacion(args.evaluacion, responsables=leido.responsables)


def cmd_exportar(alm, args):
    eva = alm.evaluacion(args.evaluacion)
    cepa = alm.cepa(eva.cepa_id)
    intercambio.escribir_respuestas(
        args.archivo, modelo.ruta_incluido(eva.tipo),
        {args.conjunto or cepa.nombre: alm.respuestas(args.evaluacion)},
        responsables=eva.responsables, procedimiento=eva.procedimiento)
    print(f'exportado a {args.archivo}')


# ------------------------------------------------------------------ reportes
def cmd_reporte(alm, args):
    if args.area:
        contenido = reporte.html_de_area(alm, args.id)
    elif args.csv:
        contenido = reporte.csv_de_evaluacion(alm, args.id)
    else:
        contenido = reporte.html_de_evaluacion(alm, args.id)

    if args.pdf:
        if not args.archivo:
            sys.exit('el PDF necesita --archivo')
        # Qt sólo se importa si de verdad se pide un PDF, para que el resto de la
        # línea de comandos siga sirviendo en un equipo sin Qt instalado.
        try:
            # Sin pantalla: la línea de comandos nunca abre una ventana, y Qt
            # necesita de todos modos una aplicación viva para medir las letras.
            os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
            from PySide6.QtGui import QGuiApplication

            from .interfaz.salidas import _a_pdf
        except ImportError as e:
            sys.exit(f'para generar PDF hace falta PySide6: {e}')
        if QGuiApplication.instance() is None:
            QGuiApplication([sys.argv[0]])
        _a_pdf(contenido, Path(args.archivo))
        print(f'guardado en {args.archivo}')
        return

    if args.archivo:
        # La codificación la decide el contenido, no la bandera: un HTML con
        # marca de orden de bytes se ve mal en algunos navegadores.
        codificacion = 'utf-8-sig' if args.csv else 'utf-8'
        Path(args.archivo).write_text(contenido, encoding=codificacion)
        print(f'guardado en {args.archivo}')
    else:
        print(contenido)


# -------------------------------------------------------------------- versión
def cmd_version_guardar(alm, args):
    v = alm.guardar_version(args.evaluacion, autor=args.autor, nota=args.nota)
    print(f'versión {v} archivada')


def cmd_version_listar(alm, args):
    filas = [(v.id, v.momento, v.autor, v.nota) for v in alm.versiones(args.evaluacion)]
    print(_tabla(filas, ('id', 'momento', 'autor', 'nota')))


def construir_analizador():
    p = argparse.ArgumentParser(prog='bioram', description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--datos', default=POR_OMISION, help=f'archivo de datos (por omisión {POR_OMISION})')
    sub = p.add_subparsers(dest='orden', required=True)

    area = sub.add_parser('area', help='áreas del laboratorio').add_subparsers(dest='sub', required=True)
    a = area.add_parser('nueva'); a.add_argument('nombre'); a.add_argument('--responsable', default='')
    a.set_defaults(func=cmd_area_nueva)
    area.add_parser('listar').set_defaults(func=cmd_area_listar)

    cepa = sub.add_parser('cepa', help='cepas de un área').add_subparsers(dest='sub', required=True)
    c = cepa.add_parser('nueva'); c.add_argument('area', type=int); c.add_argument('nombre')
    c.add_argument('--agente', default=''); c.set_defaults(func=cmd_cepa_nueva)
    cl = cepa.add_parser('listar'); cl.add_argument('--area', type=int)
    cl.set_defaults(func=cmd_cepa_listar)

    ev = sub.add_parser('evaluacion', help='evaluaciones de una cepa').add_subparsers(dest='sub', required=True)
    en = ev.add_parser('nueva'); en.add_argument('cepa', type=int)
    en.add_argument('tipo', choices=modelo.TIPOS); en.add_argument('--responsables', default='')
    en.add_argument('--plantilla', help='precargar con un agente del cuestionario')
    en.add_argument('--copiar-de', dest='copiar_de', type=int, help='copiar las respuestas de otra evaluación')
    en.set_defaults(func=cmd_evaluacion_nueva)
    ev.add_parser('listar').set_defaults(func=cmd_evaluacion_listar)

    pl = sub.add_parser('plantillas', help='agentes que trae un cuestionario')
    pl.add_argument('tipo', choices=modelo.TIPOS); pl.set_defaults(func=cmd_plantillas)

    pr = sub.add_parser('preguntas', help='ver el cuestionario')
    pr.add_argument('tipo', choices=modelo.TIPOS)
    pr.add_argument('--detalle', action='store_true', help='mostrar los criterios de puntuación')
    pr.set_defaults(func=cmd_preguntas)

    rs = sub.add_parser('responder', help='responder una pregunta por su número')
    rs.add_argument('evaluacion', type=int); rs.add_argument('numero', type=int)
    rs.add_argument('valor', type=float)
    rs.add_argument('--aproximada', action='store_true',
                    help='marcar la respuesta como una estimación')
    rs.set_defaults(func=cmd_responder)

    re = sub.add_parser('resultados', help='calcular los resultados de una evaluación')
    re.add_argument('evaluacion', type=int); re.set_defaults(func=cmd_resultados)

    im = sub.add_parser('importar', help='traer respuestas de un .raml del BioRAM original')
    im.add_argument('evaluacion', type=int); im.add_argument('archivo')
    im.add_argument('--conjunto'); im.set_defaults(func=cmd_importar)

    ex = sub.add_parser('exportar', help='guardar las respuestas como .raml')
    ex.add_argument('evaluacion', type=int); ex.add_argument('archivo')
    ex.add_argument('--conjunto'); ex.set_defaults(func=cmd_exportar)

    rp = sub.add_parser('reporte', help='generar el reporte (HTML o CSV)')
    rp.add_argument('id', type=int, help='id de la evaluación, o del área con --area')
    rp.add_argument('--area', action='store_true', help='resumen del área en vez de una evaluación')
    formato = rp.add_mutually_exclusive_group()
    formato.add_argument('--csv', action='store_true',
                         help='hoja de cálculo en vez de página web (no se puede con --area)')
    formato.add_argument('--pdf', action='store_true',
                         help='PDF en vez de página web; necesita --archivo')
    rp.add_argument('--archivo', help='dónde guardarlo (si no, se imprime)')
    rp.set_defaults(func=cmd_reporte)

    vr = sub.add_parser('version', help='historial de una evaluación').add_subparsers(dest='sub', required=True)
    vg = vr.add_parser('guardar'); vg.add_argument('evaluacion', type=int)
    vg.add_argument('--autor', default=''); vg.add_argument('--nota', default='')
    vg.set_defaults(func=cmd_version_guardar)
    vl = vr.add_parser('listar'); vl.add_argument('evaluacion', type=int)
    vl.set_defaults(func=cmd_version_listar)

    return p


def main(argv=None):
    args = construir_analizador().parse_args(argv)
    if getattr(args, 'area', False) and getattr(args, 'csv', False):
        sys.exit('error: el resumen de área no se puede generar como hoja de cálculo')
    try:
        alm = Almacen(Path(args.datos))
    except datos.ArchivoDeDatosInvalido as e:
        sys.exit(f'error: {e}')
    with alm:
        try:
            args.func(alm, args)
        except (LookupError, ValueError) as e:
            sys.exit(f'error: {e}')
        except BrokenPipeError:
            # Pasa con «resultados | head»: la salida se cerró antes de tiempo.
            # Sin esto Python imprime una traza al terminar.
            try:
                sys.stdout.close()
            except BrokenPipeError:
                pass
            os._exit(0)


if __name__ == '__main__':
    main()
