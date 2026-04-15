"""
app.py – Hospital Rísquez · OphthalmAI v3.1
Sistema de Apoyo Diagnóstico Oftalmológico
"""

import streamlit as st
import time
import database
import modelo_vision

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
# OJO SVG — FUNCIÓN ÚNICA (un solo diseño, múltiples tamaños)
# ──────────────────────────────────────────────────────────────────────────────
def eye_svg(width="120px", pulse_dur="3s", radar_dur="2.6s"):
    """Retorna el HTML del ojo SVG hiperrealista. Mismo diseño en cualquier tamaño."""
    uid = width.replace("px", "")  # IDs únicos por instancia
    return f"""<svg viewBox="0 0 200 110" xmlns="http://www.w3.org/2000/svg"
    style="width:{width};height:auto;display:block;margin:0 auto;
           filter:drop-shadow(0 0 10px rgba(0,229,216,0.55))
                  drop-shadow(0 0 28px rgba(0,229,216,0.22));">
  <defs>
    <radialGradient id="iris{uid}" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#001a18"/>
      <stop offset="25%"  stop-color="#003530"/>
      <stop offset="55%"  stop-color="#006e68"/>
      <stop offset="82%"  stop-color="#00b8af"/>
      <stop offset="100%" stop-color="#00e5d8"/>
    </radialGradient>
    <radialGradient id="pupil{uid}" cx="38%" cy="35%" r="55%">
      <stop offset="0%"   stop-color="#0d1f28"/>
      <stop offset="100%" stop-color="#010608"/>
    </radialGradient>
    <radialGradient id="sclera{uid}" cx="50%" cy="44%" r="58%">
      <stop offset="0%"   stop-color="#eaf6f7"/>
      <stop offset="55%"  stop-color="#c0e4e8"/>
      <stop offset="100%" stop-color="#82bfc4"/>
    </radialGradient>
    <filter id="iglow{uid}" x="-35%" y="-35%" width="170%" height="170%">
      <feGaussianBlur stdDeviation="3.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="eglow{uid}" x="-10%" y="-25%" width="120%" height="150%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="eshape{uid}">
      <path d="M8,55 Q100,4 192,55 Q100,106 8,55 Z"/>
    </clipPath>
  </defs>

  <!-- Aura difuminada exterior -->
  <ellipse cx="100" cy="55" rx="96" ry="52" fill="none"
    stroke="#00e5d8" stroke-width="0.4" opacity="0.12" filter="url(#eglow{uid})"/>

  <!-- Esclerótica con gradiente natural -->
  <path d="M8,55 Q100,4 192,55 Q100,106 8,55 Z"
    fill="url(#sclera{uid})" clip-path="url(#eshape{uid})"/>

  <!-- Venas sutiles -->
  <g clip-path="url(#eshape{uid})" opacity="0.15">
    <path d="M25,55 Q55,47 78,54" fill="none" stroke="#c0392b" stroke-width="0.6"/>
    <path d="M30,59 Q50,53 68,57" fill="none" stroke="#c0392b" stroke-width="0.4"/>
    <path d="M152,53 Q168,49 180,52" fill="none" stroke="#c0392b" stroke-width="0.4"/>
    <path d="M148,57 Q165,54 178,56" fill="none" stroke="#c0392b" stroke-width="0.3"/>
  </g>

  <!-- Iris con gradiente radial profundo -->
  <circle cx="100" cy="55" r="33"
    fill="url(#iris{uid})" filter="url(#iglow{uid})"
    clip-path="url(#eshape{uid})"/>

  <!-- Fibras radiales del iris -->
  <g clip-path="url(#eshape{uid})" opacity="0.2">
    <line x1="100" y1="22" x2="100" y2="88" stroke="#00e5d8" stroke-width="0.7"/>
    <line x1="67"  y1="31" x2="133" y2="79" stroke="#00e5d8" stroke-width="0.6"/>
    <line x1="67"  y1="79" x2="133" y2="31" stroke="#00e5d8" stroke-width="0.6"/>
    <line x1="54"  y1="55" x2="146" y2="55" stroke="#00e5d8" stroke-width="0.6"/>
    <line x1="70"  y1="37" x2="130" y2="73" stroke="#00cfff" stroke-width="0.45"/>
    <line x1="70"  y1="73" x2="130" y2="37" stroke="#00cfff" stroke-width="0.45"/>
    <line x1="60"  y1="43" x2="140" y2="67" stroke="#00e5d8" stroke-width="0.4"/>
    <line x1="60"  y1="67" x2="140" y2="43" stroke="#00e5d8" stroke-width="0.4"/>
    <circle cx="100" cy="55" r="26" fill="none" stroke="#00cfff" stroke-width="0.6"/>
    <circle cx="100" cy="55" r="19" fill="none" stroke="#00857d" stroke-width="0.7"/>
    <circle cx="100" cy="55" r="33" fill="none" stroke="#00e5d8" stroke-width="0.9" opacity="0.45"/>
  </g>

  <!-- Pupila -->
  <circle cx="100" cy="55" r="13.5"
    fill="url(#pupil{uid})" clip-path="url(#eshape{uid})"/>

  <!-- Anillo de dilatación animado -->
  <circle cx="100" cy="55" r="13.5" fill="none"
    stroke="#00e5d8" stroke-width="1.1" opacity="0.75"
    clip-path="url(#eshape{uid})">
    <animate attributeName="r"       values="13.5;18;13.5" dur="{pulse_dur}" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.75;0.08;0.75" dur="{pulse_dur}" repeatCount="indefinite"/>
  </circle>

  <!-- Reflejos corneales -->
  <ellipse cx="87" cy="43" rx="4.8" ry="2.6" fill="white" opacity="0.78"
    transform="rotate(-28,87,43)" clip-path="url(#eshape{uid})"/>
  <ellipse cx="93" cy="41" rx="1.6" ry="0.9" fill="white" opacity="0.45"
    clip-path="url(#eshape{uid})"/>
  <circle  cx="113" cy="63" r="1.3" fill="white" opacity="0.22"
    clip-path="url(#eshape{uid})"/>

  <!-- Contorno párpados -->
  <path d="M8,55 Q100,4 192,55"  fill="none" stroke="#002820" stroke-width="2.2" opacity="0.6"/>
  <path d="M8,55 Q100,106 192,55" fill="none" stroke="#002820" stroke-width="2.2" opacity="0.6"/>

  <!-- Borde teal con glow -->
  <path d="M8,55 Q100,4 192,55 Q100,106 8,55 Z" fill="none"
    stroke="#00e5d8" stroke-width="1.3" opacity="0.55"
    filter="url(#eglow{uid})"/>

  <!-- Anillos de radar desde iris hacia afuera -->
  <ellipse cx="100" cy="55" rx="33" ry="33" fill="none"
    stroke="#00e5d8" stroke-width="1.8" opacity="0" clip-path="url(#eshape{uid})">
    <animate attributeName="rx"      values="33;96" dur="{radar_dur}" repeatCount="indefinite"/>
    <animate attributeName="ry"      values="33;52" dur="{radar_dur}" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.85;0" dur="{radar_dur}" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="100" cy="55" rx="33" ry="33" fill="none"
    stroke="#00cfff" stroke-width="1.2" opacity="0" clip-path="url(#eshape{uid})">
    <animate attributeName="rx"      values="33;96" dur="{radar_dur}" begin="1.3s" repeatCount="indefinite"/>
    <animate attributeName="ry"      values="33;52" dur="{radar_dur}" begin="1.3s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.55;0" dur="{radar_dur}" begin="1.3s" repeatCount="indefinite"/>
  </ellipse>
</svg>"""


