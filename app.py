"""
app.py – Hospital Rísquez · OphthalmAI v3.3
Sistema de Apoyo Diagnóstico Oftalmológico
Efecto Inmersivo (Arena.site) + Borrado Automático de Sesión
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
# OJO SVG — (Animado y Flotante)
# ──────────────────────────────────────────────────────────────────────────────
def eye_svg(width="120px", uid="a", pulse_dur="3s", radar_dur="2.6s"):
    return f"""<svg viewBox="0 0 220 120" xmlns="http://www.w3.org/2000/svg"
  style="width:{width};height:auto;display:block;margin:0 auto;
         filter:drop-shadow(0 0 15px rgba(0,229,216,0.7))
                drop-shadow(0 0 40px rgba(0,229,216,0.3));">
  <defs>
    <radialGradient id="sc{uid}" cx="50%" cy="44%" r="60%">
      <stop offset="0%"   stop-color="#eef7f8"/>
      <stop offset="55%"  stop-color="#c4e5ea"/>
      <stop offset="100%" stop-color="#88c0c6"/>
    </radialGradient>
    <radialGradient id="ir{uid}" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#001412"/>
      <stop offset="22%"  stop-color="#002e2a"/>
      <stop offset="52%"  stop-color="#005e58"/>
      <stop offset="78%"  stop-color="#00a89f"/>
      <stop offset="100%" stop-color="#00e5d8"/>
    </radialGradient>
    <radialGradient id="pu{uid}" cx="36%" cy="33%" r="58%">
      <stop offset="0%"   stop-color="#0e1e28"/>
      <stop offset="100%" stop-color="#010507"/>
    </radialGradient>
    <filter id="ig{uid}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="eg{uid}" x="-12%" y="-28%" width="124%" height="156%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="ey{uid}">
      <path d="M6,60 Q110,4 214,60 Q110,116 6,60 Z"/>
    </clipPath>
  </defs>

  <ellipse cx="110" cy="60" rx="108" ry="58" fill="none" stroke="#00e5d8" stroke-width="0.5" opacity="0.1" filter="url(#eg{uid})"/>
  <ellipse cx="110" cy="60" rx="112" ry="62" fill="none" stroke="#00cfff" stroke-width="0.3" opacity="0.07" filter="url(#eg{uid})"/>
  <path d="M6,60 Q110,4 214,60 Q110,116 6,60 Z" fill="url(#sc{uid})" clip-path="url(#ey{uid})"/>
  
  <g clip-path="url(#ey{uid})" opacity="0.13">
    <path d="M20,60 Q52,51 78,59" fill="none" stroke="#c0392b" stroke-width="0.7"/>
    <path d="M24,65 Q48,57 72,63" fill="none" stroke="#c0392b" stroke-width="0.5"/>
    <path d="M162,58 Q182,53 200,56" fill="none" stroke="#c0392b" stroke-width="0.5"/>
    <path d="M160,63 Q178,59 196,62" fill="none" stroke="#c0392b" stroke-width="0.4"/>
  </g>

  <circle cx="110" cy="60" r="36" fill="url(#ir{uid})" filter="url(#ig{uid})" clip-path="url(#ey{uid})"/>
  
  <g clip-path="url(#ey{uid})" opacity="0.19">
    <line x1="110" y1="24" x2="110" y2="96" stroke="#00e5d8" stroke-width="0.7"/>
    <line x1="75"  y1="34" x2="145" y2="86" stroke="#00e5d8" stroke-width="0.6"/>
    <line x1="75"  y1="86" x2="145" y2="34" stroke="#00e5d8" stroke-width="0.6"/>
    <line x1="60"  y1="60" x2="160" y2="60" stroke="#00e5d8" stroke-width="0.6"/>
    <circle cx="110" cy="60" r="29" fill="none" stroke="#00cfff" stroke-width="0.65"/>
    <circle cx="110" cy="60" r="22" fill="none" stroke="#00857d" stroke-width="0.7"/>
    <circle cx="110" cy="60" r="15" fill="none" stroke="#005e58" stroke-width="0.5"/>
  </g>

  <circle cx="110" cy="60" r="14.5" fill="url(#pu{uid})" clip-path="url(#ey{uid})"/>
  <circle cx="110" cy="60" r="14.5" fill="none" stroke="#00e5d8" stroke-width="1.2" opacity="0.8" clip-path="url(#ey{uid})">
    <animate attributeName="r" values="14.5;20;14.5" dur="{pulse_dur}" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.8;0.05;0.8" dur="{pulse_dur}" repeatCount="indefinite"/>
  </circle>

  <ellipse cx="96" cy="47" rx="5.2" ry="2.8" fill="white" opacity="0.8" transform="rotate(-28,96,47)" clip-path="url(#ey{uid})"/>
  <ellipse cx="103" cy="45" rx="1.8" ry="1" fill="white" opacity="0.5" clip-path="url(#ey{uid})"/>
  
  <path d="M6,60 Q110,4 214,60" fill="none" stroke="#003028" stroke-width="2.4" opacity="0.65"/>
  <path d="M6,60 Q110,116 214,60" fill="none" stroke="#003028" stroke-width="2.4" opacity="0.65"/>
  <path d="M6,60 Q110,4 214,60 Q110,116 6,60 Z" fill="none" stroke="#00e5d8" stroke-width="1.4" opacity="0.6" filter="url(#eg{uid})"/>

  <ellipse cx="110" cy="60" rx="36" ry="36" fill="none" stroke="#00e5d8" stroke-width="2" opacity="0" clip-path="url(#ey{uid})">
    <animate attributeName="rx" values="36;108" dur="{radar_dur}" repeatCount="indefinite"/>
    <animate attributeName="ry" values="36;58" dur="{radar_dur}" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.9;0" dur="{radar_dur}" repeatCount="indefinite"/>
  </ellipse>
