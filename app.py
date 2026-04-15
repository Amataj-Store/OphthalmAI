import streamlit as st
import time
import database
import modelo_vision

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="OphthalmAI · Hospital Rísquez",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS – ESTÉTICA HUD MÉDICO FUTURISTA
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

:root {
    --void:       #020812;
    --navy-mid:   #080f20;
    --panel:      rgba(8, 20, 45, 0.85);
    --teal:       #00e5d8;
    --teal-dim:   #00857d;
    --cyan:       #00cfff;
    --amber:      #ffb547;
    --green-ok:   #00e59b;
    --text-main:  #ddeeff;
    --text-muted: #4a7090;
    --glass-brd:  rgba(0, 229, 216, 0.14);
    --scan-line:  rgba(0, 229, 216, 0.025);
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--void) !important;
    background-image:
        repeating-linear-gradient(0deg, transparent, transparent 2px, var(--scan-line) 2px, var(--scan-line) 4px),
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,229,216,0.07) 0%, transparent 65%),
        radial-gradient(ellipse 40% 30% at 90% 90%, rgba(0,207,255,0.04) 0%, transparent 55%);
    color: var(--text-main) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--glass-brd) !important;
    background-image: linear-gradient(180deg, rgba(0,229,216,0.04) 0%, transparent 35%) !important;
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }

.sidebar-logo {
    text-align: center; padding: 24px 16px 16px;
    border-bottom: 1px solid var(--glass-brd);
    margin-bottom: 4px; position: relative;
}
.sidebar-logo::before {
    content: ''; position: absolute; top: 0; left: 50%;
    transform: translateX(-50%); width: 60%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--teal), transparent);
}
.svg-eye-wrap {
    margin-bottom: 10px;
    filter: drop-shadow(0 0 10px rgba(0,229,216,0.6)) drop-shadow(0 0 24px rgba(0,229,216,0.3));
    animation: eye-pulse 3.5s ease-in-out infinite;
}
.svg-eye { width: 100%; max-width: 130px; display: block; margin: 0 auto; }
@keyframes eye-pulse {
    0%,100% { filter: drop-shadow(0 0 12px var(--teal)) drop-shadow(0 0 24px rgba(0,229,216,0.3)); }
    50%     { filter: drop-shadow(0 0 22px var(--teal)) drop-shadow(0 0 44px rgba(0,229,216,0.6)); }
}
.logo-title { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.25rem; color: var(--text-main); letter-spacing: 1px; }
.logo-title span { color: var(--teal); }
.logo-sub { font-family: 'Space Mono', monospace; font-size: 0.6rem; color: var(--text-muted); letter-spacing: 2.5px; text-transform: uppercase; margin-top: 3px; }

.model-badge {
    display: flex; align-items: center; gap: 7px;
    background: rgba(0,229,216,0.05); border: 1px solid rgba(0,229,216,0.18);
    border-radius: 6px; padding: 6px 12px;
    font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--teal);
    letter-spacing: 1px; text-transform: uppercase; margin: 10px 0 2px;
}
.mb-dot { width: 6px; height: 6px; background: var(--green-ok); border-radius: 50%; box-shadow: 0 0 6px var(--green-ok); flex-shrink: 0; }

.s-section {
    font-family: 'Space Mono', monospace; font-size: 0.58rem; font-weight: 700;
    color: var(--teal); text-transform: uppercase; letter-spacing: 2px;
    padding: 14px 0 5px; border-top: 1px solid var(--glass-brd); margin-top: 10px;
}
.s-section::before { content: '// '; opacity: 0.5; }

.s-info {
    background: rgba(0,229,216,0.03); border: 1px solid var(--glass-brd);
    border-radius: 8px; padding: 10px 13px;
    font-size: 0.8rem; color: var(--text-muted); line-height: 1.65; margin-top: 6px;
}
.s-info strong { color: var(--text-main); font-weight: 500; }

.session-card {
    background: linear-gradient(135deg, rgba(0,229,216,0.07), rgba(0,207,255,0.03));
    border: 1px solid var(--glass-brd); border-radius: 10px;
    padding: 12px 14px 12px 18px; margin-top: 8px; position: relative; overflow: hidden;
}
.session-card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, var(--teal), var(--cyan));
}
.sc-label { font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; }
.sc-value { font-size: 0.88rem; color: var(--text-main); font-weight: 500; margin-top: 1px; }

