# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Lectura de los cuestionarios de BioRAM.

Un cuestionario es un archivo .raml: un ZIP con model.xml, que describe las
preguntas y cómo se combinan para dar los resultados, más las imágenes.

Aquí solo se lee. El cálculo está en motor.py y las respuestas del laboratorio
en datos.py; el cuestionario nunca se modifica.
"""
from __future__ import annotations

import functools
import hashlib
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

# Los dos cuestionarios viajan dentro del programa: no hay archivos sueltos
# que el usuario pueda confundir o borrar.
CUESTIONARIOS = Path(__file__).resolve().parent / 'cuestionarios'
TIPOS = ('bioseguridad', 'bioproteccion')

# Tipos de nodo del árbol de resultados que el motor sabe calcular.
NODOS_RESULTADO = (
    'ResultTitle', 'ResultCategory', 'ResultQuestion', 'ResultReference',
    'ResultMathOpAdd', 'ResultMathOpSubtract', 'ResultMathOpMultiply',
    'ResultMathOpDivide', 'ResultMathOpExponent', 'ResultMathOpConstant',
    'ResultMathOpMin', 'ResultMathOpMax',
)


@dataclass
class Pregunta:
    uuid: str
    titulo: str
    detalle: str
    peso: float
    minimo: float
    maximo: float


@dataclass
class Categoria:
    uuid: str
    titulo: str
    hijos: list = field(default_factory=list)   # Categoria | Pregunta


@dataclass
class Nodo:
    """Un nodo del árbol que calcula un resultado."""
    tipo: str
    peso_bruto: float
    normaliza_hijos: bool
    hijos: list = field(default_factory=list)
    pregunta_uuid: str | None = None
    perfil_uuid: str | None = None
    constante: float = 0.0
    exponente: float = 1.0
    peso_normalizado: float = 0.0
    padre: 'Nodo | None' = None

    @property
    def peso(self) -> float:
        """El peso lo decide el padre: si normaliza, manda el normalizado."""
        if self.padre is None:
            return self.peso_bruto
        return self.peso_normalizado if self.padre.normaliza_hijos else self.peso_bruto


@dataclass
class Perfil:
    uuid: str
    titulo: str
    raiz: Nodo


@dataclass
class PuntoGrafica:
    leyenda: str
    perfil_x: str
    perfil_y: str


@dataclass
class Grafica:
    titulo: str
    eje_x: str
    eje_y: str
    minimo: float
    maximo: float
    fondo: bytes | None
    puntos: list[PuntoGrafica]


@dataclass
class Cuestionario:
    nombre: str
    raiz: Categoria
    preguntas: dict[str, Pregunta]
    perfiles: dict[str, Perfil]
    graficas: list[Grafica]
    portada_html: str
    portada_imagen: bytes | None
    # Conjuntos de respuestas que trae el propio cuestionario. En bioprotección
    # son los 80 agentes (Bacillus anthracis, etc.), que sirven de plantilla.
    plantillas: dict[str, dict[str, float]]
    # Huella de lo que afecta al cálculo, para poder decir en un reporte con
    # qué revisión del cuestionario se obtuvieron los números.
    revision: str = ''

    def preguntas_en_orden(self) -> list[Pregunta]:
        orden = []

        def recorrer(nodo):
            for hijo in nodo.hijos:
                if isinstance(hijo, Pregunta):
                    orden.append(hijo)
                else:
                    recorrer(hijo)

        recorrer(self.raiz)
        return orden


def _texto(elem, etiqueta, por_omision=''):
    valor = elem.findtext(etiqueta)
    return por_omision if valor is None else valor


def _leer_nodo(elem, padre=None) -> Nodo:
    nodo = Nodo(
        tipo=elem.tag,
        peso_bruto=float(_texto(elem, 'rawWeight', '1.0')),
        normaliza_hijos=_texto(elem, 'normalizeChildren', 'false') == 'true',
        pregunta_uuid=elem.findtext('questionUUID'),
        perfil_uuid=elem.findtext('rpUUID'),
        constante=float(_texto(elem, 'constant', '0')),
        exponente=float(_texto(elem, 'exponent', '1')),
        padre=padre,
    )
    hijos = elem.find('Children')
    if hijos is not None:
        nodo.hijos = [_leer_nodo(h, nodo) for h in hijos if h.tag in NODOS_RESULTADO]
    if nodo.normaliza_hijos and nodo.hijos:
        # Igual que ResultObject.setNormalizeChildren: si la suma es 0, divide
        # entre 1, o sea deja el peso tal cual.
        total = sum(h.peso_bruto for h in nodo.hijos) or 1.0
        for h in nodo.hijos:
            h.peso_normalizado = h.peso_bruto / total
    return nodo


def _leer_cuestionario(elem, preguntas) -> Categoria:
    cat = Categoria(uuid=_texto(elem, 'uuid'), titulo=_texto(elem, 'title'))
    hijos = elem.find('Children')
    for hijo in (hijos if hijos is not None else []):
        if hijo.tag == 'QuestionSetQuestion':
            limites = hijo.find('bounds')
            pregunta = Pregunta(
                uuid=_texto(hijo, 'uuid'),
                titulo=_texto(hijo, 'title'),
                detalle=_texto(hijo, 'detailText'),
                peso=float(_texto(hijo, 'defaultWeight', '1.0')),
                minimo=float(_texto(limites, 'min', '0')) if limites is not None else 0.0,
                maximo=float(_texto(limites, 'max', '4')) if limites is not None else 4.0,
            )
            preguntas[pregunta.uuid] = pregunta
            cat.hijos.append(pregunta)
        elif hijo.tag in ('QuestionSetCategory', 'QuestionSetRoot'):
            cat.hijos.append(_leer_cuestionario(hijo, preguntas))
    return cat


def cargar(ruta) -> Cuestionario:
    """Lee un .raml y devuelve el cuestionario."""
    ruta = Path(ruta)
    with zipfile.ZipFile(ruta) as z:
        raiz_xml = ET.fromstring(z.read('model.xml'))
        imagenes = {n: z.read(n) for n in z.namelist() if n.startswith('media/') and not n.endswith('/')}

    preguntas: dict[str, Pregunta] = {}
    modulos = raiz_xml.findall('QuestionModule')
    raices = [_leer_cuestionario(m.find('QuestionSetRoot'), preguntas) for m in modulos]
    if len(raices) == 1:
        raiz = raices[0]
    else:
        # Los cuestionarios de este proyecto vienen con un módulo único, pero
        # un .raml ajeno puede traer varios: se presentan como uno solo.
        raiz = Categoria(uuid='', titulo=raices[0].titulo, hijos=list(raices))

    plantillas: dict[str, dict[str, float]] = {}
    for conjunto in raiz_xml.iter('ResponseSet'):
        nombre = _texto(conjunto, 'responseSetName')
        # Las respuestas van por módulo: un conjunto repartido entre varios
        # módulos es un solo conjunto, y se junta por nombre.
        plantillas.setdefault(nombre, {}).update(
            {r.get('uuid'): float(r.text) for r in conjunto.findall('response')})

    perfiles = {}
    for p in raiz_xml.findall('ResultProfile'):
        uuid = _texto(p, 'uuid')
        titulo_elem = p.find('ResultTitle')
        perfiles[uuid] = Perfil(uuid=uuid,
                                titulo=_texto(titulo_elem, 'title'),
                                raiz=_leer_nodo(titulo_elem))

    graficas = []
    for g in raiz_xml.findall('Chart'):
        eje_x, eje_y = g.find('XAxis'), g.find('YAxis')
        graficas.append(Grafica(
            titulo=_texto(g, 'chartTitle'),
            eje_x=_texto(eje_x, 'title'),
            eje_y=_texto(eje_y, 'title'),
            minimo=float(_texto(eje_x, 'min', '0')),
            maximo=float(_texto(eje_x, 'max', '4')),
            fondo=imagenes.get(_texto(g, 'backgroundImagePath')),
            puntos=[PuntoGrafica(leyenda=_texto(d, 'legendTitle'),
                                 perfil_x=_texto(d, 'xResultProfileUUID'),
                                 perfil_y=_texto(d, 'yResultProfileUUID'))
                    for d in g.findall('DataPoint')],
        ))

    info = raiz_xml.find('ModelInformation')
    return Cuestionario(
        nombre=raiz.titulo,
        raiz=raiz,
        preguntas=preguntas,
        perfiles=perfiles,
        graficas=graficas,
        portada_html=_texto(info, 'frontHTML') if info is not None else '',
        portada_imagen=imagenes.get(_texto(info, 'frontImagePath')) if info is not None else None,
        plantillas=plantillas,
        revision=_revision(raiz_xml),
    )


# ---------------------------------------------------------------- revisión
# Dos cuestionarios con el mismo nombre pueden dar números distintos: así pasó
# con la referencia de puntuación que la traducción de Sandia había perdido.
# Como el programa no guarda los puntajes sino que los recalcula cada vez, hace
# falta poder decir con qué revisión se calculó un resultado; si no, un reporte
# impreso el año pasado y otro de hoy pueden no coincidir sin que nada lo
# explique.
#
# La huella se calcula SÓLO sobre lo que afecta al cálculo: los árboles de los
# perfiles de resultados y los límites de cada pregunta. Así, corregir la
# redacción de una pregunta o cambiar la portada no cambia la revisión, y
# cambiar un peso sí.

REVISIONES_CONOCIDAS = {
    # --- bioseguridad
    '53c8ebff': 'traducción oficial de Sandia tal cual, a la que le falta la '
                'referencia de ingestión; usada hasta el 23/10/2026',
    'fc20862a': 'referencia de ingestión repuesta el 23/10/2026; el cálculo '
                'queda idéntico al de la revisión inglesa de 2014 de la que se '
                'tradujo, que tiene esta misma huella',
    # --- bioprotección
    'e94994e1': 'Sandia, sin cambios en el cálculo; idéntica a la inglesa',
}


def _revision(raiz_xml) -> str:
    """Huella corta de lo que afecta al cálculo, más su descripción si se conoce."""
    partes = []
    for q in raiz_xml.iter('QuestionSetQuestion'):
        b = q.find('bounds')
        partes.append('Q' + (q.findtext('uuid') or '')
                      + ('' if b is None else f'|{b.get("lower")}|{b.get("upper")}'))
    for p in raiz_xml.findall('ResultProfile'):
        def recorrer(e):
            partes.append(e.tag + '|' + (e.findtext('rawWeight') or '')
                          + '|' + (e.findtext('questionUUID') or '')
                          + '|' + (e.findtext('value') or '')
                          + '|' + (e.findtext('normalizeChildren') or ''))
            hijos = e.find('Children')
            if hijos is not None:
                for c in hijos:
                    if c.tag.startswith('Result'):
                        recorrer(c)
        titulo = p.find('ResultTitle')
        if titulo is not None:
            recorrer(titulo)
    huella = hashlib.sha256('\n'.join(partes).encode()).hexdigest()[:8]
    descripcion = REVISIONES_CONOCIDAS.get(huella)
    return f'{huella} ({descripcion})' if descripcion else huella


@functools.lru_cache(maxsize=None)
def incluido(tipo: str) -> Cuestionario:
    """El cuestionario que viene con el programa: 'bioseguridad' o 'bioproteccion'."""
    if tipo not in TIPOS:
        raise ValueError(f'tipo desconocido: {tipo} (use {" o ".join(TIPOS)})')
    return cargar(CUESTIONARIOS / f'{tipo}.raml')


def ruta_incluido(tipo: str) -> Path:
    if tipo not in TIPOS:
        raise ValueError(f'tipo desconocido: {tipo}')
    return CUESTIONARIOS / f'{tipo}.raml'
