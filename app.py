"""
app.py – Hospital Rísquez · OphthalmAI v3.6
Diseño Arena.site — Sin ojo superior, sin errores de espaciado, completo.
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

b64_ojo = get_base64_image("ojo_portada.png")
if not b64_ojo:
    b64_ojo = get_base64_image("ojo_portada.jpg") 

mime_type = "image/jpeg" if b64_ojo.startswith("/9j/") else "image/png"
IMG_SRC = f"data:{mime_type};base64,{b64_ojo}" if b64_ojo else "https://images.unsplash.com/photo-1542282088-fe8426682b8f?auto=format&fit=crop&w=500&q=80"

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
}[data-testid="stAppViewContainer"] {
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

[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--glass-brd) !important;
    background-image: linear-gradient(180deg, rgba(0,229,216,0.04) 0%, transparent 30%) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

/* LOGO Y OJO SIDEBAR */
.sidebar-logo {
    text-align: center; padding: 22px 16px 16px; border-bottom: 1px solid var(--glass-brd); margin-bottom: 4px; position: relative;
}
.sidebar-logo::before {
    content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 60%; height: 1px; background: linear-gradient(90deg, transparent, var(--teal), transparent);
}
.logo-title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.5rem; color: var(--text-main); letter-spacing: 1px; }
.logo-title span { color: var(--teal); }
.logo-sub { font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-muted); letter-spacing: 2.5px; text-transform: uppercase; margin-top: 3px; }

.eye-sidebar-wrap { display: flex; justify-content: center; align-items: center; margin-bottom: 10px; position: relative; }
.eye-sidebar-img {
    width: 120px; height: 120px; object-fit: cover; border-radius: 50%;
    -webkit-mask-image: radial-gradient(ellipse 55% 55% at center, black 20%, rgba(0,0,0,0.8) 42%, rgba(0,0,0,0.3) 60%, transparent 75%);
    mask-image: radial-gradient(ellipse 55% 55% at center, black 20%, rgba(0,0,0,0.8) 42%, rgba(0,0,0,0.3) 60%, transparent 75%);
    filter: drop-shadow(0 0 14px rgba(0,229,216,0.6)) drop-shadow(0 0 30px rgba(0,229,216,0.25));
    animation: eye-pulse 3.5s ease-in-out infinite;
}

.model-badge { display: flex; align-items: center; gap: 7px; background: rgba(0,229,216,0.05); border: 1px solid rgba(0,229,216,0.18); border-radius: 6px; padding: 6px 12px; font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--teal); letter-spacing: 1px; text-transform: uppercase; margin: 8px 0 2px; }
.mb-dot { width: 6px; height: 6px; background: var(--green-ok); border-radius: 50%; box-shadow: 0 0 6px var(--green-ok); flex-shrink: 0; animation: blink 1.8s ease-in-out infinite; }

.s-section { font-family: 'Space Mono', monospace; font-size: 0.58rem; font-weight: 700; color: var(--teal); text-transform: uppercase; letter-spacing: 2px; padding: 12px 0 5px; border-top: 1px solid var(--glass-brd); margin-top: 8px; }
.s-info { background: rgba(0,229,216,0.03); border: 1px solid var(--glass-brd); border-radius: 8px; padding: 10px 13px; font-size: 0.8rem; color: var(--text-muted); line-height: 1.65; margin-top: 6px; }

.session-card { background: linear-gradient(135deg, rgba(0,229,216,0.07), rgba(0,207,255,0.03)); border: 1px solid var(--glass-brd); border-radius: 10px; padding: 12px 14px 12px 18px; margin-top: 8px; position: relative; overflow: hidden; }
.session-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: linear-gradient(180deg, var(--teal), var(--cyan)); }
.sc-label { font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; }
.sc-value { font-size: 0.88rem; color: var(--text-main); font-weight: 500; margin-top: 1px; }

[data-testid="stSidebar"] label, .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label { font-family: 'Space Mono', monospace !important; font-size: 0.62rem !important; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 1.2px; }[data-testid="stSidebar"] input, .stTextInput input, .stNumberInput input, textarea { background: rgba(5,13,26,0.9) !important; color: var(--teal) !important; border: 1px solid var(--glass-brd) !important; border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-size: 0.82rem !important; }[data-testid="stSidebar"] input:focus, .stTextInput input:focus, textarea:focus { border-color: var(--teal) !important; box-shadow: 0 0 0 2px rgba(0,229,216,0.12) !important; }

.stButton > button { background: transparent !important; color: var(--teal) !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.8rem !important; border: 1px solid var(--teal) !important; border-radius: 8px !important; padding: 10px 20px !important; width: 100% !important; letter-spacing: 1.5px; text-transform: uppercase; transition: all 0.22s ease !important; }
.stButton > button:hover { color: var(--void) !important; background: var(--teal) !important; box-shadow: 0 0 22px rgba(0,229,216,0.5) !important; transform: translateY(-1px) !important; }

/* HEADER LIMPIO SIN OJO */
.hud-header { display: flex; align-items: center; gap: 20px; padding: 18px 0 14px; border-bottom: 1px solid var(--glass-brd); margin-bottom: 16px; position: relative; }
.hud-header::after { content: ''; position: absolute; bottom: -1px; left: 0; width: 140px; height: 1px; background: linear-gradient(90deg, var(--teal), transparent); }
.hud-title h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; font-size: 2rem !important; color: var(--text-main) !important; margin: 0 !important; letter-spacing: -0.5px; line-height: 1; }
.hud-title h1 em { font-style: normal; color: var(--teal); text-shadow: 0 0 20px rgba(0,229,216,0.5); }
.hud-subtitle { font-family: 'Space Mono', monospace; font-size: 0.6rem; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase; margin-top: 6px; }
.hud-meta { margin-left: auto; text-align: right; font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-muted); line-height: 1.9; }
.hud-meta .ver { color: var(--teal); font-weight: 700; }

.status-strip { display: flex; align-items: center; gap: 16px; margin-bottom: 14px; padding: 8px 16px; background: var(--panel); border: 1px solid var(--glass-brd); border-radius: 8px; font-family: 'Space Mono', monospace; font-size: 0.62rem; color: var(--text-muted); flex-wrap: wrap; }
.indicator { display: flex; align-items: center; gap: 6px; }
.s-dot { width: 7px; height: 7px; border-radius: 50%; }
.dot-active { background: var(--green-ok); box-shadow: 0 0 6px var(--green-ok); animation: blink 1.4s ease-in-out infinite; }
.dot-inactive { background: var(--text-muted); }

/* WELCOME SCREEN ARENA Y OJO GIGANTE */
.welcome-screen { text-align: center; padding: 60px 40px; border: 1px solid var(--glass-brd); border-radius: 20px; margin-top: 20px; background: linear-gradient(135deg, rgba(0,229,216,0.03) 0%, transparent 50%), var(--panel); position: relative; overflow: hidden; }
.ws-conic { position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: conic-gradient(transparent 0deg, rgba(0,229,216,0.025) 60deg, transparent 120deg); animation: rotate-bg 14s linear infinite; pointer-events: none; z-index: 0; }
.ws-corner { position: absolute; width: 30px; height: 30px; z-index: 2; }
.ws-tl { top: 16px; left: 16px; border-top: 1px solid rgba(0,229,216,0.4); border-left: 1px solid rgba(0,229,216,0.4); }
.ws-tr { top: 16px; right: 16px; border-top: 1px solid rgba(0,229,216,0.4); border-right: 1px solid rgba(0,229,216,0.4); }
.ws-bl { bottom: 16px; left: 16px; border-bottom: 1px solid rgba(0,229,216,0.4); border-left: 1px solid rgba(0,229,216,0.4); }
.ws-br { bottom: 16px; right: 16px; border-bottom: 1px solid rgba(0,229,216,0.4); border-right: 1px solid rgba(0,229,216,0.4); }

.scan-line-anim { position: absolute; left: 10%; right: 10%; height: 2px; background: linear-gradient(90deg, transparent, rgba(0,229,216,0.8), transparent); animation: scan-down 2.4s linear infinite; border-radius: 1px; pointer-events: none; z-index: 5; box-shadow: 0 2px 10px rgba(0,229,216,0.6); }
.eye-hero-wrap { position: relative; z-index: 1; display: flex; justify-content: center; margin-bottom: 28px; animation: float-y 4s ease-in-out infinite; }
.eye-hero-container { position: relative; width: 260px; height: 260px; }
.eye-hero-img { width: 260px; height: 260px; object-fit: cover; border-radius: 50%; display: block; -webkit-mask-image: radial-gradient(ellipse 52% 52% at center, black 10%, rgba(0,0,0,0.8) 35%, rgba(0,0,0,0.3) 55%, transparent 72%); mask-image: radial-gradient(ellipse 52% 52% at center, black 10%, rgba(0,0,0,0.8) 35%, rgba(0,0,0,0.3) 55%, transparent 72%); filter: drop-shadow(0 0 30px rgba(0,229,216,0.6)) drop-shadow(0 0 60px rgba(0,229,216,0.25)); animation: eye-pulse 3.5s ease-in-out infinite; position: relative; z-index: 1; }
.welcome-screen h2 { font-family: 'Syne', sans-serif !important; font-weight: 800; font-size: 1.8rem; color: var(--text-main) !important; margin: 0 0 8px !important; position: relative; z-index: 1; }
.welcome-screen p { color: var(--text-muted); font-size: 0.92rem; max-width: 460px; margin: 0 auto; line-height: 1.75; position: relative; z-index: 1; }
.w-tag { display: inline-block; margin-top: 20px; font-family: 'Space Mono', monospace; font-size: 0.62rem; color: var(--teal); border: 1px solid var(--glass-brd); border-radius: 4px; padding: 4px 14px; letter-spacing: 1.5px; position: relative; z-index: 1; }

[data-testid="stChatMessage"] { background: var(--panel) !important; border: 1px solid var(--glass-brd) !important; border-radius: 12px !important; padding: 16px 20px !important; margin-bottom: 10px !important; backdrop-filter: blur(12px); position: relative; animation: fadeInUp 0.3s ease forwards; }
[data-testid="stChatMessage"]::before { content: ''; position: absolute; top: 0; left: 16px; width: 40px; height: 1px; background: linear-gradient(90deg, var(--teal), transparent); }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { border-color: rgba(255,181,71,0.2) !important; background: rgba(255,181,71,0.04) !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])::before { background: linear-gradient(90deg, var(--amber), transparent); }
[data-testid="stChatInput"] textarea { background: rgba(5,13,26,0.95) !important; color: var(--text-main) !important; border: 1px solid var(--glass-brd) !important; border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.9rem !important; }
[data-testid="stImage"] img { border-radius: 10px !important; border: 1px solid var(--glass-brd) !important; }[data-testid="stFileUploader"] { background: rgba(5,13,26,0.8) !important; border: 1px dashed var(--glass-brd) !important; border-radius: 10px !important; }
[data-testid="stExpander"] { background: var(--panel) !important; border: 1px solid var(--glass-brd) !important; border-radius: 10px !important; margin-bottom: 8px !important; }
[data-testid="stExpander"] summary { font-family: 'Space Mono', monospace !important; font-size: 0.65rem !important; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 1.5px; }

/* Chips de síntomas */
div[data-testid="column"] .stButton>button { font-family:'DM Sans',sans-serif!important;font-size:0.72rem!important;font-weight:500!important;padding:6px 4px!important;letter-spacing:0.3px!important;text-transform:none!important;border-color:rgba(0,229,216,0.25)!important;color:var(--text-muted)!important;border-radius:20px!important;transition:all 0.18s ease!important;white-space:nowrap; }
div[data-testid="column"] .stButton>button:hover { border-color:var(--teal)!important;color:var(--teal)!important;background:rgba(0,229,216,0.06)!important;box-shadow:0 0 10px rgba(0,229,216,0.2)!important;transform:translateY(-1px)!important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb { background: var(--teal-dim); border-radius: 2px; }

@keyframes eye-pulse { 0%,100% { filter: drop-shadow(0 0 12px rgba(0,229,216,0.6)) drop-shadow(0 0 28px rgba(0,229,216,0.3)); } 50% { filter: drop-shadow(0 0 24px rgba(0,229,216,0.9)) drop-shadow(0 0 52px rgba(0,229,216,0.5)); } }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
@keyframes rotate-bg { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
@keyframes scan-down { 0% { top: -4px; opacity: 0.7; } 100% { top: 100%; opacity: 0; } }
@keyframes float-y { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# INIT
# ──────────────────────────────────────────────────────────────────────────────
database.init_db()

defaults = {
    "messages":[], "session_active": False, "doctor_name": "",
    "patient_name": "", "session_idx": 0, "view": "chat",
    "patient_id": None, "visita_id": None, "paciente_data": {},
    "total_consultas": 0
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
        <div class="eye-sidebar-wrap">
            <img src="{IMG_SRC}" class="eye-sidebar-img">
        </div>
        <div class="logo-title">Ophthalm<span>AI</span></div>
        <div class="logo-sub">Hospital Rísquez · Caracas</div>
    </div>
    <div class="model-badge">
        <div class="mb-dot"></div> EfficientNetB0 · Nube AI
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
                
                resultados = database.buscar_paciente(patient_input.strip())
                if resultados:
                    p = resultados[0]
                    st.session_state.patient_id = p["id"]
                    st.session_state.paciente_data = p
                    vid = database.abrir_visita(p["id"], doctor_input.strip(), "Consulta OphthalmAI")
                    st.session_state.visita_id = vid
                    msg = f"Bienvenido, **Dr. {doctor_input.strip()}**. Paciente: **{p['nombre_completo']}**.\n\nEspecialidad activa: **Úlceras Corneales** y **Uveítis**.\n¿Desea ingresar síntomas o subir fotografías?"
                else:
                    st.session_state.patient_id = None
                    st.session_state.paciente_data = {}
                    st.session_state.visita_id = None
                    msg = f"Bienvenido, **Dr. {doctor_input.strip()}**.\n\nNo encontré a **{patient_input.strip()}**. Puede registrarlo en **📋 Registro**.\n\n¿Cómo le asisto hoy?"

                st.session_state.session_active = True
                st.session_state.messages       =[]
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.session_state.view = "chat"
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
        st.markdown('<div class="s-section">Imágenes · Segmento Anterior</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Fotografías", type=["jpg","jpeg","png"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"up_{st.session_state.session_idx}",
        )
        if uploaded_files:
            cols = st.columns(min(len(uploaded_files), 2))
            for i, f in enumerate(uploaded_files):
                cols[i % 2].image(f, use_container_width=True)
            st.markdown('<div style="color:var(--teal);text-align:center;font-size:0.6rem;margin-top:5px;">✓ IMÁGENES LISTAS</div>', unsafe_allow_html=True)

    st.markdown('<div class="s-section">Especialidades (Tesis)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="s-info">
        ⚠️ <strong>Úlcera Corneal / Queratitis</strong><br>
        🔵 <strong>Uveítis Anterior</strong><br>
        ✅ <strong>Ojo Sano / Control</strong>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN AREA
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hud-header">
    <div class="hud-title">
        <h1>Ophthalm<em>AI</em></h1>
        <div class="hud-subtitle">Úlceras Corneales & Uveítis · Hospital Rísquez · Tesis UCV</div>
    </div>
    <div class="hud-meta">
        <div class="ver">v3.6-CLOUD</div>
        <div>EfficientNetB0</div>
        <div>SQLite · $0 API</div>
    </div>
</div>
""", unsafe_allow_html=True)

