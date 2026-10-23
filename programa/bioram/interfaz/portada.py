# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""La ventana de créditos: logotipo, portada institucional y datos del programa.

Antes esto era una pestaña más, en medio del camino de trabajo. No tenía por qué
estarlo: nadie necesita leer los créditos para contestar un cuestionario, y en
cambio quien sí los busca —para citar el programa, para saber de quién es el
método o qué licencia tiene— los busca en el menú, que es donde se buscan
siempre. Así que vive aquí, en Ayuda.

Los avisos de Sandia van tal cual vienen en la portada del cuestionario. No se
resumen ni se reescriben: son del titular de los derechos.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QScrollArea,
                               QTextBrowser, QVBoxLayout, QWidget)

from .. import modelo
from .estilo import Ayuda, TARJETA

# El logotipo del laboratorio es casi cuadrado, muy distinto del banner apaisado
# que traía el original, así que conviene limitarlo para que no se coma la
# ventana.
ALTO_LOGO = 130


class CuadroAcercaDe(QDialog):
    """Quién hizo esto, con qué método y bajo qué licencia."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Acerca de BioRAM LESP')
        self.resize(640, 700)

        cuestionario = modelo.incluido('bioseguridad')

        contenido = QWidget()
        columna = QVBoxLayout(contenido)
        columna.setContentsMargins(20, 18, 20, 18)
        columna.setSpacing(12)

        if cuestionario.portada_imagen:
            imagen = QImage()
            imagen.loadFromData(cuestionario.portada_imagen)
            if imagen.height() > ALTO_LOGO:
                imagen = imagen.scaledToHeight(ALTO_LOGO, Qt.SmoothTransformation)
            logo = QLabel()
            logo.setPixmap(QPixmap.fromImage(imagen))
            logo.setAlignment(Qt.AlignHCenter)
            columna.addWidget(logo)

        texto = QTextBrowser()
        texto.setHtml(cuestionario.portada_html)
        texto.setOpenExternalLinks(False)
        texto.setStyleSheet(f'QTextBrowser {{ background: {TARJETA}; border: none; }}')
        columna.addWidget(texto, 1)

        columna.addWidget(Ayuda(
            'Los cuestionarios y el cálculo son los de BioRAM, de Sandia National '
            'Laboratories, traducidos al español y comprobados contra el programa '
            'original: los resultados son los mismos. El detalle de esa comprobación '
            'está en VERIFICACION.md, y la procedencia y los derechos en AVISO.md.\n\n'
            'Este programa es software libre bajo la Licencia Pública General de GNU, '
            'versión 3 o posterior. El texto completo está en el archivo LICENSE.'))

        area = QScrollArea()
        area.setWidget(contenido)
        area.setWidgetResizable(True)

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)

        disposicion = QVBoxLayout(self)
        disposicion.addWidget(area, 1)
        disposicion.addWidget(botones)
