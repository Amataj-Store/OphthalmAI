"""
app.py – Hospital Rísquez · OphthalmAI v3.5
Diseño Arena.site + Ojo Personalizado con Láser de Escaneo
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
# FUNCIÓN PARA CARGAR LA IMAGEN LOCAL DEL OJO (DETECTOR INTELIGENTE)
# ──────────────────────────────────────────────────────────────────────────────
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

b64_ojo = get_base64_image("ojo_portada.png")
if not b64_ojo:
    # Por si acaso la subiste como .jpg
    b64_ojo = get_base64_image("ojo_portada.jpg") 

# Detecta automáticamente si es jpeg o png por el código base64
mime_type = "image/jpeg" if b64_ojo.startswith("/9j/") else "image/png"
IMG_SRC = f"data:{mime_type};base64,{b64_ojo}" if b64_ojo else "https://images.unsplash.com/photo-1542282088-fe8426682b8f?auto=format&fit=crop&w=500&q=80"


# ──────────────────────────────────────────────────────────────────────────────
# UTILIDAD: generar resumen
# ──────────────────────────────────────────────────────────────────────────────
def _generar_resumen(doctor: str, paciente: str, mensajes: list) -> str:
    from datetime import datetime
    lineas =[
        "=" * 62,
        "   HOSPITAL RÍSQUEZ · OphthalmAI v3.5",
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
        "Reporte generado por OphthalmAI v3.5 · Hospital Rísquez",
        "Apoyo diagnóstico — criterio clínico del médico tratante.",
        "=" * 62,
    ]
    return "\n".join(lineas)


# ──────────────────────────────────────────────────────────────────────────────
# CSS INMERSIVO (Arena.site + Efecto Escáner Láser)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');

:root {
    --void:      #02050a;
    --navy-mid:  #050a14;
    --panel:     rgba(5,10,20,0.75);
    --teal:      #00e5d8;
    --cyan:      #00cfff;
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

.sidebar-logo { text-align:center; padding:20px 16px; border-bottom:1px solid var(--glass-brd); margin-bottom:10px; }
.logo-title { font-family:'Syne',sans-serif; font-weight:800; font-size:1.5rem; color:var(--text-main); letter-spacing:1px; }
.logo-title span { color:var(--teal); }
.logo-sub { font-family:'Space Mono',monospace; font-size:0.6rem; color:var(--text-muted); letter-spacing:2.5px; text-transform:uppercase; margin-top:2px; }

.welcome-screen {
    position: relative;
    text-align: center; 
    padding: 70px 20px;
    background: radial-gradient(circle at center, rgba(0,229,216,0.06) 0%, transparent 60%);
    border: 1px solid rgba(0,229,216,0.03);
    margin-top: 20px;
}
.ws-tr { position:absolute; top:0; right:0; width:40px; height:40px; border-top:2px solid var(--teal); border-right:2px solid var(--teal); opacity:0.6; }
.ws-bl { position:absolute; bottom:0; left:0; width:40px; height:40px; border-bottom:2px solid var(--teal); border-left:2px solid var(--teal); opacity:0.6; }

/* ========================================================= */
/* EFECTO DEL OJO: DIFUMINADO Y LÁSER ESCÁNER                */
/* ========================================================= */
.ojo-container {
    position: relative;
    width: 280px;  
    height: 280px;
    margin: 0 auto 30px auto;
    border-radius: 50%;
    mask-image: radial-gradient(circle, black 40%, transparent 70%);
    -webkit-mask-image: radial-gradient(circle, black 40%, transparent 70%);
    animation: float-eye 6s ease-in-out infinite;
}
.ojo-imagen {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}
.scanner-line {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 15px;
    background: linear-gradient(to bottom, transparent 0%, rgba(0,229,216,0.4) 80%, #00e5d8 100%);
    box-shadow: 0 5px 20px rgba(0,229,216,0.6);
    animation: scan 3.5s cubic-bezier(0.4, 0.0, 0.2, 1) infinite;
    z-index: 10;
}
@keyframes scan {
    0%   { top: -10%; opacity: 0; }
    15%  { opacity: 1; }
    85%  { opacity: 1; }
    100% { top: 110%; opacity: 0; }
}
@keyframes float-eye {
    0% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-10px) scale(1.02); }
    100% { transform: translateY(0px) scale(1); }
}
/* ========================================================= */

.welcome-screen h2 { font-family:'Syne',sans-serif!important; font-weight:800; font-size:2rem; color:var(--text-main)!important; margin:0 0 8px!important; }
.welcome-screen p { color:var(--text-muted); font-size:0.95rem; max-width:500px; margin:0 auto; line-height:1.8; }

.hud-header{display:flex;align-items:center;padding:10px 0 20px;border-bottom:1px solid var(--glass-brd);margin-bottom:20px;}
.hud-title h1{font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.8rem!important;color:var(--text-main)!important;margin:0!important;}
.hud-title h1 em{font-style:normal;color:var(--teal);}
.hud-meta{margin-left:auto;text-align:right;font-family:'Space Mono',monospace;font-size:0.6rem;color:var(--text-muted);}

.model-badge{display:flex;align-items:center;gap:7px;background:rgba(0,229,216,0.05);border:1px solid rgba(0,229,216,0.18);border-radius:6px;padding:6px 12px;font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--teal);letter-spacing:1px;text-transform:uppercase;margin:8px 0 2px;}
.mb-dot{width:6px;height:6px;background:var(--green-ok);border-radius:50%;box-shadow:0 0 6px var(--green-ok);flex-shrink:0;animation:blink 1.8s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.3;}}

[data-testid="stSidebar"] label, .stTextInput label {font-family:'Space Mono',monospace!important;font-size:0.62rem!important;color:var(--text-muted)!important;text-transform:uppercase;}
[data-testid="stSidebar"] input, .stTextInput input, textarea {background:rgba(5,10,20,0.9)!important;color:var(--teal)!important;border:1px solid var(--glass-brd)!important;border-radius:8px!important;font-family:'Space Mono',monospace!important;font-size:0.82rem!important;}
[data-testid="stSidebar"] input:focus, textarea:focus{border-color:var(--teal)!important;box-shadow:0 0 0 2px rgba(0,229,216,0.12)!important;}

.stButton>button {background:transparent!important;color:var(--teal)!important;font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:0.8rem!important;border:1px solid var(--teal)!important;border-radius:8px!important;padding:10px 20px!important;width:100%!important;transition:all 0.2s ease!important;}
.stButton>button:hover {background:var(--teal)!important;color:var(--void)!important;box-shadow:0 0 20px rgba(0,229,216,0.4)!important;}
div[data-testid="column"] .stButton>button{font-family:'DM Sans',sans-serif!important;font-size:0.72rem!important;border-radius:20px!important;}

[data-testid="stChatMessage"]{background:var(--panel)!important;border:1px solid var(--glass-brd)!important;border-radius:12px!important;backdrop-filter:blur(12px);}
[data-testid="stImage"] img{border-radius:10px!important;border:1px solid var(--glass-brd)!important;}[data-testid="stFileUploader"]{background:rgba(5,10,20,0.8)!important;border:1px dashed var(--glass-brd)!important;}

.s-section{font-family:'Space Mono',monospace;font-size:0.58rem;font-weight:700;color:var(--teal);text-transform:uppercase;letter-spacing:2px;padding:12px 0 5px;border-top:1px solid var(--glass-brd);margin-top:8px;}
.s-info{background:rgba(0,229,216,0.03);border:1px solid var(--glass-brd);border-radius:8px;padding:10px 13px;font-size:0.8rem;color:var(--text-muted);line-height:1.65;margin-top:6px;}
.session-card{background:linear-gradient(135deg,rgba(0,229,216,0.07),rgba(0,207,255,0.03));border:1px solid var(--glass-brd);border-radius:10px;padding:12px 14px 12px 18px;margin-top:8px;position:relative;}
.session-card::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:linear-gradient(180deg,var(--teal),var(--cyan));}
.sc-label{font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1.5px;}
.sc-value{font-size:0.88rem;color:var(--text-main);font-weight:500;margin-top:1px;}
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
    "session_idx":     0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
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
                    n_v  = len(visitas_prev) + 1
                    vid  = database.abrir_visita(p["id"], doctor_input.strip(), "Consulta OphthalmAI")
                    st.session_state.visita_id = vid
                    hay  = len(visitas_prev)
                    msg  = (
                        f"Sistema en línea. Bienvenido, **Dr. {doctor_input.strip()}**.\n\n"
                        f"Paciente identificado: **{p['nombre_completo']}**"
                        + (f"  ·  Cédula: `{p['cedula']}`" if p.get("cedula") else "") + "\n\n"
                        f"Esta es la **visita N.° {n_v}**."
                        + (f" Tiene **{hay}** consulta(s) previa(s) registradas." if hay else "") +
                        "\n\nEspecializado en **Úlceras Corneales** y **Uveítis**. ¿Con qué empezamos?"
                    )
                else:
                    st.session_state.patient_id   = None
                    st.session_state.paciente_data = {}
                    st.session_state.visita_id     = None
                    msg = (
                        f"Bienvenido, **Dr. {doctor_input.strip()}**.\n\n"
                        f"No encontré a **{patient_input.strip()}** en el sistema. "
                        "Puede registrarlo en **📋 Registro** o continuar con la consulta.\n\n"
                        "¿Cómo puedo asistirle?"
                    )
                st.session_state.session_active  = True
                st.session_state.messages        =[]
                st.session_state.total_consultas = 0
                st.session_state.messages.append({"role": "assistant", "content": msg})
                st.session_state.view = "chat"
                st.rerun()
            else:
                st.error("Complete ambos campos.")
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
            <div class="sc-label" style="margin-top:6px;">Interacciones</div>
            <div class="sc-value" style="color:var(--teal);">{st.session_state.total_consultas}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="s-section">Imágenes · Segmento Anterior</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Fotografías oculares", type=["jpg","jpeg","png"],
        accept_multiple_files=True,
        disabled=not st.session_state.session_active,
        label_visibility="collapsed",
        key=f"uploader_{st.session_state.session_idx}"
    )
    
    if uploaded_files:
        n_f  = len(uploaded_files)
        cols = st.columns(min(n_f, 2))
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
st.markdown("""
<div class="hud-header">
    <div class="hud-title">
        <h1>Ophthalm<em>AI</em></h1>
    </div>
    <div class="hud-meta">
        <div class="ver">v3.5-CLOUD</div>
        <div>EfficientNetB0 · Tesis UCV</div>
    </div>
