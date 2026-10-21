"""Entrada y salida de archivos .raml, los del BioRAM original.

Importar sirve para no perder lo ya evaluado con el programa viejo. Exportar,
para que el laboratorio pueda seguir abriendo sus evaluaciones en él o
mandárselas a alguien que no tenga este programa.

Al importar se avisa de las respuestas que no corresponden a ninguna pregunta
del cuestionario: pasa cuando el archivo viene de otra versión del modelo, y es
justo lo que conviene saber antes de darlo por bueno.
"""
from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from .datos import Respuesta
from .modelo import Cuestionario


@dataclass
class Importacion:
    """Lo que trae un archivo de respuestas, ya cotejado con el cuestionario."""
    conjuntos: dict[str, dict[str, Respuesta]] = field(default_factory=dict)
    desconocidas: dict[str, int] = field(default_factory=dict)   # conjunto -> cuántas
    responsables: str = ''
    procedimiento: str = ''

    def __bool__(self):
        return bool(self.conjuntos)


def leer_respuestas(ruta, cuestionario: Cuestionario) -> Importacion:
    """Lee los conjuntos de respuestas de un .raml y los coteja con el cuestionario."""
    with zipfile.ZipFile(ruta) as z:
        raiz = ET.fromstring(z.read('model.xml'))

    resultado = Importacion()
    info = raiz.find('ModelInformation')
    if info is not None:
        resultado.responsables = info.findtext('names') or ''
        resultado.procedimiento = info.findtext('procedure') or ''

    for conjunto in raiz.iter('ResponseSet'):
        nombre = conjunto.findtext('responseSetName') or 'sin nombre'
        # Un conjunto repartido entre varios módulos es un solo conjunto.
        destino = resultado.conjuntos.setdefault(nombre, {})
        for r in conjunto.findall('response'):
            uuid = r.get('uuid')
            if uuid in cuestionario.preguntas:
                destino[uuid] = Respuesta(float(r.text))
            else:
                resultado.desconocidas[nombre] = resultado.desconocidas.get(nombre, 0) + 1
    return resultado


def escribir_respuestas(ruta, cuestionario_raml, conjuntos: dict[str, dict],
                        responsables='', procedimiento=''):
    """Escribe un .raml de respuestas que el BioRAM original puede cargar.

    Se copia la raíz del cuestionario de origen porque el programa original
    empareja las respuestas con el módulo por ese identificador.
    """
    with zipfile.ZipFile(cuestionario_raml) as z:
        origen = ET.fromstring(z.read('model.xml'))

    salida = ET.Element('RamModel')
    info = ET.SubElement(salida, 'ModelInformation')
    ET.SubElement(info, 'names').text = responsables
    ET.SubElement(info, 'procedure').text = procedimiento

    for modulo_origen in origen.findall('QuestionModule'):
        raiz_origen = modulo_origen.find('QuestionSetRoot')
        preguntas_del_modulo = {q.findtext('uuid') for q in raiz_origen.iter('QuestionSetQuestion')}

        modulo = ET.SubElement(salida, 'QuestionModule')
        raiz = ET.SubElement(modulo, 'QuestionSetRoot')
        ET.SubElement(raiz, 'uuid').text = raiz_origen.findtext('uuid')

        for nombre, respuestas in conjuntos.items():
            conjunto = ET.SubElement(modulo, 'ResponseSet')
            ET.SubElement(conjunto, 'responseSetName').text = nombre
            for pregunta, r in respuestas.items():
                if pregunta not in preguntas_del_modulo:
                    continue
                valor = r.valor if isinstance(r, Respuesta) else float(r)
                elem = ET.SubElement(conjunto, 'response')
                elem.set('uuid', pregunta)
                elem.text = repr(float(valor))

    ruta = Path(ruta)
    with zipfile.ZipFile(ruta, 'w', zipfile.ZIP_DEFLATED) as out:
        out.writestr('model.xml', ET.tostring(salida, encoding='UTF-8', xml_declaration=True))
    return ruta