# ──────────────────────────────────────────────────────────────────────────────
# CSS
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
    --scan-line: rgba(0,229,216,0.022);
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--void) !important;
    background-image:
        repeating-linear-gradient(0deg,transparent,transparent 2px,var(--scan-line) 2px,var(--scan-line) 4px),
        radial-gradient(ellipse 80% 50% at 50% -10%,rgba(0,229,216,0.07) 0%,transparent 65%),
        radial-gradient(ellipse 40% 30% at 90% 90%,rgba(0,207,255,0.04) 0%,transparent 55%);
    color: var(--text-main) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--glass-brd) !important;
    background-image: linear-gradient(180deg,rgba(0,229,216,0.04) 0%,transparent 30%) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* Logo */
.sidebar-logo {
    text-align:center; padding:18px 16px 12px;
    border-bottom:1px solid var(--glass-brd); margin-bottom:4px; position:relative;
}
.sidebar-logo::before {
    content:''; position:absolute; top:0; left:50%; transform:translateX(-50%);
    width:60%; height:1px; background:linear-gradient(90deg,transparent,var(--teal),transparent);
}
.logo-title { font-family:'Syne',sans-serif; font-weight:800; font-size:1.2rem; color:var(--text-main); letter-spacing:1px; margin-top:6px; }
.logo-title span { color:var(--teal); }
.logo-sub { font-family:'Space Mono',monospace; font-size:0.58rem; color:var(--text-muted); letter-spacing:2.5px; text-transform:uppercase; margin-top:2px; }

/* Model badge */
.model-badge {
    display:flex; align-items:center; gap:7px;
    background:rgba(0,229,216,0.05); border:1px solid rgba(0,229,216,0.18);
    border-radius:6px; padding:6px 12px;
    font-family:'Space Mono',monospace; font-size:0.58rem; color:var(--teal);
    letter-spacing:1px; text-transform:uppercase; margin:8px 0 2px;
}
.mb-dot { width:6px; height:6px; background:var(--green-ok); border-radius:50%; box-shadow:0 0 6px var(--green-ok); flex-shrink:0; animation:blink 1.8s ease-in-out infinite; }

/* Sections */
.s-section {
    font-family:'Space Mono',monospace; font-size:0.58rem; font-weight:700;
    color:var(--teal); text-transform:uppercase; letter-spacing:2px;
    padding:12px 0 5px; border-top:1px solid var(--glass-brd); margin-top:8px;
}
.s-section::before { content:'// '; opacity:0.5; }
.s-info {
    background:rgba(0,229,216,0.03); border:1px solid var(--glass-brd);
    border-radius:8px; padding:10px 13px;
    font-size:0.8rem; color:var(--text-muted); line-height:1.65; margin-top:6px;
}
.s-info strong { color:var(--text-main); font-weight:500; }

/* Session card */
.session-card {
    background:linear-gradient(135deg,rgba(0,229,216,0.07),rgba(0,207,255,0.03));
    border:1px solid var(--glass-brd); border-radius:10px;
    padding:12px 14px 12px 18px; margin-top:8px; position:relative; overflow:hidden;
}
.session-card::before {
    content:''; position:absolute; top:0; left:0; width:3px; height:100%;
    background:linear-gradient(180deg,var(--teal),var(--cyan));
}
.sc-label { font-family:'Space Mono',monospace; font-size:0.58rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:1.5px; }
.sc-value { font-size:0.88rem; color:var(--text-main); font-weight:500; margin-top:1px; }

