# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""La ventana de BioRAM LESP.

Dos pantallas, no más: la del laboratorio (áreas y cepas) y la de una
evaluación. Se va y se vuelve con un botón grande, como en un navegador.
"""
from __future__ import annotations

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QHBoxLayout, QMainWindow, QMessageBox, QStackedWidget,
                               QTabWidget, QVBoxLayout, QWidget)

from .. import modelo
from ..datos import Almacen
from .captura import PanelCaptura
from .estilo import (Ayuda, BotonGrande, COLOR_TIPO, INICIAL_TIPO, NOMBRE_TIPO,
                     Titulo, insignia)
from .ficha import PanelFicha
from .inicio import PantallaInicio
from .portada import PanelPortada
from .resultados import PanelResultados
from .salidas import guardar_reporte, imagenes_de


class PaginaEvaluacion(QWidget):
    """Una evaluación abierta: encabezado de color y sus pestañas."""

    def __init__(self, almacen: Almacen, evaluacion_id: int, volver, parent=None):
        super().__init__(parent)
        self.almacen = almacen
        self.evaluacion_id = evaluacion_id
        evaluacion = almacen.evaluacion(evaluacion_id)
        cepa = almacen.cepa(evaluacion.cepa_id)
        area = almacen.area(cepa.area_id)
        color = COLOR_TIPO[evaluacion.tipo]
        cuestionario = modelo.incluido(evaluacion.tipo)

        disposicion = QVBoxLayout(self)
        disposicion.setContentsMargins(18, 14, 18, 18)
        disposicion.setSpacing(12)

        encabezado = QHBoxLayout()
        encabezado.setSpacing(12)
        atras = BotonGrande(f'←  Volver a {area.nombre}')
        atras.clicked.connect(volver)
        encabezado.addWidget(atras)

        marca = QWidget()
        fila = QHBoxLayout(marca)
        fila.setContentsMargins(0, 0, 0, 0)
        fila.setSpacing(10)
        sello = QWidget()
        sello.setFixedSize(38, 38)
        sello.setStyleSheet(
            f'background-image: url();')
        from PySide6.QtWidgets import QLabel
        etiqueta_sello = QLabel()
        etiqueta_sello.setPixmap(insignia(INICIAL_TIPO[evaluacion.tipo], color, 38))
        fila.addWidget(etiqueta_sello)
        textos = QVBoxLayout()
        textos.setSpacing(0)
        textos.addWidget(Titulo(f'{NOMBRE_TIPO[evaluacion.tipo]} — {cepa.nombre}',
                                tamano=14, color=color))
        textos.addWidget(Ayuda(area.nombre))
        fila.addLayout(textos)
        encabezado.addWidget(marca, 1)
        reporte = BotonGrande('Guardar reporte…', color)
        reporte.setToolTip('Guardar esta evaluación como PDF, página web u hoja de cálculo')
        reporte.clicked.connect(self._guardar_reporte)
        encabezado.addWidget(reporte)
        disposicion.addLayout(encabezado)

        self.portada = PanelPortada(cuestionario)
        self.captura = PanelCaptura(cuestionario, color, evaluacion.tipo)
        self.resultados = PanelResultados(cuestionario, evaluacion.tipo)
        self.ficha = PanelFicha(almacen, evaluacion_id)
        self.captura.cambiada.connect(self._guardar)
        self.portada.cambiada.connect(self._guardar_cabecera)
        self.ficha.respuestas_cambiadas.connect(self._recargar_respuestas)

        self.pestanas = QTabWidget()
        self.pestanas.addTab(self.captura, '1 · Contestar')
        self.pestanas.addTab(self.resultados, '2 · Resultados')
        self.pestanas.addTab(self.portada, 'Portada')
        self.pestanas.addTab(self.ficha, 'Datos y respaldo')
        self.pestanas.currentChanged.connect(self._cambio_de_pestana)
        disposicion.addWidget(self.pestanas, 1)

        self.portada.mostrar(evaluacion.responsables, evaluacion.procedimiento)
        self.captura.mostrar(almacen.respuestas(evaluacion_id))
        self.resultados.mostrar(almacen.puntajes(evaluacion_id))

    def _guardar_reporte(self):
        # Las gráficas se dibujan con los resultados al día.
        self.resultados.mostrar(self.almacen.puntajes(self.evaluacion_id))
        guardar_reporte(self, self.almacen, self.evaluacion_id,
                        imagenes_de(self.resultados))

    def _guardar(self, pregunta, respuesta):
        """Guarda una respuesta, y si no se pudo guardar lo dice.

        Sin este aviso la pregunta se pintaba de contestada y la barra llegaba a
        «¡Cuestionario completo!» aunque no se hubiera guardado nada: el error
        salía por la consola, que en el ejecutable de Windows no existe. Pasaba
        con el archivo de datos abierto por otra copia del programa, en una
        carpeta de red, o sin permiso de escritura.
        """
        try:
            if respuesta is None:
                self.almacen.borrar_respuesta(self.evaluacion_id, pregunta)
            else:
                self.almacen.guardar_respuestas(self.evaluacion_id, {pregunta: respuesta})
        except (sqlite3.Error, ValueError) as e:
            QMessageBox.critical(
                self, 'No se pudo guardar la respuesta',
                'Esta respuesta NO quedó guardada:\n\n'
                f'{e}\n\n'
                'Puede ser que el programa esté abierto en otra ventana sobre el '
                'mismo archivo, que el archivo esté en una carpeta de red, o que '
                'no tenga permiso de escritura.\n\n'
                'Revise el archivo de datos antes de seguir contestando: '
                f'{self.almacen.ruta}')
            # Se vuelve a pintar desde la base, para que la pantalla muestre lo
            # que de verdad está guardado y no lo que se creyó guardar.
            self.captura.mostrar(self.almacen.respuestas(self.evaluacion_id))

    def _guardar_cabecera(self, responsables, procedimiento):
        try:
            self.almacen.actualizar_evaluacion(self.evaluacion_id,
                                               responsables=responsables,
                                               procedimiento=procedimiento)
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'No se pudo guardar',
                                 f'Los datos de la portada no quedaron guardados:\n\n{e}')

    def _recargar_respuestas(self):
        self.captura.mostrar(self.almacen.respuestas(self.evaluacion_id))
        self.resultados.mostrar(self.almacen.puntajes(self.evaluacion_id))

    def _cambio_de_pestana(self, indice):
        if self.pestanas.widget(indice) is self.resultados:
            self.resultados.mostrar(self.almacen.puntajes(self.evaluacion_id))
        elif self.pestanas.widget(indice) is self.ficha:
            self.ficha.recargar()


class Ventana(QMainWindow):
    def __init__(self, almacen: Almacen):
        super().__init__()
        self.almacen = almacen
        self.setWindowTitle('BioRAM LESP — evaluación de riesgos del laboratorio')
        self.resize(1240, 820)

        self.inicio = PantallaInicio(almacen)
        self.inicio.abrir_evaluacion.connect(self.abrir_evaluacion)

        self.pila = QStackedWidget()
        self.pila.addWidget(self.inicio)
        self.setCentralWidget(self.pila)
        self._menus()

    def _menus(self):
        archivo = self.menuBar().addMenu('&Archivo')
        donde = QAction('¿Dónde se guarda mi trabajo?', self)
        donde.triggered.connect(lambda: QMessageBox.information(
            self, 'Dónde se guarda',
            'Todo su trabajo está en este único archivo:\n\n'
            f'{self.almacen.ruta.resolve()}\n\n'
            'Para respaldarlo, cópielo a una memoria USB o a la nube. Para '
            'llevárselo a otra computadora, copie ese archivo y abra el '
            'programa junto a él.\n\n'
            'IMPORTANTE: cierre el programa antes de copiarlo. Mientras está '
            'abierto, los últimos cambios pueden estar todavía en dos archivos '
            'de apoyo que se llaman igual y terminan en «-wal» y «-shm».'))
        archivo.addAction(donde)
        archivo.addSeparator()
        salir = QAction('Salir', self)
        salir.triggered.connect(self.close)
        archivo.addAction(salir)

        ayuda = self.menuBar().addMenu('A&yuda')
        acerca = QAction('Acerca de BioRAM LESP', self)
        acerca.triggered.connect(lambda: QMessageBox.information(
            self, 'BioRAM LESP',
            'Evaluación de riesgos de bioseguridad y bioprotección.\n\n'
            'Los cuestionarios y el cálculo son los de BioRAM (Sandia National '
            'Laboratories), traducidos al español y comprobados contra el '
            'programa original: los resultados son los mismos.'))
        ayuda.addAction(acerca)

    def abrir_evaluacion(self, evaluacion_id: int):
        pagina = PaginaEvaluacion(self.almacen, evaluacion_id, self.volver_al_inicio)
        self.pila.addWidget(pagina)
        self.pila.setCurrentWidget(pagina)

    def volver_al_inicio(self):
        anterior = self.pila.currentWidget()
        self.pila.setCurrentWidget(self.inicio)
        if anterior is not self.inicio:
            self.pila.removeWidget(anterior)
            anterior.deleteLater()
        self.inicio.recargar_cepas()
