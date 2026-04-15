"""
database.py – Hospital Rísquez · OphthalmAI v3.0
Sistema completo de gestión clínica oftalmológica.

Tablas:
  doctores    → Personal médico registrado
  pacientes   → Registro completo del paciente (ficha clínica)
  visitas     → Cada consulta del paciente (puede tener N visitas)
  seguimientos → Notas de evolución y avances por visita
  interacciones → Log del chat IA por visita
"""

import sqlite3
from datetime import datetime

DB_PATH = "risquez_ophthalm.db"


# ══════════════════════════════════════════════
# INICIALIZACIÓN DEL ESQUEMA
# ══════════════════════════════════════════════

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        PRAGMA foreign_keys = ON;

        -- ── Personal médico ───────────────────────────
        CREATE TABLE IF NOT EXISTS doctores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL UNIQUE,
            especialidad TEXT DEFAULT 'Oftalmología',
            creado_en   TEXT NOT NULL
        );

        -- ── Ficha del paciente ────────────────────────
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

        -- ── Visitas / Consultas ───────────────────────
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

        -- ── Seguimiento / Evolución ───────────────────
        CREATE TABLE IF NOT EXISTS seguimientos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            visita_id   INTEGER NOT NULL,
            paciente_id INTEGER NOT NULL,
            tipo        TEXT NOT NULL,  -- 'mejoria' | 'sin_cambio' | 'empeoramiento' | 'alta'
            nota        TEXT NOT NULL,
            doctor      TEXT,
            fecha_hora  TEXT NOT NULL,
            FOREIGN KEY (visita_id)   REFERENCES visitas(id),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        );

        -- ── Log del chat IA ───────────────────────────
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


# ══════════════════════════════════════════════
# PACIENTES
# ══════════════════════════════════════════════

def registrar_paciente(
    nombre_completo: str,
    doctor_registro: str,
    cedula: str = None,
    fecha_nacimiento: str = None,
    edad: int = None,
    sexo: str = None,
    telefono: str = None,
    direccion: str = None,
    antecedentes: str = None,
    alergias: str = None,
    medicamentos_act: str = None,
) -> int:
    """Registra un nuevo paciente. Retorna el ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO pacientes
            (cedula, nombre_completo, fecha_nacimiento, edad, sexo,
             telefono, direccion, antecedentes, alergias,
             medicamentos_act, doctor_registro, fecha_registro)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        cedula, nombre_completo, fecha_nacimiento, edad, sexo,
        telefono, direccion, antecedentes, alergias,
        medicamentos_act, doctor_registro, datetime.now().isoformat()
    ))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid


def buscar_paciente(termino: str) -> list[dict]:
    """Busca pacientes por nombre o cédula."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM pacientes
        WHERE nombre_completo LIKE ? OR cedula LIKE ?
        ORDER BY fecha_registro DESC
    """, (f"%{termino}%", f"%{termino}%"))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def obtener_paciente_por_id(pid: int) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM pacientes WHERE id = ?", (pid,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def obtener_todos_los_pacientes() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM pacientes WHERE activo=1 ORDER BY nombre_completo")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ══════════════════════════════════════════════
# VISITAS
# ══════════════════════════════════════════════

def abrir_visita(
    paciente_id: int,
    doctor_nombre: str,
    motivo_consulta: str = None,
) -> int:
    """Abre una nueva visita y calcula el número de visita del paciente."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) FROM visitas WHERE paciente_id = ?", (paciente_id,)
    )
    n = c.fetchone()[0] + 1
    c.execute("""
        INSERT INTO visitas
            (paciente_id, doctor_nombre, numero_visita, motivo_consulta, fecha_hora)
        VALUES (?,?,?,?,?)
    """, (paciente_id, doctor_nombre, n, motivo_consulta, datetime.now().isoformat()))
    vid = c.lastrowid
    conn.commit()
    conn.close()
    return vid