/* Patient card */
.patient-card {
    background:linear-gradient(135deg,rgba(0,229,216,0.05),rgba(0,207,255,0.02));
    border:1px solid var(--glass-brd); border-radius:12px; padding:16px 18px; margin:8px 0;
}
.patient-card .pc-name { font-family:'Syne',sans-serif; font-weight:700; font-size:1.05rem; color:var(--teal); margin-bottom:6px; }
.patient-card .pc-row { display:flex; gap:20px; flex-wrap:wrap; font-family:'Space Mono',monospace; font-size:0.65rem; color:var(--text-muted); margin-bottom:3px; }
.patient-card .pc-row span { color:var(--text-main); }
.visit-badge {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(255,181,71,0.08); border:1px solid rgba(255,181,71,0.3);
    border-radius:6px; padding:4px 10px;
    font-family:'Space Mono',monospace; font-size:0.62rem; color:var(--amber); letter-spacing:1px; margin:8px 0;
}

/* Inputs */
[data-testid="stSidebar"] label, .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label {
    font-family:'Space Mono',monospace !important; font-size:0.62rem !important;
    color:var(--text-muted) !important; text-transform:uppercase; letter-spacing:1.2px;
}
[data-testid="stSidebar"] input, .stTextInput input {
    background:rgba(5,13,26,0.9) !important; color:var(--teal) !important;
    border:1px solid var(--glass-brd) !important; border-radius:8px !important;
    font-family:'Space Mono',monospace !important; font-size:0.82rem !important;
}
[data-testid="stSidebar"] input:focus {
    border-color:var(--teal) !important; box-shadow:0 0 0 2px rgba(0,229,216,0.12) !important;
}
input::placeholder, textarea::placeholder { color:#1e3550 !important; }
.stSelectbox > div > div {
    background:rgba(5,13,26,0.9) !important; border:1px solid var(--glass-brd) !important;
    color:var(--teal) !important; border-radius:8px !important;
}
textarea { background:rgba(5,13,26,0.9) !important; color:var(--text-main) !important; border:1px solid var(--glass-brd) !important; border-radius:8px !important; font-family:'DM Sans',sans-serif !important; }

/* Buttons — main */
.stButton > button {
    background:transparent !important; color:var(--teal) !important;
    font-family:'Syne',sans-serif !important; font-weight:700 !important; font-size:0.8rem !important;
    border:1px solid var(--teal) !important; border-radius:8px !important;
    padding:10px 20px !important; width:100% !important;
    letter-spacing:1.5px; text-transform:uppercase; transition:all 0.22s ease !important;
}
.stButton > button:hover {
    color:var(--void) !important; background:var(--teal) !important;
    box-shadow:0 0 22px rgba(0,229,216,0.5) !important; transform:translateY(-1px) !important;
}
/* Chip buttons */
div[data-testid="column"] .stButton > button {
    font-family:'DM Sans',sans-serif !important; font-size:0.72rem !important;
    font-weight:500 !important; padding:6px 4px !important;
    letter-spacing:0.3px !important; text-transform:none !important;
    border-color:rgba(0,229,216,0.25) !important; color:var(--text-muted) !important;
    border-radius:20px !important;
}
div[data-testid="column"] .stButton > button:hover {
    border-color:var(--teal) !important; color:var(--teal) !important;
    background:rgba(0,229,216,0.06) !important;
}

/* HUD Header */
.hud-header {
    display:flex; align-items:center; gap:20px;
    padding:16px 0 12px; border-bottom:1px solid var(--glass-brd);
    margin-bottom:14px; position:relative;
}
.hud-header::after {
    content:''; position:absolute; bottom:-1px; left:0;
    width:140px; height:1px; background:linear-gradient(90deg,var(--teal),transparent);
}
.hud-title h1 {
    font-family:'Syne',sans-serif !important; font-weight:800 !important;
    font-size:1.9rem !important; color:var(--text-main) !important;
    margin:0 !important; letter-spacing:-0.5px; line-height:1;
}
.hud-title h1 em { font-style:normal; color:var(--teal); text-shadow:0 0 20px rgba(0,229,216,0.5); }
.hud-subtitle { font-family:'Space Mono',monospace; font-size:0.6rem; color:var(--text-muted); letter-spacing:2px; text-transform:uppercase; margin-top:6px; }
.hud-meta { margin-left:auto; text-align:right; font-family:'Space Mono',monospace; font-size:0.58rem; color:var(--text-muted); line-height:1.9; }
.hud-meta .ver { color:var(--teal); font-weight:700; }

/* Status strip */
.status-strip {
    display:flex; align-items:center; gap:16px; margin-bottom:12px;
    padding:8px 16px; background:var(--panel);
    border:1px solid var(--glass-brd); border-radius:8px;
    font-family:'Space Mono',monospace; font-size:0.62rem; color:var(--text-muted); flex-wrap:wrap;
}
.indicator { display:flex; align-items:center; gap:6px; }
.s-dot { width:7px; height:7px; border-radius:50%; }
.dot-active   { background:var(--green-ok); box-shadow:0 0 6px var(--green-ok); animation:blink 1.4s ease-in-out infinite; }
.dot-inactive { background:var(--text-muted); }
.dot-img      { background:var(--amber); box-shadow:0 0 6px var(--amber); }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* Chat */
[data-testid="stChatMessage"] {
    background:var(--panel) !important; border:1px solid var(--glass-brd) !important;
    border-radius:12px !important; padding:16px 20px !important;
    margin-bottom:10px !important; backdrop-filter:blur(12px); position:relative;
}
[data-testid="stChatMessage"]::before {
    content:''; position:absolute; top:0; left:16px;
    width:40px; height:1px; background:linear-gradient(90deg,var(--teal),transparent);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    border-color:rgba(255,181,71,0.2) !important; background:rgba(255,181,71,0.04) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])::before {
    background:linear-gradient(90deg,var(--amber),transparent);
}
[data-testid="stChatInput"] textarea {
    background:rgba(5,13,26,0.95) !important; color:var(--text-main) !important;
    border:1px solid var(--glass-brd) !important; border-radius:10px !important;
    font-family:'DM Sans',sans-serif !important; font-size:0.9rem !important;
}
[data-testid="stChatInput"] textarea:focus { border-color:var(--teal) !important; box-shadow:0 0 0 1px rgba(0,229,216,0.18) !important; }