view = st.session_state.view

# ──────────────────────────────────────────────────────────────────────────────
# VISTA: CHAT
# ──────────────────────────────────────────────────────────────────────────────
if view == "chat":

    if not st.session_state.session_active:
        st.markdown(f"""
        <div class="welcome-screen">
            <div class="ws-conic"></div>
            <div class="ws-corner ws-tl"></div><div class="ws-corner ws-tr"></div>
            <div class="ws-corner ws-bl"></div><div class="ws-corner ws-br"></div>

            <div class="eye-hero-wrap">
                <div class="eye-hero-container">
                    <img src="{EYE_SRC}" class="eye-hero-img">
                    <div class="scan-line-anim" style="top:-4px;"></div>
                </div>
            </div>

            <h2>OphthalmAI · en espera</h2>
            <p>Sistema diagnóstico asistido por Red Neuronal Convolucional (EfficientNetB0). Especializado en la detección de <strong style="color:var(--teal);">Úlceras Corneales</strong> y <strong style="color:var(--teal);">Uveítis</strong>.</p>
            <br><span style="font-family:Space Mono, monospace; color:var(--teal); font-size:0.8rem; letter-spacing: 2px;">// INICIE SESIÓN EN EL PANEL LATERAL PARA COMENZAR //</span>
        </div>
        """, unsafe_allow_html=True)

    else:
        if "uploaded_files" not in dir(): uploaded_files =[]

        if st.session_state.patient_id:
            visitas = database.obtener_visitas_paciente(st.session_state.patient_id)
            if len(visitas) > 1:
                with st.expander(f"📂 {len(visitas)-1} visita(s) previa(s)", expanded=False):
                    for v in visitas[1:]:
                        st.markdown(f"<div style='font-size:0.7rem; color:var(--text-muted);'>Visita #{v['numero_visita']} - {v['fecha_hora'][:10]}</div>", unsafe_allow_html=True)

        if st.session_state.visita_id and st.session_state.patient_id:
            with st.expander("📈 Registrar evolución del paciente", expanded=False):
                sc1, sc2 = st.columns([2, 1])
                nota_seg = sc1.text_area("Nota", height=70, label_visibility="collapsed")
                tipo_seg = sc2.selectbox("Estado",["mejoria", "sin_cambio", "empeoramiento", "alta"], label_visibility="collapsed")
                if st.button("💾 GUARDAR EVOLUCIÓN"):
                    if nota_seg.strip():
                        database.registrar_seguimiento(st.session_state.visita_id, st.session_state.patient_id, tipo_seg, nota_seg.strip(), st.session_state.doctor_name)
                        st.success("Guardado.")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if st.session_state.total_consultas > 0:
            try:
                resumen = _generar_resumen(st.session_state.doctor_name, st.session_state.patient_name, st.session_state.messages).encode("utf-8")
                st.download_button("⬇ Exportar resumen", data=resumen, file_name="consulta.txt")
            except: pass

        st.markdown('<div style="font-size:0.6rem;color:var(--text-muted);margin-bottom:6px;">// SÍNTOMAS RÁPIDOS</div>', unsafe_allow_html=True)
        cc = st.columns(4)
        chips =[("🔴 Ojo rojo", "ojo rojo"), ("💧 Secreción", "secreción"), ("⚡ Fotofobia", "fotofobia"), ("🌀 Dolor", "dolor")]
        chip_prompt = None
        for i, (lbl, txt) in enumerate(chips):
            if cc[i].button(lbl, key=f"chip_{i}"): chip_prompt = txt

        prompt = st.chat_input("Escriba síntomas, pida un protocolo, o analice fotos...")
        prompt = chip_prompt or prompt

        if prompt:
            with st.chat_message("user"): st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            lista_imgs =[f.getvalue() for f in uploaded_files] if uploaded_files else[]

            with st.chat_message("assistant"):
                ph = st.empty()
                ph.markdown('<span style="color:var(--teal);font-size:0.7rem;">// Procesando...</span>', unsafe_allow_html=True)
                try:
                    respuesta_ia = modelo_vision.analizar_imagen_y_sintomas(lista_imgs, prompt)
                except Exception as e:
                    respuesta_ia = f"⚠️ Error: `{e}`"

                full_response = ""
                for chunk in respuesta_ia.split():
                    full_response += chunk + " "
                    ph.markdown(full_response + "▌")
                    time.sleep(0.015)
                ph.markdown(full_response.strip())

            st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})
            st.session_state.total_consultas += 1


