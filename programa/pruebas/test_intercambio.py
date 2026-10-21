"""Importar y exportar .raml: no perder lo hecho, y poder volver al programa viejo."""
from pathlib import Path

import pytest

from bioram import intercambio, modelo, motor
from bioram.datos import Respuesta

AQUI = Path(__file__).resolve().parent
# Archivo de respuestas del BioRAM original que viene con el código fuente.
ORIGINAL = AQUI / 'referencias' / 'BiosafetyTestResponses.raml'


@pytest.mark.skipif(not ORIGINAL.exists(), reason='falta el archivo de ejemplo')
def test_importar_un_archivo_del_programa_original():
    cuestionario = modelo.incluido('bioseguridad')
    leido = intercambio.leer_respuestas(ORIGINAL, cuestionario)

    assert 'All fours' in leido.conjuntos
    assert len(leido.conjuntos['All fours']) == 105
    assert not leido.desconocidas, 'ninguna respuesta debería sobrar'


@pytest.mark.skipif(not ORIGINAL.exists(), reason='falta el archivo de ejemplo')
def test_las_respuestas_importadas_dan_el_puntaje_conocido():
    """'All fours' ya tiene resultado conocido, calculado con el motor Java."""
    cuestionario = modelo.incluido('bioseguridad')
    respuestas = intercambio.leer_respuestas(ORIGINAL, cuestionario).conjuntos['All fours']
    puntajes = motor.resultados(cuestionario, {u: r.valor for u, r in respuestas.items()})
    por_titulo = {p.titulo: puntajes[u] for u, p in cuestionario.perfiles.items()}

    assert por_titulo['Probabilidad por ingestión (individuo)'] == pytest.approx(2.246251, abs=1e-6)
    assert por_titulo['Probabilidad por inhalación (individuo)'] == pytest.approx(0.938083, abs=1e-6)


def test_ida_y_vuelta(tmp_path):
    """Exportar y volver a importar tiene que devolver lo mismo."""
    cuestionario = modelo.incluido('bioproteccion')
    original = {u: Respuesta(float(i % 5))
                for i, u in enumerate(sorted(cuestionario.preguntas))}

    archivo = tmp_path / 'ida.raml'
    intercambio.escribir_respuestas(archivo, modelo.ruta_incluido('bioproteccion'),
                                    {'Cepa X': original}, responsables='Pérez')
    leido = intercambio.leer_respuestas(archivo, cuestionario)

    assert leido.responsables == 'Pérez'
    assert {u: r.valor for u, r in leido.conjuntos['Cepa X'].items()} == \
           {u: r.valor for u, r in original.items()}


def test_se_avisa_de_las_respuestas_que_no_son_de_este_cuestionario(tmp_path):
    """Un archivo de otra versión del modelo no debe colarse en silencio."""
    cuestionario = modelo.incluido('bioseguridad')
    conocida = sorted(cuestionario.preguntas)[0]
    archivo = tmp_path / 'mezcla.raml'
    intercambio.escribir_respuestas(
        archivo, modelo.ruta_incluido('bioseguridad'),
        {'mezcla': {conocida: Respuesta(4.0)}})

    # se añade a mano una respuesta con un identificador inventado
    import xml.etree.ElementTree as ET, zipfile
    with zipfile.ZipFile(archivo) as z:
        raiz = ET.fromstring(z.read('model.xml'))
    conjunto = raiz.find('.//ResponseSet')
    extra = ET.SubElement(conjunto, 'response')
    extra.set('uuid', '00000000-0000-0000-0000-000000000000')
    extra.text = '1.0'
    with zipfile.ZipFile(archivo, 'w') as z:
        z.writestr('model.xml', ET.tostring(raiz, encoding='UTF-8', xml_declaration=True))

    leido = intercambio.leer_respuestas(archivo, cuestionario)
    assert leido.desconocidas == {'mezcla': 1}
    assert len(leido.conjuntos['mezcla']) == 1
