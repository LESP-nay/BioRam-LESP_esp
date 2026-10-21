"""La pantalla donde se contesta el cuestionario.

En el programa original cada pregunta se respondía tecleando un número, con los
criterios ("4 = ...", "2 = ...") en un texto aparte que había que leer y
traducir a mano. Aquí cada criterio es una opción de la lista, así que se elige
la frase y el número lo pone el programa. Se escribe lo mismo en el archivo.
"""
from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QHBoxLayout,
                               QInputDialog, QLabel, QLineEdit, QProgressBar,
                               QPushButton, QScrollArea, QVBoxLayout, QWidget)

from ..datos import Respuesta
from ..modelo import Cuestionario, Pregunta
from .estilo import (Ayuda, BORDE, BotonGrande, COMPLETO, TARJETA, TEXTO_SUAVE,
                     Tarjeta, insignia)

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
# El cuestionario de bioseguridad numera sus preguntas en el propio enunciado,
# "(17) ¿Qué tipo de material…". Se usa ese número y no se repite en el texto.
NUMERADA = re.compile(r'^\s*\((\d+)\)\s*')


def opciones_de(pregunta: Pregunta) -> list[tuple[float, str]]:
    """Las opciones de respuesta que describe el texto de criterios."""
    opciones = []
    for linea in (pregunta.detalle or '').splitlines():
        m = CRITERIO.match(linea)
        if m:
            opciones.append((float(m.group(1)), m.group(2).strip()))
    return opciones


class FilaPregunta(Tarjeta):
    """Una pregunta: su número, su texto, sus criterios y la respuesta."""

    cambiada = Signal(str, object)      # uuid, Respuesta | None

    def __init__(self, numero: int, pregunta: Pregunta, color: str, parent=None):
        super().__init__(parent)
        self.pregunta = pregunta
        propia = NUMERADA.match(pregunta.titulo)
        self.numero = int(propia.group(1)) if propia else numero
        enunciado = NUMERADA.sub('', pregunta.titulo) if propia else pregunta.titulo
        self.color = color

        disposicion = QVBoxLayout(self)
        disposicion.setContentsMargins(14, 12, 14, 12)
        disposicion.setSpacing(8)

        arriba = QHBoxLayout()
        arriba.setSpacing(12)
        self.sello = QLabel()
        self.sello.setPixmap(insignia(str(numero), TEXTO_SUAVE, 30))
        self.sello.setFixedWidth(32)
        arriba.addWidget(self.sello, 0, Qt.AlignTop)
        titulo = QLabel(enunciado)
        titulo.setWordWrap(True)
        titulo.setStyleSheet('font-size: 11pt;')
        arriba.addWidget(titulo, 1)
        disposicion.addLayout(arriba)

        self.opciones = opciones_de(pregunta)
        fila = QHBoxLayout()
        self.respuesta = QComboBox()
        self.respuesta.addItem(SIN_RESPONDER, None)
        for valor, texto in self.opciones:
            self.respuesta.addItem(f'{valor:g} — {texto}', valor)
        self.respuesta.addItem(OTRO, OTRO)
        self.respuesta.setMinimumWidth(420)
        self.respuesta.setMinimumHeight(38)
        if not self.opciones:
            self.respuesta.setToolTip(
                f'Esta pregunta no trae criterios; use «{OTRO}» para escribir un '
                f'número entre {pregunta.minimo:g} y {pregunta.maximo:g}')
        fila.addWidget(self.respuesta, 1)

        self.aproximada = QCheckBox('Es una estimación')
        self.aproximada.setToolTip('Marque si no está seguro del dato')
        fila.addWidget(self.aproximada)
        disposicion.addLayout(fila)

        if pregunta.detalle and not self.opciones:
            criterios = QLabel(pregunta.detalle)
            criterios.setWordWrap(True)
            criterios.setStyleSheet('color: #555;')
            disposicion.addWidget(criterios)

        self.respuesta.currentIndexChanged.connect(self._avisar)
        self.aproximada.toggled.connect(self._avisar)
        self._pintar()

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
        self._pintar()
        self.cambiada.emit(self.pregunta.uuid,
                           None if valor is None else Respuesta(valor, self.aproximada.isChecked()))

    def _pintar(self):
        """Verde y número en color cuando ya está contestada."""
        contestada = self._valor() is not None
        color = self.color if contestada else TEXTO_SUAVE
        self.sello.setPixmap(insignia(str(self.numero), color, 30))
        self.setStyleSheet(
            f'#tarjeta {{ background: {TARJETA}; border-radius: 12px;'
            f' border: 1px solid {COMPLETO if contestada else BORDE};'
            f' border-left: 5px solid {color}; }}')

    def contestada(self) -> bool:
        return self._valor() is not None

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
        self._pintar()

    def coincide_con(self, texto: str) -> bool:
        texto = texto.lower()
        return texto in self.pregunta.titulo.lower() or texto in (self.pregunta.detalle or '').lower()


