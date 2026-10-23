# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Los resultados: la tabla de perfiles y la gráfica de riesgo.

El dibujo de la gráfica y sus ajustes viven en grafica.py. Aquí se arma la
pantalla y se enlazan las dos cosas.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QHeaderView, QLabel,
                               QMessageBox, QScrollArea, QSplitter, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from .. import motor, secciones
from ..modelo import Cuestionario, Grafica
from .estilo import Ayuda, BotonGrande, TEXTO, TEXTO_SUAVE, color_de_avance
from .grafica import COLORES, CuadroPersonalizar, LienzoGrafica, Preferencias
from .salidas import nombre_de_archivo_seguro


class PanelResultados(QWidget):
    """Tabla de perfiles a la izquierda, gráficas a la derecha."""

    def __init__(self, cuestionario: Cuestionario, tipo: str | None = None,
                 almacen=None, parent=None):
        super().__init__(parent)
        self.cuestionario = cuestionario
        self.tipo = tipo
        self.preferencias = Preferencias(almacen)

        izquierda = QWidget()
        columna_izq = QVBoxLayout(izquierda)
        columna_izq.setContentsMargins(0, 0, 0, 0)
        columna_izq.setSpacing(8)

        self.avance = Ayuda('')
        columna_izq.addWidget(self.avance)

        self.tabla = QTableWidget(0, 3)
        self.tabla.setHorizontalHeaderLabels(['Resultado', 'Puntaje', 'De qué depende'])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        columna_izq.addWidget(self.tabla, 1)

        interior = QWidget()
        interior.setStyleSheet('background: transparent;')
        columna = QVBoxLayout(interior)
        columna.setSpacing(6)
        self.lienzos = []
        for grafica in cuestionario.graficas:
            titulo = QLabel(f'<b>{grafica.titulo}</b>')
            titulo.setWordWrap(True)
            titulo.setAlignment(Qt.AlignHCenter)
            columna.addWidget(titulo)

            nota = self._nota_de_ejes(grafica)
            if nota:
                etiqueta = Ayuda(nota)
                etiqueta.setAlignment(Qt.AlignHCenter)
                columna.addWidget(etiqueta)
            lienzo = LienzoGrafica(grafica, self.preferencias)
            self.lienzos.append(lienzo)
            columna.addWidget(lienzo, 1)
            leyenda = QLabel()
            leyenda.setWordWrap(True)
            leyenda.setTextFormat(Qt.RichText)
            leyenda.setStyleSheet('font-size: 10pt;')
            columna.addWidget(leyenda)
            columna.addSpacing(10)
            lienzo.leyenda = leyenda

        botones = QHBoxLayout()
        personalizar = BotonGrande('Personalizar la gráfica…')
        personalizar.setToolTip('Quitar resultados que su laboratorio no evalúa, '
                                'cambiarles el nombre o el tamaño de la letra')
        personalizar.clicked.connect(self.personalizar)
        botones.addWidget(personalizar)
        guardar = BotonGrande('Guardar la imagen…')
        guardar.setToolTip('Guardar la gráfica como JPEG o PNG para pegarla en un '
                           'informe o en una presentación')
        guardar.clicked.connect(self.guardar_imagen)
        botones.addWidget(guardar)
        botones.addStretch(1)

        # Con varias gráficas no caben de golpe: mejor desplazar que encimarlas.
        derecha = QScrollArea()
        derecha.setWidget(interior)
        derecha.setWidgetResizable(True)
        derecha.viewport().setStyleSheet('background: transparent;')

        panel_derecho = QWidget()
        columna_der = QVBoxLayout(panel_derecho)
        columna_der.setContentsMargins(0, 0, 0, 0)
        columna_der.setSpacing(8)
        columna_der.addLayout(botones)
        columna_der.addWidget(derecha, 1)

        division = QSplitter(Qt.Horizontal)
        division.addWidget(izquierda)
        division.addWidget(panel_derecho)
        division.setStretchFactor(0, 5)
        division.setStretchFactor(1, 5)
        division.setSizes([560, 500])

        disposicion = QHBoxLayout(self)
        disposicion.addWidget(division)

    def _nota_de_ejes(self, grafica: Grafica) -> str:
        """De qué sección depende cada eje. Sale del propio modelo."""
        if not self.tipo:
            return ''

        def seccion_de(uuids):
            usadas = set()
            for uuid in uuids:
                perfil = self.cuestionario.perfiles.get(uuid)
                if perfil is not None:
                    usadas |= secciones.de_que_depende(self.cuestionario, self.tipo, perfil)
            if usadas == {secciones.AGENTE}:
                return 'depende solo del agente'
            if usadas == {secciones.INSTALACION}:
                return 'depende solo de las instalaciones'
            return 'depende del agente y de las instalaciones'

        x = seccion_de({p.perfil_x for p in grafica.puntos})
        y = seccion_de({p.perfil_y for p in grafica.puntos})
        return f'{grafica.eje_x}: {x}  ·  {grafica.eje_y}: {y}'

    def mostrar(self, respuestas: dict[str, float]):
        puntajes = motor.resultados(self.cuestionario, respuestas)
        self.tabla.setRowCount(len(puntajes))
        for fila, (uuid, valor) in enumerate(puntajes.items()):
            perfil = self.cuestionario.perfiles[uuid]
            celda_titulo = QTableWidgetItem(perfil.titulo)
            celda_titulo.setToolTip(perfil.titulo)
            celda_titulo.setData(Qt.UserRole, uuid)
            self.tabla.setItem(fila, 0, celda_titulo)
            celda = QTableWidgetItem(f'{valor:.4f}')
            celda.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(fila, 1, celda)

            origen = ''
            if self.tipo:
                usadas = secciones.de_que_depende(self.cuestionario, self.tipo, perfil)
                if usadas == {secciones.AGENTE}:
                    origen = 'Agente'
                elif usadas == {secciones.INSTALACION}:
                    origen = 'Instalaciones'
                elif usadas:
                    origen = 'Agente + instalaciones'
            celda_origen = QTableWidgetItem(origen)
            celda_origen.setForeground(QColor(TEXTO_SUAVE))
            celda_origen.setToolTip(
                secciones.resumen_de_dependencia(usadas) if self.tipo else '')
            self.tabla.setItem(fila, 2, celda_origen)

        if self.tipo:
            avance = secciones.avance(self.cuestionario, self.tipo, respuestas)
            partes = []
            for seccion in secciones.ORDEN:
                hechas, total = avance[seccion]
                tono = color_de_avance(hechas, total)
                partes.append(f'<span style="color:{tono}">●</span> '
                              f'{secciones.NOMBRE[seccion]}: <b>{hechas}</b> de {total}')
            faltan = sum(t - h for h, t in avance.values())
            aviso = ('' if not faltan else
                     f'<br><span style="color:#b45309">Faltan {faltan} preguntas; '
                     'cuentan como 0 y los puntajes salen más bajos.</span>')
            self.avance.setText('&nbsp;&nbsp;&nbsp;'.join(partes) + aviso)

        self.ultimas_respuestas = respuestas
        for lienzo, puntos in zip(self.lienzos,
                                  motor.puntos_de_grafica(self.cuestionario, respuestas)):
            lienzo.mostrar(puntos)
        self._poner_leyendas()
        self._marcar_apagados()

    def _poner_leyendas(self):
        """La leyenda lista sólo lo que se dibuja, y con el nombre que se le puso."""
        for lienzo in self.lienzos:
            visibles = lienzo.visibles()
            if visibles:
                lienzo.leyenda.setText('<br>'.join(
                    f'<span style="color:{COLORES[i % len(COLORES)]}">●</span>&nbsp;'
                    f'{lienzo.nombre_de(i)}' for i in visibles))
            else:
                lienzo.leyenda.setText(
                    '<i>No se está dibujando ningún resultado en esta gráfica. '
                    'Use «Personalizar la gráfica…» para volver a mostrarlos.</i>')

    # ------------------------------------------------------------- personalizar
    def _apagados(self) -> set[str]:
        """Perfiles que el laboratorio quitó de todas las gráficas donde salían.

        Un perfil que no aparece en ninguna gráfica no cuenta: la mayoría no
        aparece, y marcarlos todos sería ruido. Sólo interesa el que sí se
        graficaba y se apagó a propósito.
        """
        sale, visible = set(), set()
        for grafica in self.cuestionario.graficas:
            for punto in grafica.puntos:
                sale.add(punto.perfil_x)
                sale.add(punto.perfil_y)
                if self.preferencias.visible(f'{punto.perfil_x}|{punto.perfil_y}'):
                    visible.add(punto.perfil_x)
                    visible.add(punto.perfil_y)
        return sale - visible

    def personalizar(self):
        CuadroPersonalizar(self.lienzos, self.preferencias,
                           self._redibujar, self).exec()

    def _redibujar(self):
        for lienzo in self.lienzos:
            lienzo.update()
        self._poner_leyendas()
        if getattr(self, 'ultimas_respuestas', None) is not None:
            self._marcar_apagados()

    def guardar_imagen(self):
        """La gráfica como archivo, para pegarla en un informe."""
        if not self.lienzos:
            return
        lienzo = self.lienzos[0]
        if len(self.lienzos) > 1:
            # Con varias, se guarda la que más arriba esté a la vista; no hay
            # forma de elegir sin complicar la pantalla, y la primera es la
            # principal en los dos cuestionarios.
            lienzo = self.lienzos[0]
        sugerido = nombre_de_archivo_seguro(lienzo.grafica.titulo) + '.jpg'
        ruta, _ = QFileDialog.getSaveFileName(
            self, 'Guardar la gráfica', sugerido,
            'Imagen JPEG (*.jpg *.jpeg);;Imagen PNG (*.png)')
        if not ruta:
            return
        imagen = lienzo.imagen(escala=3.0)
        formato = 'PNG' if ruta.lower().endswith('.png') else 'JPG'
        # 92: la gráfica tiene texto y bordes finos, y una calidad más baja los
        # ensucia con los artefactos cuadrados típicos del JPEG.
        if not imagen.save(ruta, formato, 92):
            QMessageBox.critical(
                self, 'No se pudo guardar',
                f'No se pudo escribir la imagen en:\n\n{ruta}\n\n'
                'Revise que la carpeta exista y que tenga permiso de escritura.')
            return
        QMessageBox.information(
            self, 'Imagen guardada',
            f'La gráfica quedó en:\n\n{ruta}\n\n'
            f'Mide {imagen.width()} × {imagen.height()} píxeles, suficiente para '
            'imprimirla o pegarla en un informe.')

    def _marcar_apagados(self):
        apagados = self._apagados()
        if not apagados:
            for fila in range(self.tabla.rowCount()):
                celda = self.tabla.item(fila, 0)
                if celda is not None:
                    celda.setForeground(QColor(TEXTO))
            return
        for fila in range(self.tabla.rowCount()):
            celda = self.tabla.item(fila, 0)
            if celda is None:
                continue
            uuid = celda.data(Qt.UserRole)
            if uuid in apagados:
                celda.setForeground(QColor(TEXTO_SUAVE))
                celda.setToolTip(f'{celda.text()}\n\n'
                                 'Su puntaje se calcula y se reporta, pero no se '
                                 'dibuja en la gráfica porque así se configuró.')
