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


class PanelPortada(QWidget):
    cambiada = Signal(str, str)      # responsables, procedimiento

    def __init__(self, cuestionario: Cuestionario, parent=None):
        super().__init__(parent)

        contenido = QWidget()
        columna = QVBoxLayout(contenido)

        if cuestionario.portada_imagen:
            imagen = QImage()
            imagen.loadFromData(cuestionario.portada_imagen)
            logo = QLabel()
            logo.setPixmap(QPixmap.fromImage(imagen))
            logo.setAlignment(Qt.AlignHCenter)
            columna.addWidget(logo)

        texto = QTextBrowser()
        texto.setHtml(cuestionario.portada_html)
        texto.setOpenExternalLinks(False)
        texto.setMinimumHeight(240)
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
