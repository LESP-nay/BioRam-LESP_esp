# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""El aspecto del programa: colores, tamaños y piezas que se repiten.

Pensado para quien usa poco la computadora: letra grande, botones con texto
(no solo iconos), colores que siempre significan lo mismo y mucho aire entre
las cosas.

Los colores salen de dos sitios, los dos propios: el azul marino #232858 del
logotipo oficial del laboratorio, que es el institucional y manda en todo el
programa, y el cian del icono del programa para el segundo plano.

El cian está en el tono 190°, y esa cifra importa. El turquesa del logotipo está
en 178°, al filo del verde, y oscurecido lo bastante para que se lea encima sale
un verde apagado: el laboratorio lo vio y pidió cambiarlo. A 190° ya no hay
duda, es azul. El icono del programa no tiene un solo píxel entre 90° y 160°,
que es donde vive el verde.

Dos reglas que no se pueden romper, y la razón:

1. Todo color que lleve letras encima está medido. El turquesa puro del
   logotipo NO admite letras blancas: su contraste es 2.53, y para leer un
   texto hacen falta 4.5. Por eso donde va texto se usa el mismo tono
   oscurecido. Las medidas las comprueba pruebas/test_estilo.py, que falla si
   alguien mete un color que no se lee.

2. El programa fija su propia paleta y no adopta la de Windows. Si la adoptara,
   en Windows con tema oscuro el fondo se volvería negro mientras las letras
   siguen siendo las de aquí: letras grises sobre negro, ilegibles. Eso lo
   reportó el laboratorio y así se corrige.

Regla de color, para que no haya que aprenderse nada:
  cian        = bioseguridad
  azul marino = bioprotección, y el color institucional de todo lo demás
  verde       = ya está completo
  ámbar       = empezado, falta terminar
  gris        = todavía sin empezar
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy

MARINO = '#232858'      # del logotipo del laboratorio: el institucional
CIAN = '#02788f'        # del icono del programa, tono 190°, lejos del verde
TURQUESA = '#21b5b1'    # el del logotipo, puro: adorno, nunca con texto encima

TEXTO = '#1b2435'
TEXTO_SUAVE = '#5a6478'
FONDO = '#eef1f7'
TARJETA = '#ffffff'
BORDE = '#d3dae6'
SURCO = '#dfe5ee'             # el canal por el que corre la barra de desplazamiento

BIOSEGURIDAD = CIAN
BIOPROTECCION = MARINO
COMPLETO = '#4b7a0f'
EMPEZADO = '#b25209'
VACIO = '#646e7f'
PELIGRO = '#b91c1c'

INSTITUCIONAL = MARINO

COLOR_TIPO = {'bioseguridad': BIOSEGURIDAD, 'bioproteccion': BIOPROTECCION}
NOMBRE_TIPO = {'bioseguridad': 'Bioseguridad', 'bioproteccion': 'Bioprotección'}
INICIAL_TIPO = {'bioseguridad': 'BS', 'bioproteccion': 'BP'}

BASE_PT = 11


def color_de_avance(hechas: int, total: int) -> str:
    if total and hechas >= total:
        return COMPLETO
    return EMPEZADO if hechas else VACIO


