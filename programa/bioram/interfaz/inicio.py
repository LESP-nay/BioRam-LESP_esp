"""La pantalla principal: las áreas del laboratorio y las cepas de cada una.

Cada cepa es una tarjeta con sus dos evaluaciones a la vista, con su avance.
Se entra a una evaluación haciendo clic en su botón: no hay que buscar nada en
menús.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QHBoxLayout, QInputDialog, QLabel, QListWidget,
                               QListWidgetItem, QMenu, QMessageBox, QProgressBar,
                               QScrollArea, QVBoxLayout, QWidget)

from .. import modelo
from ..datos import Almacen
from .estilo import (Ayuda, BotonGrande, COLOR_TIPO, INICIAL_TIPO, NOMBRE_TIPO,
                     PELIGRO, TEXTO_SUAVE, Tarjeta, Titulo, color_de_avance, icono,
                     insignia)
from .salidas import guardar_resumen_de_area

TOTAL_PREGUNTAS = 105


class BotonEvaluacion(BotonGrande):
    """El botón de una evaluación: color del tipo y barra de avance debajo."""

    def __init__(self, tipo: str, hechas: int, existe: bool, parent=None):
        color = COLOR_TIPO[tipo]
        if existe:
            super().__init__(NOMBRE_TIPO[tipo], color, parent)
        else:
            super().__init__(f'  Empezar {NOMBRE_TIPO[tipo].lower()}', None, parent)
            self.setStyleSheet(
                f'QPushButton {{ background: white; color: {color};'
                f' border: 2px dashed {color}; border-radius: 10px;'
                f' padding: 10px 18px; font-weight: 600; }}'
                f'QPushButton:hover {{ background: #f6f9ff; }}')
        from .. import secciones
        que_es = secciones.con_sinonimo(tipo)
        self.setToolTip(f'{que_es}: ' + ('abrir el cuestionario' if existe
                                         else 'crear esta evaluación'))


class TarjetaCepa(Tarjeta):
    abrir = Signal(int)                 # id de evaluación
    crear = Signal(int, str)            # id de cepa, tipo
    renombrar = Signal(int)
    eliminar = Signal(int)

    def __init__(self, almacen: Almacen, cepa, parent=None):
        super().__init__(parent)
        self.cepa = cepa
        disposicion = QVBoxLayout(self)
        disposicion.setContentsMargins(16, 14, 16, 16)
        disposicion.setSpacing(10)

        encabezado = QHBoxLayout()
        nombre = Titulo(cepa.nombre, tamano=13)
        encabezado.addWidget(nombre, 1)
        menu = BotonGrande('⋯')
        menu.setFixedWidth(46)
        menu.setToolTip('Cambiar el nombre o eliminar esta cepa')
        menu.clicked.connect(self._menu)
        encabezado.addWidget(menu)
        disposicion.addLayout(encabezado)

        if cepa.agente:
            disposicion.addWidget(Ayuda(cepa.agente))

        existentes = {e.tipo: e for e in almacen.evaluaciones(cepa.id)}
        fila = QHBoxLayout()
        fila.setSpacing(12)
        for tipo in modelo.TIPOS:
            evaluacion = existentes.get(tipo)
            columna = QVBoxLayout()
            columna.setSpacing(6)
            hechas = len(almacen.respuestas(evaluacion.id)) if evaluacion else 0
            boton = BotonEvaluacion(tipo, hechas, evaluacion is not None)
            if evaluacion is not None:
                boton.clicked.connect(lambda _=False, i=evaluacion.id: self.abrir.emit(i))
            else:
                boton.clicked.connect(lambda _=False, t=tipo: self.crear.emit(cepa.id, t))
            columna.addWidget(boton)

            if evaluacion is not None:
                color_avance = color_de_avance(hechas, TOTAL_PREGUNTAS)
                barra = QProgressBar()
                barra.setRange(0, TOTAL_PREGUNTAS)
                barra.setValue(hechas)
                barra.setTextVisible(False)
                barra.setFixedHeight(10)
                barra.setStyleSheet(
                    f'QProgressBar {{ background: #e7ecf3; border: none; border-radius: 5px; }}'
                    f'QProgressBar::chunk {{ background: {color_avance}; border-radius: 5px; }}')
                columna.addWidget(barra)
                texto = ('Completa ✓' if hechas >= TOTAL_PREGUNTAS
                         else f'{hechas} de {TOTAL_PREGUNTAS} contestadas')
                etiqueta = Ayuda(texto)
                etiqueta.setStyleSheet(f'color: {color_avance}; font-weight: 600;')
                columna.addWidget(etiqueta)
            else:
                columna.addWidget(Ayuda('Sin empezar'))
            fila.addLayout(columna, 1)
        disposicion.addLayout(fila)

    def _menu(self):
        menu = QMenu(self)
        menu.addAction('Cambiar el nombre…', lambda: self.renombrar.emit(self.cepa.id))
        menu.addSeparator()
        quitar = menu.addAction('Eliminar esta cepa…')
        quitar.triggered.connect(lambda: self.eliminar.emit(self.cepa.id))
        menu.exec(self.cursor().pos())


class PantallaInicio(QWidget):
    """Áreas a la izquierda, cepas del área seleccionada a la derecha."""

    abrir_evaluacion = Signal(int)

    def __init__(self, almacen: Almacen, parent=None):
        super().__init__(parent)
        self.almacen = almacen

        # ------------------------------------------------------------ áreas
        izquierda = QVBoxLayout()
        izquierda.setSpacing(10)
        izquierda.addWidget(Titulo('Áreas del laboratorio', tamano=13))
        self.lista = QListWidget()
        self.lista.setIconSize(insignia('', 'white', 30).size())
        self.lista.currentRowChanged.connect(lambda _: self.recargar_cepas())
        izquierda.addWidget(self.lista, 1)

        agregar_area = BotonGrande('＋  Nueva área')
        agregar_area.clicked.connect(self.nueva_area)
        izquierda.addWidget(agregar_area)
        self.renombrar_area = BotonGrande('Cambiar el nombre del área')
        self.renombrar_area.clicked.connect(self._renombrar_area)
        izquierda.addWidget(self.renombrar_area)
        self.eliminar_area = BotonGrande('Eliminar el área')
        self.eliminar_area.setStyleSheet(f'QPushButton {{ color: {PELIGRO}; }}')
        self.eliminar_area.clicked.connect(self._eliminar_area)
        izquierda.addWidget(self.eliminar_area)

        panel_izquierdo = QWidget()
        panel_izquierdo.setLayout(izquierda)
        panel_izquierdo.setFixedWidth(300)

        # ------------------------------------------------------------ cepas
        derecha = QVBoxLayout()
        derecha.setSpacing(12)
        cabecera = QHBoxLayout()
        self.titulo_area = Titulo('', tamano=16)
        cabecera.addWidget(self.titulo_area, 1)
        self.boton_resumen = BotonGrande('Resumen del área…')
        self.boton_resumen.setToolTip('Guardar un PDF con todas las cepas del área')
        self.boton_resumen.clicked.connect(self._resumen_de_area)
        cabecera.addWidget(self.boton_resumen)
        self.boton_cepa = BotonGrande('＋  Nueva cepa', COLOR_TIPO['bioproteccion'])
        self.boton_cepa.clicked.connect(self.nueva_cepa)
        cabecera.addWidget(self.boton_cepa)
        derecha.addLayout(cabecera)

        self.explicacion = Ayuda('')
        derecha.addWidget(self.explicacion)

        contenedor = QWidget()
        contenedor.setStyleSheet('background: transparent;')
        self.columna_cepas = QVBoxLayout(contenedor)
        self.columna_cepas.setSpacing(14)
        self.columna_cepas.addStretch(1)
        area = QScrollArea()
        area.setWidget(contenedor)
        area.setWidgetResizable(True)
        area.viewport().setStyleSheet('background: transparent;')
        derecha.addWidget(area, 1)

        disposicion = QHBoxLayout(self)
        disposicion.setContentsMargins(18, 18, 18, 18)
        disposicion.setSpacing(18)
        disposicion.addWidget(panel_izquierdo)
        disposicion.addLayout(derecha, 1)

        self.recargar()

    # ------------------------------------------------------------- recargar
    def recargar(self, seleccionar_area=None):
        actual = seleccionar_area or self.area_actual()
        self.lista.blockSignals(True)
        self.lista.clear()
        for area in self.almacen.areas():
            cepas = len(self.almacen.cepas(area.id))
            elemento = QListWidgetItem(f'{area.nombre}\n{cepas} cepa' + ('s' if cepas != 1 else ''))
            elemento.setData(Qt.UserRole, area.id)
            elemento.setIcon(icono(area.nombre[:1].upper(), COLOR_TIPO['bioseguridad'], 30))
            self.lista.addItem(elemento)
            if area.id == actual:
                self.lista.setCurrentItem(elemento)
        self.lista.blockSignals(False)
        if self.lista.currentRow() < 0 and self.lista.count():
            self.lista.setCurrentRow(0)
        self.recargar_cepas()

    def area_actual(self):
        elemento = self.lista.currentItem()
        return None if elemento is None else elemento.data(Qt.UserRole)

    def recargar_cepas(self):
        while self.columna_cepas.count() > 1:
            elemento = self.columna_cepas.takeAt(0)
            if elemento.widget():
                elemento.widget().deleteLater()

        area_id = self.area_actual()
        hay_area = area_id is not None
        self.boton_cepa.setEnabled(hay_area)
        self.boton_resumen.setEnabled(hay_area)
        self.renombrar_area.setEnabled(hay_area)
        self.eliminar_area.setEnabled(hay_area)

        if not hay_area:
            self.titulo_area.setText('Todavía no hay áreas')
            self.explicacion.setText(
                'Un área es cada zona del laboratorio: bacteriología, virología, '
                'parasitología…\n\nEmpiece con el botón «Nueva área» de la izquierda.')
            return

        area = self.almacen.area(area_id)
        self.titulo_area.setText(area.nombre)
        cepas = self.almacen.cepas(area_id)
        if cepas:
            self.explicacion.setText(
                'Cada cepa necesita sus dos evaluaciones. Haga clic en un botón de '
                'color para contestar su cuestionario.')
        else:
            self.explicacion.setText(
                f'El área «{area.nombre}» todavía no tiene cepas. '
                'Agregue la primera con el botón de arriba a la derecha.')

        for cepa in cepas:
            tarjeta = TarjetaCepa(self.almacen, cepa)
            tarjeta.abrir.connect(self.abrir_evaluacion)
            tarjeta.crear.connect(self._crear_evaluacion)
            tarjeta.renombrar.connect(self._renombrar_cepa)
            tarjeta.eliminar.connect(self._eliminar_cepa)
            self.columna_cepas.insertWidget(self.columna_cepas.count() - 1, tarjeta)

    # ---------------------------------------------------------------- altas
    def nueva_area(self):
        nombre, ok = QInputDialog.getText(self, 'Nueva área',
                                          'Nombre del área del laboratorio:')
        if ok and nombre.strip():
            self.recargar(seleccionar_area=self.almacen.crear_area(nombre))

    def nueva_cepa(self):
        area_id = self.area_actual()
        if area_id is None:
            return
        nombre, ok = QInputDialog.getText(
            self, 'Nueva cepa', 'Nombre de la cepa o del agente biológico:')
        if ok and nombre.strip():
            self.almacen.crear_cepa(area_id, nombre)
            self.recargar()

    def _resumen_de_area(self):
        area_id = self.area_actual()
        if area_id is not None:
            guardar_resumen_de_area(self, self.almacen, area_id)

    def _crear_evaluacion(self, cepa_id, tipo):
        nueva = self.almacen.crear_evaluacion(cepa_id, tipo)
        self.recargar()
        self.abrir_evaluacion.emit(nueva)

    # ------------------------------------------------------------- cambios
    def _renombrar_area(self):
        area_id = self.area_actual()
        if area_id is None:
            return
        area = self.almacen.area(area_id)
        nombre, ok = QInputDialog.getText(self, 'Cambiar el nombre',
                                          'Nuevo nombre del área:', text=area.nombre)
        if ok and nombre.strip():
            self.almacen.cx.execute('UPDATE area SET nombre = ? WHERE id = ?',
                                    (nombre.strip(), area_id))
            self.almacen.cx.commit()
            self.recargar(seleccionar_area=area_id)

    def _eliminar_area(self):
        area_id = self.area_actual()
        if area_id is None:
            return
        area = self.almacen.area(area_id)
        cepas = len(self.almacen.cepas(area_id))
        if QMessageBox.question(
                self, 'Eliminar el área',
                f'¿Eliminar «{area.nombre}»?\n\nSe borran también sus {cepas} cepa(s) '
                'y todas sus evaluaciones. Esto no se puede deshacer.',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.almacen.borrar_area(area_id)
            self.recargar()

    def _renombrar_cepa(self, cepa_id):
        cepa = self.almacen.cepa(cepa_id)
        nombre, ok = QInputDialog.getText(self, 'Cambiar el nombre',
                                          'Nuevo nombre de la cepa:', text=cepa.nombre)
        if ok and nombre.strip():
            self.almacen.cx.execute('UPDATE cepa SET nombre = ? WHERE id = ?',
                                    (nombre.strip(), cepa_id))
            self.almacen.cx.commit()
            self.recargar_cepas()

    def _eliminar_cepa(self, cepa_id):
        cepa = self.almacen.cepa(cepa_id)
        evaluaciones = len(self.almacen.evaluaciones(cepa_id))
        if QMessageBox.question(
                self, 'Eliminar la cepa',
                f'¿Eliminar «{cepa.nombre}»?\n\nSe borran sus {evaluaciones} '
                'evaluación(es) con todas sus respuestas. Esto no se puede deshacer.',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.almacen.borrar_cepa(cepa_id)
            self.recargar_cepas()
