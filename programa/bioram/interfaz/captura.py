"""La pantalla donde se contesta el cuestionario.

En el programa original cada pregunta se respondía tecleando un número, con los
criterios ("4 = ...", "2 = ...") en un texto aparte que había que leer y
traducir a mano. Aquí cada criterio es una opción de la lista, así que se elige
la frase y el número lo pone el programa. Se escribe lo mismo en el archivo.
"""
from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFrame, QHBoxLayout, QInputDialog,
                               QLabel, QLineEdit, QScrollArea, QVBoxLayout, QWidget)

from ..datos import Respuesta
from ..modelo import Cuestionario, Pregunta

SIN_RESPONDER = 'Sin responder'
OTRO = 'Otro valor…'
# Los cuestionarios oficiales traen respuestas con valores que no figuran en la
# lista de criterios (por ejemplo 3 donde los criterios son 4, 2, 1 y 0): el
# programa original dejaba teclear cualquier número dentro de los límites. Hay
# que poder mostrarlos y capturarlos, o se perderían respuestas.
INTERMEDIO = 'valor intermedio'
# Los criterios vienen como "4 = Materiales biológicos purificados", una línea
# por opción. A veces el mismo puntaje aparece dos veces, con redacciones
# distintas, y hay que conservar las dos.
CRITERIO = re.compile(r'^\s*(\d+(?:\.\d+)?)\s*=\s*(.+)$')


def opciones_de(pregunta: Pregunta) -> list[tuple[float, str]]:
    """Las opciones de respuesta que describe el texto de criterios."""
    opciones = []
    for linea in (pregunta.detalle or '').splitlines():
        m = CRITERIO.match(linea)
        if m:
            opciones.append((float(m.group(1)), m.group(2).strip()))
    return opciones


class FilaPregunta(QFrame):
    """Una pregunta: su número, su texto, sus criterios y la respuesta."""

    cambiada = Signal(str, object)      # uuid, Respuesta | None

    def __init__(self, numero: int, pregunta: Pregunta, parent=None):
        super().__init__(parent)
        self.pregunta = pregunta
        self.setFrameShape(QFrame.StyledPanel)

        disposicion = QVBoxLayout(self)
        disposicion.setSpacing(6)

        titulo = QLabel(f'<b>{numero}.</b> {pregunta.titulo}')
        titulo.setWordWrap(True)
        disposicion.addWidget(titulo)

        self.opciones = opciones_de(pregunta)
        fila = QHBoxLayout()
        self.respuesta = QComboBox()
        self.respuesta.addItem(SIN_RESPONDER, None)
        for valor, texto in self.opciones:
            self.respuesta.addItem(f'{valor:g} — {texto}', valor)
        self.respuesta.addItem(OTRO, OTRO)
        self.respuesta.setMinimumWidth(420)
        if not self.opciones:
            self.respuesta.setToolTip(
                f'Esta pregunta no trae criterios; use «{OTRO}» para escribir un '
                f'número entre {pregunta.minimo:g} y {pregunta.maximo:g}')
        fila.addWidget(self.respuesta, 1)

        self.aproximada = QCheckBox('Aproximada')
        self.aproximada.setToolTip('Marque si la respuesta es una estimación')
        fila.addWidget(self.aproximada)
        disposicion.addLayout(fila)

        if pregunta.detalle and not self.opciones:
            criterios = QLabel(pregunta.detalle)
            criterios.setWordWrap(True)
            criterios.setStyleSheet('color: #555;')
            disposicion.addWidget(criterios)

        self.respuesta.currentIndexChanged.connect(self._avisar)
        self.aproximada.toggled.connect(self._avisar)

    def _valor(self):
        dato = self.respuesta.currentData()
        return None if dato is None or dato == OTRO else float(dato)

    def _indice_de(self, valor: float) -> int:
        """Índice de la opción con ese valor; si no existe, la crea."""
        indice = self.respuesta.findData(valor)
        if indice >= 0:
            return indice
        self.respuesta.insertItem(self.respuesta.count() - 1,
                                  f'{valor:g} — ({INTERMEDIO})', valor)
        return self.respuesta.count() - 2

    def _pedir_otro(self):
        valor, ok = QInputDialog.getDouble(
            self, 'Otro valor', f'Puntaje entre {self.pregunta.minimo:g} y '
            f'{self.pregunta.maximo:g}:', self.pregunta.minimo,
            self.pregunta.minimo, self.pregunta.maximo, 2)
        self.respuesta.blockSignals(True)
        self.respuesta.setCurrentIndex(self._indice_de(valor) if ok else self._ultimo_indice)
        self.respuesta.blockSignals(False)

    _ultimo_indice = 0

    def _avisar(self, *_):
        if self.respuesta.currentData() == OTRO:
            self._pedir_otro()
        self._ultimo_indice = self.respuesta.currentIndex()
        valor = self._valor()
        self.aproximada.setEnabled(valor is not None)
        self.cambiada.emit(self.pregunta.uuid,
                           None if valor is None else Respuesta(valor, self.aproximada.isChecked()))

    def mostrar(self, respuesta: Respuesta | None):
        """Pone la respuesta guardada, sin disparar avisos."""
        for control in (self.respuesta, self.aproximada):
            control.blockSignals(True)
        if respuesta is None:
            self.respuesta.setCurrentIndex(0)
            self.aproximada.setChecked(False)
        else:
            self.respuesta.setCurrentIndex(self._indice_de(respuesta.valor))
            self.aproximada.setChecked(respuesta.aproximada)
        self._ultimo_indice = self.respuesta.currentIndex()
        self.aproximada.setEnabled(respuesta is not None)
        for control in (self.respuesta, self.aproximada):
            control.blockSignals(False)

    def coincide_con(self, texto: str) -> bool:
        texto = texto.lower()
        return texto in self.pregunta.titulo.lower() or texto in (self.pregunta.detalle or '').lower()


