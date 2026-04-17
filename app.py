"""
app.py – Hospital Rísquez · OphthalmAI v3.8
Diseño Arena.site — Responsivo Celular/PC, Panel de Navegación Futurista, DB Logging
"""

import streamlit as st
import time
import database
import modelo_vision
import base64
import os
import re

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
# FUNCIÓN PARA CARGAR LA IMAGEN LOCAL DEL OJO
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
EYE_SRC = f"data:{mime_type};base64,{b64_ojo}" if b64_ojo else "https://images.unsplash.com/photo-1542282088-fe8426682b8f?auto=format&fit=crop&w=500&q=80"

# ──────────────────────────────────────────────────────────────────────────────
# UTILIDAD: generar resumen
# ──────────────────────────────────────────────────────────────────────────────
def _generar_resumen(doctor: str, paciente: str, mensajes: list) -> str:
    from datetime import datetime
    lineas =[
        "=" * 62,
        "   HOSPITAL RÍSQUEZ · OphthalmAI",
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
        "Reporte generado por OphthalmAI · Hospital Rísquez",
        "Apoyo diagnóstico — criterio clínico del médico tratante.",
        "=" * 62,
    ]
    return "\n".join(lineas)

# ──────────────────────────────────────────────────────────────────────────────
# CSS INMERSIVO (Arena.site + Doble Escáner + Responsive Mobile)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

:root {
    --void:      #02050a;
    --navy-mid:  #050a14;
    --panel:     rgba(5,10,20,0.75);
    --teal:      #00e5d8;
    --teal-dim:  #00857d;
    --cyan:      #00cfff;
    --amber:     #ffb547;
    --green-ok:  #00e59b;
    --text-main: #ddeeff;
    --text-muted:#4a7090;
    --glass-brd: rgba(0,229,216,0.14);
}

[data-testid="stAppViewContainer"] {
    background-color: var(--void) !important;
    background-image: 
        linear-gradient(rgba(0, 229, 216, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 229, 216, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    color: var(--text-main) !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--glass-brd) !important;
}

/* ── ESTILO BOTÓN DE HAMBURGUESA (CELULAR) ── */
[data-testid="collapsedControl"] {
    color: var(--teal) !important;
    background-color: var(--navy-mid) !important;
    border: 1px solid var(--glass-brd);
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0,229,216,0.2);
}

/* LOGO SIDEBAR */
.sidebar-logo { text-align:center; padding:20px 16px 10px; border-bottom:1px solid var(--glass-brd); margin-bottom:10px; }
.logo-title { font-family:'Syne',sans-serif; font-weight:800; font-size:1.5rem; color:var(--text-main); letter-spacing:1px; margin-top: 10px;}
.logo-title span { color:var(--teal); }
.logo-sub { font-family:'Space Mono',monospace; font-size:0.6rem; color:var(--text-muted); letter-spacing:2.5px; text-transform:uppercase; margin-top:2px; }

/* OJO SIDEBAR CON ESCÁNER */
.eye-sidebar-wrap { position: relative; width: 120px; height: 120px; margin: 0 auto; display: flex; justify-content: center; align-items: center; }
.eye-sidebar-inner { 
    position: relative; width: 100px; height: 100px; border-radius: 50%; overflow: hidden;
    -webkit-mask-image: radial-gradient(ellipse at center, black 20%, rgba(0,0,0,0.8) 45%, transparent 70%);
    mask-image: radial-gradient(ellipse at center, black 20%, rgba(0,0,0,0.8) 45%, transparent 70%);
}
.eye-sidebar-img { width: 100%; height: 100%; object-fit: cover; }
.scan-line-small {
    position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: rgba(0,229,216,0.9);
    box-shadow: 0 0 10px rgba(0,229,216,1); animation: scan-down 3s linear infinite; z-index: 5;
}
.eye-sidebar-ring {
    position: absolute; width: 110px; height: 110px; border-radius: 50%;
    border: 1px solid rgba(0,229,216,0.3); animation: radar-ring 3s ease-out infinite; pointer-events: none;
}