[data-testid="stSidebar"] label {
    font-family: 'Space Mono', monospace !important; font-size: 0.62rem !important;
    color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 1.2px;
}
[data-testid="stSidebar"] input {
    background: rgba(5,13,26,0.9) !important; color: var(--teal) !important;
    border: 1px solid var(--glass-brd) !important; border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.82rem !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 2px rgba(0,229,216,0.12) !important;
}
input::placeholder { color: #1e3550 !important; }

.stButton > button {
    background: transparent !important; color: var(--teal) !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.8rem !important;
    border: 1px solid var(--teal) !important; border-radius: 8px !important;
    padding: 10px 20px !important; width: 100% !important;
    letter-spacing: 1.5px; text-transform: uppercase; transition: all 0.22s ease !important;
}
.stButton > button:hover {
    color: var(--void) !important; background: var(--teal) !important;
    box-shadow: 0 0 22px rgba(0,229,216,0.5), 0 0 44px rgba(0,229,216,0.2) !important;
    transform: translateY(-1px) !important;
}

.hud-header {
    display: flex; align-items: center; gap: 20px;
    padding: 22px 0 16px; border-bottom: 1px solid var(--glass-brd);
    margin-bottom: 18px; position: relative;
}
.hud-header::after {
    content: ''; position: absolute; bottom: -1px; left: 0;
    width: 130px; height: 1px;
    background: linear-gradient(90deg, var(--teal), transparent);
}
.hud-eye {
    width: 62px; height: 62px; border: 1px solid var(--glass-brd); border-radius: 14px;
    display: flex; align-items: center; justify-content: center; font-size: 30px;
    background: linear-gradient(135deg, rgba(0,229,216,0.08), transparent);
    position: relative; flex-shrink: 0; animation: eye-pulse 3.5s ease-in-out infinite;
}
.hud-eye::before, .hud-eye::after {
    content: ''; position: absolute; border-radius: 14px;
    border: 1px solid rgba(0,229,216,0.3);
    animation: radar-ring 2.5s ease-out infinite;
}
.hud-eye::after { animation-delay: 1.25s; }
@keyframes radar-ring { 0% { inset: 0; opacity: 0.6; } 100% { inset: -14px; opacity: 0; } }

.hud-title h1 {
    font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
    font-size: 2rem !important; color: var(--text-main) !important;
    margin: 0 !important; letter-spacing: -0.5px; line-height: 1;
}
.hud-title h1 em { font-style: normal; color: var(--teal); text-shadow: 0 0 20px rgba(0,229,216,0.5); }
.hud-subtitle { font-family: 'Space Mono', monospace; font-size: 0.6rem; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase; margin-top: 6px; }
.hud-meta { margin-left: auto; text-align: right; font-family: 'Space Mono', monospace; font-size: 0.58rem; color: var(--text-muted); line-height: 1.9; }
.hud-meta .ver { color: var(--teal); font-weight: 700; }

.status-strip {
    display: flex; align-items: center; gap: 18px; margin-bottom: 16px;
    padding: 8px 16px; background: var(--panel);
    border: 1px solid var(--glass-brd); border-radius: 8px;
    font-family: 'Space Mono', monospace; font-size: 0.62rem; color: var(--text-muted);
}
.indicator { display: flex; align-items: center; gap: 6px; }
.s-dot { width: 7px; height: 7px; border-radius: 50%; }
.dot-active   { background: var(--green-ok); box-shadow: 0 0 6px var(--green-ok); animation: blink 1.4s ease-in-out infinite; }
.dot-inactive { background: var(--text-muted); }
.dot-img      { background: var(--amber); box-shadow: 0 0 6px var(--amber); }
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

[data-testid="stChatMessage"] {
    background: var(--panel) !important; border: 1px solid var(--glass-brd) !important;
    border-radius: 12px !important; padding: 16px 20px !important;
    margin-bottom: 10px !important; backdrop-filter: blur(12px); position: relative;
}
[data-testid="stChatMessage"]::before {
    content: ''; position: absolute; top: 0; left: 16px;
    width: 40px; height: 1px;
    background: linear-gradient(90deg, var(--teal), transparent);
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
[data-testid="stChatInput"] textarea::placeholder { color: #1e3550 !important; }
[data-testid="stChatInput"] textarea:focus { border-color: var(--teal) !important; box-shadow: 0 0 0 1px rgba(0,229,216,0.18) !important; }

[data-testid="stImage"] img { border-radius: 10px !important; border: 1px solid var(--glass-brd) !important; box-shadow: 0 0 20px rgba(0,229,216,0.08) !important; }
[data-testid="stFileUploader"] { background: rgba(5,13,26,0.8) !important; border: 1px dashed var(--glass-brd) !important; border-radius: 10px !important; }

.welcome-screen {
    text-align: center; padding: 70px 40px;
    border: 1px solid var(--glass-brd); border-radius: 20px; margin-top: 20px;
    background: linear-gradient(135deg, rgba(0,229,216,0.03) 0%, transparent 50%), var(--panel);
    position: relative; overflow: hidden;
}
.welcome-screen::before {
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: conic-gradient(transparent 0deg, rgba(0,229,216,0.025) 60deg, transparent 120deg);
    animation: rotate-bg 14s linear infinite;
}
@keyframes rotate-bg { from{transform:rotate(0deg);} to{transform:rotate(360deg);} }
.w-eye { font-size: 64px; position: relative; z-index: 1; filter: drop-shadow(0 0 24px var(--teal)); animation: eye-pulse 3.5s ease-in-out infinite; display: block; margin-bottom: 16px; }
.welcome-screen h2 { font-family: 'Syne', sans-serif !important; font-weight: 800; font-size: 1.7rem; color: var(--text-main) !important; margin: 0 0 8px !important; position: relative; z-index: 1; }
.welcome-screen p { color: var(--text-muted); font-size: 0.9rem; max-width: 440px; margin: 0 auto; line-height: 1.7; position: relative; z-index: 1; }
.w-tag { display: inline-block; margin-top: 20px; font-family: 'Space Mono', monospace; font-size: 0.62rem; color: var(--teal); border: 1px solid var(--glass-brd); border-radius: 4px; padding: 4px 14px; letter-spacing: 1.5px; position: relative; z-index: 1; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb { background: var(--teal-dim); border-radius: 2px; }
[data-testid="stAlert"] { border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-size: 0.76rem !important; }

/* ── Symptom chips ──────────────────────────── */
div[data-testid="column"] .stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.72rem !important; font-weight: 500 !important;
    padding: 6px 4px !important; letter-spacing: 0.3px !important;
    text-transform: none !important; border-color: rgba(0,229,216,0.3) !important;
    color: var(--text-muted) !important; border-radius: 20px !important;
    transition: all 0.18s ease !important; white-space: nowrap;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: var(--teal) !important; color: var(--teal) !important;
    background: rgba(0,229,216,0.06) !important; box-shadow: 0 0 10px rgba(0,229,216,0.2) !important;
    transform: translateY(-1px) !important;
}
/* ── Expander ────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--panel) !important; border: 1px solid var(--glass-brd) !important; border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Space Mono', monospace !important; font-size: 0.65rem !important;
    color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 1.5px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INICIALIZACIÓN
# ─────────────────────────────────────────────
database.init_db()

defaults = {
    "messages":        [],
    "session_active":  False,
    "doctor_name":     "",
    "patient_name":    "",
    "total_consultas": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:

    st.markdown("""
    <div class="sidebar-logo">
        <div class="svg-eye-wrap">
          <svg class="svg-eye" viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <radialGradient id="irisG" cx="50%" cy="50%" r="50%">
                <stop offset="0%"   stop-color="#002a28"/>
                <stop offset="40%"  stop-color="#005f5a"/>
                <stop offset="70%"  stop-color="#00857d"/>
                <stop offset="100%" stop-color="#00e5d8"/>
              </radialGradient>
              <radialGradient id="pupilG" cx="40%" cy="38%" r="50%">
                <stop offset="0%"   stop-color="#1a3a38"/>
                <stop offset="100%" stop-color="#020812"/>
              </radialGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="2.5" result="blur"/>
                <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
              </filter>
              <filter id="outerGlow">
                <feGaussianBlur stdDeviation="4" result="blur"/>
                <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
              </filter>
              <clipPath id="eyeClip">
                <ellipse cx="50" cy="30" rx="46" ry="26"/>
              </clipPath>
            </defs>
            <!-- Outer glow halo -->
            <ellipse cx="50" cy="30" rx="48" ry="28" fill="none"
              stroke="#00e5d8" stroke-width="0.4" opacity="0.25" filter="url(#outerGlow)"/>
            <!-- White of eye with gradient -->
            <ellipse cx="50" cy="30" rx="46" ry="26"
              fill="url(#eyeClip)"
              style="fill: radial-gradient(ellipse, #d0eef0 0%, #8ecfd4 60%, #3a8a8f 100%)"/>
            <ellipse cx="50" cy="30" rx="46" ry="26" fill="#c8eaec" clip-path="url(#eyeClip)"/>
            <!-- Iris -->
            <circle cx="50" cy="30" r="16" fill="url(#irisG)" filter="url(#glow)" clip-path="url(#eyeClip)"/>
            <!-- Iris texture lines -->
            <g clip-path="url(#eyeClip)" opacity="0.35">
              <line x1="50" y1="14" x2="50" y2="46" stroke="#00e5d8" stroke-width="0.4"/>
              <line x1="34" y1="19" x2="66" y2="41" stroke="#00e5d8" stroke-width="0.4"/>
              <line x1="34" y1="41" x2="66" y2="19" stroke="#00e5d8" stroke-width="0.4"/>
              <line x1="27" y1="30" x2="73" y2="30" stroke="#00e5d8" stroke-width="0.4"/>
              <circle cx="50" cy="30" r="10" fill="none" stroke="#00cfff" stroke-width="0.5"/>
              <circle cx="50" cy="30" r="13.5" fill="none" stroke="#00857d" stroke-width="0.4"/>
            </g>
            <!-- Pupil -->
            <circle cx="50" cy="30" r="7" fill="url(#pupilG)" clip-path="url(#eyeClip)"/>
            <!-- Pupil animated dilation ring -->
            <circle cx="50" cy="30" r="7" fill="none"
              stroke="#00e5d8" stroke-width="0.6" opacity="0.5" clip-path="url(#eyeClip)">
              <animate attributeName="r" values="7;9;7" dur="3s" repeatCount="indefinite"/>
              <animate attributeName="opacity" values="0.5;0.1;0.5" dur="3s" repeatCount="indefinite"/>
            </circle>
            <!-- Corneal reflex (light glint) -->
            <ellipse cx="44" cy="24" rx="2.5" ry="1.5" fill="white" opacity="0.7" transform="rotate(-20,44,24)"/>
            <ellipse cx="47" cy="23" rx="0.8" ry="0.5" fill="white" opacity="0.4"/>
            <!-- Eyelid edges -->
            <path d="M4,30 Q50,4 96,30" fill="none" stroke="#002830" stroke-width="1.5" opacity="0.6"/>
            <path d="M4,30 Q50,56 96,30" fill="none" stroke="#002830" stroke-width="1.5" opacity="0.6"/>
            <!-- Teal edge glow -->
            <ellipse cx="50" cy="30" rx="46" ry="26" fill="none"
              stroke="#00e5d8" stroke-width="1" opacity="0.5" filter="url(#glow)"/>
            <!-- Radar pulse rings -->
            <ellipse cx="50" cy="30" rx="46" ry="26" fill="none"
              stroke="#00e5d8" stroke-width="1.5" opacity="0">
              <animate attributeName="rx" values="16;54" dur="2.8s" repeatCount="indefinite"/>
              <animate attributeName="ry" values="16;30" dur="2.8s" repeatCount="indefinite"/>
              <animate attributeName="opacity" values="0.7;0" dur="2.8s" repeatCount="indefinite"/>
            </ellipse>
            <ellipse cx="50" cy="30" rx="46" ry="26" fill="none"
              stroke="#00cfff" stroke-width="1" opacity="0">
              <animate attributeName="rx" values="16;54" dur="2.8s" begin="1.4s" repeatCount="indefinite"/>
              <animate attributeName="ry" values="16;30" dur="2.8s" begin="1.4s" repeatCount="indefinite"/>
              <animate attributeName="opacity" values="0.5;0" dur="2.8s" begin="1.4s" repeatCount="indefinite"/>
            </ellipse>
          </svg>
        </div>
        <div class="logo-title">Ophthalm<span>AI</span></div>
        <div class="logo-sub">Hospital Rísquez · Caracas</div>
    </div>
    <div class="model-badge">
        <div class="mb-dot"></div>
        Motor: EfficientNetB0 · Local · Sin Internet
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="s-section">Datos de la Consulta</div>', unsafe_allow_html=True)

    doctor_input = st.text_input(
        "Nombre del Doctor",
        placeholder="Dr. García",
        value=st.session_state.doctor_name,
        disabled=st.session_state.session_active,
    )
    patient_input = st.text_input(
        "Nombre del Paciente",
        placeholder="Juan Pérez",
        value=st.session_state.patient_name,
        disabled=st.session_state.session_active,
    )

    if not st.session_state.session_active:
        if st.button("▶  INICIAR SESIÓN DEL PACIENTE"):
            if doctor_input.strip() and patient_input.strip():
                st.session_state.doctor_name     = doctor_input.strip()
                st.session_state.patient_name    = patient_input.strip()
                st.session_state.session_active  = True
                st.session_state.messages        = []
                st.session_state.total_consultas = 0
                bienvenida = (
                    f"Sistema en línea. Bienvenido, **Dr. {st.session_state.doctor_name}**.\n\n"
                    f"Consulta iniciada para el paciente: **{st.session_state.patient_name}**.\n\n"
                    "El módulo **EfficientNetB0** está activo y listo para analizar imágenes del segmento anterior. "
                    "Puede describir los síntomas del paciente, sus antecedentes, o adjuntar una fotografía para comenzar el análisis.\n\n"
                    "¿Con qué empezamos, Doctor?"
                )
                st.session_state.messages.append({"role": "assistant", "content": bienvenida})
                st.rerun()
            else:
                st.error("Complete ambos campos para continuar.")
    else:
        if st.button("⏹  FINALIZAR CONSULTA"):
            st.session_state.session_active  = False
            st.session_state.messages        = []
            st.session_state.doctor_name     = ""
            st.session_state.patient_name    = ""
            st.session_state.total_consultas = 0
            st.rerun()

    if st.session_state.session_active:
        st.markdown(f"""
        <div class="session-card">
            <div class="sc-label">Doctor</div>
            <div class="sc-value">{st.session_state.doctor_name}</div>
            <div class="sc-label" style="margin-top:8px;">Paciente</div>
            <div class="sc-value">{st.session_state.patient_name}</div>
            <div class="sc-label" style="margin-top:8px;">Interacciones</div>
            <div class="sc-value" style="color:var(--teal);">{st.session_state.total_consultas}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="s-section">Imagen del Segmento Anterior</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Subir fotografías oculares",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        disabled=not st.session_state.session_active,
        label_visibility="collapsed",
    )
    if uploaded_files:
        n = len(uploaded_files)
        cols = st.columns(min(n, 2))
        for i, f in enumerate(uploaded_files):
            cols[i % 2].image(f, use_container_width=True)
        st.markdown(
            f'<div style="font-family:Space Mono,monospace;font-size:0.6rem;'
            f'color:var(--teal);text-align:center;margin-top:6px;letter-spacing:1px;">'
            f'✓ {n} IMAGEN(ES) EN BUFFER · EfficientNet ACTIVA</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="s-section">Áreas Diagnósticas</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="s-info">
        🔵 <strong>Úlcera Corneal</strong><br>
        &emsp;Bacteriana · Fúngica · Viral<br><br>
        🟠 <strong>Uveítis</strong><br>
        &emsp;Anterior · Intermedia · Posterior<br><br>
        <span style="color:#1e3d55;font-family:Space Mono,monospace;font-size:0.6rem;">
        REF: AAO · ESCRS · SVO
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Historial reciente ────────────────────
    st.markdown('<div class="s-section">Historial de Consultas</div>', unsafe_allow_html=True)
    try:
        consultas = database.obtener_historial_paciente(st.session_state.patient_name) if st.session_state.patient_name else []
        if consultas:
            with st.expander(f"Ver {len(consultas)} consulta(s) previas", expanded=False):
                for c in consultas[:5]:
                    st.markdown(f"""
                    <div style="font-family:Space Mono,monospace;font-size:0.6rem;
                    color:var(--text-muted);border-bottom:1px solid var(--glass-brd);
                    padding:6px 0;line-height:1.6;">
                        <span style="color:var(--teal);">{c.get('fecha_hora','')[:16]}</span><br>
                        <span style="color:var(--text-main);">Doctor:</span> {c.get('doctor_nombre','')}<br>
                        <span style="color:var(--text-main);">P:</span> {c.get('pregunta_doctor','')[:60]}...
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="s-info" style="font-size:0.72rem;">Sin consultas previas para este paciente.</div>', unsafe_allow_html=True)
    except:
        pass

    st.markdown("""
    <div style="margin-top:20px;padding:10px 12px;border-top:1px solid rgba(0,229,216,0.07);
    font-family:Space Mono,monospace;font-size:0.56rem;color:#1e3550;text-align:center;line-height:1.8;">
        CNN · EfficientNetB0 · Transfer Learning<br>
        Procesamiento 100% local · Sin API<br>
        <span style="color:#254060;">© Tesis UCV · Hospital Rísquez</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ÁREA PRINCIPAL
# ─────────────────────────────────────────────

st.markdown("""
<div class="hud-header">
    <div class="hud-eye">
      <svg viewBox="0 0 100 60" xmlns="http://www.w3.org/2000/svg" style="width:62px;height:auto;display:block;">
        <defs>
          <radialGradient id="iG2" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#002a28"/>
            <stop offset="50%" stop-color="#005f5a"/>
            <stop offset="100%" stop-color="#00e5d8"/>
          </radialGradient>
          <radialGradient id="pG2" cx="40%" cy="38%" r="50%">
            <stop offset="0%" stop-color="#1a3a38"/>
            <stop offset="100%" stop-color="#020812"/>
          </radialGradient>
          <filter id="g2"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          <clipPath id="eC2"><ellipse cx="50" cy="30" rx="46" ry="26"/></clipPath>
        </defs>
        <ellipse cx="50" cy="30" rx="46" ry="26" fill="#c2e8eb" clip-path="url(#eC2)"/>
        <circle cx="50" cy="30" r="16" fill="url(#iG2)" filter="url(#g2)" clip-path="url(#eC2)"/>
        <g clip-path="url(#eC2)" opacity="0.3">
          <line x1="50" y1="14" x2="50" y2="46" stroke="#00e5d8" stroke-width="0.5"/>
          <line x1="34" y1="19" x2="66" y2="41" stroke="#00e5d8" stroke-width="0.5"/>
          <line x1="34" y1="41" x2="66" y2="19" stroke="#00e5d8" stroke-width="0.5"/>
          <circle cx="50" cy="30" r="10" fill="none" stroke="#00cfff" stroke-width="0.6"/>
        </g>
        <circle cx="50" cy="30" r="7" fill="url(#pG2)" clip-path="url(#eC2)"/>
        <circle cx="50" cy="30" r="7" fill="none" stroke="#00e5d8" stroke-width="0.8" opacity="0.6" clip-path="url(#eC2)">
          <animate attributeName="r" values="7;9.5;7" dur="3s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.6;0.1;0.6" dur="3s" repeatCount="indefinite"/>
        </circle>
        <ellipse cx="44" cy="24" rx="2.5" ry="1.5" fill="white" opacity="0.75" transform="rotate(-20,44,24)"/>
        <ellipse cx="50" cy="30" rx="46" ry="26" fill="none" stroke="#00e5d8" stroke-width="1.2" opacity="0.6" filter="url(#g2)"/>
        <ellipse cx="50" cy="30" rx="16" ry="16" fill="none" stroke="#00e5d8" stroke-width="1.5" opacity="0">
          <animate attributeName="rx" values="16;52" dur="2.5s" repeatCount="indefinite"/>
          <animate attributeName="ry" values="16;28" dur="2.5s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.8;0" dur="2.5s" repeatCount="indefinite"/>
        </ellipse>
      </svg>
    </div>
    <div class="hud-title">
        <h1>Ophthalm<em>AI</em></h1>
        <div class="hud-subtitle">Sistema de Apoyo Diagnóstico · Úlceras Corneales & Uveítis</div>
    </div>
    <div class="hud-meta">
        <div class="ver">v3.0-LOCAL</div>
        <div>EfficientNetB0</div>
        <div>Multi-imagen · NLP</div>
        <div>SQLite · $0 API</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.session_active:
    n_imgs = len(uploaded_files) if uploaded_files else 0
    img_html = (
        f'<div class="indicator"><div class="s-dot dot-img"></div>{n_imgs} IMAGEN(ES) EN BUFFER</div>'
        if n_imgs > 0 else
        '<div class="indicator"><div class="s-dot dot-inactive"></div>SIN IMAGEN</div>'
    )
    st.markdown(f"""
    <div class="status-strip">
        <div class="indicator"><div class="s-dot dot-active"></div>SESIÓN ACTIVA</div>
        <div>PACIENTE: <span style="color:var(--text-main);">{st.session_state.patient_name.upper()}</span></div>
        <div>DR: <span style="color:var(--text-main);">{st.session_state.doctor_name.upper()}</span></div>
        {img_html}
        <div style="margin-left:auto;">CNN: <span style="color:var(--green-ok);">ONLINE</span></div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="status-strip">
        <div class="indicator"><div class="s-dot dot-inactive"></div>STANDBY</div>
        <div style="color:#1e3550;">Ingrese datos del doctor y paciente para comenzar</div>
        <div style="margin-left:auto;">CNN: <span style="color:var(--green-ok);">READY</span></div>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.session_active:
    st.markdown("""
    <div class="welcome-screen">
        <span class="w-eye">👁️</span>
        <h2>OphthalmAI en espera</h2>
        <p>
            Sistema de diagnóstico asistido por Red Neuronal Convolucional (EfficientNetB0)
            con Transfer Learning. Procesamiento 100% local, sin internet, costo cero.
        </p>
        <div class="w-tag">// MOTOR LOCAL · PRIVACIDAD TOTAL · COSTO $0 //</div>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.session_active:

    # ── Chips de síntomas rápidos ──────────────
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.58rem;color:var(--text-muted);letter-spacing:1px;margin-bottom:6px;">// SÍNTOMAS RÁPIDOS</div>', unsafe_allow_html=True)
    chip_cols = st.columns(4)
    chips = [
        ("🔴 Ojo rojo", "El paciente presenta ojo rojo intenso con secreción"),
        ("💧 Secreción", "El paciente tiene secreción ocular purulenta"),
        ("⚡ Fotofobia", "El paciente refiere fotofobia intensa y lagrimeo"),
        ("🌀 Dolor ocular", "El paciente describe dolor ocular profundo y fotofobia"),
    ]
    chip_prompt = None
    for i, (label, texto) in enumerate(chips):
        if chip_cols[i].button(label, key=f"chip_{i}"):
            chip_prompt = texto

    placeholder_text = (
        f"[Dr. {st.session_state.doctor_name}]  Describa síntomas, antecedentes o hallazgos de {st.session_state.patient_name}..."
    )

    user_input = st.chat_input(placeholder_text)
    prompt = chip_prompt or user_input

    if prompt:

        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Lista de bytes de todas las imágenes cargadas
        lista_imagenes = [f.getvalue() for f in uploaded_files] if uploaded_files else []

        with st.chat_message("assistant"):
            ph = st.empty()
            ph.markdown(
                '<span style="font-family:Space Mono,monospace;font-size:0.72rem;'
                'color:var(--teal);">// Procesando con EfficientNetB0...</span>',
                unsafe_allow_html=True,
            )
            time.sleep(0.35)

            try:
                respuesta_ia = modelo_vision.analizar_imagen_y_sintomas(
                    lista_imagenes=lista_imagenes,
                    texto_doctor=prompt,
                )
            except Exception as e:
                respuesta_ia = (
                    f"⚠️ **Error en módulo CNN:** `{str(e)}`\n\n"
                    "Verifique que `modelo_vision.py` esté en el mismo directorio del proyecto."
                )

            full_response = ""
            words = respuesta_ia.split()
            for i, word in enumerate(words):
                full_response += word + " "
                if i % 4 == 0 or i == len(words) - 1:
                    ph.markdown(full_response + "▌")
                    time.sleep(0.022)
            ph.markdown(full_response.strip())

        st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})
        st.session_state.total_consultas += 1

        try:
            database.registrar_consulta(
                doctor_nombre   = st.session_state.doctor_name,
                paciente_nombre = st.session_state.patient_name,
                pregunta_doctor = prompt,
                respuesta_ia    = full_response.strip(),
                tiene_imagen    = (len(lista_imagenes) > 0),
            )
        except Exception as e:
            st.warning(f"BD: No se pudo registrar la consulta — {e}")
