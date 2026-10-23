# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""La gráfica de riesgo: cómo se dibuja y cómo la ajusta el laboratorio.

Nada de lo que hay aquí toca el cálculo. Los puntajes se calculan, se guardan y
se reportan todos; esto decide únicamente qué se dibuja y cómo se ve. Un
resultado que el laboratorio quita de la gráfica sigue en la tabla y en el
reporte, con su puntaje, señalado como no graficado: una evaluación no puede
perder un número porque alguien prefiera una imagen más limpia.

LAS ZONAS DE RIESGO

El fondo original de Sandia es una imagen de 485x485 con cuatro arcos grises y
los nombres de las cinco zonas en letra muy pequeña. Para poder rellenarlas de
color y escribir sus nombres de forma legible hacía falta saber dónde están, y
eso se midió sobre la propia imagen en vez de suponerlo: se tomaron los 2 737
píxeles de los arcos y se ajustó el centro.

    centro      la esquina de riesgo máximo, (4,4)
    radios      1, 2, 3 y 4 unidades de la gráfica
    error       0.05 unidades sobre 2 737 píxeles

Es decir: la zona de un punto depende de su distancia a la esquina donde la
consecuencia y la probabilidad son máximas. Cuanto más cerca, peor. Dibujadas
así, las zonas caen exactamente encima de los arcos del original, y quien
prefiera el fondo de Sandia tal cual puede desactivarlas.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QFontMetricsF, QImage, QPainter,
                           QPen, QPixmap)
from PySide6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QMessageBox,
                               QSizePolicy, QSpinBox, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from ..modelo import Grafica
from .estilo import Ayuda, BotonGrande, MARINO, TEXTO, TEXTO_SUAVE, Titulo

# Colores de los puntos, en el orden en que aparecen en la leyenda.
COLORES = ['#1f4e79', '#c00000', '#2e7d32', '#e07b00', '#6a1b9a',
           '#00838f', '#9e3d00', '#37474f', '#ad1457', '#4e6b1f',
           '#5d4037', '#0277bd']


@dataclass(frozen=True)
class Zona:
    """Una banda de riesgo: hasta qué distancia llega, cómo se llama y se ve."""
    hasta: float            # radio exterior, en unidades de la gráfica
    nombre: str
    relleno: str
    letra: str


# De dentro hacia fuera. El radio exterior de la última es la diagonal entera.
ZONAS = (
    Zona(1.0, 'Muy alto', '#f8d0cf', '#a51919'),
    Zona(2.0, 'Alto', '#fbdcc1', '#9c4708'),
    Zona(3.0, 'Moderado', '#fdf1c6', '#7a5500'),
    Zona(4.0, 'Bajo', '#d8ecc3', '#44700d'),
    Zona(math.sqrt(32), 'Muy bajo', '#e9f2e4', '#38601f'),
)

CLAVE = 'grafica'
POR_OMISION = {
    'zonas': True,              # rellenar las bandas de color
    'tamano': 10,               # tamaño de las letras de la gráfica, en puntos
    'nombres': False,           # escribir el nombre junto a cada punto
    'series': {},               # {clave: {'nombre': str, 'visible': bool}}
}


def clave_de(punto) -> str:
    """Identidad estable de una serie, que no cambia si se renombra."""
    return f'{punto.perfil_x}|{punto.perfil_y}'


class Preferencias:
    """Cómo quiere este laboratorio ver sus gráficas.

    Viven en el archivo de datos, no en cada evaluación: es una decisión del
    laboratorio. Si el archivo se tocó a mano y trae algo que no se entiende, se
    vuelve a lo de siempre en lugar de fallar; esto es sólo el aspecto.
    """

    def __init__(self, almacen=None):
        self.almacen = almacen
        guardado = almacen.preferencia(CLAVE) if almacen is not None else None
        self.datos = dict(POR_OMISION)
        if isinstance(guardado, dict):
            for llave, valor in guardado.items():
                if llave in POR_OMISION and isinstance(valor, type(POR_OMISION[llave])):
                    self.datos[llave] = valor
        self.datos['series'] = dict(self.datos['series'])

    # ------------------------------------------------------------- consultar
    @property
    def zonas(self) -> bool:
        return bool(self.datos['zonas'])

    @property
    def tamano(self) -> int:
        return max(6, min(28, int(self.datos['tamano'])))

    @property
    def nombres(self) -> bool:
        return bool(self.datos['nombres'])

    def _serie(self, clave: str) -> dict:
        valor = self.datos['series'].get(clave)
        return valor if isinstance(valor, dict) else {}

    def nombre(self, clave: str, original: str) -> str:
        puesto = self._serie(clave).get('nombre')
        return puesto if isinstance(puesto, str) and puesto.strip() else original

    def visible(self, clave: str) -> bool:
        return self._serie(clave).get('visible', True) is not False

    # -------------------------------------------------------------- cambiar
    def poner(self, llave: str, valor):
        self.datos[llave] = valor

    def poner_serie(self, clave: str, **campos):
        serie = dict(self._serie(clave))
        serie.update(campos)
        if serie.get('nombre', '') == '':
            serie.pop('nombre', None)
        if serie.get('visible') is True:
            serie.pop('visible', None)
        if serie:
            self.datos['series'][clave] = serie
        else:
            self.datos['series'].pop(clave, None)

    def restablecer(self):
        self.datos = dict(POR_OMISION)
        self.datos['series'] = {}

    def guardar(self):
        if self.almacen is not None:
            self.almacen.guardar_preferencia(CLAVE, self.datos)


