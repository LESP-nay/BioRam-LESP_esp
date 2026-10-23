# BioRAM LESP — Copyright (C) 2025-2026 Laboratorio Estatal de Salud Pública de Nayarit.
# Software libre bajo la Licencia Pública General de GNU v3 o posterior (ver LICENSE).
# Método y cuestionarios: BioRAM, de Sandia National Laboratories (ver AVISO.md).
"""Dónde guarda el programa el trabajo del laboratorio.

Todo vive en un solo archivo SQLite, para que respaldarlo sea copiarlo y
llevarlo a otro equipo sea pegarlo. La estructura sigue la del laboratorio:

    área  ->  cepa  ->  evaluación (bioseguridad o bioprotección)  ->  respuestas

Cada evaluación guarda, además del puntaje de cada pregunta, si la respuesta se
marcó como aproximada. El programa original tenía ese dato en pantalla pero no
lo guardaba en el archivo, así que se perdía al cerrar.

Al terminar una evaluación se puede archivar una versión: una copia de las
respuestas de ese momento, con fecha y autor, que queda como historial.
"""
from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

VERSION_ESQUEMA = 3
TIPOS = ('bioseguridad', 'bioproteccion')


class ArchivoDeDatosInvalido(Exception):
    """El archivo de datos no se puede abrir: corrupto, ajeno o sin permiso."""

    def __init__(self, ruta, causa=None):
        self.ruta = Path(ruta)
        self.causa = causa
        super().__init__(
            f'No se pudo abrir el archivo de datos:\n\n{self.ruta}\n\n'
            'Puede estar dañado, no ser un archivo de BioRAM LESP, o no tener '
            'permiso de escritura. Si tiene un respaldo, recupérelo; si no, '
            'mueva este archivo a un lado y el programa creará uno nuevo.'
            + (f'\n\nDetalle técnico: {causa}' if causa else ''))

# Nota sobre la columna «revision» de la tabla evaluacion: guarda con qué
# revisión del cuestionario se capturaron las respuestas. El programa no guarda
# los puntajes, los recalcula cada vez; sin ese dato, un reporte impreso antes
# de corregir el cuestionario y otro de después no coincidirían y nada lo
# explicaría.
#
# Los comentarios van aquí y no dentro del SQL a propósito: SQLite reescribe el
# DDL al hacer ALTER TABLE, y un comentario dentro de un CREATE TABLE hace que
# una migración posterior falle con «incomplete input».
ESQUEMA = """
CREATE TABLE IF NOT EXISTS meta (
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS area (
    id          INTEGER PRIMARY KEY,
    nombre      TEXT NOT NULL UNIQUE,
    responsable TEXT NOT NULL DEFAULT '',
    notas       TEXT NOT NULL DEFAULT '',
    creada      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cepa (
    id      INTEGER PRIMARY KEY,
    area_id INTEGER NOT NULL REFERENCES area(id) ON DELETE CASCADE,
    nombre  TEXT NOT NULL,
    agente  TEXT NOT NULL DEFAULT '',
    notas   TEXT NOT NULL DEFAULT '',
    creada  TEXT NOT NULL,
    UNIQUE (area_id, nombre)
);

CREATE TABLE IF NOT EXISTS evaluacion (
    id            INTEGER PRIMARY KEY,
    cepa_id       INTEGER NOT NULL REFERENCES cepa(id) ON DELETE CASCADE,
    tipo          TEXT NOT NULL CHECK (tipo IN ('bioseguridad', 'bioproteccion')),
    titulo        TEXT NOT NULL DEFAULT '',
    responsables  TEXT NOT NULL DEFAULT '',
    procedimiento TEXT NOT NULL DEFAULT '',
    estado        TEXT NOT NULL DEFAULT 'borrador'
                  CHECK (estado IN ('borrador', 'terminada')),
    creada        TEXT NOT NULL,
    actualizada   TEXT NOT NULL,
    revision      TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS respuesta (
    evaluacion_id INTEGER NOT NULL REFERENCES evaluacion(id) ON DELETE CASCADE,
    pregunta      TEXT NOT NULL,
    valor         REAL NOT NULL,
    aproximada    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (evaluacion_id, pregunta)
);

-- Las respuestas que valen para toda el área: las instalaciones del
-- laboratorio son las mismas para todas las cepas que se trabajan ahí, así que
-- se contestan una vez y cada cepa nueva las hereda.
CREATE TABLE IF NOT EXISTS respuesta_area (
    area_id    INTEGER NOT NULL REFERENCES area(id) ON DELETE CASCADE,
    tipo       TEXT NOT NULL CHECK (tipo IN ('bioseguridad', 'bioproteccion')),
    pregunta   TEXT NOT NULL,
    valor      REAL NOT NULL,
    aproximada INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (area_id, tipo, pregunta)
);

CREATE TABLE IF NOT EXISTS version (
    id            INTEGER PRIMARY KEY,
    evaluacion_id INTEGER NOT NULL REFERENCES evaluacion(id) ON DELETE CASCADE,
    momento       TEXT NOT NULL,
    autor         TEXT NOT NULL DEFAULT '',
    nota          TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS respuesta_version (
    version_id INTEGER NOT NULL REFERENCES version(id) ON DELETE CASCADE,
    pregunta   TEXT NOT NULL,
    valor      REAL NOT NULL,
    aproximada INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (version_id, pregunta)
);

CREATE INDEX IF NOT EXISTS idx_cepa_area ON cepa(area_id);
CREATE INDEX IF NOT EXISTS idx_evaluacion_cepa ON evaluacion(cepa_id);
"""


