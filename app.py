"""
app.py – Hospital Rísquez · OphthalmAI v3.6
Diseño Arena.site — Ojo real con disolución, grid, animaciones HUD, UI Premium
"""

import streamlit as st
import time
import database
import modelo_vision
import base64
import os

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OphthalmAI · Hospital Rísquez",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PARA CARGAR LA IMAGEN LOCAL DEL OJO (SOPORTA PNG/JPG)
# ──────────────────────────────────────────────────────────────────────────────
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# Busca la foto que subiste a GitHub / Carpeta
b64_ojo = get_base64_image("ojo_portada.png")
if not b64_ojo:
    b64_ojo = get_base64_image("ojo_portada.jpg") 

mime_type = "image/jpeg" if b64_ojo.startswith("/9j/") else "image/png"
EYE_SRC = f"data:{mime_type};base64,{b64_ojo}" if b64_ojo else "https://images.unsplash.com/photo-1542282088-fe8426682b8f?auto=format&fit=crop&w=500&q=80"

# ──────────────────────────────────────────────────────────────────────────────
# UTILIDAD: generar resumen
# ──────────────────────────────────────────────────────────────────────────────
def _generar_resumen(doctor: str, paciente: str, mensajes: list) -> str:
    from datetime import datetime
    lineas =[
        "=" * 62,
        "   HOSPITAL RÍSQUEZ · OphthalmAI v3.6",
        "   RESUMEN DE CONSULTA OFTALMOLÓGICA",
        "=" * 62,
        f"Fecha:    {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Doctor:   {doctor}",
        f"Paciente: {paciente}",
        "-" * 62,
        "HISTORIAL DE LA CONSULTA:",
        "-" * 62,
    ]
    for msg in mensajes:
        rol = f"Dr. {doctor}" if msg["role"] == "user" else "OphthalmAI"
        lineas.append(f"\n[{rol}]\n{msg['content']}\n")
    lineas +=[
        "=" * 62,
        "Reporte generado por OphthalmAI v3.6 · Hospital Rísquez",
        "Apoyo diagnóstico — criterio clínico del médico tratante.",
        "=" * 62,
    ]
    return "\n".join(lineas)

# ──────────────────────────────────────────────────────────────────────────────
# CSS — Pixel-perfect del diseño Arena.site
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

:root {
    --void:      #020812;
    --navy-mid:  #080f20;
    --panel:     rgba(8,20,45,0.85);
    --teal:      #00e5d8;
    --teal-dim:  #00857d;
    --cyan:      #00cfff;
    --amber:     #ffb547;
    --green-ok:  #00e59b;
    --red-alert: #ff3d5a;
    --text-main: #ddeeff;
    --text-muted:#4a7090;
    --glass-brd: rgba(0,229,216,0.14);
    --scan-line: rgba(0,229,216,0.025);
}

/* ── Fondo: scanlines + gradientes + GRID ──────────────────── */
html, body,[data-testid="stAppViewContainer"] {
    background-color: var(--void) !important;
    background-image:
        linear-gradient(rgba(0,229,216,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,216,0.03) 1px, transparent 1px),
        repeating-linear-gradient(0deg, transparent, transparent 2px, var(--scan-line) 2px, var(--scan-line) 4px),
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,229,216,0.07) 0%, transparent 65%),
        radial-gradient(ellipse 40% 30% at 90% 90%, rgba(0,207,255,0.04) 0%, transparent 55%);
    background-size: 40px 40px, 40px 40px, 100% 100%, 100% 100%, 100% 100%;
    color: var(--text-main) !important;
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--glass-brd) !important;
    background-image: linear-gradient(180deg, rgba(0,229,216,0.04) 0%, transparent 30%) !important;
}[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* ── Logo sidebar ──────────────────────── */
.sidebar-logo {
    text-align: center;
    padding: 22px 16px 16px;
    border-bottom: 1px solid var(--glass-brd);
    margin-bottom: 4px;
    position: relative;
}
.sidebar-logo::before {
    content: '';
    position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 60%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--teal), transparent);
}
.logo-title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.5rem; color: var(--text-main); letter-spacing: 1px; }
.logo-title span { color: var(--teal); }
.logo-sub { font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-muted); letter-spacing: 2.5px; text-transform: uppercase; margin-top: 3px; }

/* Ojo sidebar — circular con máscara de disolución */
.eye-sidebar-wrap {
    display: flex; justify-content: center; align-items: center;
    margin-bottom: 10px; position: relative;
}
.eye-sidebar-img {
    width: 120px; height: 120px;
    object-fit: cover;
    border-radius: 50%;
    -webkit-mask-image: radial-gradient(ellipse 55% 55% at center, black 20%, rgba(0,0,0,0.8) 42%, rgba(0,0,0,0.3) 60%, transparent 75%);
    mask-image: radial-gradient(ellipse 55% 55% at center, black 20%, rgba(0,0,0,0.8) 42%, rgba(0,0,0,0.3) 60%, transparent 75%);
    filter: drop-shadow(0 0 14px rgba(0,229,216,0.6)) drop-shadow(0 0 30px rgba(0,229,216,0.25));
    animation: eye-pulse 3.5s ease-in-out infinite;
}
.eye-sidebar-ring {
    position: absolute; border-radius: 50%;
    border: 1px solid rgba(0,229,216,0.3);
    animation: radar-ring 2.8s ease-out infinite;
    pointer-events: none;
    inset: -12px;
}
.eye-sidebar-ring2 {
    position: absolute; border-radius: 50%;
    border: 1px solid rgba(0,207,255,0.18);
    animation: radar-ring 2.8s ease-out 1.4s infinite;
    pointer-events: none;
    inset: -12px;
}

