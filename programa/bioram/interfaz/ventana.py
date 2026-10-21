"""La ventana principal de BioRAM LESP.

A la izquierda, el laboratorio: áreas, sus cepas y, por cepa, sus dos
evaluaciones. A la derecha, la evaluación seleccionada.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QInputDialog, QLabel, QMainWindow,
                               QMessageBox, QPushButton, QSplitter, QStackedWidget,
                               QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                               QWidget)

from .. import modelo
from ..datos import Almacen
from .captura import PanelCaptura
from .portada import PanelPortada
from .resultados import PanelResultados

NOMBRE = {'bioseguridad': 'Bioseguridad', 'bioproteccion': 'Bioprotección'}
# Qué guarda cada elemento del árbol: ('area'|'cepa'|'evaluacion', id)
CLASE, ID = Qt.UserRole, Qt.UserRole + 1


class PanelEvaluacion(QWidget):
    """Las pestañas de una evaluación: preguntas y resultados."""

    def __init__(self, almacen: Almacen, evaluacion_id: int, parent=None):
        super().__init__(parent)
        self.almacen = almacen
        self.evaluacion_id = evaluacion_id
        evaluacion = almacen.evaluacion(evaluacion_id)
        cepa = almacen.cepa(evaluacion.cepa_id)
        area = almacen.area(cepa.area_id)
        cuestionario = modelo.incluido(evaluacion.tipo)

        disposicion = QVBoxLayout(self)
        encabezado = QLabel(
            f'<b>{NOMBRE[evaluacion.tipo]}</b> — {cepa.nombre}'
            f'<br><span style="color:#555">{area.nombre}</span>')
        encabezado.setTextFormat(Qt.RichText)
        disposicion.addWidget(encabezado)

        self.portada = PanelPortada(cuestionario)
        self.captura = PanelCaptura(cuestionario)
        self.resultados = PanelResultados(cuestionario)
        self.captura.cambiada.connect(self._guardar)
        self.portada.cambiada.connect(self._guardar_cabecera)

        pestanas = QTabWidget()
        pestanas.addTab(self.portada, 'Información preliminar')
        pestanas.addTab(self.captura, 'Preguntas')
        pestanas.addTab(self.resultados, 'Resultados')
        pestanas.setCurrentIndex(1)
        pestanas.currentChanged.connect(self._cambio_de_pestana)
        disposicion.addWidget(pestanas, 1)

        self.portada.mostrar(evaluacion.responsables, evaluacion.procedimiento)
        self.captura.mostrar(almacen.respuestas(evaluacion_id))
        self.resultados.mostrar(almacen.puntajes(evaluacion_id))

    def _guardar(self, pregunta, respuesta):
        if respuesta is None:
            self.almacen.borrar_respuesta(self.evaluacion_id, pregunta)
        else:
            self.almacen.guardar_respuestas(self.evaluacion_id, {pregunta: respuesta})

    def _guardar_cabecera(self, responsables, procedimiento):
        self.almacen.actualizar_evaluacion(self.evaluacion_id,
                                           responsables=responsables,
                                           procedimiento=procedimiento)

    def _cambio_de_pestana(self, indice):
        if indice == 2:      # al entrar a Resultados, recalcular
            self.resultados.mostrar(self.almacen.puntajes(self.evaluacion_id))


class Ventana(QMainWindow):
    def __init__(self, almacen: Almacen):
        super().__init__()
        self.almacen = almacen
        self.paneles: dict[int, PanelEvaluacion] = {}
        self.setWindowTitle(f'BioRAM LESP — {almacen.ruta.name}')
        self.resize(1180, 760)

        self.arbol = QTreeWidget()
        self.arbol.setHeaderLabels(['Laboratorio', 'Avance'])
        self.arbol.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.arbol.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.arbol.currentItemChanged.connect(self._seleccion)

        botones = QHBoxLayout()
        for texto, accion in (('Nueva área', self.nueva_area),
                              ('Nueva cepa', self.nueva_cepa),
                              ('Nueva evaluación', self.nueva_evaluacion)):
            b = QPushButton(texto)
            b.clicked.connect(accion)
            botones.addWidget(b)

        izquierda = QWidget()
        columna = QVBoxLayout(izquierda)
        columna.setContentsMargins(0, 0, 0, 0)
        columna.addWidget(self.arbol, 1)
        columna.addLayout(botones)

        self.pila = QStackedWidget()
        self.vacio = QLabel('Seleccione una evaluación en el árbol de la izquierda,\n'
                            'o cree un área para empezar.')
        self.vacio.setAlignment(Qt.AlignCenter)
        self.vacio.setStyleSheet('color:#666;')
        self.pila.addWidget(self.vacio)

        division = QSplitter(Qt.Horizontal)
        division.addWidget(izquierda)
        division.addWidget(self.pila)
        division.setStretchFactor(0, 1)
        division.setStretchFactor(1, 4)
        division.setSizes([300, 880])
        self.setCentralWidget(division)

        self._menus()
        self.recargar_arbol()

    def _menus(self):
        archivo = self.menuBar().addMenu('&Archivo')
        salir = QAction('Salir', self)
        salir.triggered.connect(self.close)
        archivo.addAction(salir)

        ayuda = self.menuBar().addMenu('A&yuda')
        acerca = QAction('Acerca de', self)
        acerca.triggered.connect(lambda: QMessageBox.information(
            self, 'BioRAM LESP',
            'Evaluación de riesgos de bioseguridad y bioprotección.\n\n'
            'Los cuestionarios y el cálculo son los de BioRAM (Sandia National '
            'Laboratories), traducidos al español y comprobados contra el '
            'programa original.'))
        ayuda.addAction(acerca)

    # ------------------------------------------------------------------ árbol
    def recargar_arbol(self, seleccionar=None):
        self.arbol.clear()
        for area in self.almacen.areas():
            nodo_area = QTreeWidgetItem(self.arbol, [area.nombre, ''])
            nodo_area.setData(0, CLASE, 'area')
            nodo_area.setData(0, ID, area.id)
            fuente = QFont(nodo_area.font(0)); fuente.setBold(True)
            nodo_area.setFont(0, fuente)

            for cepa in self.almacen.cepas(area.id):
                nodo_cepa = QTreeWidgetItem(nodo_area, [cepa.nombre, ''])
                nodo_cepa.setData(0, CLASE, 'cepa')
                nodo_cepa.setData(0, ID, cepa.id)

                for evaluacion in self.almacen.evaluaciones(cepa.id):
                    total = len(modelo.incluido(evaluacion.tipo).preguntas)
                    hechas = len(self.almacen.respuestas(evaluacion.id))
                    nodo = QTreeWidgetItem(nodo_cepa,
                                           [NOMBRE[evaluacion.tipo], f'{hechas}/{total}'])
                    nodo.setData(0, CLASE, 'evaluacion')
                    nodo.setData(0, ID, evaluacion.id)
                    if seleccionar == evaluacion.id:
                        self.arbol.setCurrentItem(nodo)
        self.arbol.expandAll()

    def _elemento(self, clases):
        actual = self.arbol.currentItem()
        while actual is not None:
            if actual.data(0, CLASE) in clases:
                return actual.data(0, CLASE), actual.data(0, ID)
            actual = actual.parent()
        return None, None

    def _seleccion(self, actual, _anterior):
        if actual is None or actual.data(0, CLASE) != 'evaluacion':
            self.pila.setCurrentWidget(self.vacio)
            return
        evaluacion_id = actual.data(0, ID)
        if evaluacion_id not in self.paneles:
            panel = PanelEvaluacion(self.almacen, evaluacion_id)
            self.paneles[evaluacion_id] = panel
            self.pila.addWidget(panel)
        self.pila.setCurrentWidget(self.paneles[evaluacion_id])

    # ------------------------------------------------------------------ altas
    def nueva_area(self):
        nombre, ok = QInputDialog.getText(self, 'Nueva área', 'Nombre del área:')
        if ok and nombre.strip():
            self.almacen.crear_area(nombre)
            self.recargar_arbol()

    def nueva_cepa(self):
        clase, area_id = self._elemento({'area'})
        if area_id is None:
            QMessageBox.information(self, 'Nueva cepa',
                                    'Seleccione primero el área a la que pertenece.')
            return
        nombre, ok = QInputDialog.getText(self, 'Nueva cepa', 'Nombre de la cepa o agente:')
        if ok and nombre.strip():
            self.almacen.crear_cepa(area_id, nombre)
            self.recargar_arbol()

    def nueva_evaluacion(self):
        clase, cepa_id = self._elemento({'cepa'})
        if cepa_id is None:
            QMessageBox.information(self, 'Nueva evaluación',
                                    'Seleccione primero la cepa que se va a evaluar.')
            return
        existentes = {e.tipo for e in self.almacen.evaluaciones(cepa_id)}
        faltantes = [t for t in modelo.TIPOS if t not in existentes]
        if not faltantes:
            QMessageBox.information(self, 'Nueva evaluación',
                                    'Esta cepa ya tiene sus dos evaluaciones.')
            return
        etiquetas = [NOMBRE[t] for t in faltantes]
        etiqueta, ok = QInputDialog.getItem(self, 'Nueva evaluación', 'Tipo de evaluación:',
                                            etiquetas, 0, False)
        if ok:
            tipo = faltantes[etiquetas.index(etiqueta)]
            nueva = self.almacen.crear_evaluacion(cepa_id, tipo)
            self.recargar_arbol(seleccionar=nueva)
