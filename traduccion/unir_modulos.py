#!/usr/bin/env python3
"""Une en uno solo todos los módulos de preguntas de un modelo.

El modelo de bioprotección reparte sus 105 preguntas en dos módulos,
"Instalación" (46) y "Agente" (59). Eso obliga a responder y guardar dos veces,
y además rompe el guardado: los dos módulos traen el mismo identificador de
raíz, y al cargar respuestas el programa las reparte por ese identificador, así
que las 46 de instalación se pierden. Con un solo módulo el problema desaparece
y el cuestionario se responde de corrido, como en bioseguridad.

No se toca ninguna pregunta: se conservan sus identificadores, sus pesos y sus
textos de detalle, y las categorías de cada módulo pasan a ser categorías del
módulo único. Los perfiles de resultados apuntan a preguntas y categorías, no a
módulos, así que los cálculos no cambian. El programa lo comprueba aquí mismo.

Uso:
  python unir_modulos.py entrada.raml salida.raml "Bioprotección"
"""
import pathlib
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import motor


def escenarios_de_prueba(raiz, cuantos=5):
    """Respuestas deterministas que cubren todas las preguntas del modelo."""
    uuids = sorted(q.findtext('uuid') for q in raiz.iter('QuestionSetQuestion'))
    return [{u: float((i * 7 + k * 3) % 5) for i, u in enumerate(uuids)}
            for k in range(cuantos)]


def puntajes(raiz, respuestas):
    perfiles = motor.cargar_perfiles(raiz)
    return [round(n.puntaje(respuestas, perfiles), 10) for n in perfiles.values()]


def unir(entrada, salida, titulo):
    with zipfile.ZipFile(entrada) as z:
        raiz = ET.fromstring(z.read('model.xml'))
        modulos = raiz.findall('QuestionModule')
        if len(modulos) < 2:
            sys.exit(f'{entrada} ya tiene un solo módulo')

        antes = [puntajes(raiz, r) for r in escenarios_de_prueba(raiz)]

        primero = modulos[0]
        raiz_unica = primero.find('QuestionSetRoot')
        hijos = raiz_unica.find('Children')
        raiz_unica.find('title').text = titulo

        preguntas = len(list(primero.iter('QuestionSetQuestion')))
        for extra in modulos[1:]:
            otra = extra.find('QuestionSetRoot')
            preguntas += len(list(otra.iter('QuestionSetQuestion')))
            hijos_otra = otra.find("Children")
            for hijo in list(hijos_otra if hijos_otra is not None else []):
                hijos.append(hijo)
            # Los conjuntos de respuestas guardados (en bioprotección, los 80
            # agentes) pasan al módulo único: van por UUID de pregunta.
            for conjunto in extra.findall('ResponseSet'):
                primero.append(conjunto)
            raiz.remove(extra)

        despues = [puntajes(raiz, r) for r in escenarios_de_prueba(raiz)]
        if antes != despues:
            sys.exit('ABORTADO: unir los módulos cambiaría los resultados')

        xml = ET.tostring(raiz, encoding='UTF-8', xml_declaration=True)
        with zipfile.ZipFile(salida, 'w', zipfile.ZIP_DEFLATED) as out:
            for info in z.infolist():
                out.writestr(info, xml if info.filename == 'model.xml' else z.read(info.filename))

    conjuntos = len(primero.findall('ResponseSet'))
    print(f'{len(modulos)} módulos unidos en "{titulo}": {preguntas} preguntas, '
          f'{conjuntos} conjuntos de respuestas; los {len(antes[0])} perfiles dan '
          f'los mismos resultados en {len(antes)} escenarios -> {salida}')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    unir(*sys.argv[1:])