def hoja_de_estilo() -> str:
    # as_posix: Qt lee las hojas de estilo con barras normales, también en
    # Windows, donde una barra invertida se tomaría por un escape.
    from .. import ubicacion
    PALOMITA = ubicacion.palomita().as_posix()
    return f"""
    QWidget {{ color: {TEXTO}; }}
    QMainWindow, QDialog {{ background: {FONDO}; }}
    QScrollArea {{ border: none; background: transparent; }}
    QToolTip {{ background: {MARINO}; color: white; padding: 6px; border: none; }}
    QMenuBar {{ background: {FONDO}; }}
    QMenuBar::item:selected {{ background: #dde3ee; border-radius: 6px; }}
    QMenu {{ background: {TARJETA}; border: 1px solid {BORDE}; padding: 6px; }}
    QMenu::item {{ padding: 8px 22px; border-radius: 6px; }}
    QMenu::item:selected {{ background: #e3e8f3; }}

    /* Las barras de desplazamiento llevan estilo propio a la fuerza. Qt obliga:
       en cuanto una hoja de estilo toca un control compuesto, deja de dibujar
       con el estilo del sistema las partes que la hoja no menciona. Sin estas
       reglas la barra salía blanca sobre blanco —existía, medía sus 14 píxeles
       y se podía arrastrar, pero no se veía—, y el laboratorio reportó, con
       razón, que no había con qué bajar a las preguntas de abajo. */
    QScrollBar:vertical {{
        background: {SURCO}; width: 14px; margin: 0; border-radius: 7px;
    }}
    QScrollBar::handle:vertical {{
        background: #8d9ab3; min-height: 40px; border-radius: 7px;
        border: 3px solid {SURCO};
    }}
    QScrollBar::handle:vertical:hover {{ background: {MARINO}; }}
    QScrollBar:horizontal {{
        background: {SURCO}; height: 14px; margin: 0; border-radius: 7px;
    }}
    QScrollBar::handle:horizontal {{
        background: #8d9ab3; min-width: 40px; border-radius: 7px;
        border: 3px solid {SURCO};
    }}
    QScrollBar::handle:horizontal:hover {{ background: {MARINO}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; border: none; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

    QPushButton {{
        background: {TARJETA};
        border: 1px solid {BORDE};
        border-radius: 8px;
        padding: 9px 16px;
    }}
    QPushButton:hover {{ background: #f3f6fa; border-color: #aeb9c6; }}
    QPushButton:pressed {{ background: #e6ebf2; }}
    QPushButton:disabled {{ color: {VACIO}; background: #f1f4f8; }}

    QPushButton[relieve="principal"] {{
        background: {MARINO}; color: white; border: none; font-weight: 600;
    }}
    QPushButton[relieve="principal"]:hover {{ background: #2e3670; }}

    QLineEdit, QPlainTextEdit, QTextBrowser, QComboBox, QSpinBox, QDoubleSpinBox {{
        background: {TARJETA};
        border: 1px solid {BORDE};
        border-radius: 8px;
        padding: 7px 10px;
        selection-background-color: #c9d4ea;
    }}
    QComboBox::drop-down {{ width: 26px; border: none; }}
    QComboBox QAbstractItemView {{
        background: {TARJETA}; border: 1px solid {BORDE};
        selection-background-color: #e3e8f3; selection-color: {TEXTO};
    }}

    QTabWidget::pane {{ border: 1px solid {BORDE}; border-radius: 10px; background: {TARJETA}; top: -1px; }}
    QTabBar::tab {{
        background: transparent; padding: 10px 20px; margin-right: 4px;
        border: 1px solid transparent; border-top-left-radius: 10px; border-top-right-radius: 10px;
        color: {TEXTO_SUAVE};
    }}
    QTabBar::tab:selected {{ background: {TARJETA}; border-color: {BORDE}; border-bottom-color: {TARJETA}; color: {TEXTO}; font-weight: 600; }}
    QTabBar::tab:hover:!selected {{ color: {TEXTO}; }}

    QListWidget, QTreeWidget, QTableWidget {{
        background: {TARJETA}; border: 1px solid {BORDE}; border-radius: 10px;
        outline: none;
    }}
    QListWidget::item {{ padding: 10px 8px; border-bottom: 1px solid #eef1f5; }}
    QListWidget::item:selected, QTreeWidget::item:selected {{
        background: #e3e8f3; color: {TEXTO};
    }}
    QHeaderView::section {{
        background: #f2f5fa; border: none; border-bottom: 1px solid {BORDE};
        padding: 9px; font-weight: 600;
    }}
    QTableWidget {{ gridline-color: #eef1f5; }}

    /* El texto de la barra iba en blanco sobre un canal casi blanco: 1.19 de
       contraste, invisible mientras la barra estuviera poco llena, que es justo
       cuando más falta hace leerlo. Ahora va en el color del texto normal, y
       quien quiera escribir encima de la parte llena pone la etiqueta aparte. */
    QProgressBar {{
        background: {SURCO}; border: none; border-radius: 9px; min-height: 18px;
        text-align: center; color: {TEXTO}; font-size: 10pt; font-weight: 600;
    }}
    QProgressBar::chunk {{ border-radius: 9px; }}

    QCheckBox {{ spacing: 8px; }}
    QCheckBox::indicator {{
        width: 20px; height: 20px;
        border: 2px solid #9aa5b1; border-radius: 5px; background: {TARJETA};
    }}
    QCheckBox::indicator:hover {{ border-color: {MARINO}; }}
    QCheckBox::indicator:checked {{
        background: {MARINO}; border-color: {MARINO};
        image: url({PALOMITA});
    }}
    QCheckBox::indicator:disabled {{ border-color: #d2d9e2; background: #f1f4f8; }}
    """