class PanelCaptura(QWidget):
    """El cuestionario completo: avance arriba, preguntas abajo."""

    cambiada = Signal(str, object)

    def __init__(self, cuestionario: Cuestionario, color: str = COMPLETO, parent=None):
        super().__init__(parent)
        self.cuestionario = cuestionario
        self.color = color
        self.filas: dict[str, FilaPregunta] = {}
        self.orden: list[FilaPregunta] = []

        disposicion = QVBoxLayout(self)
        disposicion.setContentsMargins(14, 14, 14, 14)
        disposicion.setSpacing(10)

        # Avance, bien visible
        self.barra = QProgressBar()
        self.barra.setRange(0, len(cuestionario.preguntas))
        self.barra.setStyleSheet(f'QProgressBar::chunk {{ background: {color}; }}')
        disposicion.addWidget(self.barra)

        # Buscar y filtrar
        barra = QHBoxLayout()
        barra.setSpacing(8)
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText('Buscar una palabra en las preguntas…')
        self.buscador.setClearButtonEnabled(True)
        self.buscador.setMinimumHeight(38)
        self.buscador.textChanged.connect(self._filtrar)
        barra.addWidget(self.buscador, 1)

        self.grupo = QButtonGroup(self)
        self.grupo.setExclusive(True)
        for i, texto in enumerate(('Todas', 'Faltan', 'Contestadas')):
            boton = QPushButton(texto)
            boton.setCheckable(True)
            boton.setChecked(i == 0)
            boton.setMinimumHeight(38)
            boton.setCursor(Qt.PointingHandCursor)
            boton.setStyleSheet(
                'QPushButton:checked { background: #dde7fb; border-color: #93b0ea;'
                ' font-weight: 600; }')
            self.grupo.addButton(boton, i)
            barra.addWidget(boton)
        self.grupo.idToggled.connect(lambda *_: self._filtrar())

        self.siguiente = BotonGrande('Ir a la siguiente sin contestar')
        self.siguiente.clicked.connect(self._ir_a_la_siguiente)
        barra.addWidget(self.siguiente)
        disposicion.addLayout(barra)

        contenedor = QWidget()
        contenedor.setStyleSheet('background: transparent;')
        self.lista = QVBoxLayout(contenedor)
        self.lista.setSpacing(10)
        for numero, pregunta in enumerate(cuestionario.preguntas_en_orden(), 1):
            fila = FilaPregunta(numero, pregunta, color)
            fila.cambiada.connect(self.cambiada)
            fila.cambiada.connect(lambda *_: self._actualizar_avance())
            self.filas[pregunta.uuid] = fila
            self.orden.append(fila)
            self.lista.addWidget(fila)
        self.lista.addStretch(1)

        self.area = QScrollArea()
        self.area.setWidget(contenedor)
        self.area.setWidgetResizable(True)
        self.area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.area.viewport().setStyleSheet('background: transparent;')
        disposicion.addWidget(self.area, 1)

        self.aviso = Ayuda('')
        disposicion.addWidget(self.aviso)

        self._actualizar_avance()

    def mostrar(self, respuestas: dict[str, Respuesta]):
        for uuid, fila in self.filas.items():
            fila.mostrar(respuestas.get(uuid))
        self._actualizar_avance()
        self._filtrar()

    def _actualizar_avance(self):
        contestadas = sum(1 for f in self.filas.values() if f.contestada())
        total = len(self.filas)
        self.barra.setValue(contestadas)
        self.barra.setFormat(
            f'{contestadas} de {total} preguntas contestadas  (%p%)'
            if contestadas < total else '¡Cuestionario completo!')
        faltan = total - contestadas
        self.siguiente.setEnabled(bool(faltan))
        self.aviso.setText(
            'Las respuestas se guardan solas en cuanto las elige.'
            if not faltan else
            f'Faltan {faltan} preguntas. Las respuestas se guardan solas.')

    def _filtrar(self, *_):
        texto = self.buscador.text()
        modo = self.grupo.checkedId()
        for fila in self.orden:
            visible = (not texto or fila.coincide_con(texto))
            if modo == 1:
                visible = visible and not fila.contestada()
            elif modo == 2:
                visible = visible and fila.contestada()
            fila.setVisible(visible)

    def _ir_a_la_siguiente(self):
        for fila in self.orden:
            if not fila.contestada() and not fila.isHidden():
                self.area.ensureWidgetVisible(fila, 0, 60)
                fila.respuesta.setFocus()
                return
