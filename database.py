"""
database.py – Hospital Rísquez · OphthalmAI v3.1
Sistema completo de gestión clínica oftalmológica.

NOTA STREAMLIT CLOUD: El archivo SQLite vive en el filesystem efímero de la nube.
Los datos persisten entre reruns de la sesión pero se resetean al redesplegar la app.
Para producción real, migrar a PostgreSQL usando st.secrets + psycopg2.

Tablas:
  doctores      → Personal médico registrado
  pacientes     → Registro completo del paciente (ficha clínica)
  visitas       → Cada consulta del paciente (puede tener N visitas)
  seguimientos  → Notas de evolución y avances por visita
  interacciones → Log del chat IA por visita
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager # NUEVO: Para manejo seguro de conexiones

# Compatible con Streamlit Cloud y entorno local
_BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BASE, "risquez_ophthalm.db")


# ══════════════════════════════════════════════
# INICIALIZACIÓN DEL ESQUEMA
# ══════════════════════════════════════════════

def init_db():
    """Crea las tablas si no existen. Seguro para llamar en cada arranque."""
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


# ══════════════════════════════════════════════
# CONEXIÓN SEGURA (CONTEXT MANAGER)
# ══════════════════════════════════════════════
@contextmanager
def _conn():
    """Devuelve una conexión segura con row_factory. Se cierra automáticamente."""
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        yield c
        c.commit()  # Guarda los cambios si todo salió bien
    except Exception as e:
        c.rollback() # Revierte si algo falló
        raise e
    finally:
        c.close()    # SIEMPRE se cierra, evitando "Database is locked"


# ══════════════════════════════════════════════
# DOCTORES
# ══════════════════════════════════════════════

def registrar_doctor(nombre: str, especialidad: str = "Oftalmología") -> int:
    with _conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO doctores (nombre, especialidad, creado_en) VALUES (?,?,?)",
            (nombre, especialidad, datetime.now().isoformat())
        )
        row = conn.execute("SELECT id FROM doctores WHERE nombre=?", (nombre,)).fetchone()
    return row["id"] if row else -1


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
    with _conn() as conn:
        try:
            conn.execute("""
                INSERT INTO pacientes
                    (cedula, nombre_completo, fecha_nacimiento, edad, sexo,
                     telefono, direccion, antecedentes, alergias,
                     medicamentos_act, doctor_registro, fecha_registro)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (cedula, nombre_completo, fecha_nacimiento, edad, sexo,
                  telefono, direccion, antecedentes, alergias,
                  medicamentos_act, doctor_registro, datetime.now().isoformat()))
            pid = conn.execute("SELECT id FROM pacientes WHERE rowid=last_insert_rowid()").fetchone()["id"]
        except sqlite3.IntegrityError:
            # Cédula duplicada → devolver el ID existente
            pid = conn.execute("SELECT id FROM pacientes WHERE cedula=?", (cedula,)).fetchone()["id"]
    return pid


