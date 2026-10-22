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

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

VERSION_ESQUEMA = 1
TIPOS = ('bioseguridad', 'bioproteccion')

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
    actualizada   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS respuesta (
    evaluacion_id INTEGER NOT NULL REFERENCES evaluacion(id) ON DELETE CASCADE,
    pregunta      TEXT NOT NULL,
    valor         REAL NOT NULL,
    aproximada    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (evaluacion_id, pregunta)
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


class Almacen:
    """El archivo de datos del laboratorio."""

    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self.cx = sqlite3.connect(self.ruta)
        self.cx.row_factory = sqlite3.Row
        self.cx.execute('PRAGMA foreign_keys = ON')
        self.cx.executescript(ESQUEMA)
        self.cx.execute('INSERT OR IGNORE INTO meta (clave, valor) VALUES (?, ?)',
                        ('version_esquema', str(VERSION_ESQUEMA)))
        self.cx.commit()
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
        cur = self.cx.execute(
            'INSERT INTO area (nombre, responsable, notas, creada) VALUES (?,?,?,?)',
            (nombre.strip(), responsable, notas, _ahora()))
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

    def borrar_area(self, area_id):
        """Borra el área con sus cepas y evaluaciones."""
        self.cx.execute('DELETE FROM area WHERE id = ?', (area_id,))
        self.cx.commit()

    # ---------------------------------------------------------------- cepas
    def crear_cepa(self, area_id, nombre, agente='', notas='') -> int:
        self.area(area_id)   # falla pronto si el área no existe
        cur = self.cx.execute(
            'INSERT INTO cepa (area_id, nombre, agente, notas, creada) VALUES (?,?,?,?,?)',
            (area_id, nombre.strip(), agente, notas, _ahora()))
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

    def borrar_cepa(self, cepa_id):
        self.cx.execute('DELETE FROM cepa WHERE id = ?', (cepa_id,))
        self.cx.commit()

    # ---------------------------------------------------------- evaluaciones
    def crear_evaluacion(self, cepa_id, tipo, titulo='', responsables='',
                         procedimiento='', copiar_de=None) -> int:
        """Crea una evaluación; con copiar_de arranca con las respuestas de otra."""
        if tipo not in TIPOS:
            raise ValueError(f'tipo desconocido: {tipo} (use {" o ".join(TIPOS)})')
        self.cepa(cepa_id)
        ahora = _ahora()
        cur = self.cx.execute(
            'INSERT INTO evaluacion (cepa_id, tipo, titulo, responsables, procedimiento,'
            ' creada, actualizada) VALUES (?,?,?,?,?,?,?)',
            (cepa_id, tipo, titulo, responsables, procedimiento, ahora, ahora))
        nueva = cur.lastrowid
        self.cx.commit()
        if copiar_de is not None:
            origen = self.evaluacion(copiar_de)
            if origen.tipo != tipo:
                raise ValueError('no se pueden copiar respuestas entre tipos distintos')
            self.guardar_respuestas(nueva, self.respuestas(copiar_de))
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
        """Guarda o reemplaza respuestas. Acepta {uuid: valor} o {uuid: Respuesta}."""
        self.evaluacion(evaluacion_id)
        filas = []
        for pregunta, r in respuestas.items():
            if isinstance(r, Respuesta):
                filas.append((evaluacion_id, pregunta, float(r.valor), int(r.aproximada)))
            else:
                filas.append((evaluacion_id, pregunta, float(r), 0))
        self.cx.executemany(
            'INSERT INTO respuesta (evaluacion_id, pregunta, valor, aproximada)'
            ' VALUES (?,?,?,?) ON CONFLICT(evaluacion_id, pregunta)'
            ' DO UPDATE SET valor = excluded.valor, aproximada = excluded.aproximada',
            filas)
        self.cx.execute('UPDATE evaluacion SET actualizada = ? WHERE id = ?',
                        (_ahora(), evaluacion_id))
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