class LienzoGrafica(QWidget):
    """Dibuja los puntos de una gráfica sobre sus zonas de riesgo."""

    MARGEN_IZQ, MARGEN_INF, MARGEN_SUP, MARGEN_DER = 56, 44, 16, 16

    def __init__(self, grafica: Grafica, preferencias: Preferencias, parent=None):
        super().__init__(parent)
        self.grafica = grafica
        self.preferencias = preferencias
        self.claves = [clave_de(p) for p in grafica.puntos]
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

    def nombre_de(self, i: int) -> str:
        original = self.puntos[i][0] if i < len(self.puntos) else ''
        return self.preferencias.nombre(self.claves[i], original)

    def visibles(self) -> list[int]:
        """Índices de las series que se dibujan, en su orden original."""
        return [i for i in range(len(self.puntos))
                if i < len(self.claves) and self.preferencias.visible(self.claves[i])]

    # ------------------------------------------------------------- geometría
    def _area(self, ancho: float, alto: float) -> QRectF:
        return QRectF(self.MARGEN_IZQ, self.MARGEN_SUP,
                      max(1.0, ancho - self.MARGEN_IZQ - self.MARGEN_DER),
                      max(1.0, alto - self.MARGEN_SUP - self.MARGEN_INF))

    def _a_pixel(self, area: QRectF, x: float, y: float) -> QPointF:
        minimo, maximo = self.grafica.minimo, self.grafica.maximo
        rango = (maximo - minimo) or 1.0
        fx = min(max((x - minimo) / rango, 0.0), 1.0)
        fy = min(max((y - minimo) / rango, 0.0), 1.0)
        return QPointF(area.left() + fx * area.width(),
                       area.bottom() - fy * area.height())

    # --------------------------------------------------------------- dibujo
    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        self._dibujar(pintor, self.width(), self.height())
        pintor.end()

    def imagen(self, escala: float = 2.0) -> QImage:
        """La gráfica como imagen, más grande que en pantalla para que imprima bien."""
        escala = max(1.0, min(4.0, escala))
        lienzo = QImage(int(self.width() * escala), int(self.height() * escala),
                        QImage.Format_RGB32)
        lienzo.fill(Qt.white)
        pintor = QPainter(lienzo)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.setRenderHint(QPainter.TextAntialiasing)
        pintor.scale(escala, escala)
        self._dibujar(pintor, self.width(), self.height())
        pintor.end()
        return lienzo

    def _dibujar(self, pintor: QPainter, ancho: float, alto: float):
        pintor.fillRect(QRectF(0, 0, ancho, alto), Qt.white)
        area = self._area(ancho, alto)
        base = self.preferencias.tamano

        if self.preferencias.zonas:
            self._dibujar_zonas(pintor, area, base)
        elif not self.fondo.isNull():
            pintor.drawPixmap(area.toRect(), self.fondo)

        pintor.setPen(QPen(QColor('#8d9ab3')))
        pintor.setBrush(Qt.NoBrush)
        pintor.drawRect(area)
        self._dibujar_ejes(pintor, area, base)
        self._dibujar_puntos(pintor, area, base)

    def _dibujar_zonas(self, pintor: QPainter, area: QRectF, base: float):
        """Las bandas de riesgo, como círculos desde la esquina de riesgo máximo."""
        rango = (self.grafica.maximo - self.grafica.minimo) or 1.0
        centro = self._a_pixel(area, self.grafica.maximo, self.grafica.maximo)
        por_unidad_x = area.width() / rango
        por_unidad_y = area.height() / rango

        pintor.save()
        pintor.setClipRect(area)
        pintor.setPen(Qt.NoPen)
        # De la más grande a la más chica: cada una tapa el centro de la anterior.
        for zona in reversed(ZONAS):
            pintor.setBrush(QBrush(QColor(zona.relleno)))
            pintor.drawEllipse(centro, zona.hasta * por_unidad_x,
                               zona.hasta * por_unidad_y)
        # Los bordes, encima, para que se vea dónde empieza cada una.
        pintor.setBrush(Qt.NoBrush)
        for zona in ZONAS:
            pintor.setPen(QPen(QColor(zona.letra).lighter(160), 1.0))
            pintor.drawEllipse(centro, zona.hasta * por_unidad_x,
                               zona.hasta * por_unidad_y)
        pintor.restore()

        # El nombre de cada zona, en la diagonal, que es donde la banda es ancha.
        fuente = QFont(self.font())
        fuente.setPointSizeF(base + 1)
        fuente.setBold(True)
        pintor.setFont(fuente)
        medidas = QFontMetricsF(fuente)
        dentro = 0.0
        for zona in ZONAS:
            medio = (dentro + zona.hasta) / 2
            dentro = zona.hasta
            # Hacia la esquina de riesgo mínimo, a 45 grados.
            dx = medio / math.sqrt(2) * por_unidad_x
            dy = medio / math.sqrt(2) * por_unidad_y
            centro_texto = QPointF(centro.x() - dx, centro.y() + dy)
            ancho_texto = medidas.horizontalAdvance(zona.nombre) + 10
            caja = QRectF(centro_texto.x() - ancho_texto / 2,
                          centro_texto.y() - medidas.height() / 2,
                          ancho_texto, medidas.height())
            if not area.contains(caja.center()):
                continue
            pintor.setPen(Qt.NoPen)
            pintor.setBrush(QBrush(QColor(255, 255, 255, 190)))
            pintor.drawRoundedRect(caja, 5, 5)
            pintor.setPen(QPen(QColor(zona.letra)))
            pintor.drawText(caja, Qt.AlignCenter, zona.nombre)

    def _dibujar_ejes(self, pintor: QPainter, area: QRectF, base: float):
        fuente = QFont(self.font())
        fuente.setPointSizeF(max(7.0, base - 1))
        pintor.setFont(fuente)
        pintor.setPen(QPen(QColor(TEXTO)))
        pasos = 4
        for i in range(pasos + 1):
            valor = (self.grafica.minimo
                     + (self.grafica.maximo - self.grafica.minimo) * i / pasos)
            p = self._a_pixel(area, valor, self.grafica.minimo)
            pintor.drawLine(QPointF(p.x(), area.bottom()), QPointF(p.x(), area.bottom() + 4))
            pintor.drawText(QRectF(p.x() - 20, area.bottom() + 6, 40, 16),
                            Qt.AlignHCenter | Qt.AlignTop, f'{valor:g}')
            q = self._a_pixel(area, self.grafica.minimo, valor)
            pintor.drawLine(QPointF(area.left() - 4, q.y()), QPointF(area.left(), q.y()))
            pintor.drawText(QRectF(area.left() - 34, q.y() - 8, 28, 16),
                            Qt.AlignRight | Qt.AlignVCenter, f'{valor:g}')

        fuente.setPointSizeF(base)
        fuente.setBold(True)
        pintor.setFont(fuente)
        pintor.drawText(QRectF(area.left(), area.bottom() + 24, area.width(), 18),
                        Qt.AlignHCenter, self.grafica.eje_x)
        pintor.save()
        pintor.translate(14, area.center().y())
        pintor.rotate(-90)
        pintor.drawText(QRectF(-90, -9, 180, 18), Qt.AlignHCenter, self.grafica.eje_y)
        pintor.restore()

    def _dibujar_puntos(self, pintor: QPainter, area: QRectF, base: float):
        radio = max(5.0, base * 0.7)
        fuente = QFont(self.font())
        fuente.setPointSizeF(base)
        medidas = QFontMetricsF(fuente)
        ocupado: list[QRectF] = []

        for i in self.visibles():
            _, x, y = self.puntos[i]
            if x != x or y != y:          # "no es un número"
                continue
            color = QColor(COLORES[i % len(COLORES)])
            centro = self._a_pixel(area, x, y)
            relleno = QColor(color); relleno.setAlpha(205)
            pintor.setPen(QPen(QColor('white'), 1.5))
            pintor.setBrush(QBrush(relleno))
            pintor.drawEllipse(centro, radio, radio)
            pintor.setPen(QPen(color.darker(140), 1.2))
            pintor.setBrush(Qt.NoBrush)
            pintor.drawEllipse(centro, radio, radio)

            if self.preferencias.nombres:
                self._escribir_nombre(pintor, area, centro, radio, color,
                                      self.nombre_de(i), fuente, medidas, ocupado)

    def _escribir_nombre(self, pintor, area, centro, radio, color, texto,
                         fuente, medidas, ocupado):
        """El nombre junto a su punto, apartándose de los que ya están puestos.

        Cuando varios resultados caen en el mismo sitio —y caen, porque muchos
        valen 0 mientras el cuestionario está a medias— los nombres se encimarían
        hasta ser ilegibles. Se prueban cuatro posiciones, se va bajando si
        ninguna sirve, y en todo caso el nombre se queda dentro del marco: antes
        se salía por los lados y la ventana lo cortaba a media palabra.
        """
        ancho = min(medidas.horizontalAdvance(texto) + 8, area.width() - 8)
        alto = medidas.height() + 2

        def dentro(caja: QRectF) -> QRectF:
            x = min(max(caja.x(), area.left() + 2), area.right() - ancho - 2)
            y = min(max(caja.y(), area.top() + 2), area.bottom() - alto - 2)
            return QRectF(x, y, ancho, alto)

        intentos = [(radio + 6, -alto / 2), (-radio - 6 - ancho, -alto / 2),
                    (-ancho / 2, -radio - 4 - alto), (-ancho / 2, radio + 4)]
        caja = None
        for dx, dy in intentos:
            posible = QRectF(centro.x() + dx, centro.y() + dy, ancho, alto)
            if posible != dentro(posible):
                continue                      # se saldría del marco
            if not any(posible.intersects(otra) for otra in ocupado):
                caja = posible
                break
        if caja is None:
            caja = dentro(QRectF(centro.x() + radio + 6, centro.y() - alto / 2,
                                 ancho, alto))
            while (any(caja.intersects(otra) for otra in ocupado)
                   and caja.bottom() + alto + 2 < area.bottom()):
                caja.translate(0, alto + 2)
        ocupado.append(caja)
        texto = medidas.elidedText(texto, Qt.ElideRight, ancho - 8)

        pintor.setFont(fuente)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QBrush(QColor(255, 255, 255, 215)))
        pintor.drawRoundedRect(caja, 4, 4)
        pintor.setPen(QPen(color.darker(130)))
        pintor.drawText(caja, Qt.AlignCenter, texto)


