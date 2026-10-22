# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Los resultados: la tabla de perfiles y la gráfica de riesgo.

La gráfica es la misma del programa original: los puntos se colocan sobre la
imagen de fondo del cuestionario, la de los arcos con "Muy bajo … Muy alto".
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QScrollArea,
                               QSizePolicy, QSplitter, QTableWidget, QTableWidgetItem,
                               QVBoxLayout, QWidget)

from .. import motor, secciones
from ..modelo import Cuestionario, Grafica
from .estilo import Ayuda, BIOPROTECCION, BIOSEGURIDAD, TEXTO_SUAVE, Titulo, color_de_avance

# Colores de los puntos, en el orden en que aparecen en la leyenda.
COLORES = ['#1f4e79', '#c00000', '#2e7d32', '#e07b00', '#6a1b9a',
           '#00838f', '#9e3d00', '#37474f', '#ad1457', '#4e6b1f',
           '#5d4037', '#0277bd']


class LienzoGrafica(QWidget):
    """Dibuja los puntos de una gráfica sobre su imagen de fondo."""

    MARGEN_IZQ, MARGEN_INF, MARGEN_SUP, MARGEN_DER = 56, 44, 16, 16

    def __init__(self, grafica: Grafica, parent=None):
        super().__init__(parent)
        self.grafica = grafica
        self.puntos: list[tuple[str, float, float]] = []
        self.fondo = QPixmap()
        if grafica.fondo:
            imagen = QImage()
            imagen.loadFromData(grafica.fondo)
            self.fondo = QPixmap.fromImage(imagen)
        self.setMinimumSize(320, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def mostrar(self, puntos):
        self.puntos = puntos
        self.update()

    def _area(self) -> QRectF:
        return QRectF(self.MARGEN_IZQ, self.MARGEN_SUP,
                      max(1, self.width() - self.MARGEN_IZQ - self.MARGEN_DER),
                      max(1, self.height() - self.MARGEN_SUP - self.MARGEN_INF))

    def _a_pixel(self, area: QRectF, x: float, y: float) -> QPointF:
        minimo, maximo = self.grafica.minimo, self.grafica.maximo
        rango = (maximo - minimo) or 1.0
        fx = min(max((x - minimo) / rango, 0.0), 1.0)
        fy = min(max((y - minimo) / rango, 0.0), 1.0)
        return QPointF(area.left() + fx * area.width(),
                       area.bottom() - fy * area.height())

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), Qt.white)
        area = self._area()

        if not self.fondo.isNull():
            pintor.drawPixmap(area.toRect(), self.fondo)
        pintor.setPen(QPen(QColor('#888')))
        pintor.drawRect(area)

        # Ejes: el nombre y las marcas de 0 a 4.
        fuente = QFont(self.font())
        fuente.setPointSizeF(max(7.0, fuente.pointSizeF() - 1))
        pintor.setFont(fuente)
        pasos = 4
        for i in range(pasos + 1):
            valor = self.grafica.minimo + (self.grafica.maximo - self.grafica.minimo) * i / pasos
            p = self._a_pixel(area, valor, self.grafica.minimo)
            pintor.drawLine(QPointF(p.x(), area.bottom()), QPointF(p.x(), area.bottom() + 4))
            pintor.drawText(QRectF(p.x() - 20, area.bottom() + 6, 40, 14),
                            Qt.AlignHCenter | Qt.AlignTop, f'{valor:g}')
            q = self._a_pixel(area, self.grafica.minimo, valor)
            pintor.drawLine(QPointF(area.left() - 4, q.y()), QPointF(area.left(), q.y()))
            pintor.drawText(QRectF(area.left() - 34, q.y() - 7, 28, 14),
                            Qt.AlignRight | Qt.AlignVCenter, f'{valor:g}')

        pintor.drawText(QRectF(area.left(), area.bottom() + 22, area.width(), 16),
                        Qt.AlignHCenter, self.grafica.eje_x)
        pintor.save()
        pintor.translate(14, area.center().y())
        pintor.rotate(-90)
        pintor.drawText(QRectF(-80, -8, 160, 16), Qt.AlignHCenter, self.grafica.eje_y)
        pintor.restore()

        for i, (_, x, y) in enumerate(self.puntos):
            if x != x or y != y:          # "no es un número"
                continue
            color = QColor(COLORES[i % len(COLORES)])
            relleno = QColor(color); relleno.setAlpha(190)
            pintor.setPen(QPen(QColor('white'), 1.5))
            pintor.setBrush(QBrush(relleno))
            pintor.drawEllipse(self._a_pixel(area, x, y), 7, 7)
            pintor.setPen(QPen(color.darker(140), 1.2))
            pintor.setBrush(Qt.NoBrush)
            pintor.drawEllipse(self._a_pixel(area, x, y), 7, 7)
        pintor.end()


class PanelResultados(QWidget):
    """Tabla de perfiles a la izquierda, gráficas a la derecha."""

    def __init__(self, cuestionario: Cuestionario, tipo: str | None = None, parent=None):
        super().__init__(parent)
        self.cuestionario = cuestionario
        self.tipo = tipo

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
            lienzo = LienzoGrafica(grafica)
            self.lienzos.append(lienzo)
            columna.addWidget(lienzo, 1)
            leyenda = QLabel()
            leyenda.setWordWrap(True)
            leyenda.setTextFormat(Qt.RichText)
            leyenda.setStyleSheet('font-size: 10pt;')
            columna.addWidget(leyenda)
            columna.addSpacing(10)
            lienzo.leyenda = leyenda

        # Con varias gráficas no caben de golpe: mejor desplazar que encimarlas.
        derecha = QScrollArea()
        derecha.setWidget(interior)
        derecha.setWidgetResizable(True)
        derecha.viewport().setStyleSheet('background: transparent;')

        division = QSplitter(Qt.Horizontal)
        division.addWidget(izquierda)
        division.addWidget(derecha)
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

        for lienzo, puntos in zip(self.lienzos,
                                  motor.puntos_de_grafica(self.cuestionario, respuestas)):
            lienzo.mostrar(puntos)
            lienzo.leyenda.setText('<br>'.join(
                f'<span style="color:{COLORES[i % len(COLORES)]}">●</span>&nbsp;{leyenda}'
                for i, (leyenda, _, _) in enumerate(puntos)))
