# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Información preliminar: la portada del cuestionario y los datos de cabecera.

Son los dos datos que salen en el reporte: quién hace la evaluación y qué
procedimiento o actividad se evalúa.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QFormLayout, QLabel, QPlainTextEdit, QScrollArea,
                               QTextBrowser, QVBoxLayout, QWidget)

from ..modelo import Cuestionario


# Alto del logotipo y de la portada, en puntos. El logotipo del laboratorio es
# casi cuadrado, muy distinto del banner apaisado que traía el original, así que
# conviene limitarlo para que no se coma la pantalla.
ALTO_LOGO = 120
ALTO_PORTADA = 380


class PanelPortada(QWidget):
    cambiada = Signal(str, str)      # responsables, procedimiento

    def __init__(self, cuestionario: Cuestionario, parent=None):
        super().__init__(parent)

        contenido = QWidget()
        columna = QVBoxLayout(contenido)

        if cuestionario.portada_imagen:
            imagen = QImage()
            imagen.loadFromData(cuestionario.portada_imagen)
            # Un logotipo muy alto empujaba el texto de la portada detrás de su
            # propia barra de desplazamiento, con dos barras anidadas a la vista.
            if imagen.height() > ALTO_LOGO:
                imagen = imagen.scaledToHeight(ALTO_LOGO, Qt.SmoothTransformation)
            logo = QLabel()
            logo.setPixmap(QPixmap.fromImage(imagen))
            logo.setAlignment(Qt.AlignHCenter)
            columna.addWidget(logo)

        texto = QTextBrowser()
        texto.setHtml(cuestionario.portada_html)
        texto.setOpenExternalLinks(False)
        # Alto suficiente para que la portada completa se lea de un vistazo:
        # encabezado, título, contacto, advertencia y créditos. Si aun así no
        # cabe, la ventana entera se desplaza, que es lo esperable.
        texto.setMinimumHeight(ALTO_PORTADA)
        columna.addWidget(texto)

        self.responsables = QPlainTextEdit()
        self.responsables.setPlaceholderText(
            'Nombre de la persona o personas responsables de la evaluación')
        self.responsables.setMaximumHeight(70)
        self.procedimiento = QPlainTextEdit()
        self.procedimiento.setPlaceholderText(
            'Procedimiento o actividad de laboratorio que se evalúa (incluya los '
            'agentes, los hospedadores en riesgo y los datos que identifican al '
            'área y al personal)')
        self.procedimiento.setMaximumHeight(110)

        formulario = QFormLayout()
        formulario.addRow('Responsables:', self.responsables)
        formulario.addRow('Procedimiento:', self.procedimiento)
        columna.addLayout(formulario)
        columna.addStretch(1)

        area = QScrollArea()
        area.setWidget(contenido)
        area.setWidgetResizable(True)
        disposicion = QVBoxLayout(self)
        disposicion.addWidget(area)

        for campo in (self.responsables, self.procedimiento):
            campo.textChanged.connect(self._avisar)

    def _avisar(self):
        self.cambiada.emit(self.responsables.toPlainText(),
                           self.procedimiento.toPlainText())

    def mostrar(self, responsables: str, procedimiento: str):
        for campo, valor in ((self.responsables, responsables),
                             (self.procedimiento, procedimiento)):
            campo.blockSignals(True)
            campo.setPlainText(valor or '')
            campo.blockSignals(False)