/* Model badge */
.model-badge {
    display: flex; align-items: center; gap: 7px;
    background: rgba(0,229,216,0.05); border: 1px solid rgba(0,229,216,0.18);
    border-radius: 6px; padding: 6px 12px;
    font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--teal);
    letter-spacing: 1px; text-transform: uppercase; margin: 8px 0 2px;
}
.mb-dot { width: 6px; height: 6px; background: var(--green-ok); border-radius: 50%; box-shadow: 0 0 6px var(--green-ok); flex-shrink: 0; animation: blink 1.8s ease-in-out infinite; }

/* Section labels */
.s-section {
    font-family: 'Space Mono', monospace; font-size: 0.58rem; font-weight: 700;
    color: var(--teal); text-transform: uppercase; letter-spacing: 2px;
    padding: 12px 0 5px; border-top: 1px solid var(--glass-brd); margin-top: 8px;
}
.s-section::before { content: '// '; opacity: 0.5; }
.s-info {
    background: rgba(0,229,216,0.03); border: 1px solid var(--glass-brd);
    border-radius: 8px; padding: 10px 13px; font-size: 0.8rem; color: var(--text-muted); line-height: 1.65; margin-top: 6px;
}
.s-info strong { color: var(--text-main); font-weight: 500; }

/* Session card */
.session-card {
    background: linear-gradient(135deg, rgba(0,229,216,0.07), rgba(0,207,255,0.03));
    border: 1px solid var(--glass-brd); border-radius: 10px;
    padding: 12px 14px 12px 18px; margin-top: 8px; position: relative; overflow: hidden;
}
.session-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--teal), var(--cyan));
}
.sc-label { font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; }
.sc-value { font-size: 0.88rem; color: var(--text-main); font-weight: 500; margin-top: 1px; }

/* Inputs */
[data-testid="stSidebar"] label, .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label {
    font-family: 'Space Mono', monospace !important; font-size: 0.62rem !important;
    color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 1.2px;
}
[data-testid="stSidebar"] input, .stTextInput input, .stNumberInput input {
    background: rgba(5,13,26,0.9) !important; color: var(--teal) !important;
    border: 1px solid var(--glass-brd) !important; border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.82rem !important;
}[data-testid="stSidebar"] input:focus, .stTextInput input:focus {
    border-color: var(--teal) !important; box-shadow: 0 0 0 2px rgba(0,229,216,0.12) !important;
}
input::placeholder, textarea::placeholder { color: #1e3550 !important; }
textarea {
    background: rgba(5,13,26,0.9) !important; color: var(--text-main) !important;
    border: 1px solid var(--glass-brd) !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Buttons */
.stButton > button {
    background: transparent !important; color: var(--teal) !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.8rem !important;
    border: 1px solid var(--teal) !important; border-radius: 8px !important;
    padding: 10px 20px !important; width: 100% !important;
    letter-spacing: 1.5px; text-transform: uppercase; transition: all 0.22s ease !important;
}
.stButton > button:hover {
    color: var(--void) !important; background: var(--teal) !important;
    box-shadow: 0 0 22px rgba(0,229,216,0.5) !important; transform: translateY(-1px) !important;
}

/* ── HUD Header ─────────────────────────────────────────── */
.hud-header {
    display: flex; align-items: center; gap: 20px;
    padding: 18px 0 14px; border-bottom: 1px solid var(--glass-brd);
    margin-bottom: 16px; position: relative;
}
.hud-header::after {
    content: ''; position: absolute; bottom: -1px; left: 0;
    width: 140px; height: 1px; background: linear-gradient(90deg, var(--teal), transparent);
}
/* Eye en header — pequeño, circular, dissolve */
.hud-eye-box {
    width: 62px; height: 62px;
    border: 1px solid var(--glass-brd); border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, rgba(0,229,216,0.08), transparent);
    position: relative; flex-shrink: 0; overflow: hidden;
    animation: eye-pulse 3.5s ease-in-out infinite;
}
.hud-eye-box::before, .hud-eye-box::after {
    content: ''; position: absolute; border-radius: 14px;
    border: 1px solid rgba(0,229,216,0.3);
    animation: radar-ring 2.5s ease-out infinite;
    inset: 0;
}
.hud-eye-box::after { animation-delay: 1.25s; }
.hud-eye-img {
    width: 70px; height: 70px; object-fit: cover; border-radius: 10px;
    -webkit-mask-image: radial-gradient(ellipse 55% 55% at center, black 20%, transparent 75%);
    mask-image: radial-gradient(ellipse 55% 55% at center, black 20%, transparent 75%);
}
.hud-title h1 {
    font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
    font-size: 2rem !important; color: var(--text-main) !important;
    margin: 0 !important; letter-spacing: -0.5px; line-height: 1;
}
.hud-title h1 em { font-style: normal; color: var(--teal); text-shadow: 0 0 20px rgba(0,229,216,0.5); }
.hud-subtitle { font-family: 'Space Mono', monospace; font-size: 0.6rem; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase; margin-top: 6px; }
.hud-meta { margin-left: auto; text-align: right; font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-muted); line-height: 1.9; }
.hud-meta .ver { color: var(--teal); font-weight: 700; }

