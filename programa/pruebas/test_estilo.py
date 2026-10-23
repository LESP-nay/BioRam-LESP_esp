# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Que los colores se lean, y que la barra de desplazamiento se vea.

El laboratorio reportó las dos cosas en la primera prueba beta: letras grises
sobre fondo negro en Windows con tema oscuro, y ninguna barra con que bajar a
las preguntas de abajo. Las dos estaban, y las dos eran de verdad. Estas
pruebas existen para que no vuelvan: miden el contraste con la fórmula de las
WCAG, que es la misma que usan los lectores de pantalla y las normas de
accesibilidad, y revisan que la hoja de estilo le dé forma a la barra.
"""
from __future__ import annotations

import pytest

from bioram.interfaz import estilo

# 4.5 es el mínimo para leer un texto normal; 3.0 el de un texto grande o un
# borde. Debajo de 3 no se distingue y no se puede usar para nada que importe.
TEXTO_NORMAL = 4.5
SOLO_GRANDE = 3.0


def _luminancia(color: str) -> float:
    color = color.lstrip('#')
    canales = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    canales = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
               for c in canales]
    return 0.2126 * canales[0] + 0.7152 * canales[1] + 0.0722 * canales[2]


def contraste(uno: str, otro: str) -> float:
    a, b = _luminancia(uno), _luminancia(otro)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def test_la_formula_del_contraste_da_los_valores_conocidos():
    """Si la fórmula se rompe, las demás pruebas mentirían."""
    assert contraste('#000000', '#ffffff') == pytest.approx(21.0, abs=0.01)
    assert contraste('#ffffff', '#ffffff') == pytest.approx(1.0, abs=0.01)


@pytest.mark.parametrize('nombre,color', [
    ('bioseguridad', estilo.BIOSEGURIDAD),
    ('bioprotección', estilo.BIOPROTECCION),
    ('institucional', estilo.INSTITUCIONAL),
    ('completo', estilo.COMPLETO),
    ('empezado', estilo.EMPEZADO),
    ('peligro', estilo.PELIGRO),
])
def test_los_colores_con_letras_blancas_encima_se_leen(nombre, color):
    assert contraste('#ffffff', color) >= TEXTO_NORMAL, (
        f'{nombre} ({color}) no admite letras blancas encima')


@pytest.mark.parametrize('nombre,color', [
    ('texto', estilo.TEXTO),
    ('texto de apoyo', estilo.TEXTO_SUAVE),
    ('bioseguridad', estilo.BIOSEGURIDAD),
    ('bioprotección', estilo.BIOPROTECCION),
    ('completo', estilo.COMPLETO),
    ('empezado', estilo.EMPEZADO),
    ('sin empezar', estilo.VACIO),
    ('peligro', estilo.PELIGRO),
])
@pytest.mark.parametrize('fondo', [estilo.TARJETA, estilo.FONDO])
def test_los_colores_de_texto_se_leen_sobre_los_dos_fondos(nombre, color, fondo):
    assert contraste(color, fondo) >= TEXTO_NORMAL, (
        f'{nombre} ({color}) no se lee sobre {fondo}')


def test_el_turquesa_puro_no_se_usa_con_texto():
    """El del logotipo es bonito pero no se lee: 2.53. Queda para adornos."""
    assert contraste('#ffffff', estilo.TURQUESA) < TEXTO_NORMAL
    hoja = estilo.hoja_de_estilo()
    assert f'background: {estilo.TURQUESA}' not in hoja
    assert estilo.TURQUESA not in (estilo.BIOSEGURIDAD, estilo.BIOPROTECCION,
                                   estilo.INSTITUCIONAL)


def test_ningun_color_con_texto_cae_en_la_franja_del_verde():
    """El laboratorio pidió que las palabras dejaran de verse verdes.

    El verde vive entre los 90° y los 160° del círculo cromático. El único que
    puede quedarse ahí es el de «ya está completo», porque verde quiere decir
    terminado en todas partes y cambiarlo costaría más de lo que vale.
    """
    for nombre, color in (('bioseguridad', estilo.BIOSEGURIDAD),
                          ('bioprotección', estilo.BIOPROTECCION),
                          ('institucional', estilo.INSTITUCIONAL),
                          ('texto', estilo.TEXTO),
                          ('texto de apoyo', estilo.TEXTO_SUAVE)):
        assert not 90 <= _tono(color) <= 160, (
            f'{nombre} ({color}) está en {_tono(color):.0f}°, que se ve verde')


def _tono(color: str) -> float:
    import colorsys
    color = color.lstrip('#')
    canales = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return colorsys.rgb_to_hls(*canales)[0] * 360


def test_los_dos_cuestionarios_se_distinguen_entre_si():
    """Si fueran casi el mismo color, el código de color no serviría de nada.

    Aquí la medida no es el contraste sino el tono. Dos colores pueden tener
    casi el mismo brillo —y por tanto poco contraste entre sí— y aun así
    distinguirse a la primera, que es lo que importa: el turquesa y el azul
    marino están a 56 grados en el círculo cromático. El contraste mide si un
    texto se lee encima de un fondo, no si dos colores se parecen.
    """
    separacion = abs(_tono(estilo.BIOSEGURIDAD) - _tono(estilo.BIOPROTECCION))
    separacion = min(separacion, 360 - separacion)
    assert separacion >= 40, (
        f'bioseguridad y bioprotección están a sólo {separacion:.0f}° de tono')


def test_la_barra_de_avance_no_escribe_en_blanco_sobre_claro():
    """Era 1.19 de contraste: el texto estaba y no se veía."""
    hoja = estilo.hoja_de_estilo()
    bloque = hoja.split('QProgressBar {')[1].split('}')[0]
    assert f'color: {estilo.TEXTO}' in bloque
    assert 'color: white' not in bloque
    assert contraste(estilo.TEXTO, estilo.SURCO) >= TEXTO_NORMAL


def test_la_barra_de_desplazamiento_tiene_estilo_propio_y_se_ve():
    """Qt deja de dibujar las partes que la hoja de estilo no menciona."""
    hoja = estilo.hoja_de_estilo()
    for regla in ('QScrollBar:vertical', 'QScrollBar::handle:vertical',
                  'QScrollBar:horizontal', 'QScrollBar::handle:horizontal'):
        assert regla in hoja, f'falta dar estilo a {regla}'
    manija = hoja.split('QScrollBar::handle:vertical {')[1].split('}')[0]
    color = manija.split('background:')[1].split(';')[0].strip()
    assert contraste(color, estilo.SURCO) >= 1.9, (
        f'la manija ({color}) no se distingue de su canal')


def test_la_paleta_no_deja_huecos_que_windows_pueda_oscurecer():
    """Un papel sin asignar lo llena el tema del sistema, y ahí viene el negro."""
    pytest.importorskip('PySide6')
    from PySide6.QtGui import QPalette

    paleta = estilo.paleta_fija()
    for papel in (QPalette.Window, QPalette.WindowText, QPalette.Base,
                  QPalette.Text, QPalette.Button, QPalette.ButtonText,
                  QPalette.Highlight, QPalette.HighlightedText):
        for grupo in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            assert paleta.isBrushSet(grupo, papel), (
                f'{papel} sin color en el grupo {grupo}')
    fondo = paleta.color(QPalette.Active, QPalette.Window).name()
    letra = paleta.color(QPalette.Active, QPalette.WindowText).name()
    assert contraste(letra, fondo) >= TEXTO_NORMAL


# ---------------------------------------------------------------------------
# El icono del programa

def test_el_icono_existe_y_trae_los_tamanos_que_windows_pide():
    """Sin los tamaños chicos, Windows escala el de 256 y se ve borroso."""
    pytest.importorskip('PySide6')
    from bioram import ubicacion
    from bioram.sin_pantalla import plataforma_sin_ventana

    ruta = ubicacion.icono_del_programa()
    assert ruta.is_file(), f'falta el icono del programa: {ruta}'

    plataforma_sin_ventana()
    # QApplication y no QGuiApplication: Qt sólo admite una por proceso, y las
    # pruebas de interfaz que corren después necesitan la de widgets. Si aquí se
    # crea la otra, aquéllas abortan el intérprete entero al crear el primer
    # widget.
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([''])
    tamanos = sorted(s.width() for s in QIcon(str(ruta)).availableSizes())
    for pedido in (16, 32, 48, 256):
        assert pedido in tamanos, f'al icono le falta el tamaño {pedido}'
