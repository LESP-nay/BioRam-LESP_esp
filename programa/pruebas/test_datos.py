# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""El almacén guarda lo que el programa original perdía."""
import pytest

from bioram import modelo
from bioram.datos import (VERSION_ESQUEMA, Almacen, ArchivoDeDatosInvalido,
                          Respuesta, limpiar_texto, revisar_valor)


@pytest.fixture
def alm(tmp_path):
    with Almacen(tmp_path / 'prueba.db') as a:
        yield a


def test_area_cepa_evaluacion(alm):
    area = alm.crear_area('Bacteriología', responsable='QFB Pérez')
    cepa = alm.crear_cepa(area, 'Mycobacterium tuberculosis')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')

    assert [a.nombre for a in alm.areas()] == ['Bacteriología']
    assert [c.nombre for c in alm.cepas(area)] == ['Mycobacterium tuberculosis']
    assert alm.evaluacion(eva).tipo == 'bioseguridad'


def test_una_cepa_lleva_las_dos_evaluaciones(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.crear_evaluacion(cepa, 'bioproteccion')
    assert {e.tipo for e in alm.evaluaciones(cepa)} == {'bioseguridad', 'bioproteccion'}


def test_se_guarda_que_una_respuesta_es_aproximada(alm):
    """Lo que el BioRAM original mostraba pero no guardaba."""
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.guardar_respuestas(eva, {'p1': Respuesta(4.0, aproximada=True),
                                 'p2': Respuesta(2.0)})

    guardadas = alm.respuestas(eva)
    assert guardadas['p1'].aproximada is True
    assert guardadas['p2'].aproximada is False
    assert alm.puntajes(eva) == {'p1': 4.0, 'p2': 2.0}


def test_guardar_dos_veces_actualiza_en_vez_de_duplicar(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.guardar_respuestas(eva, {'p1': 1.0})
    alm.guardar_respuestas(eva, {'p1': 3.0})
    assert alm.puntajes(eva) == {'p1': 3.0}


def test_historial_y_restauracion(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.guardar_respuestas(eva, {'p1': 1.0})
    v1 = alm.guardar_version(eva, autor='Pérez', nota='primera revisión')

    alm.guardar_respuestas(eva, {'p1': 4.0})
    assert alm.puntajes(eva) == {'p1': 4.0}

    assert [v.nota for v in alm.versiones(eva)] == ['primera revisión']
    alm.restaurar_version(v1)
    assert alm.puntajes(eva) == {'p1': 1.0}


def test_copiar_respuestas_de_otra_evaluacion(alm):
    area = alm.crear_area('A')
    a = alm.crear_evaluacion(alm.crear_cepa(area, 'cepa 1'), 'bioseguridad')
    alm.guardar_respuestas(a, {'p1': 2.0, 'p2': 4.0})
    b = alm.crear_evaluacion(alm.crear_cepa(area, 'cepa 2'), 'bioseguridad', copiar_de=a)
    assert alm.puntajes(b) == {'p1': 2.0, 'p2': 4.0}


def test_no_se_copian_respuestas_entre_tipos_distintos(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    a = alm.crear_evaluacion(cepa, 'bioseguridad')
    with pytest.raises(ValueError):
        alm.crear_evaluacion(cepa, 'bioproteccion', copiar_de=a)


def test_borrar_un_area_se_lleva_sus_cepas_y_evaluaciones(alm):
    area = alm.crear_area('A')
    cepa = alm.crear_cepa(area, 'cepa')
    alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.borrar_area(area)
    assert alm.areas() == [] and alm.cepas() == [] and alm.evaluaciones() == []


def test_tipo_invalido(alm):
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    with pytest.raises(ValueError):
        alm.crear_evaluacion(cepa, 'quimica')


def test_el_archivo_se_vuelve_a_abrir(tmp_path):
    ruta = tmp_path / 'lab.db'
    with Almacen(ruta) as a:
        eva = a.crear_evaluacion(a.crear_cepa(a.crear_area('A'), 'cepa'), 'bioseguridad')
        a.guardar_respuestas(eva, {'p1': 3.0})
    with Almacen(ruta) as a:
        assert a.puntajes(1) == {'p1': 3.0}


def test_resumen_para_la_pantalla_principal(alm):
    area = alm.crear_area('Bacteriología')
    cepa = alm.crear_cepa(area, 'M. tuberculosis')
    eva = alm.crear_evaluacion(cepa, 'bioseguridad')
    alm.guardar_respuestas(eva, {f'p{i}': 1.0 for i in range(10)})

    fila = alm.resumen()[0]
    assert fila['area'] == 'Bacteriología'
    assert fila['cepa'] == 'M. tuberculosis'
    assert fila['respondidas'] == 10


def test_las_plantillas_de_agentes_se_pueden_guardar(alm):
    cuestionario = modelo.incluido('bioproteccion')
    cepa = alm.crear_cepa(alm.crear_area('A'), 'cepa')
    eva = alm.crear_evaluacion(cepa, 'bioproteccion')
    alm.guardar_respuestas(eva, cuestionario.plantillas['Bacillus anthracis'])
    assert len(alm.puntajes(eva)) == len(cuestionario.plantillas['Bacillus anthracis'])


# ---------------------------------------------------------------------------
# Lo que el programa tiene que avisar en vez de callarse. Cada una de estas
# pruebas corresponde a una falla real que se encontró probando el programa.

def test_un_nombre_de_area_repetido_se_rechaza_con_un_mensaje(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        alm.crear_area('Bacteriología')
        with pytest.raises(ValueError, match='ya existe un área'):
            alm.crear_area('Bacteriología')


def test_un_nombre_de_cepa_repetido_en_la_misma_area_se_rechaza(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        a1 = alm.crear_area('Área 1')
        a2 = alm.crear_area('Área 2')
        alm.crear_cepa(a1, 'M. tuberculosis')
        with pytest.raises(ValueError, match='ya tiene una cepa'):
            alm.crear_cepa(a1, 'M. tuberculosis')
        # en otra área sí se puede: es la misma cepa en otro lugar
        assert alm.crear_cepa(a2, 'M. tuberculosis')


def test_un_nombre_vacio_se_rechaza(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        with pytest.raises(ValueError, match='necesita un nombre'):
            alm.crear_area('   ')
        area = alm.crear_area('Área')
        with pytest.raises(ValueError, match='necesita un nombre'):
            alm.crear_cepa(area, '\t\n')


def test_los_caracteres_que_xml_no_admite_se_quitan_al_capturar(tmp_path):
    """Si entran, el .raml que se exporta queda ilegible para los dos programas."""
    with Almacen(tmp_path / 'b.db') as alm:
        area = alm.crear_area('Bacter\x00iolog\x08ía')
        assert alm.area(area).nombre == 'Bacteriología'
        cepa = alm.crear_cepa(area, 'M.\x1f tuberculosis')
        assert alm.cepa(cepa).nombre == 'M. tuberculosis'


def test_renombrar_a_un_nombre_que_ya_existe_se_rechaza(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        a1 = alm.crear_area('Área 1')
        alm.crear_area('Área 2')
        with pytest.raises(ValueError, match='ya existe un área'):
            alm.renombrar_area(a1, 'Área 2')
        alm.renombrar_area(a1, 'Virología')
        assert alm.area(a1).nombre == 'Virología'


def test_una_respuesta_que_no_es_un_numero_finito_se_rechaza(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        area = alm.crear_area('Área')
        cepa = alm.crear_cepa(area, 'Cepa')
        eva = alm.crear_evaluacion(cepa, 'bioseguridad')
        for malo in (float('nan'), float('inf'), float('-inf')):
            with pytest.raises(ValueError, match='número finito'):
                alm.guardar_respuestas(eva, {'una-pregunta': malo})
        with pytest.raises(ValueError, match='no es un número'):
            alm.guardar_respuestas(eva, {'una-pregunta': 'dos'})


def test_los_limites_de_la_pregunta_se_respetan():
    from bioram import modelo
    pregunta = modelo.incluido('bioseguridad').preguntas_en_orden()[0]
    assert revisar_valor(2.5, pregunta) == 2.5
    assert revisar_valor(0, pregunta) == 0.0
    assert revisar_valor(4, pregunta) == 4.0
    for fuera in (999, -5, 4.1):
        with pytest.raises(ValueError, match='fuera de los límites'):
            revisar_valor(fuera, pregunta)


def test_guardar_solo_el_numero_no_borra_la_marca_de_estimacion(tmp_path):
    """Pasaba al contestar de nuevo una pregunta ya marcada como estimación."""
    with Almacen(tmp_path / 'b.db') as alm:
        area = alm.crear_area('Área')
        cepa = alm.crear_cepa(area, 'Cepa')
        eva = alm.crear_evaluacion(cepa, 'bioseguridad')
        alm.guardar_respuestas(eva, {'p1': Respuesta(4.0, aproximada=True)})
        assert alm.respuestas(eva)['p1'].aproximada is True
        alm.guardar_respuestas(eva, {'p1': 3.0})
        r = alm.respuestas(eva)['p1']
        assert (r.valor, r.aproximada) == (3.0, True)
        # y un objeto Respuesta sí la cambia
        alm.guardar_respuestas(eva, {'p1': Respuesta(2.0, aproximada=False)})
        assert alm.respuestas(eva)['p1'].aproximada is False


def test_un_archivo_que_no_es_una_base_de_datos_da_un_mensaje_claro(tmp_path):
    malo = tmp_path / 'malo.db'
    malo.write_text('esto no es una base de datos', encoding='utf-8')
    with pytest.raises(ArchivoDeDatosInvalido) as e:
        Almacen(malo)
    assert 'No se pudo abrir el archivo de datos' in str(e.value)
    assert str(malo) in str(e.value)


# ---------------------------------------------------------------------------
# Herencia: las instalaciones del laboratorio son las mismas para todas las
# cepas de un área, así que se contestan una vez y cada cepa nueva las trae.

def _area_con_cepa(alm, nombre_area='Área', nombre_cepa='Cepa'):
    area = alm.crear_area(nombre_area)
    return area, alm.crear_cepa(area, nombre_cepa)


def test_una_cepa_nueva_hereda_las_respuestas_del_area(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        area, cepa = _area_con_cepa(alm)
        alm.guardar_respuestas_de_area(area, 'bioseguridad',
                                       {'p1': 3.0, 'p2': Respuesta(4.0, True)})
        eva = alm.crear_evaluacion(cepa, 'bioseguridad')
        traidas = alm.respuestas(eva)
        assert set(traidas) == {'p1', 'p2'}
        assert traidas['p1'].valor == 3.0
        assert traidas['p2'].aproximada is True
        # otra cepa del área también
        otra = alm.crear_cepa(area, 'Otra cepa')
        assert len(alm.respuestas(alm.crear_evaluacion(otra, 'bioseguridad'))) == 2


def test_con_heredar_apagado_la_evaluacion_arranca_vacia(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        area, cepa = _area_con_cepa(alm)
        alm.guardar_respuestas_de_area(area, 'bioseguridad', {'p1': 3.0})
        eva = alm.crear_evaluacion(cepa, 'bioseguridad', heredar=False)
        assert alm.respuestas(eva) == {}


def test_modificar_lo_heredado_no_toca_las_respuestas_del_area(tmp_path):
    """Es lo que pidió el laboratorio: heredar, pero poder modificar."""
    with Almacen(tmp_path / 'b.db') as alm:
        area, cepa = _area_con_cepa(alm)
        alm.guardar_respuestas_de_area(area, 'bioseguridad', {'p1': 3.0})
        eva = alm.crear_evaluacion(cepa, 'bioseguridad')
        alm.guardar_respuestas(eva, {'p1': 1.0})
        assert alm.respuestas(eva)['p1'].valor == 1.0
        assert alm.respuestas_de_area(area, 'bioseguridad')['p1'].valor == 3.0
        # y una cepa nueva sigue heredando la del área, no la modificada
        otra = alm.crear_cepa(area, 'Otra')
        nueva = alm.crear_evaluacion(otra, 'bioseguridad')
        assert alm.respuestas(nueva)['p1'].valor == 3.0


def test_limpiar_las_respuestas_de_la_evaluacion_no_toca_las_del_area(tmp_path):
    """La otra mitad de lo que pidió el laboratorio: empezar de cero."""
    with Almacen(tmp_path / 'b.db') as alm:
        area, cepa = _area_con_cepa(alm)
        alm.guardar_respuestas_de_area(area, 'bioseguridad', {'p1': 3.0, 'p2': 2.0})
        eva = alm.crear_evaluacion(cepa, 'bioseguridad')
        for pregunta in list(alm.respuestas(eva)):
            alm.borrar_respuesta(eva, pregunta)
        assert alm.respuestas(eva) == {}
        assert len(alm.respuestas_de_area(area, 'bioseguridad')) == 2


def test_cada_evaluacion_hereda_lo_de_su_propio_tipo(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        area, cepa = _area_con_cepa(alm)
        alm.guardar_respuestas_de_area(area, 'bioseguridad', {'p1': 3.0})
        alm.guardar_respuestas_de_area(area, 'bioproteccion', {'q1': 1.0, 'q2': 2.0})
        assert len(alm.respuestas(alm.crear_evaluacion(cepa, 'bioseguridad'))) == 1
        assert len(alm.respuestas(alm.crear_evaluacion(cepa, 'bioproteccion'))) == 2


def test_borrar_el_area_se_lleva_sus_respuestas(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        area, _ = _area_con_cepa(alm)
        alm.guardar_respuestas_de_area(area, 'bioseguridad', {'p1': 3.0})
        alm.borrar_area(area)
        assert alm.cx.execute('SELECT COUNT(*) FROM respuesta_area').fetchone()[0] == 0


def test_las_respuestas_del_area_tambien_se_validan(tmp_path):
    with Almacen(tmp_path / 'b.db') as alm:
        area, _ = _area_con_cepa(alm)
        with pytest.raises(ValueError, match='número finito'):
            alm.guardar_respuestas_de_area(area, 'bioseguridad', {'p1': float('nan')})
        with pytest.raises(ValueError, match='tipo desconocido'):
            alm.guardar_respuestas_de_area(area, 'otra cosa', {'p1': 1.0})


def test_un_archivo_de_una_version_anterior_se_actualiza_al_abrirlo(tmp_path):
    """Las tablas y columnas nuevas se crean, y la versión queda al día."""
    ruta = tmp_path / 'vieja.db'
    with Almacen(ruta) as alm:
        # se deja como la versión 1: sin respuestas de área y sin la columna
        # de revisión del cuestionario
        alm.cx.execute("UPDATE meta SET valor = '1' WHERE clave = 'version_esquema'")
        alm.cx.execute('DROP TABLE respuesta_area')
        alm.cx.execute('ALTER TABLE evaluacion DROP COLUMN revision')
        alm.cx.commit()

    with Almacen(ruta) as alm:
        guardada = alm.cx.execute(
            "SELECT valor FROM meta WHERE clave = 'version_esquema'").fetchone()[0]
        assert int(guardada) == VERSION_ESQUEMA

        area = alm.crear_area('Área')
        alm.guardar_respuestas_de_area(area, 'bioseguridad', {'p1': 1.0})
        assert len(alm.respuestas_de_area(area, 'bioseguridad')) == 1

        cepa = alm.crear_cepa(area, 'Cepa')
        eva = alm.crear_evaluacion(cepa, 'bioseguridad')
        assert alm.evaluacion(eva).revision, 'la evaluación debe quedar sellada'


def test_la_evaluacion_guarda_con_que_revision_se_capturo(tmp_path):
    """Sin esto, un reporte de antes y otro de después no se podrían explicar."""
    with Almacen(tmp_path / 'b.db') as alm:
        area, cepa = _area_con_cepa(alm)
        eva = alm.crear_evaluacion(cepa, 'bioseguridad')
        esperada = modelo.incluido('bioseguridad').revision
        assert alm.evaluacion(eva).revision == esperada
        # y se vuelve a sellar al contestar
        alm.cx.execute("UPDATE evaluacion SET revision = 'otra' WHERE id = ?", (eva,))
        alm.cx.commit()
        alm.guardar_respuestas(eva, {'p1': 2.0})
        assert alm.evaluacion(eva).revision == esperada


def test_las_dos_evaluaciones_tienen_revisiones_distintas():
    """Son cuestionarios distintos, así que su huella de cálculo no coincide."""
    a = modelo.incluido('bioseguridad').revision
    b = modelo.incluido('bioproteccion').revision
    assert a and b and a != b


# ---------------------------------------------------------------------------
# Responsables y procedimiento: se capturan en el área y los hereda cada
# evaluación nueva. El laboratorio los pidió en la pantalla del área para no
# recapturarlos cepa por cepa.

def test_la_evaluacion_nueva_hereda_los_responsables_del_area(tmp_path):
    alm = Almacen(tmp_path / 'b.db')
    area = alm.crear_area('Virología')
    alm.actualizar_area(area, responsables='QFB Ana Gómez',
                        procedimiento='Aislamiento viral, BSL-2')
    cepa = alm.crear_cepa(area, 'Influenza A/H1N1')
    evaluacion = alm.evaluacion(alm.crear_evaluacion(cepa, 'bioseguridad'))
    assert evaluacion.responsables == 'QFB Ana Gómez'
    assert evaluacion.procedimiento == 'Aislamiento viral, BSL-2'
    alm.cerrar()


def test_cambiar_el_area_no_reescribe_una_evaluacion_ya_hecha(tmp_path):
    """Un reporte ya emitido no puede cambiar solo porque después cambie el área."""
    alm = Almacen(tmp_path / 'b.db')
    area = alm.crear_area('Virología')
    alm.actualizar_area(area, responsables='Equipo de 2026')
    cepa = alm.crear_cepa(area, 'Influenza A/H1N1')
    vieja = alm.crear_evaluacion(cepa, 'bioseguridad')

    alm.actualizar_area(area, responsables='Equipo de 2027')
    nueva = alm.crear_evaluacion(cepa, 'bioproteccion')

    assert alm.evaluacion(vieja).responsables == 'Equipo de 2026'
    assert alm.evaluacion(nueva).responsables == 'Equipo de 2027'
    alm.cerrar()


def test_lo_que_se_pasa_a_mano_le_gana_a_lo_del_area(tmp_path):
    alm = Almacen(tmp_path / 'b.db')
    area = alm.crear_area('Virología')
    alm.actualizar_area(area, responsables='Del área', procedimiento='Del área')
    cepa = alm.crear_cepa(area, 'Influenza A/H1N1')
    evaluacion = alm.evaluacion(
        alm.crear_evaluacion(cepa, 'bioseguridad', responsables='Sólo esta vez'))
    assert evaluacion.responsables == 'Sólo esta vez'
    assert evaluacion.procedimiento == 'Del área'      # lo vacío sí se hereda
    alm.cerrar()


def test_sin_heredar_no_se_trae_nada_del_area(tmp_path):
    alm = Almacen(tmp_path / 'b.db')
    area = alm.crear_area('Virología')
    alm.actualizar_area(area, responsables='Del área')
    cepa = alm.crear_cepa(area, 'Influenza A/H1N1')
    evaluacion = alm.evaluacion(
        alm.crear_evaluacion(cepa, 'bioseguridad', heredar=False))
    assert evaluacion.responsables == ''
    alm.cerrar()


def test_un_archivo_del_esquema_anterior_se_actualiza_sin_perder_nada(tmp_path):
    """El laboratorio ya tiene archivos del esquema 3; tienen que seguir abriendo."""
    import sqlite3
    ruta = tmp_path / 'viejo.db'
    cx = sqlite3.connect(ruta)
    cx.executescript("""
    CREATE TABLE meta (clave TEXT PRIMARY KEY, valor TEXT NOT NULL);
    INSERT INTO meta VALUES ('version_esquema','3');
    CREATE TABLE area (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE,
      responsable TEXT NOT NULL DEFAULT '', notas TEXT NOT NULL DEFAULT '',
      creada TEXT NOT NULL);
    INSERT INTO area (nombre, creada) VALUES ('Bacteriología','2026-01-01');
    """)
    cx.commit()
    cx.close()

    alm = Almacen(ruta)
    area = alm.areas()[0]
    assert area.nombre == 'Bacteriología'
    assert area.responsables == '' and area.procedimiento == ''
    alm.actualizar_area(area.id, responsables='Se puede escribir')
    assert alm.area(area.id).responsables == 'Se puede escribir'
    alm.cerrar()


def test_actualizar_area_rechaza_un_campo_que_no_existe(tmp_path):
    alm = Almacen(tmp_path / 'b.db')
    area = alm.crear_area('Virología')
    with pytest.raises(ValueError, match='campos desconocidos'):
        alm.actualizar_area(area, color_favorito='azul')
    alm.cerrar()