/* Status strip */
.status-strip {
    display: flex; align-items: center; gap: 16px; margin-bottom: 14px;
    padding: 8px 16px; background: var(--panel);
    border: 1px solid var(--glass-brd); border-radius: 8px;
    font-family: 'Space Mono', monospace; font-size: 0.62rem; color: var(--text-muted); flex-wrap: wrap;
}
.indicator { display: flex; align-items: center; gap: 6px; }
.s-dot { width: 7px; height: 7px; border-radius: 50%; }
.dot-active { background: var(--green-ok); box-shadow: 0 0 6px var(--green-ok); animation: blink 1.4s ease-in-out infinite; }
.dot-inactive { background: var(--text-muted); }
.dot-img { background: var(--amber); box-shadow: 0 0 6px var(--amber); }

/* ── Welcome screen — estilo Arena exacto ───────────────── */
.welcome-screen {
    text-align: center; padding: 60px 40px;
    border: 1px solid var(--glass-brd); border-radius: 20px; margin-top: 20px;
    background: linear-gradient(135deg, rgba(0,229,216,0.03) 0%, transparent 50%), var(--panel);
    position: relative; overflow: hidden;
}
/* Grid interior */
.welcome-screen::before {
    content: ''; position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(0,229,216,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,216,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    border-radius: 20px; z-index: 0; pointer-events: none;
}
/* Fondo cónico giratorio */
.ws-conic {
    position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: conic-gradient(transparent 0deg, rgba(0,229,216,0.025) 60deg, transparent 120deg);
    animation: rotate-bg 14s linear infinite; pointer-events: none; z-index: 0;
}
/* Esquinas HUD */
.ws-corner { position: absolute; width: 30px; height: 30px; z-index: 2; }
.ws-tl { top: 16px; left: 16px; border-top: 1px solid rgba(0,229,216,0.4); border-left: 1px solid rgba(0,229,216,0.4); }
.ws-tr { top: 16px; right: 16px; border-top: 1px solid rgba(0,229,216,0.4); border-right: 1px solid rgba(0,229,216,0.4); }
.ws-bl { bottom: 16px; left: 16px; border-bottom: 1px solid rgba(0,229,216,0.4); border-left: 1px solid rgba(0,229,216,0.4); }
.ws-br { bottom: 16px; right: 16px; border-bottom: 1px solid rgba(0,229,216,0.4); border-right: 1px solid rgba(0,229,216,0.4); }

/* Línea de scan sobre el ojo */
.scan-line-anim {
    position: absolute; left: 10%; right: 10%; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0,229,216,0.8), transparent);
    animation: scan-down 2.4s linear infinite;
    border-radius: 1px; pointer-events: none; z-index: 5;
    box-shadow: 0 2px 10px rgba(0,229,216,0.6);
}

/* Ojo hero — GRANDE, circular, dissolve */
.eye-hero-wrap {
    position: relative; z-index: 1;
    display: flex; justify-content: center; margin-bottom: 28px;
    animation: float-y 4s ease-in-out infinite;
}
.eye-hero-container { position: relative; width: 240px; height: 240px; }
.eye-hero-ring1 {
    position: absolute; inset: -20px; border-radius: 50%;
    border: 1px solid rgba(0,229,216,0.15);
    animation: radar-ring 3s ease-out infinite;
}
.eye-hero-ring2 {
    position: absolute; inset: -20px; border-radius: 50%;
    border: 1px solid rgba(0,207,255,0.1);
    animation: radar-ring 3s ease-out 1.5s infinite;
}
.eye-hero-ring3 {
    position: absolute; inset: -40px; border-radius: 50%;
    border: 1px solid rgba(0,229,216,0.07);
    animation: radar-ring 3.5s ease-out 0.75s infinite;
}
.eye-hero-img {
    width: 240px; height: 240px; object-fit: cover; border-radius: 50%; display: block;
    -webkit-mask-image: radial-gradient(ellipse 52% 52% at center, black 10%, rgba(0,0,0,0.8) 35%, rgba(0,0,0,0.3) 55%, transparent 72%);
    mask-image: radial-gradient(ellipse 52% 52% at center, black 10%, rgba(0,0,0,0.8) 35%, rgba(0,0,0,0.3) 55%, transparent 72%);
    filter: drop-shadow(0 0 30px rgba(0,229,216,0.6)) drop-shadow(0 0 60px rgba(0,229,216,0.25));
    animation: eye-pulse 3.5s ease-in-out infinite;
    position: relative; z-index: 1;
}
.welcome-screen h2 {
    font-family: 'Syne', sans-serif !important; font-weight: 800; font-size: 1.8rem;
    color: var(--text-main) !important; margin: 0 0 8px !important; position: relative; z-index: 1;
}
.welcome-screen p { color: var(--text-muted); font-size: 0.92rem; max-width: 460px; margin: 0 auto; line-height: 1.75; position: relative; z-index: 1; }
.w-tag {
    display: inline-block; margin-top: 20px;
    font-family: 'Space Mono', monospace; font-size: 0.62rem; color: var(--teal);
    border: 1px solid var(--glass-brd); border-radius: 4px; padding: 4px 14px;
    letter-spacing: 1.5px; position: relative; z-index: 1;
}