@dataclass
class Area:
    id: int
    nombre: str
    responsable: str
    notas: str
    creada: str


@dataclass
class Cepa:
    id: int
    area_id: int
    nombre: str
    agente: str
    notas: str
    creada: str


@dataclass
class Evaluacion:
    id: int
    cepa_id: int
    tipo: str
    titulo: str
    responsables: str
    procedimiento: str
    estado: str
    creada: str
    actualizada: str
    revision: str = ''      # revisión del cuestionario con que se capturó


@dataclass
class Respuesta:
    valor: float
    aproximada: bool = False


@dataclass
class Version:
    id: int
    evaluacion_id: int
    momento: str
    autor: str
    nota: str


def _ahora() -> str:
    return datetime.now().isoformat(timespec='seconds')


def _revision_en_vigor(tipo: str) -> str:
    """La revisión del cuestionario que el programa tiene cargada ahora.

    Se importa aquí dentro y no arriba para no obligar a datos.py a depender de
    modelo.py: así el almacén se puede usar con cuestionarios que no son los
    incluidos, sin que falle.
    """
    try:
        from . import modelo
        return modelo.incluido(tipo).revision
    except Exception:
        return ''


# Caracteres que XML 1.0 no admite. Si uno entra en el nombre de un área o de
# una cepa, el .raml que se exporta queda ilegible para el programa original y
# para este, así que se limpian al capturar y no al escribir.
_PROHIBIDOS = ''.join(chr(c) for c in range(0x20) if chr(c) not in '\t\n\r')
_PROHIBIDOS += ''.join(chr(c) for c in range(0x7F, 0xA0))
_LIMPIAR = str.maketrans('', '', _PROHIBIDOS)


def limpiar_texto(texto: str) -> str:
    """Quita los caracteres que no se pueden escribir en un XML."""
    return str(texto or '').translate(_LIMPIAR).strip()


def revisar_valor(valor, pregunta=None) -> float:
    """Comprueba que una respuesta sea un número usable.

    El «no es un número» y el infinito se rechazan siempre: entran por un error
    de captura y luego salen impresos en el reporte. Si se pasa la pregunta, se
    comprueban además sus límites, que en los dos cuestionarios son 0 y 4.
    """
    try:
        v = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f'«{valor}» no es un número') from None
    if math.isnan(v) or math.isinf(v):
        raise ValueError('la respuesta tiene que ser un número finito')
    if pregunta is not None:
        minimo = getattr(pregunta, 'minimo', None)
        maximo = getattr(pregunta, 'maximo', None)
        if minimo is not None and maximo is not None and not (minimo <= v <= maximo):
            raise ValueError(
                f'la respuesta {v:g} está fuera de los límites de la pregunta '
                f'({minimo:g} a {maximo:g})')
    return v