</div>
""", unsafe_allow_html=True)

view = st.session_state.view

# ────────────────────────────────────────────────────────────────────────
# VISTA: CHAT (Y Portada)
# ────────────────────────────────────────────────────────────────────────
if view == "chat":

    if not st.session_state.session_active:
        # PANTALLA DE INICIO CON LA IMAGEN PNG SUBLIME (HTML EN LÍNEA PARA EVITAR ERRORES DE MARKDOWN)
        st.markdown(f"""<div class="welcome-screen">
    <div class="ws-tr"></div><div class="ws-bl"></div>
    <div class="ojo-container">
        <img src="{IMG_SRC}" class="ojo-imagen" alt="Ojo IA">
        <div class="scanner-line"></div>
    </div>
    <h2>OphthalmAI en espera</h2>
    <p>Sistema diagnóstico asistido por Inteligencia Artificial (EfficientNetB0). Especializado en la detección de <strong>Úlceras Corneales</strong> y <strong>Uveítis Anterior</strong>.</p>
    <br><span style="font-family:Space Mono, monospace; color:var(--teal); font-size:0.8rem; letter-spacing: 2px;">// INICIE SESIÓN EN EL PANEL LATERAL PARA COMENZAR //</span>
</div>""", unsafe_allow_html=True)

    else:
        if st.session_state.patient_id:
            visitas_prev = database.obtener_visitas_paciente(st.session_state.patient_id)
            if len(visitas_prev) > 1:
                with st.expander(f"📂 {len(visitas_prev)-1} visita(s) previa(s)", expanded=False):
                    for v in visitas_prev[1:]:
                        st.markdown(f"""
                        <div style="font-family:Space Mono,monospace;font-size:0.63rem;border-bottom:1px solid var(--glass-brd);padding:8px 0;">
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
            except Exception: pass

        st.markdown('<div style="font-family:Space Mono;font-size:0.58rem;color:var(--text-muted);letter-spacing:1px;margin-bottom:6px;">// SÍNTOMAS RÁPIDOS</div>', unsafe_allow_html=True)
        cc = st.columns(4)
        chips =[("🔴 Ojo rojo", "ojo rojo"), ("💧 Secreción", "secreción"), ("⚡ Fotofobia", "fotofobia"), ("🌀 Dolor", "dolor profundo")]
        chip_prompt = None
        for i, (label, texto) in enumerate(chips):
            if cc[i].button(label, key=f"chip_{i}"):
                chip_prompt = texto

        user_input = st.chat_input(f"[Dr. {st.session_state.doctor_name}] Escriba síntomas, pida un protocolo, o analice fotos...")
        prompt = chip_prompt or user_input

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            lista_imgs =[f.getvalue() for f in uploaded_files] if uploaded_files else[]

            with st.chat_message("assistant"):
                ph = st.empty()
                ph.markdown('<span style="color:var(--teal);font-size:0.7rem;">// Procesando...</span>', unsafe_allow_html=True)
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
            st.session_state.total_consultas += 1

            if st.session_state.visita_id:
                try:
                    database.actualizar_visita(visita_id=st.session_state.visita_id, diagnostico_ia=full_response.strip()[:600], tiene_imagen=bool(lista_imgs))
                except Exception: pass
            try:
                database.registrar_consulta(st.session_state.doctor_name, st.session_state.patient_name, prompt, full_response.strip(), bool(lista_imgs), st.session_state.visita_id, st.session_state.patient_id)
            except Exception: pass