class CuadroPersonalizar(QDialog):
    """Qué resultados se grafican, cómo se llaman y de qué tamaño se ven.

    Los cambios se ven en el acto en la gráfica de atrás: no hay que aceptar
    nada para saber si quedó bien. Se guardan al cerrar.
    """

    def __init__(self, lienzos, preferencias: Preferencias, al_cambiar, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Personalizar la gráfica')
        self.resize(760, 620)
        self.lienzos = lienzos
        self.preferencias = preferencias
        self.al_cambiar = al_cambiar
        self._cargando = True

        disposicion = QVBoxLayout(self)
        disposicion.setContentsMargins(18, 16, 18, 16)
        disposicion.setSpacing(10)

        disposicion.addWidget(Titulo('Qué se dibuja', tamano=13))
        disposicion.addWidget(Ayuda(
            'Quite la palomita a lo que su laboratorio no evalúa y no se dibujará. '
            'El puntaje se sigue calculando y sigue saliendo en la tabla y en el '
            'reporte: aquí sólo decide qué entra en la imagen.'))

        self.tabla = QTableWidget(0, 3)
        self.tabla.setHorizontalHeaderLabels(
            ['Se dibuja', 'Nombre que aparece', 'Nombre original'])
        self.tabla.verticalHeader().setVisible(False)
        # Renglones holgados: con la altura de siempre, las letras con cola —la
        # «g» de «Riesgo»— salían cortadas por abajo.
        self.tabla.verticalHeader().setDefaultSectionSize(38)
        self.tabla.itemChanged.connect(self._cambio_de_palomita)
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        disposicion.addWidget(self.tabla, 1)

        disposicion.addWidget(Titulo('Cómo se ve', tamano=13))

        fila_tamano = QHBoxLayout()
        fila_tamano.addWidget(QLabel('Tamaño de la letra:'))
        self.tamano = QSpinBox()
        self.tamano.setRange(6, 28)
        self.tamano.setSuffix(' pt')
        self.tamano.setToolTip('Si los nombres se enciman, baje el tamaño o apague '
                               'los que no necesite')
        self.tamano.valueChanged.connect(self._cambio)
        fila_tamano.addWidget(self.tamano)
        fila_tamano.addStretch(1)
        disposicion.addLayout(fila_tamano)

        self.nombres = QCheckBox('Escribir el nombre junto a cada punto de la gráfica')
        self.nombres.setToolTip('Útil para imprimir: el nombre va en la imagen y no '
                                'hay que buscarlo en la lista de abajo')
        self.nombres.stateChanged.connect(self._cambio)
        disposicion.addWidget(self.nombres)

        self.zonas = QCheckBox('Rellenar de color las zonas de riesgo')
        self.zonas.setToolTip('Las zonas quedan donde los arcos del original: se '
                              'midieron sobre su imagen. Apáguelo para ver el fondo '
                              'original de Sandia tal cual')
        self.zonas.stateChanged.connect(self._cambio)
        disposicion.addWidget(self.zonas)

        acciones = QHBoxLayout()
        volver = BotonGrande('Volver a como estaba')
        volver.setToolTip('Deshace todos estos ajustes y deja la gráfica original')
        volver.clicked.connect(self._restablecer)
        acciones.addWidget(volver)
        acciones.addStretch(1)
        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.accept)
        acciones.addWidget(botones)
        disposicion.addLayout(acciones)

        self._llenar()
        self._cargando = False

    # ------------------------------------------------------------------ datos
    def _series(self):
        """Las series de todas las gráficas, sin repetir, en su orden."""
        vistas, salida = set(), []
        for lienzo in self.lienzos:
            for i, clave in enumerate(lienzo.claves):
                if clave in vistas:
                    continue
                vistas.add(clave)
                original = (lienzo.puntos[i][0] if i < len(lienzo.puntos)
                            else lienzo.grafica.puntos[i].leyenda)
                salida.append((clave, original, COLORES[i % len(COLORES)]))
        return salida

    def _llenar(self):
        self.tamano.setValue(self.preferencias.tamano)
        self.nombres.setChecked(self.preferencias.nombres)
        self.zonas.setChecked(self.preferencias.zonas)

        series = self._series()
        self.tabla.setRowCount(len(series))
        self.campos = {}
        for fila, (clave, original, color) in enumerate(series):
            # La palomita es un elemento de la tabla y no un QCheckBox suelto a
            # propósito: la hoja de estilo del programa le quita el dibujo de la
            # palomita a los QCheckBox y deja sólo un cuadro de color, que aquí
            # no basta. El que dibuja la tabla sí la trae.
            marca = QTableWidgetItem()
            marca.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            marca.setCheckState(
                Qt.Checked if self.preferencias.visible(clave) else Qt.Unchecked)
            marca.setData(Qt.UserRole, clave)
            marca.setToolTip('Quite la palomita para que este resultado no se '
                             'dibuje en la gráfica')
            self.tabla.setItem(fila, 0, marca)

            campo = QLineEdit(self.preferencias.nombre(clave, original))
            campo.setPlaceholderText(original)
            campo.textChanged.connect(
                lambda _texto, c=clave: self._cambio_de_serie(c))
            self.tabla.setCellWidget(fila, 1, campo)

            celda = QTableWidgetItem(original)
            celda.setForeground(QColor(TEXTO_SUAVE))
            celda.setToolTip(original)
            celda.setFlags(Qt.ItemIsEnabled)
            self.tabla.setItem(fila, 2, celda)

            self.campos[clave] = (marca, campo, original)

    # ----------------------------------------------------------------- cambios
    def _cambio_de_palomita(self, elemento):
        clave = elemento.data(Qt.UserRole)
        if clave is not None:
            self._cambio_de_serie(clave)

    def _cambio_de_serie(self, clave):
        if self._cargando:
            return
        marca, campo, original = self.campos[clave]
        nombre = campo.text().strip()
        self.preferencias.poner_serie(
            clave,
            nombre='' if nombre == original else nombre,
            visible=marca.checkState() == Qt.Checked)
        self._avisar()

    def _cambio(self):
        if self._cargando:
            return
        self.preferencias.poner('tamano', self.tamano.value())
        self.preferencias.poner('nombres', self.nombres.isChecked())
        self.preferencias.poner('zonas', self.zonas.isChecked())
        self._avisar()

    def _restablecer(self):
        if QMessageBox.question(
                self, 'Volver a como estaba',
                '¿Deshacer todos los ajustes de la gráfica?\n\n'
                'Vuelven a dibujarse todos los resultados, con sus nombres '
                'originales. No se pierde ningún puntaje: los ajustes sólo '
                'cambiaban el dibujo.',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        self.preferencias.restablecer()
        self._cargando = True
        self._llenar()
        self._cargando = False
        self._avisar()

    def _avisar(self):
        self.preferencias.guardar()
        self.al_cambiar()
