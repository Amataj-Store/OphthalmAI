"""
database.py – Hospital Rísquez · OphthalmAI v3.8
Sistema completo de gestión clínica oftalmológica.
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

_BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BASE, "risquez_ophthalm.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        PRAGMA foreign_keys = ON;
        PRAGMA journal_mode = WAL;

        CREATE TABLE IF NOT EXISTS doctores (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre       TEXT NOT NULL UNIQUE,
            especialidad TEXT DEFAULT 'Oftalmología',
            creado_en    TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pacientes (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula           TEXT UNIQUE,
            nombre_completo  TEXT NOT NULL,
            fecha_nacimiento TEXT,
            edad             INTEGER,
            sexo             TEXT,
            telefono         TEXT,
            direccion        TEXT,
            antecedentes     TEXT,
            alergias         TEXT,
            medicamentos_act TEXT,
            doctor_registro  TEXT,
            fecha_registro   TEXT NOT NULL,
            activo           INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS visitas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id     INTEGER NOT NULL,
            doctor_nombre   TEXT NOT NULL,
            numero_visita   INTEGER DEFAULT 1,
            motivo_consulta TEXT,
            diagnostico_ia  TEXT,
            diagnostico_doc TEXT,
            tratamiento     TEXT,
            agudeza_visual  TEXT,
            pio             TEXT,
            tiene_imagen    INTEGER DEFAULT 0,
            fecha_hora      TEXT NOT NULL,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        );

        CREATE TABLE IF NOT EXISTS seguimientos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            visita_id   INTEGER NOT NULL,
            paciente_id INTEGER NOT NULL,
            tipo        TEXT NOT NULL,
            nota        TEXT NOT NULL,
            doctor      TEXT,
            fecha_hora  TEXT NOT NULL,
            FOREIGN KEY (visita_id)   REFERENCES visitas(id),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        );

        CREATE TABLE IF NOT EXISTS interacciones (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            visita_id       INTEGER,
            paciente_id     INTEGER,
            doctor_nombre   TEXT NOT NULL,
            paciente_nombre TEXT NOT NULL,
            pregunta_doctor TEXT NOT NULL,
            respuesta_ia    TEXT NOT NULL,
            tiene_imagen    INTEGER DEFAULT 0,
            fecha_hora      TEXT NOT NULL,
            FOREIGN KEY (visita_id)   REFERENCES visitas(id),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        );
    """)
    conn.commit()
    conn.close()

@contextmanager
def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        yield c
        c.commit()
    except Exception as e:
        c.rollback()
        raise e
    finally:
        c.close()

def registrar_doctor(nombre: str, especialidad: str = "Oftalmología") -> int:
    with _conn() as conn:
        conn.execute("INSERT OR IGNORE INTO doctores (nombre, especialidad, creado_en) VALUES (?,?,?)", (nombre, especialidad, datetime.now().isoformat()))
        row = conn.execute("SELECT id FROM doctores WHERE nombre=?", (nombre,)).fetchone()
    return row["id"] if row else -1