# ────────────────────────────────────────────────────────────────────────
# VISTAS RESTANTES (Registro, Historial, Dashboard)
# ────────────────────────────────────────────────────────────────────────
elif view == "registro":
    st.markdown("### 📋 Registro de Nuevo Paciente")
    with st.form("form_reg", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre_completo = c1.text_input("Nombre Completo *")
        cedula          = c2.text_input("Cédula")
        c3, c4, c5 = st.columns(3)
        edad      = c3.number_input("Edad", 0, 120, 0, step=1)
        sexo      = c4.selectbox("Sexo",["", "Masculino", "Femenino", "Otro"])
        fecha_nac = c5.text_input("Fecha de Nac.", placeholder="DD/MM/AAAA")
        c6, c7    = st.columns(2)
        telefono  = c6.text_input("Teléfono")
        direccion = c7.text_input("Dirección")
        antec     = st.text_area("Antecedentes Oftalmológicos y Médicos", height=75)
        doc_reg   = st.text_input("Doctor que Registra *", value=st.session_state.doctor_name)

        if st.form_submit_button("💾  REGISTRAR PACIENTE"):
            if nombre_completo.strip() and doc_reg.strip():
                try:
                    pid = database.registrar_paciente(
                        nombre_completo=nombre_completo.strip(), doctor_registro=doc_reg.strip(),
                        cedula=cedula.strip() or None, fecha_nacimiento=fecha_nac.strip() or None,
                        edad=int(edad) if edad else None, sexo=sexo or None,
                        telefono=telefono.strip() or None, direccion=direccion.strip() or None,
                        antecedentes=antec.strip() or None
                    )
                    st.success(f"✓ **{nombre_completo}** registrado con éxito.")
                except Exception as e: st.error(f"Error: {e}")
            else:
                st.warning("Los campos con * son obligatorios.")

elif view == "historial":
    st.markdown("### 📂 Historial de Pacientes")
    busqueda  = st.text_input("Buscar por nombre o cédula", placeholder="Escriba para buscar...")
    pacientes = database.buscar_paciente(busqueda) if busqueda else database.obtener_todos_los_pacientes()

    if pacientes:
        for p in pacientes:
            lbl = f"👤  {p['nombre_completo']}"
            if p.get("cedula"): lbl += f"  ·  {p['cedula']}"
            with st.expander(lbl, expanded=False):
                st.markdown(f"**CÉDULA:** {p.get('cedula','—')} | **EDAD:** {p.get('edad','—')}")
                st.markdown(f"**ANTECEDENTES:** {p.get('antecedentes','—')}")
    else:
        st.info("No se encontraron pacientes.")

elif view == "dashboard":
    st.markdown("### 📊 Dashboard")
    stats = database.stats_generales()
    m1, m2, m3 = st.columns(3)
    m1.metric("Pacientes", stats["total_pacientes"])
    m2.metric("Visitas", stats["total_visitas"])
    m3.metric("Interacciones IA", stats["total_interacciones"])