def actualizar_visita(
    visita_id: int,
    diagnostico_ia: str = None,
    diagnostico_doc: str = None,
    tratamiento: str = None,
    agudeza_visual: str = None,
    pio: str = None,
    tiene_imagen: bool = False,
):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE visitas SET
            diagnostico_ia  = COALESCE(?, diagnostico_ia),
            diagnostico_doc = COALESCE(?, diagnostico_doc),
            tratamiento     = COALESCE(?, tratamiento),
            agudeza_visual  = COALESCE(?, agudeza_visual),
            pio             = COALESCE(?, pio),
            tiene_imagen    = MAX(tiene_imagen, ?)
        WHERE id = ?
    """, (diagnostico_ia, diagnostico_doc, tratamiento,
          agudeza_visual, pio, 1 if tiene_imagen else 0, visita_id))
    conn.commit()
    conn.close()


def obtener_visitas_paciente(paciente_id: int) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM visitas
        WHERE paciente_id = ?
        ORDER BY fecha_hora DESC
    """, (paciente_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ══════════════════════════════════════════════
# SEGUIMIENTOS
# ══════════════════════════════════════════════

def registrar_seguimiento(
    visita_id: int,
    paciente_id: int,
    tipo: str,
    nota: str,
    doctor: str = None,
) -> int:
    """
    Registra la evolución del paciente.
    tipo: 'mejoria' | 'sin_cambio' | 'empeoramiento' | 'alta'
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO seguimientos
            (visita_id, paciente_id, tipo, nota, doctor, fecha_hora)
        VALUES (?,?,?,?,?,?)
    """, (visita_id, paciente_id, tipo, nota, doctor, datetime.now().isoformat()))
    sid = c.lastrowid
    conn.commit()
    conn.close()
    return sid


def obtener_seguimientos_paciente(paciente_id: int) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT s.*, v.numero_visita, v.diagnostico_ia
        FROM seguimientos s
        JOIN visitas v ON s.visita_id = v.id
        WHERE s.paciente_id = ?
        ORDER BY s.fecha_hora ASC
    """, (paciente_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ══════════════════════════════════════════════
# INTERACCIONES (chat IA) – compatibilidad
# ══════════════════════════════════════════════

def registrar_consulta(
    doctor_nombre: str,
    paciente_nombre: str,
    pregunta_doctor: str,
    respuesta_ia: str,
    tiene_imagen: bool = False,
    visita_id: int = None,
    paciente_id: int = None,
) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Garantizar que el doctor existe
    c.execute(
        "INSERT OR IGNORE INTO doctores (nombre, creado_en) VALUES (?,?)",
        (doctor_nombre, datetime.now().isoformat())
    )

    c.execute("""
        INSERT INTO interacciones
            (visita_id, paciente_id, doctor_nombre, paciente_nombre,
             pregunta_doctor, respuesta_ia, tiene_imagen, fecha_hora)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        visita_id, paciente_id, doctor_nombre, paciente_nombre,
        pregunta_doctor, respuesta_ia,
        1 if tiene_imagen else 0,
        datetime.now().isoformat()
    ))
    iid = c.lastrowid
    conn.commit()
    conn.close()
    return iid


def obtener_historial_paciente(paciente_nombre: str) -> list[dict]:
    """Compatibilidad con código anterior – busca por nombre."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT * FROM interacciones
        WHERE paciente_nombre = ?
        ORDER BY fecha_hora DESC
    """, (paciente_nombre,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def obtener_todas_las_consultas() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM interacciones ORDER BY fecha_hora DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ══════════════════════════════════════════════
# ESTADÍSTICAS
# ══════════════════════════════════════════════

def stats_generales() -> dict:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    stats = {}
    c.execute("SELECT COUNT(*) FROM pacientes WHERE activo=1")
    stats["total_pacientes"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM visitas")
    stats["total_visitas"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM interacciones")
    stats["total_interacciones"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM seguimientos WHERE tipo='alta'")
    stats["altas"] = c.fetchone()[0]
    conn.close()
    return stats