/* OJO GIGANTE CENTRAL CON ESCÁNER */
.welcome-screen {
    position: relative; text-align: center; padding: 70px 20px;
    background: radial-gradient(circle at center, rgba(0,229,216,0.06) 0%, transparent 60%);
    border: 1px solid rgba(0,229,216,0.03); margin-top: 20px;
}
.ws-tr { position:absolute; top:0; right:0; width:40px; height:40px; border-top:2px solid var(--teal); border-right:2px solid var(--teal); opacity:0.6; }
.ws-bl { position:absolute; bottom:0; left:0; width:40px; height:40px; border-bottom:2px solid var(--teal); border-left:2px solid var(--teal); opacity:0.6; }

.eye-hero-wrap { position: relative; width: 280px; height: 280px; margin: 0 auto 30px auto; animation: float-eye 6s ease-in-out infinite; display: flex; justify-content: center; align-items: center; }
.eye-hero-inner {
    position: relative; width: 240px; height: 240px; border-radius: 50%; overflow: hidden;
    -webkit-mask-image: radial-gradient(ellipse at center, black 30%, rgba(0,0,0,0.8) 50%, transparent 72%);
    mask-image: radial-gradient(ellipse at center, black 30%, rgba(0,0,0,0.8) 50%, transparent 72%);
}
.eye-hero-img { width: 100%; height: 100%; object-fit: cover; }
.scan-line-large {
    position: absolute; top: 0; left: 0; width: 100%; height: 5px; background: rgba(0,229,216,0.9);
    box-shadow: 0 0 20px rgba(0,229,216,1); animation: scan-down 3.5s linear infinite; z-index: 5;
}
.eye-hero-ring1 { position: absolute; width: 260px; height: 260px; border-radius: 50%; border: 1px solid rgba(0,229,216,0.2); animation: radar-ring 4s ease-out infinite; pointer-events: none; }
.eye-hero-ring2 { position: absolute; width: 260px; height: 260px; border-radius: 50%; border: 1px solid rgba(0,207,255,0.1); animation: radar-ring 4s ease-out 2s infinite; pointer-events: none; }

/* ANIMACIONES GLOBALES */
@keyframes scan-down { 0% { top: -10%; opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { top: 110%; opacity: 0; } }
@keyframes float-eye { 0% { transform: translateY(0px); } 50% { transform: translateY(-12px); } 100% { transform: translateY(0px); } }
@keyframes radar-ring { 0% { transform: scale(0.9); opacity: 0.8; } 100% { transform: scale(1.4); opacity: 0; } }
@keyframes blink{ 0%,100%{opacity:1;} 50%{opacity:0.3;} }

.welcome-screen h2 { font-family:'Syne',sans-serif!important; font-weight:800; font-size:2rem; color:var(--text-main)!important; margin:0 0 8px!important; }
.welcome-screen p { color:var(--text-muted); font-size:0.95rem; max-width:500px; margin:0 auto; line-height:1.8; }

/* HEADER Y DEMÁS UI */
.hud-header{display:flex;align-items:center;padding:10px 0 20px;border-bottom:1px solid var(--glass-brd);margin-bottom:20px;}
.hud-title h1{font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.8rem!important;color:var(--text-main)!important;margin:0!important;}
.hud-title h1 em{font-style:normal;color:var(--teal);}
.hud-meta{margin-left:auto;text-align:right;font-family:'Space Mono',monospace;font-size:0.6rem;color:var(--text-muted);}

/* ── PANEL DE BOTONES FUTURISTA (NAVEGACIÓN) ── */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(0, 229, 216, 0.04) !important;
    color: var(--teal) !important;
    border: 1px solid rgba(0, 229, 216, 0.2) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.70rem !important;
    font-weight: 700 !important;
    height: 45px !important;
    border-radius: 6px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 10px rgba(0,0,0,0.5) !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--teal) !important;
    color: var(--void) !important;
    border: 1px solid var(--teal) !important;
    box-shadow: 0 0 15px rgba(0, 229, 216, 0.5) !important;
    transform: translateY(-2px) !important;
}

