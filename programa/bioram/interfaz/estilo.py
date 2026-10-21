"""El aspecto del programa: colores, tamaños y piezas que se repiten.

Pensado para quien usa poco la computadora: letra grande, botones con texto
(no solo iconos), colores que siempre significan lo mismo y mucho aire entre
las cosas.

Regla de color, para que no haya que aprenderse nada:
  verde  = bioseguridad, y también "ya está completo"
  azul   = bioprotección
  ámbar  = empezado, falta terminar
  gris   = todavía sin empezar
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy

# Paleta
TEXTO = '#1f2933'
TEXTO_SUAVE = '#616e7c'
FONDO = '#eef2f7'
TARJETA = '#ffffff'
BORDE = '#d6dde6'

BIOSEGURIDAD = '#15803d'
BIOPROTECCION = '#1d4ed8'
COMPLETO = '#15803d'
EMPEZADO = '#b45309'
VACIO = '#9aa5b1'
PELIGRO = '#b91c1c'

COLOR_TIPO = {'bioseguridad': BIOSEGURIDAD, 'bioproteccion': BIOPROTECCION}
NOMBRE_TIPO = {'bioseguridad': 'Bioseguridad', 'bioproteccion': 'Bioprotección'}
INICIAL_TIPO = {'bioseguridad': 'BS', 'bioproteccion': 'BP'}

BASE_PT = 11


def color_de_avance(hechas: int, total: int) -> str:
    if total and hechas >= total:
        return COMPLETO
    return EMPEZADO if hechas else VACIO


def hoja_de_estilo() -> str:
    return f"""
    QWidget {{ color: {TEXTO}; }}
    QMainWindow, QDialog {{ background: {FONDO}; }}
    QScrollArea {{ border: none; background: transparent; }}
    QToolTip {{ background: #111; color: white; padding: 6px; border: none; }}

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
        background: {BIOPROTECCION}; color: white; border: none; font-weight: 600;
    }}
    QPushButton[relieve="principal"]:hover {{ background: #1b45bd; }}

    QLineEdit, QPlainTextEdit, QTextBrowser, QComboBox, QSpinBox, QDoubleSpinBox {{
        background: {TARJETA};
        border: 1px solid {BORDE};
        border-radius: 8px;
        padding: 7px 10px;
        selection-background-color: #cfe0ff;
    }}
    QComboBox::drop-down {{ width: 26px; border: none; }}
    QComboBox QAbstractItemView {{
        background: {TARJETA}; border: 1px solid {BORDE};
        selection-background-color: #e8eefc; selection-color: {TEXTO};
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
        background: #e8eefc; color: {TEXTO};
    }}
    QHeaderView::section {{
        background: #f4f7fb; border: none; border-bottom: 1px solid {BORDE};
        padding: 9px; font-weight: 600;
    }}
    QTableWidget {{ gridline-color: #eef1f5; }}

    QProgressBar {{
        background: #e7ecf3; border: none; border-radius: 9px; min-height: 18px;
        text-align: center; color: white; font-size: 10pt; font-weight: 600;
    }}
    QProgressBar::chunk {{ border-radius: 9px; }}

    QCheckBox {{ spacing: 8px; }}
    QCheckBox::indicator {{
        width: 20px; height: 20px;
        border: 2px solid #9aa5b1; border-radius: 5px; background: {TARJETA};
    }}
    QCheckBox::indicator:hover {{ border-color: {BIOPROTECCION}; }}
    QCheckBox::indicator:checked {{
        background: {BIOPROTECCION}; border-color: {BIOPROTECCION};
        image: none;
    }}
    QCheckBox::indicator:disabled {{ border-color: #d2d9e2; background: #f1f4f8; }}
    """


def aplicar(app):
    fuente = QFont(app.font())
    fuente.setPointSize(BASE_PT)
    app.setFont(fuente)
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
