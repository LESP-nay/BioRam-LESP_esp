# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Lo que tiene que viajar dentro del ejecutable.

Estas pruebas existen por un fallo real: el programa cargaba la traducción al
español de Qt desde la biblioteca instalada, y funcionaba en Linux. La rueda de
PySide6 para Windows NO trae esa carpeta, así que el armado del ejecutable se
detuvo justo en la máquina donde hacía falta. Lo que viaje con el programa tiene
que estar en el repositorio y comprobarse aquí, no darse por supuesto.
"""
from __future__ import annotations

import pathlib

import pytest

from bioram import ubicacion
from bioram.sin_pantalla import plataforma_sin_ventana

SPEC = pathlib.Path(__file__).resolve().parent.parent / 'empaquetar' / 'bioram_lesp.spec'


def _aplicacion():
    """La de widgets, no la de Gui: Qt sólo admite una por proceso."""
    plataforma_sin_ventana()
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([''])


def test_el_icono_existe_y_trae_los_tamanos_que_windows_pide():
    """Sin los tamaños chicos, Windows escala el de 256 y se ve borroso."""
    pytest.importorskip('PySide6')
    ruta = ubicacion.icono_del_programa()
    assert ruta.is_file(), f'falta el icono del programa: {ruta}'

    _aplicacion()
    from PySide6.QtGui import QIcon
    tamanos = sorted(s.width() for s in QIcon(str(ruta)).availableSizes())
    for pedido in (16, 32, 48, 256):
        assert pedido in tamanos, f'al icono le falta el tamaño {pedido}'


def test_la_traduccion_de_qt_viaja_con_el_programa():
    """En el repositorio, no en la biblioteca: en Windows no está ahí."""
    ruta = ubicacion.traduccion_de_qt()
    assert ruta.is_file(), (
        f'falta la traducción al español de Qt: {ruta}. Sin ella los botones de '
        'los cuadros de diálogo salen en inglés.')


def test_los_botones_de_qt_salen_en_espanol():
    """La prueba de verdad: que el archivo sirva, no sólo que exista."""
    pytest.importorskip('PySide6')
    from PySide6.QtCore import QTranslator
    from PySide6.QtWidgets import QDialogButtonBox

    app = _aplicacion()
    traductor = QTranslator()
    assert traductor.load(str(ubicacion.traduccion_de_qt()))
    app.installTranslator(traductor)
    try:
        caja = QDialogButtonBox(QDialogButtonBox.Close | QDialogButtonBox.Cancel)
        textos = {b.text().replace('&', '') for b in caja.buttons()}
        assert textos == {'Cerrar', 'Cancelar'}, textos
    finally:
        app.removeTranslator(traductor)


def test_la_palomita_de_las_casillas_viaja_y_la_hoja_de_estilo_la_usa():
    """Sin ella, una casilla marcada es sólo un cuadro de color."""
    pytest.importorskip('PySide6')
    from bioram.interfaz import estilo

    ruta = ubicacion.palomita()
    assert ruta.is_file(), f'falta la palomita: {ruta}'
    hoja = estilo.hoja_de_estilo()
    assert f'image: url({ruta.as_posix()})' in hoja
    assert '\\' not in ruta.as_posix(), (
        'en una hoja de estilo de Qt la barra invertida se toma por un escape')


@pytest.mark.parametrize('archivo', ['bioram.ico', 'qtbase_es.qm', 'palomita.png'])
def test_la_receta_del_ejecutable_se_lleva_esos_archivos(archivo):
    """De nada sirve que estén si PyInstaller no los mete dentro."""
    assert SPEC.is_file()
    assert archivo in SPEC.read_text(encoding='utf-8'), (
        f'{archivo} no aparece en {SPEC.name}: no viajaría dentro del ejecutable')


# ---------------------------------------------------------------------------
# Las rutas al histórico

def test_las_rutas_al_historico_apuntan_a_algo_que_existe():
    """Mover una carpeta no puede romper en silencio una comprobación.

    Al separar el repositorio en «programa», «traduccion» e «historico», una
    prueba que compara contra el modelo inglés de Sandia dejó de encontrarlo y
    pasó a saltarse sola: seguía saliendo todo en verde con una comprobación
    menos. Esta prueba recorre lo que apunta al histórico y falla si algo no
    está, que es lo que debió pasar entonces.
    """
    raiz = pathlib.Path(__file__).resolve().parent.parent.parent
    if not (raiz / 'historico').is_dir():
        pytest.skip('sólo se distribuyó la carpeta programa/, sin el histórico')

    import re
    faltan = []
    for carpeta in ('traduccion', 'programa'):
        if not (raiz / carpeta).is_dir():
            continue
        for archivo in list((raiz / carpeta).rglob('*.py')) + \
                       list((raiz / carpeta).rglob('*.sh')):
            if '__pycache__' in str(archivo):
                continue
            texto = archivo.read_text(encoding='utf-8', errors='replace')
            rutas = set(re.findall(r"historico/[\w\-./ ]+?\.(?:raml|jar|zip|exe|pdf)",
                                   texto))
            for trozos in re.findall(r"'historico'(?:\s*/\s*'[^']+')+", texto):
                rutas.add('/'.join(re.findall(r"'([^']+)'", trozos)))
            for ruta in rutas:
                if not (raiz / ruta).exists():
                    faltan.append(f'{archivo.relative_to(raiz)} apunta a {ruta}')
    assert not faltan, 'rutas al histórico que ya no existen:\n  ' + '\n  '.join(faltan)