/* CHIPS SINTOMAS */
div[data-testid="column"] .stButton>button {
    font-family:'DM Sans',sans-serif!important;font-size:0.72rem!important;font-weight:500!important;
    padding:6px 4px!important;letter-spacing:0.3px!important;text-transform:none!important;
    border-color:rgba(0,229,216,0.25)!important;color:var(--text-muted)!important;border-radius:20px!important;
    transition:all 0.18s ease!important;white-space:nowrap; height: auto !important; box-shadow: none !important; background: transparent !important;
}
div[data-testid="column"] .stButton>button:hover {
    border-color:var(--teal)!important;color:var(--teal)!important;background:rgba(0,229,216,0.06)!important;
    box-shadow:0 0 10px rgba(0,229,216,0.2)!important;transform:translateY(-1px)!important;
}

.model-badge{display:flex;align-items:center;justify-content:center; gap:7px;background:rgba(0,229,216,0.05);border:1px solid rgba(0,229,216,0.18);border-radius:6px;padding:6px 12px;font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--teal);letter-spacing:1px;text-transform:uppercase;margin:8px 0 2px;}
.s-section{font-family:'Space Mono',monospace;font-size:0.58rem;font-weight:700;color:var(--teal);text-transform:uppercase;letter-spacing:2px;padding:12px 0 5px;border-top:1px solid var(--glass-brd);margin-top:8px;}
.s-info{background:rgba(0,229,216,0.03);border:1px solid var(--glass-brd);border-radius:8px;padding:10px 13px;font-size:0.8rem;color:var(--text-muted);line-height:1.65;margin-top:6px;}
.session-card{background:var(--panel);border:1px solid var(--glass-brd);border-radius:10px;padding:12px 14px 12px 18px;margin-top:8px;position:relative;}
.session-card::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:linear-gradient(180deg,var(--teal),var(--cyan));}
.sc-label{font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1.5px;}
.sc-value{font-size:0.88rem;color:var(--text-main);font-weight:500;margin-top:1px;}

[data-testid="stSidebar"] label, .stTextInput label {font-family:'Space Mono',monospace!important;font-size:0.62rem!important;color:var(--text-muted)!important;text-transform:uppercase;}
[data-testid="stSidebar"] input, .stTextInput input, textarea {background:rgba(5,10,20,0.9)!important;color:var(--teal)!important;border:1px solid var(--glass-brd)!important;border-radius:8px!important;font-family:'Space Mono',monospace!important;font-size:0.82rem!important;}
[data-testid="stSidebar"] input:focus, textarea:focus{border-color:var(--teal)!important;box-shadow:0 0 0 2px rgba(0,229,216,0.12)!important;}

[data-testid="stChatMessage"]{background:var(--panel)!important;border:1px solid var(--glass-brd)!important;border-radius:12px!important;backdrop-filter:blur(12px);}[data-testid="stImage"] img{border-radius:10px!important;border:1px solid var(--glass-brd)!important;}
[data-testid="stFileUploader"]{background:rgba(5,10,20,0.8)!important;border:1px dashed var(--glass-brd)!important;}[data-testid="stExpander"] { background: var(--panel) !important; border: 1px solid var(--glass-brd) !important; border-radius: 10px !important; margin-bottom: 8px !important; }
[data-testid="stExpander"] summary { font-family: 'Space Mono', monospace !important; font-size: 0.65rem !important; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 1.5px; }

.status-strip{display:flex;align-items:center;gap:16px;margin-bottom:14px;padding:8px 16px;background:var(--panel);border:1px solid var(--glass-brd);border-radius:8px;font-family:'Space Mono',monospace;font-size:0.62rem;color:var(--text-muted);flex-wrap:wrap;}
.indicator{display:flex;align-items:center;gap:6px;}
.s-dot{width:7px;height:7px;border-radius:50%;}
.dot-active{background:var(--green-ok);box-shadow:0 0 6px var(--green-ok);animation:blink 1.4s ease-in-out infinite;}
.dot-inactive{background:var(--text-muted);}

::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:var(--void);}::-webkit-scrollbar-thumb{background:var(--teal-dim);border-radius:2px;}

