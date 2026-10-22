# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Los reportes: por cepa y por área.

Se arman en HTML porque así se pueden ver, imprimir, guardar como PDF y pegar
en un oficio sin depender de nada. Aquí no se usa Qt: eso deja que el reporte
se genere también desde la línea de comandos y que las pruebas lo revisen.

Las gráficas se pasan ya dibujadas (imagenes), porque dibujarlas sí necesita
Qt. Sin ellas el reporte sale igual, solo que sin las figuras.
"""
from __future__ import annotations

import base64
import csv
import html
import io
import math
from datetime import datetime

from . import modelo, motor, secciones
from .datos import Almacen

ESTILO = """
  /* Arial y su equivalente libre: están en Windows y en Linux, y el texto del
     PDF se puede copiar y buscar. Con otras tipografías Qt escribe los dos
     puntos y las rayas en un código privado y el texto sale ilegible al
     copiarlo. */
  body { font-family: Arial, 'Liberation Sans', Helvetica, sans-serif;
         color: #1f2933; font-size: 11pt; }
  h1 { font-size: 17pt; margin-bottom: 2px; }
  h2 { font-size: 13pt; margin-top: 22px; border-bottom: 2px solid #d6dde6; padding-bottom: 4px; }
  h3 { font-size: 11.5pt; margin-top: 16px; margin-bottom: 4px; }
  .sub { color: #616e7c; margin-top: 0; }
  table { border-collapse: collapse; width: 100%; margin-top: 8px; }
  th { background: #f4f7fb; text-align: left; padding: 6px 8px; border-bottom: 2px solid #d6dde6; }
  td { padding: 5px 8px; border-bottom: 1px solid #eef1f5; vertical-align: top; }
  td.num { text-align: right; white-space: nowrap; }
  .aviso { background: #fff6e5; border-left: 4px solid #b45309; padding: 8px 12px; }
  .suave { color: #616e7c; }
  .pie { color: #616e7c; font-size: 9.5pt; margin-top: 26px;
         border-top: 1px solid #d6dde6; padding-top: 8px; }
"""


def _e(texto) -> str:
    return html.escape(str(texto or ''))


def _celda(texto) -> str:
    """Texto para una hoja de cálculo, sin que Excel lo tome por fórmula.

    Una cepa llamada «=SUMA(...)», «-80 °C» o «+H1N1» se convierte en fórmula al
    abrir el archivo, y en vez del nombre aparece un error o un número.
    """
    s = str(texto or '')
    return "'" + s if s[:1] in ('=', '+', '-', '@', '\t', '\r') else s


def _fecha() -> str:
    return datetime.now().strftime('%d/%m/%Y %H:%M')


def _tabla(encabezados, filas, clases=()) -> str:
    cabeza = ''.join(f'<th>{_e(h)}</th>' for h in encabezados)
    cuerpo = []
    for fila in filas:
        celdas = ''.join(
            f'<td class="{clases[i] if i < len(clases) else ""}">{valor}</td>'
            for i, valor in enumerate(fila))
        cuerpo.append(f'<tr>{celdas}</tr>')
    return f'<table><tr>{cabeza}</tr>{"".join(cuerpo)}</table>'


def _imagen(datos: bytes) -> str:
    return (f'<img src="data:image/png;base64,{base64.b64encode(datos).decode()}" '
            'style="max-width:100%">')


def _descripcion_de(pregunta, valor) -> str:
    """La frase del criterio que corresponde al puntaje, si la hay."""
    if valor is None:
        return ''
    for linea in (pregunta.detalle or '').splitlines():
        if '=' in linea:
            numero, _, texto = linea.partition('=')
            try:
                if float(numero.strip()) == valor:
                    return texto.strip()
            except ValueError:
                continue
    return ''


def _encabezado(titulo: str, subtitulo: str) -> str:
    return (f'<h1>{_e(titulo)}</h1>\n<p class="sub">{_e(subtitulo)}</p>\n'
            f'<p class="suave">Generado el {_fecha()}</p>')


def _pie() -> str:
    return ('<p class="pie">BioRAM LESP. Los cuestionarios y el cálculo son los de '
            'BioRAM, de Sandia National Laboratories, traducidos al español. Los '
            'resultados son los mismos que los del programa original.</p>')


def html_de_evaluacion(almacen: Almacen, evaluacion_id: int,
                       imagenes: list[bytes] | None = None,
                       incluir_respuestas: bool = True) -> str:
    """El reporte de una evaluación: datos, resultados, gráficas y respuestas."""
    evaluacion = almacen.evaluacion(evaluacion_id)
    cepa = almacen.cepa(evaluacion.cepa_id)
    area = almacen.area(cepa.area_id)
    cuestionario = modelo.incluido(evaluacion.tipo)
    respuestas = almacen.respuestas(evaluacion_id)
    puntajes = motor.resultados(cuestionario, {p: r.valor for p, r in respuestas.items()})
    avance = secciones.avance(cuestionario, evaluacion.tipo, respuestas)

    partes = [f'<html><head><meta charset="utf-8"><style>{ESTILO}</style></head><body>']
    partes.append(_encabezado(
        f'{secciones.NOMBRE_EVALUACION[evaluacion.tipo]} — {cepa.nombre}',
        f'{area.nombre}'))

    ficha = [('Área', _e(area.nombre)), ('Cepa o agente', _e(cepa.nombre))]
    if cepa.agente:
        ficha.append(('Agente', _e(cepa.agente)))
    ficha += [('Responsables', _e(evaluacion.responsables) or '<span class="suave">sin anotar</span>'),
              ('Procedimiento evaluado', _e(evaluacion.procedimiento) or '<span class="suave">sin anotar</span>'),
              ('Estado', _e(evaluacion.estado)),
              ('Última modificación', _e(evaluacion.actualizada.replace('T', ' ')))]
    partes.append('<h2>Datos de la evaluación</h2>')
    partes.append(_tabla(['Dato', 'Valor'], ficha))

    faltan = sum(t - h for h, t in avance.values())
    partes.append('<h2>Avance del cuestionario</h2>')
    partes.append(_tabla(
        ['Sección', 'Contestadas', 'De'],
        [(_e(secciones.NOMBRE[s]), avance[s][0], avance[s][1]) for s in secciones.ORDEN],
        clases=('', 'num', 'num')))
    if faltan:
        partes.append(f'<p class="aviso">Faltan {faltan} preguntas por contestar. '
                      'Las preguntas sin respuesta cuentan como cero, así que los '
                      'puntajes de abajo salen más bajos de lo que saldrían al '
                      'terminar la evaluación.</p>')

    partes.append('<h2>Resultados</h2>')
    filas = []
    no_finitos = 0
    for uuid, valor in puntajes.items():
        perfil = cuestionario.perfiles[uuid]
        depende = secciones.de_que_depende(cuestionario, evaluacion.tipo, perfil)
        if math.isnan(valor) or math.isinf(valor):
            no_finitos += 1
            texto = 'sin valor' if math.isnan(valor) else ('∞' if valor > 0 else '−∞')
        else:
            texto = f'{valor:.4f}'
        filas.append((_e(perfil.titulo), texto,
                      _e(secciones.resumen_de_dependencia(depende))))
    partes.append(_tabla(['Resultado', 'Puntaje', 'De qué depende'], filas,
                         clases=('', 'num', '')))
    if no_finitos:
        partes.append(
            f'<p class="aviso">{no_finitos} resultado(s) no se pudieron calcular. '
            'Pasa cuando una combinación de respuestas lleva el cálculo a una '
            'división entre cero o a la raíz de un número negativo. Revise las '
            'respuestas de las preguntas de las que depende ese resultado; si '
            'están completas y el valor sigue sin salir, anótelo así en el '
            'expediente: es el comportamiento del modelo original.</p>')

    if imagenes:
        partes.append('<h2>Gráficas de riesgo</h2>')
        for grafica, imagen in zip(cuestionario.graficas, imagenes):
            if imagen:
                partes.append(f'<h3>{_e(grafica.titulo)}</h3>{_imagen(imagen)}')

    if incluir_respuestas:
        partes.append('<h2>Respuestas</h2>')
        seccion_de = secciones.por_pregunta(cuestionario, evaluacion.tipo)
        for seccion in secciones.ORDEN:
            filas = []
            for numero, pregunta in enumerate(cuestionario.preguntas_en_orden(), 1):
                if seccion_de.get(pregunta.uuid) != seccion:
                    continue
                respuesta = respuestas.get(pregunta.uuid)
                valor = respuesta.valor if respuesta else None
                marca = ' <span class="suave">(estimación)</span>' if respuesta and respuesta.aproximada else ''
                filas.append((
                    numero,
                    _e(pregunta.titulo),
                    '<span class="suave">sin contestar</span>' if valor is None else f'{valor:g}',
                    _e(_descripcion_de(pregunta, valor)) + marca))
            partes.append(f'<h3>{_e(secciones.NOMBRE[seccion])}</h3>')
            partes.append(_tabla(['#', 'Pregunta', 'Puntaje', 'Respuesta'], filas,
                                 clases=('num', '', 'num', '')))

    partes.append(_pie())
    partes.append('</body></html>')
    return '\n'.join(partes)


def html_de_area(almacen: Almacen, area_id: int) -> str:
    """El consolidado del área: todas sus cepas y el estado de sus evaluaciones."""
    area = almacen.area(area_id)
    cepas = almacen.cepas(area_id)

    partes = [f'<html><head><meta charset="utf-8"><style>{ESTILO}</style></head><body>']
    partes.append(_encabezado(f'Resumen del área — {area.nombre}',
                              f'{len(cepas)} cepa(s)'))
    if area.responsable:
        partes.append(f'<p>Responsable del área: <b>{_e(area.responsable)}</b></p>')

    filas = []
    for cepa in cepas:
        evaluaciones = {e.tipo: e for e in almacen.evaluaciones(cepa.id)}
        celdas = [_e(cepa.nombre)]
        for tipo in modelo.TIPOS:
            evaluacion = evaluaciones.get(tipo)
            if evaluacion is None:
                celdas.append('<span class="suave">sin empezar</span>')
            else:
                hechas = len(almacen.respuestas(evaluacion.id))
                total = len(modelo.incluido(tipo).preguntas)
                celdas.append(f'{hechas} de {total}' if hechas < total else 'completa')
        filas.append(tuple(celdas))
    partes.append('<h2>Estado de las evaluaciones</h2>')
    partes.append(_tabla(['Cepa', secciones.NOMBRE_EVALUACION['bioseguridad'],
                          secciones.NOMBRE_EVALUACION['bioproteccion']], filas))

    for tipo in modelo.TIPOS:
        cuestionario = modelo.incluido(tipo)
        titulos = [p.titulo for p in cuestionario.perfiles.values()]
        columnas, filas = ['Cepa'] + titulos, []
        hubo = False
        for cepa in cepas:
            for evaluacion in almacen.evaluaciones(cepa.id, tipo=tipo):
                puntajes = motor.resultados(cuestionario, almacen.puntajes(evaluacion.id))
                filas.append((_e(cepa.nombre),
                              *[f'{puntajes[u]:.3f}' for u in cuestionario.perfiles]))
                hubo = True
        if hubo:
            partes.append(f'<h2>{_e(secciones.NOMBRE_EVALUACION[tipo])}: '
                          'comparación entre cepas</h2>')
            partes.append(_tabla(columnas, filas,
                                 clases=('',) + ('num',) * len(titulos)))

    partes.append(_pie())
    partes.append('</body></html>')
    return '\n'.join(partes)


def csv_de_evaluacion(almacen: Almacen, evaluacion_id: int) -> str:
    """Las respuestas y los resultados, para abrirlos en una hoja de cálculo."""
    evaluacion = almacen.evaluacion(evaluacion_id)
    cepa = almacen.cepa(evaluacion.cepa_id)
    area = almacen.area(cepa.area_id)
    cuestionario = modelo.incluido(evaluacion.tipo)
    respuestas = almacen.respuestas(evaluacion_id)
    seccion_de = secciones.por_pregunta(cuestionario, evaluacion.tipo)

    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(['área', 'cepa', 'evaluación', 'sección', 'número',
                       'pregunta', 'puntaje', 'estimación', 'respuesta'])
    for numero, pregunta in enumerate(cuestionario.preguntas_en_orden(), 1):
        respuesta = respuestas.get(pregunta.uuid)
        valor = respuesta.valor if respuesta else None
        escritor.writerow([
            _celda(area.nombre), _celda(cepa.nombre),
            secciones.NOMBRE_EVALUACION[evaluacion.tipo],
            secciones.NOMBRE.get(seccion_de.get(pregunta.uuid), ''), numero,
            _celda(' '.join(pregunta.titulo.split())),
            '' if valor is None else f'{valor:g}',
            'sí' if respuesta and respuesta.aproximada else '',
            _celda(_descripcion_de(pregunta, valor))])

    escritor.writerow([])
    escritor.writerow(['resultado', 'puntaje'])
    puntajes = motor.resultados(cuestionario, {p: r.valor for p, r in respuestas.items()})
    for uuid, valor in puntajes.items():
        texto = ('sin valor' if math.isnan(valor)
                 else 'infinito' if math.isinf(valor) else f'{valor:.6f}')
        escritor.writerow([_celda(cuestionario.perfiles[uuid].titulo), texto])
    return salida.getvalue()
