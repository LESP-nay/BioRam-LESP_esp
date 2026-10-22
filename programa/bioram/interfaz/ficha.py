# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Datos y respaldo de una evaluación: historial, copiar y exportar.

Guardar una versión es como sacarle una foto a la evaluación: queda con fecha y
nombre, y siempre se puede volver a ella.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QHeaderView, QInputDialog,
                               QMessageBox, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from .. import intercambio, modelo
from ..datos import Almacen
from .estilo import Ayuda, BotonGrande, COLOR_TIPO, PELIGRO, Titulo


class PanelFicha(QWidget):
    respuestas_cambiadas = Signal()

    def __init__(self, almacen: Almacen, evaluacion_id: int, parent=None):
        super().__init__(parent)
        self.almacen = almacen
        self.evaluacion_id = evaluacion_id
        evaluacion = almacen.evaluacion(evaluacion_id)
        self.tipo = evaluacion.tipo

        disposicion = QVBoxLayout(self)
        disposicion.setContentsMargins(18, 18, 18, 18)
        disposicion.setSpacing(14)

        # ------------------------------------------------------- historial
        disposicion.addWidget(Titulo('Historial de la evaluación', tamano=13))
        disposicion.addWidget(Ayuda(
            'Guarde una versión cuando termine una revisión. Queda registrada con '
            'la fecha y puede volver a ella cuando quiera.'))

        self.tabla = QTableWidget(0, 3)
        self.tabla.setHorizontalHeaderLabels(['Fecha', 'Quién', 'Nota'])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setMinimumHeight(170)
        disposicion.addWidget(self.tabla)

        fila = QHBoxLayout()
        guardar = BotonGrande('Guardar una versión', COLOR_TIPO[self.tipo])
        guardar.clicked.connect(self.guardar_version)
        fila.addWidget(guardar)
        self.boton_volver = BotonGrande('Volver a la versión seleccionada')
        self.boton_volver.clicked.connect(self.restaurar)
        fila.addWidget(self.boton_volver)
        fila.addStretch(1)
        disposicion.addLayout(fila)

        # ------------------------------------------------- copiar y exportar
        disposicion.addSpacing(8)
        disposicion.addWidget(Titulo('Copiar y exportar', tamano=13))
        disposicion.addWidget(Ayuda(
            'Copiar respuestas sirve cuando otra cepa del laboratorio se evalúa casi '
            'igual: se traen sus respuestas y solo se ajusta lo que cambia.'))

        acciones = QHBoxLayout()
        copiar = BotonGrande('Copiar respuestas de otra cepa…')
        copiar.clicked.connect(self.copiar_de_otra)
        acciones.addWidget(copiar)

        if modelo.incluido(self.tipo).plantillas:
            plantilla = BotonGrande('Usar un agente conocido…')
            plantilla.setToolTip('Precarga las respuestas del agente según el '
                                 'cuestionario oficial')
            plantilla.clicked.connect(self.usar_plantilla)
            acciones.addWidget(plantilla)

        exportar = BotonGrande('Exportar a un archivo…')
        exportar.setToolTip('Genera un .raml que abre el BioRAM original')
        exportar.clicked.connect(self.exportar)
        acciones.addWidget(exportar)

        importar = BotonGrande('Importar de un archivo…')
        importar.clicked.connect(self.importar)
        acciones.addWidget(importar)
        acciones.addStretch(1)
        disposicion.addLayout(acciones)

        borrar = BotonGrande('Borrar todas las respuestas')
        borrar.setStyleSheet(f'QPushButton {{ color: {PELIGRO}; }}')
        borrar.clicked.connect(self.borrar_todo)
        disposicion.addWidget(borrar, 0, Qt.AlignLeft)

        disposicion.addStretch(1)
        self.recargar()

    # ------------------------------------------------------------ historial
    def recargar(self):
        versiones = self.almacen.versiones(self.evaluacion_id)
        self.tabla.setRowCount(len(versiones))
        for fila, version in enumerate(versiones):
            momento = version.momento.replace('T', '  ')
            for columna, texto in enumerate((momento, version.autor, version.nota)):
                celda = QTableWidgetItem(texto)
                celda.setData(Qt.UserRole, version.id)
                self.tabla.setItem(fila, columna, celda)
        self.tabla.resizeColumnsToContents()
        self.boton_volver.setEnabled(bool(versiones))

    def guardar_version(self):
        autor, ok = QInputDialog.getText(self, 'Guardar una versión',
                                         '¿Quién hizo esta revisión?')
        if not ok:
            return
        nota, ok = QInputDialog.getText(self, 'Guardar una versión',
                                        'Nota (opcional): qué se revisó')
        if not ok:
            return
        self.almacen.guardar_version(self.evaluacion_id, autor=autor, nota=nota)
        self.recargar()

    def _version_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.information(self, 'Historial',
                                    'Seleccione primero una versión de la lista.')
            return None
        return self.tabla.item(fila, 0).data(Qt.UserRole)

    def restaurar(self):
        version_id = self._version_seleccionada()
        if version_id is None:
            return
        if QMessageBox.question(
                self, 'Volver a esta versión',
                'Las respuestas actuales se reemplazan por las de esa versión.\n\n'
                '¿Continuar?', QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No) == QMessageBox.Yes:
            self.almacen.restaurar_version(version_id)
            self.respuestas_cambiadas.emit()

    # ------------------------------------------------------ copiar/exportar
    def copiar_de_otra(self):
        propia = self.almacen.evaluacion(self.evaluacion_id)
        candidatas = []
        for evaluacion in self.almacen.evaluaciones(tipo=self.tipo):
            if evaluacion.id == self.evaluacion_id:
                continue
            cepa = self.almacen.cepa(evaluacion.cepa_id)
            area = self.almacen.area(cepa.area_id)
            candidatas.append((f'{area.nombre} — {cepa.nombre}', evaluacion.id))
        if not candidatas:
            QMessageBox.information(
                self, 'Copiar respuestas',
                'Todavía no hay otra evaluación del mismo tipo de la cual copiar.')
            return

        etiquetas = [e for e, _ in candidatas]
        etiqueta, ok = QInputDialog.getItem(self, 'Copiar respuestas',
                                            'Traer las respuestas de:', etiquetas, 0, False)
        if not ok:
            return
        origen = candidatas[etiquetas.index(etiqueta)][1]
        respuestas = self.almacen.respuestas(origen)
        if QMessageBox.question(
                self, 'Copiar respuestas',
                f'Se van a traer {len(respuestas)} respuestas de «{etiqueta}» y '
                'reemplazarán lo que tenga contestado.\n\n¿Continuar?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        self.almacen.guardar_respuestas(self.evaluacion_id, respuestas)
        self.respuestas_cambiadas.emit()

    def usar_plantilla(self):
        plantillas = modelo.incluido(self.tipo).plantillas
        nombres = sorted(plantillas)
        nombre, ok = QInputDialog.getItem(self, 'Agente conocido',
                                          'Precargar las respuestas de:', nombres, 0, True)
        if not ok or nombre not in plantillas:
            return
        self.almacen.guardar_respuestas(self.evaluacion_id, plantillas[nombre])
        self.respuestas_cambiadas.emit()
        QMessageBox.information(
            self, 'Agente conocido',
            f'Se precargaron {len(plantillas[nombre])} respuestas de «{nombre}».\n\n'
            'Revise cada una: son los valores del cuestionario oficial y pueden no '
            'coincidir con su laboratorio.')

    def exportar(self):
        evaluacion = self.almacen.evaluacion(self.evaluacion_id)
        cepa = self.almacen.cepa(evaluacion.cepa_id)
        ruta, _ = QFileDialog.getSaveFileName(
            self, 'Exportar las respuestas', f'{cepa.nombre} - {self.tipo}.raml',
            'Archivos de BioRAM (*.raml)')
        if not ruta:
            return
        intercambio.escribir_respuestas(
            ruta, modelo.ruta_incluido(self.tipo),
            {cepa.nombre: self.almacen.respuestas(self.evaluacion_id)},
            responsables=evaluacion.responsables, procedimiento=evaluacion.procedimiento)
        QMessageBox.information(self, 'Exportar', f'Guardado en:\n{ruta}')

    def importar(self):
        ruta, _ = QFileDialog.getOpenFileName(self, 'Importar respuestas', '',
                                              'Archivos de BioRAM (*.raml)')
        if not ruta:
            return
        cuestionario = modelo.incluido(self.tipo)
        leido = intercambio.leer_respuestas(ruta, cuestionario)
        if not leido.conjuntos:
            QMessageBox.warning(self, 'Importar',
                                'Ese archivo no trae respuestas.')
            return
        nombres = sorted(leido.conjuntos)
        nombre = nombres[0]
        if len(nombres) > 1:
            nombre, ok = QInputDialog.getItem(self, 'Importar',
                                              'El archivo trae varios conjuntos:',
                                              nombres, 0, False)
            if not ok:
                return
        respuestas = leido.conjuntos[nombre]
        aviso = ''
        if leido.desconocidas.get(nombre):
            aviso = (f'\n\nAtención: {leido.desconocidas[nombre]} respuestas del '
                     'archivo no corresponden a ninguna pregunta de este '
                     'cuestionario y no se importaron.')
        self.almacen.guardar_respuestas(self.evaluacion_id, respuestas)
        self.respuestas_cambiadas.emit()
        QMessageBox.information(self, 'Importar',
                                f'Se importaron {len(respuestas)} respuestas.{aviso}')

    def borrar_todo(self):
        cuantas = len(self.almacen.respuestas(self.evaluacion_id))
        if not cuantas:
            return
        if QMessageBox.question(
                self, 'Borrar las respuestas',
                f'¿Borrar las {cuantas} respuestas de esta evaluación?\n\n'
                'Si guardó una versión antes, puede volver a ella.',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            for pregunta in list(self.almacen.respuestas(self.evaluacion_id)):
                self.almacen.borrar_respuesta(self.evaluacion_id, pregunta)
            self.respuestas_cambiadas.emit()