/* ── RESPONSIVIDAD PARA TELÉFONOS CELULARES ── */
@media (max-width: 768px) {
    .eye-hero-wrap { transform: scale(0.65); margin-bottom: -10px; margin-top: -20px; }
    .welcome-screen { padding: 30px 15px; margin-top: 10px; }
    .hud-header { flex-direction: column; text-align: center; gap: 8px; padding-bottom: 10px; }
    .hud-meta { margin: 0 auto; text-align: center; }
    .status-strip { justify-content: center; text-align: center; gap: 10px; }
    .ws-corner { width: 20px; height: 20px; }
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# INIT
# ──────────────────────────────────────────────────────────────────────────────
database.init_db()

# DIAGNÓSTICO DEL MODELO DE IA
if modelo_vision.ERROR_CARGA:
    st.error(modelo_vision.ERROR_CARGA, icon="🚨")

defaults = {
    "messages":[], "session_active": False, "doctor_name": "",
    "patient_name": "", "session_idx": 0, "view": "chat",
    "patient_id": None, "visita_id": None, "paciente_data": {},
    "total_consultas": 0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "current_images_bytes" not in st.session_state:
    st.session_state.current_images_bytes =[]

# ──────────────────────────────────────────────────────────────────────────────
# STRINGS DE HTML
# ──────────────────────────────────────────────────────────────────────────────
SIDEBAR_LOGO_HTML = f"""
<div class="sidebar-logo">
    <div class="eye-sidebar-wrap">
        <div class="eye-sidebar-ring"></div>
        <div class="eye-sidebar-inner">
            <img src="{EYE_SRC}" class="eye-sidebar-img">
            <div class="scan-line-small"></div>
        </div>
    </div>
    <div class="logo-title">Ophthalm<span>AI</span></div>
    <div class="logo-sub">Hospital Rísquez · Caracas</div>
</div>
<div class="model-badge">
    <div class="mb-dot"></div> EfficientNetB0 · Nube AI
</div>
"""

WELCOME_SCREEN_HTML = f"""
<div class="welcome-screen">
    <div class="ws-tr"></div><div class="ws-bl"></div>
    <div class="eye-hero-wrap">
        <div class="eye-hero-ring1"></div>
        <div class="eye-hero-ring2"></div>
        <div class="eye-hero-inner">
            <img src="{EYE_SRC}" class="eye-hero-img">
            <div class="scan-line-large"></div>
        </div>
    </div>
    <h2>OphthalmAI en espera</h2>
    <p>Sistema diagnóstico asistido por Red Neuronal Convolucional (EfficientNetB0). Especializado en la detección de <strong style="color:var(--teal);">Úlceras Corneales</strong> y <strong style="color:var(--teal);">Uveítis</strong>.</p>
    <br><span style="font-family:Space Mono, monospace; color:var(--teal); font-size:0.8rem; letter-spacing: 2px;">// INICIE SESIÓN EN EL PANEL LATERAL PARA COMENZAR //</span>
</div>
"""

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(SIDEBAR_LOGO_HTML, unsafe_allow_html=True)

    st.markdown('<div class="s-section">Panel de Control</div>', unsafe_allow_html=True)
    
    nc = st.columns(2)
    if nc[0].button("💬 Consulta", use_container_width=True):
        st.session_state.view = "chat"; st.rerun()
    if nc[1].button("📋 Registro", use_container_width=True):
        st.session_state.view = "registro"; st.rerun()
    
    nc2 = st.columns(2)
    if nc2[0].button("📂 Historial", use_container_width=True):
        st.session_state.view = "historial"; st.rerun()
    if nc2[1].button("📊 Dashboard", use_container_width=True):
        st.session_state.view = "dashboard"; st.rerun()

    st.markdown('<div class="s-section">Datos de la Consulta</div>', unsafe_allow_html=True)
    doctor_input  = st.text_input("Nombre del Doctor",  value=st.session_state.doctor_name,  disabled=st.session_state.session_active)
    patient_input = st.text_input("Paciente",           value=st.session_state.patient_name, disabled=st.session_state.session_active)

    if not st.session_state.session_active:
        if st.button("▶ INICIAR SESIÓN", use_container_width=True):
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
        if st.button("⏹ FINALIZAR CONSULTA", use_container_width=True):
            if "current_images_bytes" in st.session_state:
                del st.session_state.current_images_bytes
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
            st.session_state.current_images_bytes = [f.getvalue() for f in uploaded_files]
            cols = st.columns(min(len(uploaded_files), 2))
            for i, f in enumerate(uploaded_files):
                cols[i % 2].image(f, use_container_width=True)
            st.markdown('<div style="color:var(--teal);text-align:center;font-size:0.6rem;margin-top:5px;">✓ IMÁGENES CARGADAS EN MEMORIA</div>', unsafe_allow_html=True)
        elif "current_images_bytes" not in st.session_state:
            st.session_state.current_images_bytes =[]

    # ── PEDACITO RECUPERADO: ESPECIALIDADES MÉDICAS ──
    st.markdown('<div class="s-section">Especialidades</div>', unsafe_allow_html=True)
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
st.markdown("""
<div class="hud-header">
    <div class="hud-title">
        <h1>Ophthalm<em>AI</em></h1>
        <div class="hud-subtitle">Úlceras Corneales & Uveítis · Hospital Rísquez</div>
    </div>
    <div class="hud-meta">
        <div class="ver">v3.8-CLOUD</div>
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
        st.markdown(WELCOME_SCREEN_HTML, unsafe_allow_html=True)

    else:
        p = st.session_state.paciente_data
        ced_h = f'· CÉD:<span style="color:var(--text-main);"> {p["cedula"]}</span>' if p.get("cedula") else ""
        
        n_imgs = len(st.session_state.get("current_images_bytes",[]))
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

        if st.session_state.patient_id:
            visitas = database.obtener_visitas_paciente(st.session_state.patient_id)
            if len(visitas) > 1:
                with st.expander(f"📂 {len(visitas)-1} visita(s) previa(s)", expanded=False):
                    for v in visitas[1:]:
                        # LÍNEA REPARADA AQUÍ:
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
            except Exception:
                pass 

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

            lista_imgs = st.session_state.get("current_images_bytes",[])

            with st.chat_message("assistant"):
                ph = st.empty()
                ph.markdown('<span style="color:var(--teal);font-family:Space Mono,monospace;font-size:0.7rem;">// Procesando con EfficientNetB0...</span>', unsafe_allow_html=True)
                time.sleep(0.25)
                try:
                    respuesta_ia = modelo_vision.analizar_imagen_y_sintomas(lista_imgs, prompt)
                except Exception as e:
                    respuesta_ia = f"⚠️ Error: `{e}`"

                full_response = ""
                tokens = re.split(r'(\s+)', respuesta_ia) 
                
                for token in tokens:
                    full_response += token
                    ph.markdown(full_response + "▌")
                    time.sleep(0.02 if token.strip() else 0) 
                    
                ph.markdown(full_response.strip())

            st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})
            st.session_state.total_consultas += 1

            try:
                tiene_img = bool(lista_imgs)
                database.registrar_consulta(
                    doctor_nombre=st.session_state.doctor_name,
                    paciente_nombre=st.session_state.patient_name,
                    pregunta_doctor=prompt,
                    respuesta_ia=full_response.strip(),
                    tiene_imagen=tiene_img,
                    visita_id=st.session_state.visita_id,
                    paciente_id=st.session_state.patient_id
                )
                
                if any(d in full_response for d in["Úlcera Corneal", "Uveítis Anterior", "Segmento Sano", "Imagen dudosa"]):
                    diag_match = re.search(r'Impresión Diagnóstica:(.*?)(💊|⚠️|$)', full_response, re.DOTALL)
                    diag_text = diag_match.group(1).strip() if diag_match else "Detectado por IA"
                    database.actualizar_visita(
                        visita_id=st.session_state.visita_id,
                        diagnostico_ia=diag_text[:250],
                        tiene_imagen=tiene_img
                    )
            except Exception:
                pass


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