def paleta_fija() -> QPalette:
    """La paleta del programa, escrita a mano y completa.

    Completa a propósito: si se deja un papel sin asignar, Qt lo toma del tema
    del sistema, y entonces en Windows con tema oscuro ese hueco sale negro
    mientras las letras de aquí siguen siendo oscuras. El laboratorio lo vio
    como letras grises sobre fondo negro.
    """
    p = QPalette()
    claro, texto, blanco = QColor(FONDO), QColor(TEXTO), QColor(TARJETA)
    for papel, color in (
            (QPalette.Window, claro),
            (QPalette.WindowText, texto),
            (QPalette.Base, blanco),
            (QPalette.AlternateBase, claro),
            (QPalette.Text, texto),
            (QPalette.Button, blanco),
            (QPalette.ButtonText, texto),
            (QPalette.BrightText, QColor(PELIGRO)),
            (QPalette.ToolTipBase, QColor(MARINO)),
            (QPalette.ToolTipText, blanco),
            (QPalette.Highlight, QColor(MARINO)),
            (QPalette.HighlightedText, blanco),
            (QPalette.Link, QColor(MARINO)),
            (QPalette.LinkVisited, QColor(CIAN)),
            (QPalette.PlaceholderText, QColor(VACIO)),
    ):
        for grupo in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
            p.setColor(grupo, papel, color)
    # Lo deshabilitado, encima: letra apagada y fondo sin resaltar.
    for papel in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText,
                  QPalette.HighlightedText):
        p.setColor(QPalette.Disabled, papel, QColor(VACIO))
    for papel in (QPalette.Base, QPalette.Button, QPalette.Highlight):
        p.setColor(QPalette.Disabled, papel, claro)
    return p


def aplicar(app):
    fuente = QFont(app.font())
    fuente.setPointSize(BASE_PT)
    app.setFont(fuente)
    # «Fusion» dibuja igual en Windows, en Linux y en cualquier tema. El estilo
    # nativo de Windows cambia solo con el tema del sistema, y entonces la mitad
    # del programa se oscurece y la otra mitad no.
    app.setStyle('Fusion')
    app.setPalette(paleta_fija())
    app.setStyleSheet(hoja_de_estilo())


def insignia(texto: str, color: str, diametro: int = 34) -> QPixmap:
    """Un círculo de color con dos letras o un número. Sirve de icono."""
    pixmap = QPixmap(diametro, diametro)
    pixmap.fill(Qt.transparent)
    pintor = QPainter(pixmap)
    pintor.setRenderHint(QPainter.Antialiasing)
    pintor.setBrush(QColor(color))
    pintor.setPen(Qt.NoPen)
    pintor.drawEllipse(0, 0, diametro - 1, diametro - 1)
    fuente = QFont()
    fuente.setBold(True)
    fuente.setPointSizeF(diametro * 0.38)
    pintor.setFont(fuente)
    pintor.setPen(QColor('white'))
    pintor.drawText(QRectF(0, 0, diametro, diametro), Qt.AlignCenter, texto)
    pintor.end()
    return pixmap


def icono(texto: str, color: str, diametro: int = 28) -> QIcon:
    return QIcon(insignia(texto, color, diametro))


class Tarjeta(QFrame):
    """Un recuadro blanco con sombra suave, para agrupar cosas."""

    def __init__(self, parent=None, color_borde: str = BORDE):
        super().__init__(parent)
        self.setObjectName('tarjeta')
        self.setStyleSheet(
            f'#tarjeta {{ background: {TARJETA}; border: 1px solid {color_borde};'
            f' border-radius: 12px; }}')


class Titulo(QLabel):
    def __init__(self, texto: str, tamano: int = BASE_PT + 6, color: str = TEXTO, parent=None):
        super().__init__(texto, parent)
        fuente = QFont(self.font())
        fuente.setPointSize(tamano)
        fuente.setBold(True)
        self.setFont(fuente)
        self.setStyleSheet(f'color: {color};')
        self.setWordWrap(True)


class Ayuda(QLabel):
    """Texto de apoyo: explica qué hacer, en gris y más chico."""

    def __init__(self, texto: str, parent=None):
        super().__init__(texto, parent)
        self.setStyleSheet(f'color: {TEXTO_SUAVE};')
        self.setWordWrap(True)


class BotonGrande(QPushButton):
    def __init__(self, texto: str, color: str | None = None, parent=None):
        super().__init__(texto, parent)
        self.setMinimumHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        if color:
            self.setStyleSheet(
                f'QPushButton {{ background: {color}; color: white; border: none;'
                f' border-radius: 10px; padding: 10px 18px; font-weight: 600; }}'
                f'QPushButton:hover {{ background: {QColor(color).darker(112).name()}; }}'
                f'QPushButton:disabled {{ background: #cbd3dd; color: #7b8794; }}')
        self.setIconSize(QSize(22, 22))