/* Images */
[data-testid="stImage"] img { border-radius:10px !important; border:1px solid var(--glass-brd) !important; box-shadow:0 0 16px rgba(0,229,216,0.08) !important; }
[data-testid="stFileUploader"] { background:rgba(5,13,26,0.8) !important; border:1px dashed var(--glass-brd) !important; border-radius:10px !important; }

/* Welcome */
.welcome-screen {
    text-align:center; padding:55px 40px;
    border:1px solid var(--glass-brd); border-radius:20px; margin-top:14px;
    background:linear-gradient(135deg,rgba(0,229,216,0.03) 0%,transparent 50%), var(--panel);
    position:relative; overflow:hidden;
}
.welcome-screen::before {
    content:''; position:absolute; top:-50%; left:-50%; width:200%; height:200%;
    background:conic-gradient(transparent 0deg,rgba(0,229,216,0.02) 60deg,transparent 120deg);
    animation:rotate-bg 14s linear infinite;
}
@keyframes rotate-bg { from{transform:rotate(0deg);}to{transform:rotate(360deg);} }
.welcome-screen h2 { font-family:'Syne',sans-serif !important; font-weight:800; font-size:1.55rem; color:var(--text-main) !important; margin:10px 0 8px !important; position:relative; z-index:1; }
.welcome-screen p { color:var(--text-muted); font-size:0.88rem; max-width:440px; margin:0 auto; line-height:1.75; position:relative; z-index:1; }
.w-tag { display:inline-block; margin-top:16px; font-family:'Space Mono',monospace; font-size:0.6rem; color:var(--teal); border:1px solid var(--glass-brd); border-radius:4px; padding:4px 14px; letter-spacing:1.5px; position:relative; z-index:1; }

/* Tabs */
[data-testid="stTabs"] [data-testid="stTab"] { font-family:'Space Mono',monospace !important; font-size:0.65rem !important; text-transform:uppercase; letter-spacing:1.5px; color:var(--text-muted) !important; }
[data-testid="stTabs"] [aria-selected="true"] { color:var(--teal) !important; border-bottom-color:var(--teal) !important; }
[data-testid="stTabPanel"] { background:var(--panel) !important; border:1px solid var(--glass-brd) !important; border-radius:0 12px 12px 12px !important; padding:16px 20px !important; margin-top:-1px; }

/* Expander */
[data-testid="stExpander"] { background:var(--panel) !important; border:1px solid var(--glass-brd) !important; border-radius:10px !important; margin-bottom:8px !important; }
[data-testid="stExpander"] summary { font-family:'Space Mono',monospace !important; font-size:0.65rem !important; color:var(--text-muted) !important; text-transform:uppercase; letter-spacing:1.5px; }

/* Metrics */
[data-testid="stMetric"] { background:var(--panel) !important; border:1px solid var(--glass-brd) !important; border-radius:10px !important; padding:12px 16px !important; }
[data-testid="stMetricLabel"] { font-family:'Space Mono',monospace !important; font-size:0.6rem !important; color:var(--text-muted) !important; text-transform:uppercase; letter-spacing:1px; }
[data-testid="stMetricValue"] { font-family:'Syne',sans-serif !important; font-size:1.5rem !important; color:var(--teal) !important; }

/* Misc */
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:var(--void); }
::-webkit-scrollbar-thumb { background:var(--teal-dim); border-radius:2px; }
[data-testid="stAlert"] { border-radius:8px !important; font-family:'Space Mono',monospace !important; font-size:0.76rem !important; }
hr { border-color:var(--glass-brd) !important; }