/* ── Chat ───────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: var(--panel) !important; border: 1px solid var(--glass-brd) !important;
    border-radius: 12px !important; padding: 16px 20px !important;
    margin-bottom: 10px !important; backdrop-filter: blur(12px); position: relative;
    animation: fadeInUp 0.3s ease forwards;
}
[data-testid="stChatMessage"]::before {
    content: ''; position: absolute; top: 0; left: 16px;
    width: 40px; height: 1px; background: linear-gradient(90deg, var(--teal), transparent);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    border-color: rgba(255,181,71,0.2) !important; background: rgba(255,181,71,0.04) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])::before {
    background: linear-gradient(90deg, var(--amber), transparent);
}
[data-testid="stChatInput"] textarea {
    background: rgba(5,13,26,0.95) !important; color: var(--text-main) !important;
    border: 1px solid var(--glass-brd) !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--teal) !important; box-shadow: 0 0 0 1px rgba(0,229,216,0.18) !important;
}
div[data-testid="column"] .stButton>button {
    font-family:'DM Sans',sans-serif!important;font-size:0.72rem!important;font-weight:500!important;padding:6px 4px!important;letter-spacing:0.3px!important;text-transform:none!important;border-color:rgba(0,229,216,0.25)!important;color:var(--text-muted)!important;border-radius:20px!important;transition:all 0.18s ease!important;white-space:nowrap;
}
div[data-testid="column"] .stButton>button:hover {
    border-color:var(--teal)!important;color:var(--teal)!important;background:rgba(0,229,216,0.06)!important;box-shadow:0 0 10px rgba(0,229,216,0.2)!important;transform:translateY(-1px)!important;
}

/* Images & uploader */
[data-testid="stImage"] img { border-radius: 10px !important; border: 1px solid var(--glass-brd) !important; }[data-testid="stFileUploader"] { background: rgba(5,13,26,0.8) !important; border: 1px dashed var(--glass-brd) !important; border-radius: 10px !important; }

/* Expander */
[data-testid="stExpander"] { background: var(--panel) !important; border: 1px solid var(--glass-brd) !important; border-radius: 10px !important; margin-bottom: 8px !important; }[data-testid="stExpander"] summary { font-family: 'Space Mono', monospace !important; font-size: 0.65rem !important; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 1.5px; }

/* Metrics */
[data-testid="stMetric"] { background: var(--panel) !important; border: 1px solid var(--glass-brd) !important; border-radius: 10px !important; padding: 12px 16px !important; }
[data-testid="stMetricLabel"] { font-family: 'Space Mono', monospace !important; font-size: 0.6rem !important; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 1px; }[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; font-size: 1.5rem !important; color: var(--teal) !important; }

/* Patient card (Historial) */
.patient-card{background:linear-gradient(135deg,rgba(0,229,216,0.05),rgba(0,207,255,0.02));border:1px solid var(--glass-brd);border-radius:12px;padding:16px 18px;margin:8px 0;}
.patient-card .pc-name{font-family:'Syne',sans-serif;font-weight:700;font-size:1.05rem;color:var(--teal);margin-bottom:6px;}
.patient-card .pc-row{display:flex;gap:20px;flex-wrap:wrap;font-family:'Space Mono',monospace;font-size:0.65rem;color:var(--text-muted);margin-bottom:3px;}
.patient-card .pc-row span{color:var(--text-main);}
.visit-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(255,181,71,0.08);border:1px solid rgba(255,181,71,0.3);border-radius:6px;padding:4px 10px;font-family:'Space Mono',monospace;font-size:0.62rem;color:var(--amber);letter-spacing:1px;margin:8px 0;}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb { background: var(--teal-dim); border-radius: 2px; }[data-testid="stAlert"] { border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-size: 0.76rem !important; }
hr { border-color: var(--glass-brd) !important; }
[data-testid="stDownloadButton"] button { background: rgba(0,229,216,0.07) !important; color: var(--teal) !important; border: 1px dashed rgba(0,229,216,0.4) !important; border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-size: 0.68rem !important; letter-spacing: 1px; text-transform: uppercase; }
[data-testid="stDownloadButton"] button:hover { background: rgba(0,229,216,0.14) !important; border-style: solid !important; }

