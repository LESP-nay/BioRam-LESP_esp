# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""La gráfica de riesgo: sus zonas, sus ajustes y lo que NO deben tocar.

La regla que vigila todo este archivo: personalizar la gráfica cambia el dibujo
y nada más. Un laboratorio puede quitar de la imagen un resultado que no
evalúa, pero ese puntaje se sigue calculando y se sigue reportando. Si alguna
vez dejara de ser cierto, una evaluación perdería un número sin que nadie se
entere, y eso en un expediente es grave.
"""
from __future__ import annotations

import math

import pytest

from bioram import modelo, motor
from bioram.datos import Almacen
from bioram.sin_pantalla import plataforma_sin_ventana

pytest.importorskip('PySide6')

from bioram.interfaz.grafica import (CLAVE, ZONAS, Preferencias,  # noqa: E402
                                     clave_de)


def _aplicacion():
    plataforma_sin_ventana()
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([''])


def _respuestas(cuestionario, valor=2.0):
    return {uuid: valor for uuid in cuestionario.preguntas}


# ---------------------------------------------------------------- las zonas

def test_las_zonas_van_de_dentro_hacia_fuera_y_cubren_toda_la_grafica():
    radios = [z.hasta for z in ZONAS]
    assert radios == sorted(radios), 'las zonas deben ir de la peor a la mejor'
    assert radios[:4] == [1.0, 2.0, 3.0, 4.0], (
        'los cuatro arcos medidos sobre la imagen de Sandia están en 1, 2, 3 y 4')
    # La última tiene que alcanzar la esquina opuesta, o quedaría sin pintar.
    assert radios[-1] >= math.sqrt(32)


def test_los_nombres_de_las_zonas_son_los_del_original():
    assert [z.nombre for z in ZONAS] == [
        'Muy alto', 'Alto', 'Moderado', 'Bajo', 'Muy bajo']


@pytest.mark.parametrize('zona', ZONAS, ids=[z.nombre for z in ZONAS])
def test_el_nombre_de_cada_zona_se_lee_sobre_su_relleno(zona):
    from pruebas.test_estilo import TEXTO_NORMAL, contraste
    assert contraste(zona.letra, zona.relleno) >= TEXTO_NORMAL, (
        f'«{zona.nombre}» no se lee sobre su propio color')


# -------------------------------------------------------------- preferencias

def test_las_preferencias_viven_en_el_archivo_y_sobreviven_a_cerrarlo(tmp_path):
    ruta = tmp_path / 'b.db'
    with Almacen(ruta) as alm:
        p = Preferencias(alm)
        p.poner('tamano', 16)
        p.poner_serie('a|b', nombre='Inhalación', visible=False)
        p.guardar()
    with Almacen(ruta) as alm:
        p = Preferencias(alm)
        assert p.tamano == 16
        assert p.nombre('a|b', 'original') == 'Inhalación'
        assert p.visible('a|b') is False


def test_sin_nada_guardado_se_dibuja_todo_con_su_nombre(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        p = Preferencias(alm)
        assert p.visible('cualquiera') is True
        assert p.nombre('cualquiera', 'El original') == 'El original'
        assert p.zonas is True


def test_un_archivo_con_preferencias_estropeadas_no_tumba_el_programa(tmp_path):
    """Son sólo el aspecto: ante algo que no se entiende, a lo de siempre."""
    with Almacen(tmp_path / 'b.db') as alm:
        alm.guardar_preferencia(CLAVE, ['esto no es lo que se esperaba'])
        p = Preferencias(alm)
        assert p.zonas is True and p.tamano == 10

        alm.guardar_preferencia(CLAVE, {'tamano': 'grande', 'series': 'nada'})
        p = Preferencias(alm)
        assert p.tamano == 10 and p.visible('x|y') is True


def test_el_tamano_de_letra_se_queda_en_lo_razonable(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        p = Preferencias(alm)
        p.poner('tamano', 999)
        assert p.tamano <= 28
        p.poner('tamano', 1)
        assert p.tamano >= 6


def test_volver_a_como_estaba_borra_todo_lo_puesto(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        p = Preferencias(alm)
        p.poner_serie('a|b', visible=False, nombre='Otro')
        p.poner('zonas', False)
        p.restablecer()
        assert p.visible('a|b') is True
        assert p.nombre('a|b', 'original') == 'original'
        assert p.zonas is True


# ------------------------------------------- lo que NO puede cambiar el dibujo

def test_apagar_y_renombrar_no_mueve_ni_un_puntaje(tmp_path):
    """La regla de todo este archivo, comprobada sobre los 19 resultados."""
    _aplicacion()
    from bioram.interfaz.resultados import PanelResultados

    cuestionario = modelo.incluido('bioseguridad')
    respuestas = _respuestas(cuestionario, 3.0)
    antes = motor.resultados(cuestionario, respuestas)

    with Almacen(tmp_path / 'b.db') as alm:
        panel = PanelResultados(cuestionario, 'bioseguridad', alm)
        panel.mostrar(respuestas)
        lienzo = panel.lienzos[0]
        for clave in lienzo.claves:
            panel.preferencias.poner_serie(clave, visible=False, nombre='Otro nombre')
        panel.preferencias.poner('zonas', False)
        panel.preferencias.guardar()
        panel._redibujar()
        panel.mostrar(respuestas)

        despues = motor.resultados(cuestionario, respuestas)
        assert despues == antes
        # Y la tabla los sigue mostrando todos, apagados o no.
        assert panel.tabla.rowCount() == len(antes)
        assert lienzo.visibles() == []


def test_lo_apagado_sigue_apareciendo_en_la_tabla_con_su_puntaje(tmp_path):
    _aplicacion()
    from bioram.interfaz.resultados import PanelResultados

    cuestionario = modelo.incluido('bioseguridad')
    respuestas = _respuestas(cuestionario, 2.0)
    with Almacen(tmp_path / 'b.db') as alm:
        panel = PanelResultados(cuestionario, 'bioseguridad', alm)
        panel.mostrar(respuestas)
        apagada = panel.lienzos[0].claves[0]
        panel.preferencias.poner_serie(apagada, visible=False)
        panel.mostrar(respuestas)

        perfil_x, perfil_y = apagada.split('|')
        titulos = {panel.tabla.item(f, 0).text() for f in range(panel.tabla.rowCount())}
        for uuid in (perfil_x, perfil_y):
            assert cuestionario.perfiles[uuid].titulo in titulos, (
                'apagar una serie no puede quitar su puntaje de la tabla')

        # Se marca como no graficado sólo el perfil que ya no usa ninguna serie
        # encendida. En estas gráficas el eje X es la consecuencia, que todas las
        # vías comparten, y el Y la probabilidad de cada vía. Así que al apagar
        # una serie se marca su probabilidad, y la consecuencia no, porque las
        # demás series la siguen usando.
        apagados = panel._apagados()
        assert perfil_y in apagados, 'la probabilidad de esa vía ya no se grafica'
        assert perfil_x not in apagados, (
            'la consecuencia la comparten otras series todavía encendidas')


# ------------------------------------------------------------------ la imagen

def test_la_imagen_sale_mas_grande_que_la_pantalla_y_no_sale_en_blanco(tmp_path):
    """Si saliera en blanco, el laboratorio pegaría un recuadro vacío en su informe."""
    _aplicacion()
    from bioram.interfaz.resultados import PanelResultados

    cuestionario = modelo.incluido('bioseguridad')
    with Almacen(tmp_path / 'b.db') as alm:
        panel = PanelResultados(cuestionario, 'bioseguridad', alm)
        panel.resize(640, 700)
        panel.mostrar(_respuestas(cuestionario, 3.0))
        lienzo = panel.lienzos[0]
        lienzo.resize(500, 400)

        imagen = lienzo.imagen(escala=3.0)
        assert imagen.width() == 1500 and imagen.height() == 1200

        colores = {imagen.pixelColor(x, y).name()
                   for x in range(0, imagen.width(), 17)
                   for y in range(0, imagen.height(), 17)}
        assert len(colores) > 5, 'la imagen salió casi vacía'

        destino = tmp_path / 'grafica.jpg'
        assert imagen.save(str(destino), 'JPG', 92)
        assert destino.stat().st_size > 10_000


def test_la_leyenda_solo_lista_lo_que_se_dibuja(tmp_path):
    _aplicacion()
    from bioram.interfaz.resultados import PanelResultados

    cuestionario = modelo.incluido('bioseguridad')
    respuestas = _respuestas(cuestionario, 2.0)
    with Almacen(tmp_path / 'b.db') as alm:
        panel = PanelResultados(cuestionario, 'bioseguridad', alm)
        panel.mostrar(respuestas)
        lienzo = panel.lienzos[0]
        original = lienzo.puntos[0][0]
        assert original in lienzo.leyenda.text()

        panel.preferencias.poner_serie(lienzo.claves[0], visible=False)
        panel.preferencias.poner_serie(lienzo.claves[1], nombre='Mi nombre')
        panel.mostrar(respuestas)
        assert original not in lienzo.leyenda.text()
        assert 'Mi nombre' in lienzo.leyenda.text()


def test_la_clave_de_una_serie_no_cambia_al_renombrarla():
    """Si cambiara, al renombrar se perdería lo que se hubiera configurado."""
    cuestionario = modelo.incluido('bioseguridad')
    punto = cuestionario.graficas[0].puntos[0]
    assert clave_de(punto) == f'{punto.perfil_x}|{punto.perfil_y}'
    assert punto.leyenda not in clave_de(punto)