class PanelCaptura(QWidget):
    """El cuestionario completo, con su buscador y el avance."""

    cambiada = Signal(str, object)

    def __init__(self, cuestionario: Cuestionario, parent=None):
        super().__init__(parent)
        self.cuestionario = cuestionario
        self.filas: dict[str, FilaPregunta] = {}

        disposicion = QVBoxLayout(self)

        barra = QHBoxLayout()
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText('Buscar en las preguntas…')
        self.buscador.setClearButtonEnabled(True)
        self.buscador.textChanged.connect(self._filtrar)
        barra.addWidget(self.buscador, 1)
        self.avance = QLabel()
        barra.addWidget(self.avance)
        disposicion.addLayout(barra)

        contenedor = QWidget()
        self.lista = QVBoxLayout(contenedor)
        self.lista.setSpacing(8)
        for numero, pregunta in enumerate(cuestionario.preguntas_en_orden(), 1):
            fila = FilaPregunta(numero, pregunta)
            fila.cambiada.connect(self.cambiada)
            fila.cambiada.connect(lambda *_: self._actualizar_avance())
            self.filas[pregunta.uuid] = fila
            self.lista.addWidget(fila)
        self.lista.addStretch(1)

        area = QScrollArea()
        area.setWidget(contenedor)
        area.setWidgetResizable(True)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        disposicion.addWidget(area, 1)

        self._actualizar_avance()

    def mostrar(self, respuestas: dict[str, Respuesta]):
        for uuid, fila in self.filas.items():
            fila.mostrar(respuestas.get(uuid))
        self._actualizar_avance()

    def _actualizar_avance(self):
        contestadas = sum(1 for f in self.filas.values() if f._valor() is not None)
        total = len(self.filas)
        self.avance.setText(f'<b>{contestadas}</b> de {total} respondidas')

    def _filtrar(self, texto):
        for fila in self.filas.values():
            fila.setVisible(not texto or fila.coincide_con(texto))