/* ── Animaciones ─────────── */
@keyframes eye-pulse {
    0%,100% { filter: drop-shadow(0 0 12px rgba(0,229,216,0.6)) drop-shadow(0 0 28px rgba(0,229,216,0.3)); }
    50%     { filter: drop-shadow(0 0 24px rgba(0,229,216,0.9)) drop-shadow(0 0 52px rgba(0,229,216,0.5)); }
}
@keyframes radar-ring {
    0%   { opacity: 0.6; transform: scale(1); }
    100% { opacity: 0;   transform: scale(1.9); }
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
@keyframes rotate-bg { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
@keyframes scan-down {
    0%   { top: -4px; opacity: 0.7; }
    100% { top: 100%; opacity: 0; }
}
@keyframes float-y {
    0%,100% { transform: translateY(0px); }
    50%     { transform: translateY(-10px); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes hud-flicker {
    0%,100%{opacity:1;} 92%{opacity:1;} 93%{opacity:0.85;} 94%{opacity:1;} 96%{opacity:0.9;} 97%{opacity:1;}
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# INIT 
# ──────────────────────────────────────────────────────────────────────────────
database.init_db()

defaults = {
    "messages":[], "session_active": False, "doctor_name": "",
    "patient_name": "", "patient_id": None, "visita_id": None,
    "total_consultas": 0, "view": "chat", "paciente_data": {},
    "session_idx": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo + ojo sidebar con dissolve
    st.markdown(f"""
    <div class="sidebar-logo">
        <div class="eye-sidebar-wrap">
            <div class="eye-sidebar-ring"></div>
            <div class="eye-sidebar-ring2"></div>
            <img src="{EYE_SRC}" class="eye-sidebar-img">
        </div>
        <div class="logo-title">Ophthalm<span>AI</span></div>
        <div class="logo-sub">Hospital Rísquez · Caracas</div>
    </div>
    <div class="model-badge">
        <div class="mb-dot"></div>
        EfficientNetB0 · Nube AI
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="s-section">Navegación</div>', unsafe_allow_html=True)
    nc = st.columns(2)
    if nc[0].button("💬 Consulta"):
        st.session_state.view = "chat"; st.rerun()
    if nc[1].button("📋 Registro"):
        st.session_state.view = "registro"; st.rerun()
    nc2 = st.columns(2)
    if nc2[0].button("📂 Historial"):
        st.session_state.view = "historial"; st.rerun()
    if nc2[1].button("📊 Dashboard"):
        st.session_state.view = "dashboard"; st.rerun()

    st.markdown('<div class="s-section">Datos de la Consulta</div>', unsafe_allow_html=True)
    doctor_input  = st.text_input("Nombre del Doctor",  value=st.session_state.doctor_name,  disabled=st.session_state.session_active)
    patient_input = st.text_input("Paciente",           value=st.session_state.patient_name, disabled=st.session_state.session_active)

    if not st.session_state.session_active:
        if st.button("▶  INICIAR SESIÓN"):
            if doctor_input.strip() and patient_input.strip():
                st.session_state.doctor_name    = doctor_input.strip()
                st.session_state.patient_name   = patient_input.strip()
                
                # Buscamos paciente en DB
                resultados = database.buscar_paciente(patient_input.strip())
                if resultados:
                    p = resultados[0]
                    st.session_state.patient_id = p["id"]
                    st.session_state.paciente_data = p
                    visitas_prev = database.obtener_visitas_paciente(p["id"])
                    vid = database.abrir_visita(p["id"], doctor_input.strip(), "Consulta OphthalmAI")
                    st.session_state.visita_id = vid
                    
                    msg = (f"Sistema en línea. Bienvenido, **Dr. {doctor_input.strip()}**.\n\n"
                           f"Paciente identificado: **{p['nombre_completo']}** (Cédula: `{p.get('cedula','')}`).\n\n"
                           f"Especialidad activa: **Úlceras Corneales** y **Uveítis**.\n"
                           "¿Desea ingresar síntomas, subir fotografías, o solicitar un protocolo de tratamiento?")
                else:
                    st.session_state.patient_id = None
                    st.session_state.paciente_data = {}
                    st.session_state.visita_id = None
                    msg = (f"Bienvenido, **Dr. {doctor_input.strip()}**.\n\n"
                           f"No encontré a **{patient_input.strip()}** en el sistema. Puede registrarlo en **📋 Registro**.\n\n"
                           "¿Cómo puedo asistirle hoy?")

                st.session_state.session_active = True
                st.session_state.messages       =[]
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.rerun()
            else:
                st.error("Complete los campos.")
    else:
        if st.button("⏹  FINALIZAR CONSULTA"):
            for k, v in defaults.items():
                if k != "session_idx":
                    st.session_state[k] = v
            st.session_state.session_idx += 1
            st.rerun()

    if st.session_state.session_active:
        p = st.session_state.paciente_data
        st.markdown(f"""
        <div class="session-card">
            <div class="sc-label">Doctor</div>
            <div class="sc-value">{st.session_state.doctor_name}</div>
            <div class="sc-label" style="margin-top:6px;">Paciente</div>
            <div class="sc-value">{p.get("nombre_completo", st.session_state.patient_name)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="s-section">Imágenes · Segmento Anterior</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Fotografías", type=["jpg","jpeg","png"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"up_{st.session_state.session_idx}",
        )
        if uploaded_files:
            n_f  = len(uploaded_files)
            cols = st.columns(min(n_f, 2))
            for i, f in enumerate(uploaded_files):
                cols[i % 2].image(f, use_container_width=True)
            st.markdown(
                f'<div style="font-family:Space Mono,monospace;font-size:0.6rem;'
                f'color:var(--teal);text-align:center;margin-top:5px;letter-spacing:1px;">'
                f'✓ {n_f} IMAGEN(ES) · CNN ACTIVA</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="s-section">Especialidades (Tesis)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="s-info">
        ⚠️ <strong>Úlcera Corneal / Queratitis</strong><br>
        🔵 <strong>Uveítis Anterior</strong><br>
        ✅ <strong>Ojo Sano / Control</strong><br>
        <span style="color:#1e3d55;font-size:0.58rem;">*El sistema solo diagnostica estas patologías.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:16px;padding:10px 12px;border-top:1px solid rgba(0,229,216,0.07);
    font-family:Space Mono,monospace;font-size:0.55rem;color:#1e3550;text-align:center;line-height:1.9;">
        EfficientNetB0 · Transfer Learning<br>
        Nube AI · Privacidad total<br>
        <span style="color:#254060;">© Tesis UCV · Hospital Rísquez</span>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN — Header HUD con ojo real
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hud-header" style="animation:hud-flicker 8s ease-in-out infinite;">
    <div class="hud-eye-box">
        <img src="{EYE_SRC}" class="hud-eye-img">
    </div>
    <div class="hud-title">
        <h1>Ophthalm<em>AI</em></h1>
        <div class="hud-subtitle">Úlceras Corneales & Uveítis · Hospital Rísquez · Tesis UCV</div>
    </div>
    <div class="hud-meta">
        <div class="ver">v3.6-CLOUD</div>
        <div>EfficientNetB0</div>
        <div>Multi-imagen · NLP</div>
        <div>SQLite · $0 API</div>
    </div>
</div>
""", unsafe_allow_html=True)

view = st.session_state.view

# ──────────────────────────────────────────────────────────────────────────────
# VISTA: CHAT (Y Portada)
# ──────────────────────────────────────────────────────────────────────────────
if view == "chat":

    if not st.session_state.session_active:
        # PANTALLA DE INICIO BLUE BOX ARENA
        st.markdown(f"""
        <div class="welcome-screen">
            <div class="ws-conic"></div>
            <div class="ws-corner ws-tl"></div>
            <div class="ws-corner ws-tr"></div>
            <div class="ws-corner ws-bl"></div>
            <div class="ws-corner ws-br"></div>

            <div class="eye-hero-wrap">
                <div class="eye-hero-container">
                    <div class="eye-hero-ring1"></div>
                    <div class="eye-hero-ring2"></div>
                    <div class="eye-hero-ring3"></div>
                    <img src="{EYE_SRC}" class="eye-hero-img">
                    <div class="scan-line-anim" style="top:-4px;"></div>
                </div>
            </div>

            <h2>OphthalmAI · en espera</h2>
            <p>
                Sistema diagnóstico asistido por Red Neuronal Convolucional (EfficientNetB0).
                Especializado en <strong style="color:var(--teal);">Úlceras Corneales</strong>
                y <strong style="color:var(--teal);">Uveítis</strong>.
            </p>
            <div class="w-tag">// INICIE SESIÓN EN EL PANEL LATERAL PARA COMENZAR //</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # PANTALLA DE CHAT (Status Strip)
        p = st.session_state.paciente_data
        ced_h = f'· CÉD:<span style="color:var(--text-main);"> {p["cedula"]}</span>' if p.get("cedula") else ""
        n_imgs = len(uploaded_files) if "uploaded_files" in locals() and uploaded_files else 0
        img_h = (f'<div class="indicator"><div class="s-dot dot-img"></div>{n_imgs} IMG</div>'
                 if n_imgs else '<div class="indicator"><div class="s-dot dot-inactive"></div>SIN IMG</div>')
        
        st.markdown(f"""
        <div class="status-strip">
            <div class="indicator"><div class="s-dot dot-active"></div>SESIÓN ACTIVA</div>
            <div>PAC:<span style="color:var(--text-main);"> {p.get("nombre_completo",st.session_state.patient_name).upper()}</span> {ced_h}</div>
            <div>DR:<span style="color:var(--text-main);"> {st.session_state.doctor_name.upper()}</span></div>
            {img_h}
            <div style="margin-left:auto;">CNN:<span style="color:var(--green-ok);"> ONLINE</span></div>
        </div>
        """, unsafe_allow_html=True)

        if "uploaded_files" not in dir(): uploaded_files =[]

        if st.session_state.patient_id:
            visitas_prev = database.obtener_visitas_paciente(st.session_state.patient_id)
            if len(visitas_prev) > 1:
                with st.expander(f"📂 {len(visitas_prev)-1} visita(s) previa(s)", expanded=False):
                    for v in visitas_prev[1:]:
                        st.markdown(f"""
                        <div style="font-family:Space Mono,monospace;font-size:0.63rem;border-bottom:1px solid var(--glass-brd);padding:8px 0;line-height:1.7;">
                            <span style="color:var(--teal);">Visita #{v['numero_visita']} · {v['fecha_hora'][:16]}</span>
                            &nbsp;·&nbsp; Dr. {v['doctor_nombre']}<br>
                            <span style="color:var(--text-muted);">Diag. IA:</span> {(v.get('diagnostico_ia') or '—')[:130]}<br>
                            <span style="color:var(--text-muted);">Tratamiento:</span> {(v.get('tratamiento') or '—')[:100]}
                        </div>
                        """, unsafe_allow_html=True)

        if st.session_state.visita_id and st.session_state.patient_id:
            with st.expander("📈 Registrar evolución del paciente", expanded=False):
                sc1, sc2 = st.columns([2, 1])
                nota_seg = sc1.text_area("Nota de evolución", placeholder="Describa el avance clínico...", height=70, label_visibility="collapsed")
                tipo_seg = sc2.selectbox("Estado",["mejoria", "sin_cambio", "empeoramiento", "alta"], label_visibility="collapsed")
                if st.button("💾  GUARDAR EVOLUCIÓN"):
                    if nota_seg.strip():
                        database.registrar_seguimiento(
                            visita_id=st.session_state.visita_id, paciente_id=st.session_state.patient_id,
                            tipo=tipo_seg, nota=nota_seg.strip(), doctor=st.session_state.doctor_name,
                        )
                        st.success("✓ Evolución guardada correctamente.")
                    else:
                        st.warning("Escriba una nota antes de guardar.")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if st.session_state.total_consultas > 0:
            try:
                resumen_data = _generar_resumen(st.session_state.doctor_name, st.session_state.patient_name, st.session_state.messages).encode("utf-8")
                fname = f"consulta_{st.session_state.patient_name.replace(' ','_')}_{time.strftime('%Y%m%d_%H%M')}.txt"
                st.download_button(label="⬇ Exportar resumen (.txt)", data=resumen_data, file_name=fname, mime="text/plain", key="export_btn")
            except Exception:
                pass

        st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.58rem;color:var(--text-muted);letter-spacing:1px;margin-bottom:6px;">// SÍNTOMAS RÁPIDOS</div>', unsafe_allow_html=True)
        cc = st.columns(4)
        chips =[
            ("🔴 Ojo rojo",     "El paciente presenta ojo rojo intenso con secreción ocular"),
            ("💧 Secreción",    "El paciente tiene secreción ocular purulenta y costra matutina"),
            ("⚡ Fotofobia",    "El paciente refiere fotofobia intensa, lagrimeo y dolor ciliar"),
            ("🌀 Dolor ocular", "El paciente describe dolor ocular profundo, miosis y visión borrosa"),
        ]
        chip_prompt = None
        for i, (label, texto) in enumerate(chips):
            if cc[i].button(label, key=f"chip_{i}"):
                chip_prompt = texto

        user_input = st.chat_input(f"[Dr. {st.session_state.doctor_name}] Pida un protocolo o analice fotos...")
        prompt = chip_prompt or user_input

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            lista_imgs = [f.getvalue() for f in uploaded_files] if uploaded_files else[]

            with st.chat_message("assistant"):
                ph = st.empty()
                ph.markdown('<span style="color:var(--teal);font-family:Space Mono,monospace;font-size:0.7rem;">// Procesando con EfficientNetB0...</span>', unsafe_allow_html=True)
                time.sleep(0.25)
                try:
                    respuesta_ia = modelo_vision.analizar_imagen_y_sintomas(lista_imagenes=lista_imgs, texto_doctor=prompt)
                except Exception as e:
                    respuesta_ia = f"⚠️ Error en módulo CNN: `{e}`"

                full_response = ""
                words = respuesta_ia.split()
                for i, word in enumerate(words):
                    full_response += word + " "
                    if i % 5 == 0 or i == len(words) - 1:
                        ph.markdown(full_response + "▌")
                        time.sleep(0.018)
                ph.markdown(full_response.strip())

            st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})
            st.session_state.total_consultas += 1

            if st.session_state.visita_id:
                try:
                    database.actualizar_visita(visita_id=st.session_state.visita_id, diagnostico_ia=full_response.strip()[:600], tiene_imagen=bool(lista_imgs))
                except Exception:
                    pass
            try:
                database.registrar_consulta(
                    doctor_nombre=st.session_state.doctor_name, paciente_nombre=st.session_state.patient_name,
                    pregunta_doctor=prompt, respuesta_ia=full_response.strip(), tiene_imagen=bool(lista_imgs),
                    visita_id=st.session_state.visita_id, paciente_id=st.session_state.patient_id,
                )
            except Exception:
                pass


# ────────────────────────────────────────────────────────────────────────
# VISTAS RESTANTES (Registro, Historial, Dashboard)
# ────────────────────────────────────────────────────────────────────────
elif view == "registro":
    st.markdown("### 📋 Registro de Nuevo Paciente")
    st.markdown('<hr>', unsafe_allow_html=True)
    with st.form("form_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre_completo = c1.text_input("Nombre Completo *", placeholder="Juan Carlos Pérez")
        cedula          = c2.text_input("Cédula", placeholder="V-12345678")
        c3, c4, c5 = st.columns(3)
        edad      = c3.number_input("Edad", 0, 120, 0, step=1)
        sexo      = c4.selectbox("Sexo",["", "Masculino", "Femenino", "Otro"])
        fecha_nac = c5.text_input("Fecha de Nac.", placeholder="DD/MM/AAAA")
        c6, c7    = st.columns(2)
        telefono  = c6.text_input("Teléfono", placeholder="0414-1234567")
        direccion = c7.text_input("Dirección",  placeholder="Calle, Ciudad")
        antec     = st.text_area("Antecedentes Oftalmológicos y Médicos", height=75)
        c8, c9    = st.columns(2)
        alergias  = c8.text_input("Alergias", placeholder="Penicilina, látex...")
        medics    = c9.text_input("Medicamentos Actuales", placeholder="Metformina 500mg...")
        doc_reg   = st.text_input("Doctor que Registra *", value=st.session_state.doctor_name)

        if st.form_submit_button("💾  REGISTRAR PACIENTE"):
            if nombre_completo.strip() and doc_reg.strip():
                try:
                    pid = database.registrar_paciente(
                        nombre_completo=nombre_completo.strip(), doctor_registro=doc_reg.strip(),
                        cedula=cedula.strip() or None, fecha_nacimiento=fecha_nac.strip() or None,
                        edad=int(edad) if edad else None, sexo=sexo or None,
                        telefono=telefono.strip() or None, direccion=direccion.strip() or None,
                        antecedentes=antec.strip() or None, alergias=alergias.strip() or None,
                        medicamentos_act=medics.strip() or None,
                    )
                    st.success(f"✓ **{nombre_completo}** registrado · ID #{pid}")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Los campos con * son obligatorios.")

elif view == "historial":
    st.markdown("### 📂 Historial de Pacientes")
    st.markdown('<hr>', unsafe_allow_html=True)
    busqueda  = st.text_input("Buscar por nombre o cédula", placeholder="Escriba para buscar...")
    pacientes = database.buscar_paciente(busqueda) if busqueda else database.obtener_todos_los_pacientes()

    if not pacientes:
        st.info("No se encontraron pacientes.")
    else:
        for p in pacientes:
            lbl = f"👤  {p['nombre_completo']}"
            if p.get("cedula"): lbl += f"  ·  {p['cedula']}"
            lbl += f"  ·  Reg: {p['fecha_registro'][:10]}"
            with st.expander(lbl, expanded=False):
                st.markdown(f"""
                <div class="patient-card">
                    <div class="pc-name">{p['nombre_completo']}</div>
                    <div class="pc-row">
                        <div>CÉD: <span>{p.get('cedula','—')}</span></div>
                        <div>EDAD: <span>{p.get('edad','—')}</span></div>
                        <div>SEXO: <span>{p.get('sexo','—')}</span></div>
                        <div>TEL: <span>{p.get('telefono','—')}</span></div>
                    </div>
                    <div class="pc-row"><div>DIRECCIÓN: <span>{p.get("direccion","—")}</span></div></div>
                    <div class="pc-row"><div>ANTECEDENTES: <span>{p.get("antecedentes","—")}</span></div></div>
                    <div class="pc-row"><div>ALERGIAS: <span>{p.get("alergias","—")}</span></div></div>
                    <div class="pc-row"><div>MEDICAMENTOS: <span>{p.get("medicamentos_act","—")}</span></div></div>
                </div>
                """, unsafe_allow_html=True)

                try:
                    ficha_txt = database.exportar_ficha_texto(p["id"])
                    st.download_button(
                        label="⬇  Descargar expediente (.txt)",
                        data=ficha_txt.encode("utf-8"),
                        file_name=f"expediente_{p['nombre_completo'].replace(' ','_')}.txt",
                        mime="text/plain", key=f"dl_{p['id']}"
                    )
                except Exception:
                    pass

                visitas = database.obtener_visitas_paciente(p["id"])
                if visitas:
                    st.markdown(f'<div class="visit-badge">🗂 {len(visitas)} VISITA(S)</div>', unsafe_allow_html=True)
                    for v in visitas:
                        st.markdown(f"""
                        <div style="font-family:Space Mono,monospace;font-size:0.62rem;
                        border:1px solid var(--glass-brd);border-radius:8px;padding:10px 14px;
                        margin:5px 0;background:rgba(0,229,216,0.03);line-height:1.7;">
                            <span style="color:var(--teal);">▸ Visita #{v['numero_visita']} · {v['fecha_hora'][:16]}</span>
                            &nbsp;·&nbsp; Dr. {v['doctor_nombre']}<br>
                            <span style="color:var(--text-muted);">Diag. IA:</span> {(v.get('diagnostico_ia') or '—')[:150]}<br>
                            <span style="color:var(--text-muted);">Tratamiento:</span> {(v.get('tratamiento') or '—')[:120]}
                        </div>
                        """, unsafe_allow_html=True)

                segs = database.obtener_seguimientos_paciente(p["id"])
                if segs:
                    st.markdown("**Evolución clínica:**")
                    cmap = {"mejoria":"var(--green-ok)","sin_cambio":"var(--amber)","empeoramiento":"var(--red-alert)","alta":"var(--cyan)"}
                    imap = {"mejoria":"✅","sin_cambio":"🔁","empeoramiento":"⚠️","alta":"🏁"}
                    for s in segs:
                        color = cmap.get(s["tipo"],"var(--text-muted)")
                        icon  = imap.get(s["tipo"],"🔵")
                        st.markdown(f"""
                        <div style="font-family:Space Mono,monospace;font-size:0.62rem;
                        border-left:3px solid {color};padding:6px 12px;margin:4px 0;
                        background:rgba(0,0,0,0.2);border-radius:0 6px 6px 0;line-height:1.6;">
                            {icon} <span style="color:{color};">{s['tipo'].upper()}</span>
                            &nbsp;·&nbsp; {s['fecha_hora'][:16]}
                            &nbsp;·&nbsp; <span style="color:var(--text-muted);">V.#{s.get('numero_visita','?')}</span><br>
                            <span style="color:var(--text-main);">{s['nota']}</span>
                        </div>
                        """, unsafe_allow_html=True)

elif view == "dashboard":
    st.markdown("### 📊 Dashboard del Sistema")
    st.markdown('<hr>', unsafe_allow_html=True)
    stats = database.stats_generales()
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Pacientes",        stats["total_pacientes"])
    m2.metric("Visitas",          stats["total_visitas"])
    m3.metric("Interacciones IA", stats["total_interacciones"])
    m4.metric("Altas médicas",    stats["altas"])
    m5.metric("Con imagen",       stats["con_imagen"])