class Almacen:
    """El archivo de datos del laboratorio."""

    def __init__(self, ruta):
        self.ruta = Path(ruta)
        try:
            # timeout: si otra copia del programa está escribiendo, espera en vez
            # de fallar de inmediato. WAL: deja leer mientras otro escribe.
            self.cx = sqlite3.connect(self.ruta, timeout=15)
            self.cx.row_factory = sqlite3.Row
            self.cx.execute('PRAGMA foreign_keys = ON')
            self.cx.execute('PRAGMA journal_mode = WAL')
            self.cx.executescript(ESQUEMA)
            self.cx.execute('INSERT OR IGNORE INTO meta (clave, valor) VALUES (?, ?)',
                            ('version_esquema', str(VERSION_ESQUEMA)))
            # Columnas que no existían en versiones anteriores del esquema.
            # CREATE TABLE IF NOT EXISTS no las agrega a una tabla que ya está.
            columnas = {f['name'] for f in
                        self.cx.execute('PRAGMA table_info(evaluacion)')}
            if 'revision' not in columnas:
                self.cx.execute("ALTER TABLE evaluacion ADD COLUMN revision "
                                "TEXT NOT NULL DEFAULT ''")
            # Un archivo de una versión anterior se actualiza al abrirlo: las
            # tablas nuevas las crea el CREATE TABLE IF NOT EXISTS de arriba, y
            # aquí se anota la versión a la que quedó.
            self.cx.execute(
                'UPDATE meta SET valor = ? WHERE clave = ? AND CAST(valor AS INTEGER) < ?',
                (str(VERSION_ESQUEMA), 'version_esquema', VERSION_ESQUEMA))
            self.cx.commit()
        except sqlite3.DatabaseError as e:
            # Archivo corrupto, truncado, de solo lectura, o que no es una base
            # de datos. Sin esto sale una traza de Python que nadie puede leer.
            raise ArchivoDeDatosInvalido(self.ruta, e) from e
        self._revisar_version()

    def _revisar_version(self):
        guardada = int(self.cx.execute(
            "SELECT valor FROM meta WHERE clave = 'version_esquema'").fetchone()[0])
        if guardada > VERSION_ESQUEMA:
            raise RuntimeError(
                f'{self.ruta} lo creó una versión más nueva del programa '
                f'(esquema {guardada}, este programa entiende el {VERSION_ESQUEMA})')

    def cerrar(self):
        self.cx.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.cerrar()

    # ---------------------------------------------------------------- áreas
    def crear_area(self, nombre, responsable='', notas='') -> int:
        nombre = limpiar_texto(nombre)
        if not nombre:
            raise ValueError('el área necesita un nombre')
        try:
            cur = self.cx.execute(
                'INSERT INTO area (nombre, responsable, notas, creada) VALUES (?,?,?,?)',
                (nombre, limpiar_texto(responsable), notas, _ahora()))
        except sqlite3.IntegrityError:
            raise ValueError(f'ya existe un área llamada «{nombre}»') from None
        self.cx.commit()
        return cur.lastrowid

    def areas(self) -> list[Area]:
        return [Area(**dict(f)) for f in
                self.cx.execute('SELECT * FROM area ORDER BY nombre')]

    def area(self, area_id) -> Area:
        f = self.cx.execute('SELECT * FROM area WHERE id = ?', (area_id,)).fetchone()
        if f is None:
            raise LookupError(f'no existe el área {area_id}')
        return Area(**dict(f))

    def renombrar_area(self, area_id, nombre):
        self.area(area_id)
        nombre = limpiar_texto(nombre)
        if not nombre:
            raise ValueError('el área necesita un nombre')
        try:
            self.cx.execute('UPDATE area SET nombre = ? WHERE id = ?',
                            (nombre, area_id))
        except sqlite3.IntegrityError:
            raise ValueError(f'ya existe un área llamada «{nombre}»') from None
        self.cx.commit()

    def borrar_area(self, area_id):
        """Borra el área con sus cepas y evaluaciones."""
        self.cx.execute('DELETE FROM area WHERE id = ?', (area_id,))
        self.cx.commit()

    # ---------------------------------------------------------------- cepas
    def crear_cepa(self, area_id, nombre, agente='', notas='') -> int:
        area = self.area(area_id)   # falla pronto si el área no existe
        nombre = limpiar_texto(nombre)
        if not nombre:
            raise ValueError('la cepa necesita un nombre')
        try:
            cur = self.cx.execute(
                'INSERT INTO cepa (area_id, nombre, agente, notas, creada)'
                ' VALUES (?,?,?,?,?)',
                (area_id, nombre, limpiar_texto(agente), notas, _ahora()))
        except sqlite3.IntegrityError:
            raise ValueError(
                f'el área «{area.nombre}» ya tiene una cepa llamada «{nombre}»') from None
        self.cx.commit()
        return cur.lastrowid

    def cepas(self, area_id=None) -> list[Cepa]:
        if area_id is None:
            filas = self.cx.execute('SELECT * FROM cepa ORDER BY area_id, nombre')
        else:
            filas = self.cx.execute(
                'SELECT * FROM cepa WHERE area_id = ? ORDER BY nombre', (area_id,))
        return [Cepa(**dict(f)) for f in filas]

    def cepa(self, cepa_id) -> Cepa:
        f = self.cx.execute('SELECT * FROM cepa WHERE id = ?', (cepa_id,)).fetchone()
        if f is None:
            raise LookupError(f'no existe la cepa {cepa_id}')
        return Cepa(**dict(f))

    # ------------------------------------------------- respuestas del área
    # Las instalaciones del laboratorio son las mismas para todas las cepas que
    # se trabajan en un área, así que se contestan una vez en el área y cada
    # evaluación nueva las hereda. Quien evalúa puede modificarlas en su cepa
    # —quedan como respuestas suyas, sin tocar las del área— o limpiarlas para
    # empezar de cero.

    def guardar_respuestas_de_area(self, area_id, tipo, respuestas: dict):
        """Guarda las respuestas que valen para toda el área."""
        self.area(area_id)
        if tipo not in TIPOS:
            raise ValueError(f'tipo desconocido: {tipo}')
        filas = []
        for pregunta, r in respuestas.items():
            if isinstance(r, Respuesta):
                filas.append((area_id, tipo, pregunta,
                              revisar_valor(r.valor), int(r.aproximada)))
            else:
                filas.append((area_id, tipo, pregunta, revisar_valor(r), 0))
        self.cx.executemany(
            'INSERT INTO respuesta_area (area_id, tipo, pregunta, valor, aproximada)'
            ' VALUES (?,?,?,?,?) ON CONFLICT(area_id, tipo, pregunta)'
            ' DO UPDATE SET valor = excluded.valor, aproximada = excluded.aproximada',
            filas)
        self.cx.commit()

    def respuestas_de_area(self, area_id, tipo) -> dict[str, Respuesta]:
        return {f['pregunta']: Respuesta(f['valor'], bool(f['aproximada']))
                for f in self.cx.execute(
                    'SELECT pregunta, valor, aproximada FROM respuesta_area'
                    ' WHERE area_id = ? AND tipo = ?', (area_id, tipo))}

    def borrar_respuestas_de_area(self, area_id, tipo, preguntas=None):
        """Borra las respuestas del área; con preguntas, sólo esas."""
        if preguntas is None:
            self.cx.execute('DELETE FROM respuesta_area WHERE area_id = ? AND tipo = ?',
                            (area_id, tipo))
        else:
            self.cx.executemany(
                'DELETE FROM respuesta_area WHERE area_id = ? AND tipo = ? AND pregunta = ?',
                [(area_id, tipo, p) for p in preguntas])
        self.cx.commit()

    def respuestas_heredables(self, cepa_id, tipo) -> dict[str, Respuesta]:
        """Las respuestas del área a la que pertenece una cepa."""
        return self.respuestas_de_area(self.cepa(cepa_id).area_id, tipo)

    def renombrar_cepa(self, cepa_id, nombre):
        cepa = self.cepa(cepa_id)
        nombre = limpiar_texto(nombre)
        if not nombre:
            raise ValueError('la cepa necesita un nombre')
        try:
            self.cx.execute('UPDATE cepa SET nombre = ? WHERE id = ?',
                            (nombre, cepa_id))
        except sqlite3.IntegrityError:
            area = self.area(cepa.area_id)
            raise ValueError(
                f'el área «{area.nombre}» ya tiene una cepa llamada «{nombre}»') from None
        self.cx.commit()

    def borrar_cepa(self, cepa_id):
        self.cx.execute('DELETE FROM cepa WHERE id = ?', (cepa_id,))
        self.cx.commit()

    # ---------------------------------------------------------- evaluaciones
    def crear_evaluacion(self, cepa_id, tipo, titulo='', responsables='',
                         procedimiento='', copiar_de=None, heredar=True) -> int:
        """Crea una evaluación.

        Con copiar_de arranca con las respuestas de otra evaluación. Si no, y
        heredar es cierto, arranca con las respuestas que el área tenga
        contestadas: las instalaciones del laboratorio son las mismas para todas
        sus cepas. Quedan como respuestas de esta evaluación, así que se pueden
        modificar o borrar sin tocar las del área.
        """
        if tipo not in TIPOS:
            raise ValueError(f'tipo desconocido: {tipo} (use {" o ".join(TIPOS)})')
        self.cepa(cepa_id)
        ahora = _ahora()
        cur = self.cx.execute(
            'INSERT INTO evaluacion (cepa_id, tipo, titulo, responsables, procedimiento,'
            ' creada, actualizada, revision) VALUES (?,?,?,?,?,?,?,?)',
            (cepa_id, tipo, titulo, responsables, procedimiento, ahora, ahora,
             _revision_en_vigor(tipo)))
        nueva = cur.lastrowid
        self.cx.commit()
        if copiar_de is not None:
            origen = self.evaluacion(copiar_de)
            if origen.tipo != tipo:
                raise ValueError('no se pueden copiar respuestas entre tipos distintos')
            self.guardar_respuestas(nueva, self.respuestas(copiar_de))
        elif heredar:
            del_area = self.respuestas_heredables(cepa_id, tipo)
            if del_area:
                self.guardar_respuestas(nueva, del_area)
        return nueva

    def evaluacion(self, evaluacion_id) -> Evaluacion:
        f = self.cx.execute('SELECT * FROM evaluacion WHERE id = ?',
                            (evaluacion_id,)).fetchone()
        if f is None:
            raise LookupError(f'no existe la evaluación {evaluacion_id}')
        return Evaluacion(**dict(f))

    def evaluaciones(self, cepa_id=None, tipo=None) -> list[Evaluacion]:
        consulta, args = 'SELECT * FROM evaluacion', []
        condiciones = []
        if cepa_id is not None:
            condiciones.append('cepa_id = ?'); args.append(cepa_id)
        if tipo is not None:
            condiciones.append('tipo = ?'); args.append(tipo)
        if condiciones:
            consulta += ' WHERE ' + ' AND '.join(condiciones)
        consulta += ' ORDER BY cepa_id, tipo, creada'
        return [Evaluacion(**dict(f)) for f in self.cx.execute(consulta, args)]

    def actualizar_evaluacion(self, evaluacion_id, **campos):
        permitidos = {'titulo', 'responsables', 'procedimiento', 'estado'}
        desconocidos = set(campos) - permitidos
        if desconocidos:
            raise ValueError(f'campos desconocidos: {sorted(desconocidos)}')
        if not campos:
            return
        asignaciones = ', '.join(f'{c} = ?' for c in campos)
        self.cx.execute(
            f'UPDATE evaluacion SET {asignaciones}, actualizada = ? WHERE id = ?',
            (*campos.values(), _ahora(), evaluacion_id))
        self.cx.commit()

    def borrar_evaluacion(self, evaluacion_id):
        self.cx.execute('DELETE FROM evaluacion WHERE id = ?', (evaluacion_id,))
        self.cx.commit()

    # ------------------------------------------------------------ respuestas
    def guardar_respuestas(self, evaluacion_id, respuestas: dict):
        """Guarda o reemplaza respuestas. Acepta {uuid: valor} o {uuid: Respuesta}.

        Si el valor llega como número desnudo, la marca de «es una estimación»
        que ya tuviera la respuesta se conserva: sólo se cambia cuando viene un
        objeto Respuesta, que es quien sabe de esa marca.
        """
        self.evaluacion(evaluacion_id)
        con_marca, sin_marca = [], []
        for pregunta, r in respuestas.items():
            if isinstance(r, Respuesta):
                con_marca.append((evaluacion_id, pregunta,
                                  revisar_valor(r.valor), int(r.aproximada)))
            else:
                sin_marca.append((evaluacion_id, pregunta, revisar_valor(r), 0))
        if con_marca:
            self.cx.executemany(
                'INSERT INTO respuesta (evaluacion_id, pregunta, valor, aproximada)'
                ' VALUES (?,?,?,?) ON CONFLICT(evaluacion_id, pregunta)'
                ' DO UPDATE SET valor = excluded.valor, aproximada = excluded.aproximada',
                con_marca)
        if sin_marca:
            self.cx.executemany(
                'INSERT INTO respuesta (evaluacion_id, pregunta, valor, aproximada)'
                ' VALUES (?,?,?,?) ON CONFLICT(evaluacion_id, pregunta)'
                ' DO UPDATE SET valor = excluded.valor',
                sin_marca)
        # La revisión se vuelve a sellar al contestar: lo que importa es con
        # cuál se capturaron las respuestas que hay hoy.
        self.cx.execute(
            'UPDATE evaluacion SET actualizada = ?, revision = ? WHERE id = ?',
            (_ahora(), _revision_en_vigor(self.evaluacion(evaluacion_id).tipo),
             evaluacion_id))
        self.cx.commit()

    def borrar_respuesta(self, evaluacion_id, pregunta):
        self.cx.execute('DELETE FROM respuesta WHERE evaluacion_id = ? AND pregunta = ?',
                        (evaluacion_id, pregunta))
        self.cx.commit()

    def respuestas(self, evaluacion_id) -> dict[str, Respuesta]:
        return {f['pregunta']: Respuesta(f['valor'], bool(f['aproximada']))
                for f in self.cx.execute(
                    'SELECT pregunta, valor, aproximada FROM respuesta'
                    ' WHERE evaluacion_id = ?', (evaluacion_id,))}

    def puntajes(self, evaluacion_id) -> dict[str, float]:
        """Las respuestas como las quiere el motor: {uuid: valor}."""
        return {p: r.valor for p, r in self.respuestas(evaluacion_id).items()}

    # -------------------------------------------------------------- historial
    def guardar_version(self, evaluacion_id, autor='', nota='') -> int:
        """Archiva las respuestas actuales como una versión del historial."""
        respuestas = self.respuestas(evaluacion_id)
        cur = self.cx.execute(
            'INSERT INTO version (evaluacion_id, momento, autor, nota) VALUES (?,?,?,?)',
            (evaluacion_id, _ahora(), autor, nota))
        version_id = cur.lastrowid
        self.cx.executemany(
            'INSERT INTO respuesta_version (version_id, pregunta, valor, aproximada)'
            ' VALUES (?,?,?,?)',
            [(version_id, p, r.valor, int(r.aproximada)) for p, r in respuestas.items()])
        self.cx.commit()
        return version_id

    def versiones(self, evaluacion_id) -> list[Version]:
        return [Version(**dict(f)) for f in self.cx.execute(
            'SELECT * FROM version WHERE evaluacion_id = ? ORDER BY momento, id',
            (evaluacion_id,))]

    def respuestas_de_version(self, version_id) -> dict[str, Respuesta]:
        return {f['pregunta']: Respuesta(f['valor'], bool(f['aproximada']))
                for f in self.cx.execute(
                    'SELECT pregunta, valor, aproximada FROM respuesta_version'
                    ' WHERE version_id = ?', (version_id,))}

    def restaurar_version(self, version_id):
        """Deja la evaluación como estaba en esa versión."""
        f = self.cx.execute('SELECT evaluacion_id FROM version WHERE id = ?',
                            (version_id,)).fetchone()
        if f is None:
            raise LookupError(f'no existe la versión {version_id}')
        evaluacion_id = f['evaluacion_id']
        self.cx.execute('DELETE FROM respuesta WHERE evaluacion_id = ?', (evaluacion_id,))
        self.cx.commit()
        self.guardar_respuestas(evaluacion_id, self.respuestas_de_version(version_id))

    # ------------------------------------------------------------------ otros
    def resumen(self) -> list[dict]:
        """Una fila por evaluación, con su cepa y su área. Para la pantalla principal."""
        consulta = """
            SELECT a.id AS area_id, a.nombre AS area,
                   c.id AS cepa_id, c.nombre AS cepa,
                   e.id AS evaluacion_id, e.tipo, e.estado, e.actualizada,
                   (SELECT COUNT(*) FROM respuesta r WHERE r.evaluacion_id = e.id) AS respondidas
            FROM area a
            JOIN cepa c ON c.area_id = a.id
            LEFT JOIN evaluacion e ON e.cepa_id = c.id
            ORDER BY a.nombre, c.nombre, e.tipo
        """
        return [dict(f) for f in self.cx.execute(consulta)]