def buscar_paciente(termino: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("""
            SELECT * FROM pacientes
            WHERE (nombre_completo LIKE ? OR cedula LIKE ?) AND activo=1
            ORDER BY nombre_completo
        """, (f"%{termino}%", f"%{termino}%")).fetchall()
    return [dict(r) for r in rows]


def obtener_paciente_por_id(pid: int) -> dict | None:
    with _conn() as conn:
        row = conn.execute("SELECT * FROM pacientes WHERE id=?", (pid,)).fetchone()
    return dict(row) if row else None


def obtener_todos_los_pacientes() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM pacientes WHERE activo=1 ORDER BY nombre_completo").fetchall()
    return [dict(r) for r in rows]


def actualizar_paciente(pid: int, **kwargs) -> bool:
    allowed = {"cedula","nombre_completo","fecha_nacimiento","edad","sexo",
               "telefono","direccion","antecedentes","alergias","medicamentos_act"}
    campos = {k: v for k, v in kwargs.items() if k in allowed}
    if not campos:
        return False
    sets = ", ".join(f"{k}=?" for k in campos)
    vals = list(campos.values()) + [pid]
    with _conn() as conn:
        conn.execute(f"UPDATE pacientes SET {sets} WHERE id=?", vals)
    return True


# ══════════════════════════════════════════════
# VISITAS
# ══════════════════════════════════════════════

def abrir_visita(paciente_id: int, doctor_nombre: str, motivo_consulta: str = None) -> int:
    with _conn() as conn:
        n = conn.execute("SELECT COUNT(*) as cnt FROM visitas WHERE paciente_id=?", (paciente_id,)).fetchone()["cnt"] + 1
        conn.execute("""
            INSERT INTO visitas (paciente_id, doctor_nombre, numero_visita, motivo_consulta, fecha_hora)
            VALUES (?,?,?,?,?)
        """, (paciente_id, doctor_nombre, n, motivo_consulta, datetime.now().isoformat()))
        vid = conn.execute("SELECT id FROM visitas WHERE rowid=last_insert_rowid()").fetchone()["id"]
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
    with _conn() as conn:
        conn.execute("""
            UPDATE visitas SET
                diagnostico_ia  = COALESCE(?, diagnostico_ia),
                diagnostico_doc = COALESCE(?, diagnostico_doc),
                tratamiento     = COALESCE(?, tratamiento),
                agudeza_visual  = COALESCE(?, agudeza_visual),
                pio             = COALESCE(?, pio),
                tiene_imagen    = MAX(tiene_imagen, ?)
            WHERE id=?
        """, (diagnostico_ia, diagnostico_doc, tratamiento,
              agudeza_visual, pio, 1 if tiene_imagen else 0, visita_id))


def obtener_visitas_paciente(paciente_id: int) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM visitas WHERE paciente_id=? ORDER BY fecha_hora DESC", (paciente_id,)).fetchall()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════
# SEGUIMIENTOS
# ══════════════════════════════════════════════

def registrar_seguimiento(visita_id: int, paciente_id: int, tipo: str, nota: str, doctor: str = None) -> int:
    with _conn() as conn:
        conn.execute("""
            INSERT INTO seguimientos (visita_id, paciente_id, tipo, nota, doctor, fecha_hora)
            VALUES (?,?,?,?,?,?)
        """, (visita_id, paciente_id, tipo, nota, doctor, datetime.now().isoformat()))
        sid = conn.execute("SELECT id FROM seguimientos WHERE rowid=last_insert_rowid()").fetchone()["id"]
    return sid


def obtener_seguimientos_paciente(paciente_id: int) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("""
            SELECT s.*, v.numero_visita, v.diagnostico_ia
            FROM seguimientos s
            JOIN visitas v ON s.visita_id = v.id
            WHERE s.paciente_id=?
            ORDER BY s.fecha_hora ASC
        """, (paciente_id,)).fetchall()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════
# INTERACCIONES (chat IA)
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
    with _conn() as conn:
        registrar_doctor(doctor_nombre) # Asegura que el doctor exista
        conn.execute("""
            INSERT INTO interacciones
                (visita_id, paciente_id, doctor_nombre, paciente_nombre,
                 pregunta_doctor, respuesta_ia, tiene_imagen, fecha_hora)
            VALUES (?,?,?,?,?,?,?,?)
        """, (visita_id, paciente_id, doctor_nombre, paciente_nombre,
              pregunta_doctor, respuesta_ia,
              1 if tiene_imagen else 0,
              datetime.now().isoformat()))
        iid = conn.execute("SELECT id FROM interacciones WHERE rowid=last_insert_rowid()").fetchone()["id"]
    return iid


def obtener_historial_paciente(paciente_nombre: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM interacciones WHERE paciente_nombre=? ORDER BY fecha_hora DESC", (paciente_nombre,)).fetchall()
    return [dict(r) for r in rows]


def obtener_todas_las_consultas(limite: int = 50) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM interacciones ORDER BY fecha_hora DESC LIMIT ?", (limite,)).fetchall()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════
# EXPORTACIÓN
# ══════════════════════════════════════════════

def exportar_ficha_texto(paciente_id: int) -> str:
    p = obtener_paciente_por_id(paciente_id)
    if not p: return "Paciente no encontrado."
    visitas = obtener_visitas_paciente(paciente_id)
    segs    = obtener_seguimientos_paciente(paciente_id)

    lineas = [
        "=" * 62, "   HOSPITAL RÍSQUEZ · OphthalmAI", "   EXPEDIENTE CLÍNICO OFTALMOLÓGICO", "=" * 62,
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", "-" * 62,
        f"Paciente:    {p['nombre_completo']}", f"Cédula:      {p.get('cedula') or '—'}",
        f"Edad:        {p.get('edad') or '—'}  |  Sexo: {p.get('sexo') or '—'}",
        f"Teléfono:    {p.get('telefono') or '—'}", f"Dirección:   {p.get('direccion') or '—'}",
        f"Antecedentes:{p.get('antecedentes') or '—'}", f"Alergias:    {p.get('alergias') or '—'}",
        f"Medicamentos:{p.get('medicamentos_act') or '—'}",
        f"Registrado por: {p.get('doctor_registro') or '—'}  el {p['fecha_registro'][:10]}",
        "=" * 62, f"VISITAS ({len(visitas)} en total):", "-" * 62,
    ]
    for v in reversed(visitas):
        lineas += [
            f"\nVisita #{v['numero_visita']} — {v['fecha_hora'][:16]} — Dr. {v['doctor_nombre']}",
            f"  Motivo:      {v.get('motivo_consulta') or '—'}",
            f"  Diag. IA:    {(v.get('diagnostico_ia') or '—')[:200]}",
            f"  Diag. Doc:   {v.get('diagnostico_doc') or '—'}",
            f"  Tratamiento: {v.get('tratamiento') or '—'}",
            f"  AV:          {v.get('agudeza_visual') or '—'}  |  PIO: {v.get('pio') or '—'}",
        ]
    if segs:
        lineas += ["\n" + "=" * 62, f"SEGUIMIENTO CLÍNICO ({len(segs)} registros):", "-" * 62]
        for s in segs:
            lineas.append(f"  [{s['fecha_hora'][:16]}] Visita #{s.get('numero_visita','?')} — {s['tipo'].upper()} — {s['nota']}")
    lineas += ["\n" + "=" * 62, "Este documento es un apoyo diagnóstico generado por IA.", "El criterio clínico definitivo corresponde al médico tratante.", "=" * 62]
    return "\n".join(lineas)


# ══════════════════════════════════════════════
# ESTADÍSTICAS
# ══════════════════════════════════════════════

def stats_generales() -> dict:
    with _conn() as conn:
        stats = {}
        stats["total_pacientes"]     = conn.execute("SELECT COUNT(*) FROM pacientes WHERE activo=1").fetchone()[0]
        stats["total_visitas"]       = conn.execute("SELECT COUNT(*) FROM visitas").fetchone()[0]
        stats["total_interacciones"] = conn.execute("SELECT COUNT(*) FROM interacciones").fetchone()[0]
        stats["altas"]               = conn.execute("SELECT COUNT(*) FROM seguimientos WHERE tipo='alta'").fetchone()[0]
        stats["con_imagen"]          = conn.execute("SELECT COUNT(*) FROM visitas WHERE tiene_imagen=1").fetchone()[0]
    return stats