/* Download button */
[data-testid="stDownloadButton"] button {
    background:rgba(0,229,216,0.07) !important; color:var(--teal) !important;
    border:1px dashed rgba(0,229,216,0.4) !important; border-radius:8px !important;
    font-family:'Space Mono',monospace !important; font-size:0.68rem !important;
    letter-spacing:1px; text-transform:uppercase;
}
[data-testid="stDownloadButton"] button:hover {
    background:rgba(0,229,216,0.14) !important; border-style:solid !important;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# INIT
# ──────────────────────────────────────────────────────────────────────────────
database.init_db()

defaults = {
    "messages":        [],
    "session_active":  False,
    "doctor_name":     "",
    "patient_name":    "",
    "patient_id":      None,
    "visita_id":       None,
    "total_consultas": 0,
    "view":            "chat",
    "paciente_data":   {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown(f"""
    <div class="sidebar-logo">
        {eye_svg(width="106px", pulse_dur="3.5s", radar_dur="2.9s")}
        <div class="logo-title">Ophthalm<span>AI</span></div>
        <div class="logo-sub">Hospital Rísquez · Caracas</div>
    </div>
    <div class="model-badge">
        <div class="mb-dot"></div>
        EfficientNetB0 · Local · Sin Internet
    </div>
    """, unsafe_allow_html=True)

    # Navegación
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

    # Datos de consulta
    st.markdown('<div class="s-section">Datos de la Consulta</div>', unsafe_allow_html=True)
    doctor_input  = st.text_input("Nombre del Doctor",  placeholder="Dr. García",        value=st.session_state.doctor_name,  disabled=st.session_state.session_active)
    patient_input = st.text_input("Paciente (nombre/cédula)", placeholder="Juan Pérez", value=st.session_state.patient_name, disabled=st.session_state.session_active)

    if not st.session_state.session_active:
        if st.button("▶  INICIAR CONSULTA"):
            if doctor_input.strip() and patient_input.strip():
                st.session_state.doctor_name  = doctor_input.strip()
                st.session_state.patient_name = patient_input.strip()

                resultados = database.buscar_paciente(patient_input.strip())
                if resultados:
                    p = resultados[0]
                    st.session_state.patient_id   = p["id"]
                    st.session_state.paciente_data = p
                    visitas_prev = database.obtener_visitas_paciente(p["id"])
                    n_v = len(visitas_prev) + 1
                    vid = database.abrir_visita(p["id"], doctor_input.strip(), "Consulta OphthalmAI")
                    st.session_state.visita_id = vid
                    hay_prev = len(visitas_prev)
                    bienvenida = (
                        f"Sistema en línea. Bienvenido, **Dr. {doctor_input.strip()}**.\n\n"
                        f"Paciente identificado: **{p['nombre_completo']}**"
                        + (f"  ·  Cédula: `{p['cedula']}`" if p.get("cedula") else "") + "\n\n"
                        f"Esta es la **visita N.° {n_v}**."
                        + (f" Tiene **{hay_prev}** consulta(s) previa(s) registradas." if hay_prev else "") +
                        "\n\nEl módulo EfficientNetB0 está activo. ¿Con qué empezamos, Doctor?"
                    )
                else:
                    st.session_state.patient_id   = None
                    st.session_state.paciente_data = {}
                    st.session_state.visita_id     = None
                    bienvenida = (
                        f"Bienvenido, **Dr. {doctor_input.strip()}**.\n\n"
                        f"No encontré a **{patient_input.strip()}** en el sistema. "
                        "Puede registrarlo en **📋 Registro** o continuar con la consulta.\n\n"
                        "¿Cómo puedo asistirle?"
                    )

                st.session_state.session_active = True
                st.session_state.messages       = []
                st.session_state.total_consultas = 0
                st.session_state.messages.append({"role": "assistant", "content": bienvenida})
                st.session_state.view = "chat"
                st.rerun()
            else:
                st.error("Complete ambos campos.")
    else:
        if st.button("⏹  FINALIZAR CONSULTA"):
            for k in ["session_active","messages","doctor_name","patient_name",
                      "patient_id","visita_id","total_consultas","paciente_data"]:
                st.session_state[k] = defaults[k]
            st.rerun()

    if st.session_state.session_active:
        p = st.session_state.paciente_data
        st.markdown(f"""
        <div class="session-card">
            <div class="sc-label">Doctor</div>
            <div class="sc-value">{st.session_state.doctor_name}</div>
            <div class="sc-label" style="margin-top:6px;">Paciente</div>
            <div class="sc-value">{p.get("nombre_completo", st.session_state.patient_name)}</div>
            {'<div class="sc-label" style="margin-top:6px;">Cédula</div><div class="sc-value">' + p["cedula"] + '</div>' if p.get("cedula") else ""}
            <div class="sc-label" style="margin-top:6px;">Interacciones</div>
            <div class="sc-value" style="color:var(--teal);">{st.session_state.total_consultas}</div>
        </div>
        """, unsafe_allow_html=True)

    # Imágenes
    st.markdown('<div class="s-section">Imágenes · Segmento Anterior</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Fotografías oculares", type=["jpg","jpeg","png"],
        accept_multiple_files=True,
        disabled=not st.session_state.session_active,
        label_visibility="collapsed",
    )
    if uploaded_files:
        n_f = len(uploaded_files)
        cols = st.columns(min(n_f, 2))
        for i, f in enumerate(uploaded_files):
            cols[i % 2].image(f, use_container_width=True)
        st.markdown(
            f'<div style="font-family:Space Mono,monospace;font-size:0.6rem;'
            f'color:var(--teal);text-align:center;margin-top:5px;letter-spacing:1px;">'
            f'✓ {n_f} IMAGEN(ES) · CNN ACTIVA</div>',
            unsafe_allow_html=True,
        )

    # Diagnósticas
    st.markdown('<div class="s-section">Áreas Diagnósticas</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="s-info">
        🔵 <strong>Úlcera / Queratitis</strong><br>
        🟠 <strong>Uveítis Anterior</strong><br>
        🟡 <strong>Glaucoma / HTO</strong><br>
        🟢 <strong>Conjuntivitis</strong><br>
        <span style="color:#1e3d55;font-family:Space Mono,monospace;font-size:0.58rem;">
        REF: AAO · ESCRS · SVO
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:16px;padding:10px 12px;border-top:1px solid rgba(0,229,216,0.07);
    font-family:Space Mono,monospace;font-size:0.55rem;color:#1e3550;text-align:center;line-height:1.9;">
        EfficientNetB0 · Transfer Learning<br>
        Procesamiento local · Sin API · $0<br>
        <span style="color:#254060;">© Tesis UCV · Hospital Rísquez</span>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hud-header">
    <div style="flex-shrink:0;">{eye_svg(width="66px", pulse_dur="3s", radar_dur="2.5s")}</div>
    <div class="hud-title">
        <h1>Ophthalm<em>AI</em></h1>
        <div class="hud-subtitle">Sistema de Apoyo Diagnóstico · Úlceras Corneales & Uveítis</div>
    </div>
    <div class="hud-meta">
        <div class="ver">v3.1-LOCAL</div>
        <div>EfficientNetB0</div>
        <div>Multi-imagen · NLP</div>
        <div>SQLite · $0 API</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Status strip
if st.session_state.session_active:
    n_imgs = len(uploaded_files) if uploaded_files else 0
    img_h  = (f'<div class="indicator"><div class="s-dot dot-img"></div>{n_imgs} IMG</div>'
              if n_imgs else '<div class="indicator"><div class="s-dot dot-inactive"></div>SIN IMG</div>')
    p      = st.session_state.paciente_data
    ced_h  = f'· CÉD:<span style="color:var(--text-main);"> {p["cedula"]}</span>' if p.get("cedula") else ""
    st.markdown(f"""
    <div class="status-strip">
        <div class="indicator"><div class="s-dot dot-active"></div>SESIÓN ACTIVA</div>
        <div>PAC:<span style="color:var(--text-main);"> {p.get("nombre_completo",st.session_state.patient_name).upper()}</span> {ced_h}</div>
        <div>DR:<span style="color:var(--text-main);"> {st.session_state.doctor_name.upper()}</span></div>
        {img_h}
        <div style="margin-left:auto;">CNN:<span style="color:var(--green-ok);"> ONLINE</span></div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="status-strip">
        <div class="indicator"><div class="s-dot dot-inactive"></div>STANDBY</div>
        <div style="color:#1e3550;">Ingrese datos del doctor y paciente para comenzar</div>
        <div style="margin-left:auto;">CNN:<span style="color:var(--green-ok);"> READY</span></div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# VISTAS
# ══════════════════════════════════════════════════════════════════════════════
view = st.session_state.view

# ────────────────────────────────────────────────────────────────────────
# VISTA: CHAT
# ────────────────────────────────────────────────────────────────────────
if view == "chat":

    if not st.session_state.session_active:
        st.markdown(f"""
        <div class="welcome-screen">
            <div style="position:relative;z-index:1;">
                {eye_svg(width="115px", pulse_dur="4s", radar_dur="3s")}
            </div>
            <h2>OphthalmAI en espera</h2>
            <p>
                Diagnóstico asistido por Red Neuronal Convolucional (EfficientNetB0).
                Cada paciente queda registrado con historial clínico y seguimiento de evolución.
                Procesamiento 100 % local — sin internet — costo cero.
            </p>
            <div class="w-tag">// MOTOR LOCAL · PRIVACIDAD TOTAL · TESIS UCV //</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Visitas previas
        if st.session_state.patient_id:
            visitas_prev = database.obtener_visitas_paciente(st.session_state.patient_id)
            if len(visitas_prev) > 1:
                with st.expander(f"📂 {len(visitas_prev)-1} visita(s) previa(s) registradas", expanded=False):
                    for v in visitas_prev[1:]:
                        st.markdown(f"""
                        <div style="font-family:Space Mono,monospace;font-size:0.63rem;
                        border-bottom:1px solid var(--glass-brd);padding:8px 0;line-height:1.7;">
                            <span style="color:var(--teal);">Visita #{v['numero_visita']} · {v['fecha_hora'][:16]}</span>
                            &nbsp;·&nbsp; Dr. {v['doctor_nombre']}<br>
                            <span style="color:var(--text-muted);">Diag. IA:</span> {(v.get('diagnostico_ia') or '—')[:120]}<br>
                            <span style="color:var(--text-muted);">Tratamiento:</span> {(v.get('tratamiento') or '—')[:100]}
                        </div>
                        """, unsafe_allow_html=True)

        # Registro de evolución
        if st.session_state.visita_id and st.session_state.patient_id:
            with st.expander("📈 Registrar evolución del paciente", expanded=False):
                sc1, sc2 = st.columns([2, 1])
                nota_seg = sc1.text_area("Nota de evolución", placeholder="Describa el avance clínico...", height=70, label_visibility="collapsed")
                tipo_seg = sc2.selectbox("Estado", ["mejoria", "sin_cambio", "empeoramiento", "alta"], label_visibility="collapsed")
                if st.button("💾  GUARDAR EVOLUCIÓN"):
                    if nota_seg.strip():
                        database.registrar_seguimiento(
                            visita_id=st.session_state.visita_id,
                            paciente_id=st.session_state.patient_id,
                            tipo=tipo_seg, nota=nota_seg.strip(),
                            doctor=st.session_state.doctor_name,
                        )
                        st.success("✓ Evolución guardada correctamente.")
                    else:
                        st.warning("Escriba una nota antes de guardar.")

        # Historial del chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Exportar resumen
        if st.session_state.total_consultas > 0:
            resumen_txt = modelo_vision.generar_resumen_consulta(
                st.session_state.doctor_name,
                st.session_state.patient_name,
                st.session_state.messages,
            )
            st.download_button(
                label="⬇  Exportar resumen de consulta (.txt)",
                data=resumen_txt.encode("utf-8"),
                file_name=f"consulta_{st.session_state.patient_name.replace(' ','_')}_{time.strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                key="export_btn",
            )

        # Chips de síntomas
        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:0.58rem;'
            'color:var(--text-muted);letter-spacing:1px;margin-bottom:6px;">'
            '// SÍNTOMAS RÁPIDOS</div>', unsafe_allow_html=True
        )
        cc = st.columns(4)
        chips = [
            ("🔴 Ojo rojo",     "El paciente presenta ojo rojo intenso con secreción"),
            ("💧 Secreción",    "El paciente tiene secreción ocular purulenta"),
            ("⚡ Fotofobia",    "El paciente refiere fotofobia intensa y lagrimeo"),
            ("🌀 Dolor ocular", "El paciente describe dolor ocular profundo con fotofobia"),
        ]
        chip_prompt = None
        for i, (label, texto) in enumerate(chips):
            if cc[i].button(label, key=f"chip_{i}"):
                chip_prompt = texto

        # Chat input
        user_input = st.chat_input(
            f"[Dr. {st.session_state.doctor_name}]  Síntomas, antecedentes o hallazgos de {st.session_state.patient_name}..."
        )
        prompt = chip_prompt or user_input

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            lista_imgs = [f.getvalue() for f in uploaded_files] if uploaded_files else []

            with st.chat_message("assistant"):
                ph = st.empty()
                ph.markdown(
                    '<span style="font-family:Space Mono,monospace;font-size:0.7rem;'
                    'color:var(--teal);">// Procesando con EfficientNetB0...</span>',
                    unsafe_allow_html=True,
                )
                time.sleep(0.28)
                try:
                    respuesta_ia = modelo_vision.analizar_imagen_y_sintomas(
                        lista_imagenes=lista_imgs,
                        texto_doctor=prompt,
                    )
                except Exception as e:
                    respuesta_ia = f"⚠️ **Error en módulo CNN:** `{e}`\n\nVerifique que `modelo_vision.py` esté en el mismo directorio."

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
                database.actualizar_visita(
                    visita_id=st.session_state.visita_id,
                    diagnostico_ia=full_response.strip()[:600],
                    tiene_imagen=bool(lista_imgs),
                )
            try:
                database.registrar_consulta(
                    doctor_nombre=st.session_state.doctor_name,
                    paciente_nombre=st.session_state.patient_name,
                    pregunta_doctor=prompt,
                    respuesta_ia=full_response.strip(),
                    tiene_imagen=bool(lista_imgs),
                    visita_id=st.session_state.visita_id,
                    paciente_id=st.session_state.patient_id,
                )
            except Exception as e:
                st.warning(f"BD: No se pudo registrar — {e}")


# ────────────────────────────────────────────────────────────────────────
# VISTA: REGISTRO
# ────────────────────────────────────────────────────────────────────────
elif view == "registro":
    st.markdown("### 📋 Registro de Nuevo Paciente")
    st.markdown('<hr>', unsafe_allow_html=True)

    with st.form("form_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre_completo = c1.text_input("Nombre Completo *", placeholder="Juan Carlos Pérez")
        cedula          = c2.text_input("Cédula", placeholder="V-12345678")
        c3, c4, c5 = st.columns(3)
        edad     = c3.number_input("Edad", 0, 120, 0, step=1)
        sexo     = c4.selectbox("Sexo", ["", "Masculino", "Femenino", "Otro"])
        fecha_nac = c5.text_input("Fecha de Nac.", placeholder="DD/MM/AAAA")
        c6, c7 = st.columns(2)
        telefono = c6.text_input("Teléfono", placeholder="0414-1234567")
        direccion = c7.text_input("Dirección", placeholder="Calle, Ciudad")
        antecedentes = st.text_area("Antecedentes Oftalmológicos y Médicos",
            placeholder="Diabetes, HTA, cirugías previas, uso de lentes de contacto...", height=75)
        c8, c9 = st.columns(2)
        alergias    = c8.text_input("Alergias", placeholder="Penicilina, látex...")
        medicamentos = c9.text_input("Medicamentos Actuales", placeholder="Metformina 500mg...")
        doctor_reg = st.text_input("Doctor que Registra *",
            value=st.session_state.doctor_name, placeholder="Dr. García")

        if st.form_submit_button("💾  REGISTRAR PACIENTE"):
            if nombre_completo.strip() and doctor_reg.strip():
                try:
                    pid = database.registrar_paciente(
                        nombre_completo=nombre_completo.strip(),
                        doctor_registro=doctor_reg.strip(),
                        cedula=cedula.strip() or None,
                        fecha_nacimiento=fecha_nac.strip() or None,
                        edad=int(edad) if edad else None,
                        sexo=sexo or None,
                        telefono=telefono.strip() or None,
                        direccion=direccion.strip() or None,
                        antecedentes=antecedentes.strip() or None,
                        alergias=alergias.strip() or None,
                        medicamentos_act=medicamentos.strip() or None,
                    )
                    st.success(f"✓ **{nombre_completo}** registrado correctamente · ID #{pid}")
                except Exception as e:
                    st.error(f"Error al registrar: {e}")
            else:
                st.warning("Los campos con * son obligatorios.")


# ────────────────────────────────────────────────────────────────────────
# VISTA: HISTORIAL
# ────────────────────────────────────────────────────────────────────────
elif view == "historial":
    st.markdown("### 📂 Historial de Pacientes")
    st.markdown('<hr>', unsafe_allow_html=True)

    busqueda  = st.text_input("Buscar por nombre o cédula", placeholder="Escriba para buscar...")
    pacientes = database.buscar_paciente(busqueda) if busqueda else database.obtener_todos_los_pacientes()

    if not pacientes:
        st.info("No se encontraron pacientes.")
    else:
        for p in pacientes:
            label = f"👤  {p['nombre_completo']}"
            if p.get("cedula"):   label += f"  ·  {p['cedula']}"
            label += f"  ·  Reg: {p['fecha_registro'][:10]}"
            with st.expander(label, expanded=False):
                st.markdown(f"""
                <div class="patient-card">
                    <div class="pc-name">{p['nombre_completo']}</div>
                    <div class="pc-row">
                        <div>CÉD: <span>{p.get('cedula','—')}</span></div>
                        <div>EDAD: <span>{p.get('edad','—')}</span></div>
                        <div>SEXO: <span>{p.get('sexo','—')}</span></div>
                        <div>TEL: <span>{p.get('telefono','—')}</span></div>
                    </div>
                    {'<div class="pc-row"><div>DIRECCIÓN: <span>' + p.get("direccion","—") + '</span></div></div>' if p.get("direccion") else ''}
                    {'<div class="pc-row"><div>ANTECEDENTES: <span>' + (p.get("antecedentes") or "—") + '</span></div></div>'}
                    {'<div class="pc-row"><div>ALERGIAS: <span>' + (p.get("alergias") or "—") + '</span></div></div>'}
                    {'<div class="pc-row"><div>MEDICAMENTOS: <span>' + (p.get("medicamentos_act") or "—") + '</span></div></div>'}
                    <div class="pc-row" style="margin-top:5px;font-size:0.58rem;">
                        <div>REGISTRADO POR: <span>{p.get('doctor_registro','—')}</span></div>
                        <div>FECHA: <span>{p['fecha_registro'][:16]}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Botón exportar ficha
                ficha_txt = database.exportar_ficha_texto(p["id"])
                st.download_button(
                    label="⬇  Descargar expediente completo (.txt)",
                    data=ficha_txt.encode("utf-8"),
                    file_name=f"expediente_{p['nombre_completo'].replace(' ','_')}.txt",
                    mime="text/plain",
                    key=f"dl_{p['id']}",
                )

                visitas = database.obtener_visitas_paciente(p["id"])
                if visitas:
                    st.markdown(f'<div class="visit-badge">🗂 {len(visitas)} VISITA(S)</div>', unsafe_allow_html=True)
                    for v in visitas:
                        st.markdown(f"""
                        <div style="font-family:Space Mono,monospace;font-size:0.62rem;
                        border:1px solid var(--glass-brd);border-radius:8px;
                        padding:10px 14px;margin:5px 0;background:rgba(0,229,216,0.03);line-height:1.7;">
                            <span style="color:var(--teal);">▸ Visita #{v['numero_visita']} · {v['fecha_hora'][:16]}</span>
                            &nbsp;·&nbsp; Dr. {v['doctor_nombre']}<br>
                            <span style="color:var(--text-muted);">Diag. IA:</span> {(v.get('diagnostico_ia') or '—')[:130]}<br>
                            <span style="color:var(--text-muted);">Tratamiento:</span> {(v.get('tratamiento') or '—')[:100]}
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
                            &nbsp;·&nbsp; <span style="color:var(--text-muted);">Visita #{s.get('numero_visita','?')}</span><br>
                            <span style="color:var(--text-main);">{s['nota']}</span>
                        </div>
                        """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────
# VISTA: DASHBOARD
# ────────────────────────────────────────────────────────────────────────
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

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns(2)

    with cl:
        st.markdown("**Últimas interacciones**")
        for c in database.obtener_todas_las_consultas(limite=8):
            st.markdown(f"""
            <div style="font-family:Space Mono,monospace;font-size:0.62rem;
            border-bottom:1px solid var(--glass-brd);padding:7px 0;line-height:1.65;">
                <span style="color:var(--teal);">{c['fecha_hora'][:16]}</span><br>
                <span style="color:var(--text-muted);">Dr.</span> {c['doctor_nombre']}
                &nbsp;→&nbsp; {c['paciente_nombre']}<br>
                <span style="color:var(--text-muted);">{c['pregunta_doctor'][:70]}...</span>
            </div>
            """, unsafe_allow_html=True)

    with cr:
        st.markdown("**Pacientes registrados**")
        for p in database.obtener_todos_los_pacientes()[:8]:
            vp = database.obtener_visitas_paciente(p["id"])
            st.markdown(f"""
            <div style="font-family:Space Mono,monospace;font-size:0.62rem;
            border-bottom:1px solid var(--glass-brd);padding:7px 0;line-height:1.65;">
                <span style="color:var(--teal);">{p['nombre_completo']}</span><br>
                <span style="color:var(--text-muted);">Céd:</span> {p.get('cedula','—')}
                &nbsp;·&nbsp; <span style="color:var(--text-muted);">Visitas:</span>
                <span style="color:var(--amber);">{len(vp)}</span>
                &nbsp;·&nbsp; {p['fecha_registro'][:10]}
            </div>
            """, unsafe_allow_html=True)