</svg>"""

# ──────────────────────────────────────────────────────────────────────────────
# CSS INMERSIVO (Efecto Arena.site en el fondo)
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
    --red-alert: #ff3d5a;
    --text-main: #ddeeff;
    --text-muted:#4a7090;
    --glass-brd: rgba(0,229,216,0.14);
}

/* ── EL FONDO CENTRAL INMERSIVO (Arena.site Vibe) ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 70vw;
    height: 70vw;
    background: radial-gradient(circle, rgba(0,229,216,0.12) 0%, rgba(0,180,255,0.05) 30%, transparent 65%);
    z-index: -1;
    pointer-events: none;
    animation: bg-pulse-arena 8s infinite alternate ease-in-out;
}
@keyframes bg-pulse-arena {
    0% { transform: translate(-50%, -50%) scale(0.85); opacity: 0.6; }
    100% { transform: translate(-50%, -50%) scale(1.15); opacity: 1; }
}

html,body,[data-testid="stAppViewContainer"] {
    background-color: var(--void) !important;
    color: var(--text-main) !important;
    font-family: 'DM Sans', sans-serif;
}[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--glass-brd) !important;
    backdrop-filter: blur(10px);
}[data-testid="stSidebar"]>div{padding-top:0!important;}

/* Animación de Flotación para el Ojo Central */
.welcome-eye-container {
    display: flex;
    justify-content: center;
    align-items: center;
    animation: float-eye 6s ease-in-out infinite;
    margin-bottom: 20px;
}
@keyframes float-eye {
    0% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-15px) scale(1.03); }
    100% { transform: translateY(0px) scale(1); }
}

.welcome-screen {
    text-align: center; 
    padding: 10vh 20px;
    background: transparent;
    border: none;
    box-shadow: none;
    position: relative;
    z-index: 1;
}
.welcome-screen h2 { font-family:'Syne',sans-serif!important; font-weight:800; font-size:1.8rem; color:var(--text-main)!important; text-shadow: 0 0 20px rgba(0,229,216,0.5); margin:10px 0 8px!important; }
.welcome-screen p { color:var(--text-muted); font-size:0.9rem; max-width:440px; margin:0 auto; line-height:1.75; }
.w-tag { display:inline-block; margin-top:16px; font-family:'Space Mono',monospace; font-size:0.6rem; color:var(--teal); border:1px solid var(--glass-brd); border-radius:4px; padding:4px 14px; letter-spacing:1.5px; }

/* Sidebar & Cards (Cleaned up) */
.sidebar-logo{text-align:center;padding:18px 16px 12px;border-bottom:1px solid var(--glass-brd);margin-bottom:4px;position:relative;}
.logo-title{font-family:'Syne',sans-serif;font-weight:800;font-size:1.2rem;color:var(--text-main);letter-spacing:1px;margin-top:6px;}
.logo-title span{color:var(--teal);}
.logo-sub{font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--text-muted);letter-spacing:2.5px;text-transform:uppercase;margin-top:2px;}
.model-badge{display:flex;align-items:center;gap:7px;background:rgba(0,229,216,0.05);border:1px solid rgba(0,229,216,0.18);border-radius:6px;padding:6px 12px;font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--teal);letter-spacing:1px;text-transform:uppercase;margin:8px 0 2px;}
.mb-dot{width:6px;height:6px;background:var(--green-ok);border-radius:50%;box-shadow:0 0 6px var(--green-ok);flex-shrink:0;animation:blink 1.8s ease-in-out infinite;}
.s-section{font-family:'Space Mono',monospace;font-size:0.58rem;font-weight:700;color:var(--teal);text-transform:uppercase;letter-spacing:2px;padding:12px 0 5px;border-top:1px solid var(--glass-brd);margin-top:8px;}
.s-info{background:rgba(0,229,216,0.03);border:1px solid var(--glass-brd);border-radius:8px;padding:10px 13px;font-size:0.8rem;color:var(--text-muted);line-height:1.65;margin-top:6px;}
.session-card{background:var(--panel);border:1px solid var(--glass-brd);border-radius:10px;padding:12px 14px 12px 18px;margin-top:8px;position:relative;}
.session-card::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:linear-gradient(180deg,var(--teal),var(--cyan));}
.sc-label{font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1.5px;}
.sc-value{font-size:0.88rem;color:var(--text-main);font-weight:500;margin-top:1px;}

[data-testid="stSidebar"] label, .stTextInput label {font-family:'Space Mono',monospace!important;font-size:0.62rem!important;color:var(--text-muted)!important;text-transform:uppercase;letter-spacing:1.2px;}
[data-testid="stSidebar"] input, .stTextInput input, textarea {background:rgba(5,10,20,0.9)!important;color:var(--teal)!important;border:1px solid var(--glass-brd)!important;border-radius:8px!important;}
.stButton>button {background:transparent!important;color:var(--teal)!important;font-family:'Syne',sans-serif!important;font-weight:700!important;border:1px solid var(--teal)!important;border-radius:8px!important;}
.stButton>button:hover {background:var(--teal)!important;color:var(--void)!important;box-shadow:0 0 20px rgba(0,229,216,0.4)!important;}
div[data-testid="column"] .stButton>button{font-family:'DM Sans',sans-serif!important;font-size:0.72rem!important;border-radius:20px!important;}

.hud-header{display:flex;align-items:center;gap:20px;padding:16px 0 12px;border-bottom:1px solid var(--glass-brd);margin-bottom:14px;}
.hud-title h1{font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.9rem!important;color:var(--text-main)!important;margin:0!important;}
.hud-title h1 em{font-style:normal;color:var(--teal);text-shadow:0 0 20px rgba(0,229,216,0.5);}
.hud-subtitle{font-family:'Space Mono',monospace;font-size:0.6rem;color:var(--text-muted);text-transform:uppercase;margin-top:6px;}
.hud-meta{margin-left:auto;text-align:right;font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--text-muted);}

.status-strip{display:flex;align-items:center;gap:16px;margin-bottom:12px;padding:8px 16px;background:var(--panel);border:1px solid var(--glass-brd);border-radius:8px;font-family:'Space Mono',monospace;font-size:0.62rem;}
.s-dot{width:7px;height:7px;border-radius:50%;}
.dot-active{background:var(--green-ok);box-shadow:0 0 6px var(--green-ok);animation:blink 1.4s infinite;}
.dot-inactive{background:var(--text-muted);}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.3;}}

[data-testid="stChatMessage"]{background:var(--panel)!important;border:1px solid var(--glass-brd)!important;border-radius:12px!important;backdrop-filter:blur(12px);}
[data-testid="stImage"] img{border-radius:10px!important;border:1px solid var(--glass-brd)!important;}
[data-testid="stFileUploader"]{background:rgba(5,10,20,0.8)!important;border:1px dashed var(--glass-brd)!important;}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:var(--teal-dim);border-radius:2px;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# INICIALIZACIÓN
# ──────────────────────────────────────────────────────────────────────────────
database.init_db()

defaults = {
    "messages":[],
    "session_active":  False,
    "doctor_name":     "",
    "patient_name":    "",
    "patient_id":      None,
    "visita_id":       None,
    "total_consultas": 0,
    "view":            "chat",
    "paciente_data":   {},
    "session_idx":     0, # <-- NUEVO: Llave para borrar las fotos al cerrar sesión
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
        <div style="filter: drop-shadow(0 0 10px rgba(0,229,216,0.5)); animation: float-eye 4s infinite ease-in-out;">
            {eye_svg(width="90px", uid="sb", pulse_dur="3.5s", radar_dur="2.9s")}
        </div>
        <div class="logo-title">Ophthalm<span>AI</span></div>
        <div class="logo-sub">Hospital Rísquez · Caracas</div>
    </div>
    <div class="model-badge"><div class="mb-dot"></div>EfficientNetB0 · Local</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="s-section">Datos de la Consulta</div>', unsafe_allow_html=True)
    doctor_input  = st.text_input("Nombre del Doctor",  placeholder="Dr. García",        value=st.session_state.doctor_name,  disabled=st.session_state.session_active)
    patient_input = st.text_input("Paciente (nombre/cédula)", placeholder="Juan Pérez", value=st.session_state.patient_name, disabled=st.session_state.session_active)

    if not st.session_state.session_active:
        if st.button("▶  INICIAR CONSULTA"):
            if doctor_input.strip() and patient_input.strip():
                st.session_state.doctor_name  = doctor_input.strip()
                st.session_state.patient_name = patient_input.strip()
                st.session_state.session_active  = True
                st.session_state.messages        =[]
                st.session_state.total_consultas = 0
                msg = (
                    f"Sistema en línea. Bienvenido, **Dr. {doctor_input.strip()}**.\n\n"
                    f"Consulta iniciada para **{patient_input.strip()}**.\n\n"
                    "Especializado estrictamente en **Úlceras Corneales** y **Uveítis Anterior**.\n"
                    "¿Con qué empezamos?"
                )
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.session_state.view = "chat"
                st.rerun()
            else:
                st.error("Complete ambos campos.")
    else:
        # 🛑 AQUÍ ESTÁ LA MAGIA PARA BORRAR LAS FOTOS AL CERRAR SESIÓN 🛑
        if st.button("⏹  FINALIZAR CONSULTA"):
            for k, v in defaults.items():
                if k != "session_idx":
                    st.session_state[k] = v
            st.session_state.session_idx += 1 # Al sumar 1, el cuadro de fotos se resetea
            st.rerun()

    if st.session_state.session_active:
        st.markdown(f"""
        <div class="session-card">
            <div class="sc-label">Doctor</div><div class="sc-value">{st.session_state.doctor_name}</div>
            <div class="sc-label" style="margin-top:6px;">Paciente</div><div class="sc-value">{st.session_state.patient_name}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="s-section">Imágenes · Segmento Anterior</div>', unsafe_allow_html=True)
    
    # Usamos la llave 'session_idx' para que se vacíe al cerrar sesión
    uploaded_files = st.file_uploader(
        "Fotografías oculares", type=["jpg","jpeg","png"],
        accept_multiple_files=True,
        disabled=not st.session_state.session_active,
        label_visibility="collapsed",
        key=f"uploader_{st.session_state.session_idx}" 
    )
    
    if uploaded_files:
        cols = st.columns(min(len(uploaded_files), 2))
        for i, f in enumerate(uploaded_files):
            cols[i % 2].image(f, use_container_width=True)
        st.markdown('<div style="color:var(--teal);text-align:center;font-size:0.6rem;margin-top:5px;">✓ IMAGEN(ES) LISTA(S)</div>', unsafe_allow_html=True)

    st.markdown('<div class="s-section">Especialidades (Tesis)</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="s-info">
        ⚠️ <strong>Úlcera Corneal / Queratitis</strong><br>
        🔵 <strong>Uveítis Anterior</strong><br>
        ✅ <strong>Ojo Sano / Control</strong><br>
        <span style="color:#1e3d55;font-size:0.58rem;">*El sistema solo diagnostica estas patologías.</span>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN AREA
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hud-header">
    <div style="flex-shrink:0;">{eye_svg(width="60px", uid="hd", pulse_dur="3s", radar_dur="2.5s")}</div>
    <div class="hud-title">
        <h1>Ophthalm<em>AI</em></h1>
        <div class="hud-subtitle">Úlceras Corneales & Uveítis · Hospital Rísquez</div>
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.session_active:
    # ── PANTALLA DE INICIO CON EL OJO FLOTANTE Y FONDO INMERSIVO ──
    st.markdown(f"""
    <div class="welcome-screen">
        <div class="welcome-eye-container">
            {eye_svg(width="180px", uid="wc", pulse_dur="4s", radar_dur="3.2s")}
        </div>
        <h2>OphthalmAI</h2>
        <p>Sistema diagnóstico asistido por Red Neuronal (EfficientNetB0). Especializado de forma exclusiva en <strong>Úlceras Corneales</strong> y <strong>Uveítis Anterior</strong>.</p>
        <div class="w-tag">// INICIE SESIÓN EN EL PANEL LATERAL //</div>
    </div>
    """, unsafe_allow_html=True)

else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.58rem;color:var(--text-muted);letter-spacing:1px;margin-bottom:6px;">// SÍNTOMAS RÁPIDOS</div>', unsafe_allow_html=True)
    cc = st.columns(4)
    chips =[("🔴 Ojo rojo", "ojo rojo"), ("💧 Secreción", "secreción"), ("⚡ Fotofobia", "fotofobia"), ("🌀 Dolor", "dolor profundo")]
    chip_prompt = None
    for i, (label, texto) in enumerate(chips):
        if cc[i].button(label, key=f"chip_{i}"):
            chip_prompt = texto

    user_input = st.chat_input(f"[Dr. {st.session_state.doctor_name}] Síntomas de {st.session_state.patient_name}...")
    prompt = chip_prompt or user_input

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        lista_imgs = [f.getvalue() for f in uploaded_files] if uploaded_files else[]

        with st.chat_message("assistant"):
            ph = st.empty()
            ph.markdown('<span style="color:var(--teal);font-size:0.7rem;">// Procesando con Red Neuronal...</span>', unsafe_allow_html=True)
            time.sleep(0.25)
            try:
                respuesta_ia = modelo_vision.analizar_imagen_y_sintomas(lista_imagenes=lista_imgs, texto_doctor=prompt)
            except Exception as e:
                respuesta_ia = f"⚠️ Error en módulo CNN: `{e}`"

            full_response = ""
            words = respuesta_ia.split()
            for i, word in enumerate(words):
                full_response += word + " "
                if i % 4 == 0 or i == len(words) - 1:
                    ph.markdown(full_response + "▌")
                    time.sleep(0.015)
            ph.markdown(full_response.strip())

        st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})
        try:
            database.registrar_consulta(st.session_state.doctor_name, st.session_state.patient_name, prompt, full_response.strip(), bool(lista_imgs))
        except:
            pass