# ──────────────────────────────────────────────────────────────────────────────
# VISTAS RESTANTES (Registro, Historial, Dashboard)
# ──────────────────────────────────────────────────────────────────────────────
elif view == "registro":
    st.markdown("### 📋 Registro de Nuevo Paciente")
    with st.form("form_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre Completo *")
        cedula = c2.text_input("Cédula")
        doc    = st.text_input("Doctor que Registra *", value=st.session_state.doctor_name)
        if st.form_submit_button("💾 REGISTRAR"):
            if nombre.strip() and doc.strip():
                database.registrar_paciente(nombre.strip(), doc.strip(), cedula.strip())
                st.success("Registrado con éxito.")

elif view == "historial":
    st.markdown("### 📂 Historial")
    busqueda = st.text_input("Buscar por nombre o cédula...")
    pacientes = database.buscar_paciente(busqueda) if busqueda else database.obtener_todos_los_pacientes()
    for p in pacientes:
        with st.expander(f"👤 {p['nombre_completo']} ({p.get('cedula','')})"):
            st.markdown(f"**Registrado:** {p['fecha_registro'][:10]}")

elif view == "dashboard":
    st.markdown("### 📊 Dashboard")
    stats = database.stats_generales()
    c1, c2, c3 = st.columns(3)
    c1.metric("Pacientes", stats["total_pacientes"])
    c2.metric("Visitas", stats["total_visitas"])
    c3.metric("Interacciones IA", stats["total_interacciones"])