def registrar_paciente(nombre_completo: str, doctor_registro: str, cedula: str = None, fecha_nacimiento: str = None, edad: int = None, sexo: str = None, telefono: str = None, direccion: str = None, antecedentes: str = None, alergias: str = None, medicamentos_act: str = None) -> int:
    with _conn() as conn:
        try:
            conn.execute("""INSERT INTO pacientes (cedula, nombre_completo, fecha_nacimiento, edad, sexo, telefono, direccion, antecedentes, alergias, medicamentos_act, doctor_registro, fecha_registro) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", 
                         (cedula, nombre_completo, fecha_nacimiento, edad, sexo, telefono, direccion, antecedentes, alergias, medicamentos_act, doctor_registro, datetime.now().isoformat()))
            pid = conn.execute("SELECT id FROM pacientes WHERE rowid=last_insert_rowid()").fetchone()["id"]
        except sqlite3.IntegrityError:
            pid = conn.execute("SELECT id FROM pacientes WHERE cedula=?", (cedula,)).fetchone()["id"]
    return pid

def buscar_paciente(termino: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM pacientes WHERE (nombre_completo LIKE ? OR cedula LIKE ?) AND activo=1 ORDER BY nombre_completo", (f"%{termino}%", f"%{termino}%")).fetchall()
    return [dict(r) for r in rows]

def obtener_todos_los_pacientes() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM pacientes WHERE activo=1 ORDER BY nombre_completo").fetchall()
    return [dict(r) for r in rows]

def abrir_visita(paciente_id: int, doctor_nombre: str, motivo_consulta: str = None) -> int:
    with _conn() as conn:
        n = conn.execute("SELECT COUNT(*) as cnt FROM visitas WHERE paciente_id=?", (paciente_id,)).fetchone()["cnt"] + 1
        conn.execute("INSERT INTO visitas (paciente_id, doctor_nombre, numero_visita, motivo_consulta, fecha_hora) VALUES (?,?,?,?,?)", (paciente_id, doctor_nombre, n, motivo_consulta, datetime.now().isoformat()))
        vid = conn.execute("SELECT id FROM visitas WHERE rowid=last_insert_rowid()").fetchone()["id"]
    return vid

def actualizar_visita(visita_id: int, diagnostico_ia: str = None, diagnostico_doc: str = None, tratamiento: str = None, agudeza_visual: str = None, pio: str = None, tiene_imagen: bool = False):
    with _conn() as conn:
        conn.execute("""UPDATE visitas SET diagnostico_ia=COALESCE(?, diagnostico_ia), diagnostico_doc=COALESCE(?, diagnostico_doc), tratamiento=COALESCE(?, tratamiento), agudeza_visual=COALESCE(?, agudeza_visual), pio=COALESCE(?, pio), tiene_imagen=MAX(tiene_imagen, ?) WHERE id=?""", 
                     (diagnostico_ia, diagnostico_doc, tratamiento, agudeza_visual, pio, 1 if tiene_imagen else 0, visita_id))

def obtener_visitas_paciente(paciente_id: int) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM visitas WHERE paciente_id=? ORDER BY fecha_hora DESC", (paciente_id,)).fetchall()
    return [dict(r) for r in rows]

def registrar_seguimiento(visita_id: int, paciente_id: int, tipo: str, nota: str, doctor: str = None) -> int:
    with _conn() as conn:
        conn.execute("INSERT INTO seguimientos (visita_id, paciente_id, tipo, nota, doctor, fecha_hora) VALUES (?,?,?,?,?,?)", (visita_id, paciente_id, tipo, nota, doctor, datetime.now().isoformat()))
        sid = conn.execute("SELECT id FROM seguimientos WHERE rowid=last_insert_rowid()").fetchone()["id"]
    return sid

def registrar_consulta(doctor_nombre: str, paciente_nombre: str, pregunta_doctor: str, respuesta_ia: str, tiene_imagen: bool = False, visita_id: int = None, paciente_id: int = None) -> int:
    with _conn() as conn:
        registrar_doctor(doctor_nombre)
        conn.execute("INSERT INTO interacciones (visita_id, paciente_id, doctor_nombre, paciente_nombre, pregunta_doctor, respuesta_ia, tiene_imagen, fecha_hora) VALUES (?,?,?,?,?,?,?,?)", 
                     (visita_id, paciente_id, doctor_nombre, paciente_nombre, pregunta_doctor, respuesta_ia, 1 if tiene_imagen else 0, datetime.now().isoformat()))
        iid = conn.execute("SELECT id FROM interacciones WHERE rowid=last_insert_rowid()").fetchone()["id"]
    return iid

def stats_generales() -> dict:
    with _conn() as conn:
        stats = {}
        stats["total_pacientes"]     = conn.execute("SELECT COUNT(*) FROM pacientes WHERE activo=1").fetchone()[0]
        stats["total_visitas"]       = conn.execute("SELECT COUNT(*) FROM visitas").fetchone()[0]
        stats["total_interacciones"] = conn.execute("SELECT COUNT(*) FROM interacciones").fetchone()[0]
    return stats
