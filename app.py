"""
app.py – Hospital Rísquez · OphthalmAI v3.4
Sistema de Apoyo Diagnóstico Oftalmológico
(Versión Oficial Completa con Registro, Historial y Efecto Arena)
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
# UTILIDAD: generar resumen
# ──────────────────────────────────────────────────────────────────────────────
def _generar_resumen(doctor: str, paciente: str, mensajes: list) -> str:
    from datetime import datetime
    lineas =[
        "=" * 62,
        "   HOSPITAL RÍSQUEZ · OphthalmAI v3.4",
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
        "Reporte generado por OphthalmAI v3.4 · Hospital Rísquez",
        "Apoyo diagnóstico — criterio clínico del médico tratante.",
        "=" * 62,
    ]
    return "\n".join(lineas)

# ──────────────────────────────────────────────────────────────────────────────
# CSS CON EFECTO ARENA.SITE (Fondo inmersivo y Ojo Central Gigante)
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

/* ── FONDO INMERSIVO TIPO ARENA.SITE ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 70vw;
    height: 70vw;
    background: radial-gradient(circle, rgba(0,229,216,0.09) 0%, rgba(0,180,255,0.04) 30%, transparent 65%);
    z-index: -1;
    pointer-events: none;
    animation: bg-pulse-arena 8s infinite alternate ease-in-out;
}
@keyframes bg-pulse-arena {
    0% { transform: translate(-50%, -50%) scale(0.85); opacity: 0.6; }
    100% { transform: translate(-50%, -50%) scale(1.15); opacity: 1; }
}

/* ── OJO REALISTA FLOTANTE ── */
.realistic-eye {
    width: 220px;
    height: auto;
    margin: 0 auto 25px auto;
    border-radius: 50%;
    display: block;
    filter: drop-shadow(0 0 25px rgba(0,229,216,0.5)) drop-shadow(0 0 50px rgba(0,207,255,0.2));
    animation: float-eye 6s ease-in-out infinite;
}
@keyframes float-eye {
    0% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-12px) scale(1.02); }
    100% { transform: translateY(0px) scale(1); }
}

html,body,[data-testid="stAppViewContainer"] {
    background-color:var(--void)!important;
    background-image:
        repeating-linear-gradient(0deg,transparent,transparent 2px,var(--scan-line) 2px,var(--scan-line) 4px),
        radial-gradient(ellipse 40% 30% at 90% 90%,rgba(0,207,255,0.04) 0%,transparent 55%);
    color:var(--text-main)!important;
    font-family:'DM Sans',sans-serif;
}[data-testid="stSidebar"] {
    background:var(--navy-mid)!important;
    border-right:1px solid var(--glass-brd)!important;
    background-image:linear-gradient(180deg,rgba(0,229,216,0.04) 0%,transparent 30%)!important;
}
[data-testid="stSidebar"]>div{padding-top:0!important;}

/* Logo Limpio (Sin ojo pequeño) */
.sidebar-logo{text-align:center;padding:18px 16px 12px;border-bottom:1px solid var(--glass-brd);margin-bottom:4px;}
.logo-title{font-family:'Syne',sans-serif;font-weight:800;font-size:1.4rem;color:var(--text-main);letter-spacing:1px;margin-top:6px;}
.logo-title span{color:var(--teal);}
.logo-sub{font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--text-muted);letter-spacing:2.5px;text-transform:uppercase;margin-top:2px;}

/* Model badge */
.model-badge{display:flex;align-items:center;gap:7px;background:rgba(0,229,216,0.05);border:1px solid rgba(0,229,216,0.18);border-radius:6px;padding:6px 12px;font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--teal);letter-spacing:1px;text-transform:uppercase;margin:8px 0 2px;}
.mb-dot{width:6px;height:6px;background:var(--green-ok);border-radius:50%;box-shadow:0 0 6px var(--green-ok);flex-shrink:0;animation:blink 1.8s ease-in-out infinite;}

/* Sections & Cards */
.s-section{font-family:'Space Mono',monospace;font-size:0.58rem;font-weight:700;color:var(--teal);text-transform:uppercase;letter-spacing:2px;padding:12px 0 5px;border-top:1px solid var(--glass-brd);margin-top:8px;}
.s-section::before{content:'// ';opacity:0.5;}
.s-info{background:rgba(0,229,216,0.03);border:1px solid var(--glass-brd);border-radius:8px;padding:10px 13px;font-size:0.8rem;color:var(--text-muted);line-height:1.65;margin-top:6px;}
.s-info strong{color:var(--text-main);font-weight:500;}
.session-card{background:linear-gradient(135deg,rgba(0,229,216,0.07),rgba(0,207,255,0.03));border:1px solid var(--glass-brd);border-radius:10px;padding:12px 14px 12px 18px;margin-top:8px;position:relative;overflow:hidden;}
.session-card::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:linear-gradient(180deg,var(--teal),var(--cyan));}
.sc-label{font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1.5px;}
.sc-value{font-size:0.88rem;color:var(--text-main);font-weight:500;margin-top:1px;}

/* Inputs & Buttons */
[data-testid="stSidebar"] label,.stTextInput label,.stSelectbox label,.stTextArea label,.stNumberInput label{font-family:'Space Mono',monospace!important;font-size:0.62rem!important;color:var(--text-muted)!important;text-transform:uppercase;letter-spacing:1.2px;}
[data-testid="stSidebar"] input,.stTextInput input, textarea{background:rgba(5,13,26,0.9)!important;color:var(--teal)!important;border:1px solid var(--glass-brd)!important;border-radius:8px!important;font-family:'Space Mono',monospace!important;font-size:0.82rem!important;}[data-testid="stSidebar"] input:focus, textarea:focus{border-color:var(--teal)!important;box-shadow:0 0 0 2px rgba(0,229,216,0.12)!important;}
.stButton>button{background:transparent!important;color:var(--teal)!important;font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:0.8rem!important;border:1px solid var(--teal)!important;border-radius:8px!important;padding:10px 20px!important;width:100%!important;letter-spacing:1.5px;text-transform:uppercase;transition:all 0.22s ease!important;}
.stButton>button:hover{color:var(--void)!important;background:var(--teal)!important;box-shadow:0 0 22px rgba(0,229,216,0.5)!important;}
div[data-testid="column"] .stButton>button{font-family:'DM Sans',sans-serif!important;font-size:0.72rem!important;font-weight:500!important;padding:6px 4px!important;letter-spacing:0.3px!important;text-transform:none!important;border-radius:20px!important;}

/* Header Limpio (Sin ojo pequeño) */
.hud-header{display:flex;align-items:center;gap:20px;padding:16px 0 12px;border-bottom:1px solid var(--glass-brd);margin-bottom:14px;position:relative;}
.hud-header::after{content:'';position:absolute;bottom:-1px;left:0;width:140px;height:1px;background:linear-gradient(90deg,var(--teal),transparent);}
.hud-title h1{font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.9rem!important;color:var(--text-main)!important;margin:0!important;letter-spacing:-0.5px;line-height:1;}
.hud-title h1 em{font-style:normal;color:var(--teal);text-shadow:0 0 20px rgba(0,229,216,0.5);}
.hud-subtitle{font-family:'Space Mono',monospace;font-size:0.6rem;color:var(--text-muted);letter-spacing:2px;text-transform:uppercase;margin-top:6px;}
.hud-meta{margin-left:auto;text-align:right;font-family:'Space Mono',monospace;font-size:0.58rem;color:var(--text-muted);line-height:1.9;}
.hud-meta .ver{color:var(--teal);font-weight:700;}

/* Chat & Misc */
.status-strip{display:flex;align-items:center;gap:16px;margin-bottom:12px;padding:8px 16px;background:var(--panel);border:1px solid var(--glass-brd);border-radius:8px;font-family:'Space Mono',monospace;font-size:0.62rem;}
.s-dot{width:7px;height:7px;border-radius:50%;}
.dot-active{background:var(--green-ok);box-shadow:0 0 6px var(--green-ok);animation:blink 1.4s infinite;}
.dot-inactive{background:var(--text-muted);}
.dot-img{background:var(--amber);box-shadow:0 0 6px var(--amber);}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.3;}}
[data-testid="stChatMessage"]{background:var(--panel)!important;border:1px solid var(--glass-brd)!important;border-radius:12px!important;padding:16px 20px!important;margin-bottom:10px!important;backdrop-filter:blur(12px);}[data-testid="stImage"] img{border-radius:10px!important;border:1px solid var(--glass-brd)!important;}
[data-testid="stFileUploader"]{background:rgba(5,13,26,0.8)!important;border:1px dashed var(--glass-brd)!important;border-radius:10px!important;}

/* Welcome Screen */
.welcome-screen{text-align:center;padding:40px 40px;border:1px solid var(--glass-brd);border-radius:20px;margin-top:14px;background:linear-gradient(135deg,rgba(0,229,216,0.03) 0%,transparent 50%),var(--panel);position:relative;overflow:hidden;}
.welcome-screen h2{font-family:'Syne',sans-serif!important;font-weight:800;font-size:1.7rem;color:var(--text-main)!important;margin:10px 0 8px!important;}
.welcome-screen p{color:var(--text-muted);font-size:0.9rem;max-width:480px;margin:0 auto;line-height:1.75;}
.w-tag{display:inline-block;margin-top:16px;font-family:'Space Mono',monospace;font-size:0.6rem;color:var(--teal);border:1px solid var(--glass-brd);border-radius:4px;padding:4px 14px;}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:var(--void);}::-webkit-scrollbar-thumb{background:var(--teal-dim);border-radius:2px;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# INIT
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
    "session_idx":     0, # Indice para vaciar las fotos
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

    # Datos consulta
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
        # LÓGICA DE BORRADO DE FOTOS AL FINALIZAR SESIÓN
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
    
    # Usamos session_idx en el key para que se resetee
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
        st.markdown(
            f'<div style="font-family:Space Mono,monospace;font-size:0.6rem;'
            f'color:var(--teal);text-align:center;margin-top:5px;letter-spacing:1px;">'
            f'✓ {n_f} IMAGEN(ES) · CNN ACTIVA</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="s-section">Especialidades</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="s-info">
        ⚠️ <strong>Úlcera Corneal / Queratitis</strong><br>
        &emsp;Bacteriana · Herpética · Fúngica<br><br>
        🔵 <strong>Uveítis Anterior</strong><br>
        &emsp;No infecciosa · Crónica · Recurrente<br>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# HEADER PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hud-header">
    <div class="hud-title">
        <h1>Ophthalm<em>AI</em></h1>
        <div class="hud-subtitle">Úlceras Corneales & Uveítis · Hospital Rísquez · Tesis UCV</div>
    </div>
    <div class="hud-meta">
        <div class="ver">v3.4-LOCAL</div>
        <div>EfficientNetB0</div>
        <div>Multi-imagen · NLP</div>
        <div>SQLite · $0 API</div>
    </div>
</div>
""", unsafe_allow_html=True)

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


# ══════════════════════════════════════════════════════════════════════════════
# VISTAS
# ══════════════════════════════════════════════════════════════════════════════
view = st.session_state.view

# ────────────────────────────────────────────────────────────────────────
# CHAT
# ────────────────────────────────────────────────────────────────────────
if view == "chat":

    if not st.session_state.session_active:
        st.markdown(f"""
        <div class="welcome-screen">
            <div style="position:relative;z-index:1;">
                <img src="https://images.unsplash.com/photo-1542282088-fe8426682b8f?auto=format&fit=crop&w=500&q=80" class="realistic-eye">
            </div>
            <h2>OphthalmAI · en espera</h2>
            <p>
                Diagnóstico asistido por Red Neuronal Convolucional (EfficientNetB0).
                Especializado en <strong>Úlceras Corneales</strong> y <strong>Uveítis</strong>.
                Historial clínico, seguimiento y privacidad total — sin internet.
            </p>
            <div class="w-tag">// MOTOR LOCAL · PRIVACIDAD TOTAL · TESIS UCV //</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        if st.session_state.patient_id:
            visitas_prev = database.obtener_visitas_paciente(st.session_state.patient_id)
            if len(visitas_prev) > 1:
                with st.expander(f"📂 {len(visitas_prev)-1} visita(s) previa(s)", expanded=False):
                    for v in visitas_prev[1:]:
                        st.markdown(f"""
                        <div style="font-family:Space Mono,monospace;font-size:0.63rem;
                        border-bottom:1px solid var(--glass-brd);padding:8px 0;line-height:1.7;">
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

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if st.session_state.total_consultas > 0:
            try:
                resumen_data = _generar_resumen(
                    st.session_state.doctor_name,
                    st.session_state.patient_name,
                    st.session_state.messages,
                ).encode("utf-8")
                fname = f"consulta_{st.session_state.patient_name.replace(' ','_')}_{time.strftime('%Y%m%d_%H%M')}.txt"
                st.download_button(
                    label="⬇  Exportar resumen de consulta (.txt)",
                    data=resumen_data, file_name=fname, mime="text/plain", key="export_btn"
                )
            except Exception:
                pass

        st.markdown(
            '<div style="font-family:Space Mono,monospace;font-size:0.58rem;'
            'color:var(--text-muted);letter-spacing:1px;margin-bottom:6px;">'
            '// SÍNTOMAS RÁPIDOS</div>', unsafe_allow_html=True
        )
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

        user_input = st.chat_input(f"[Dr. {st.session_state.doctor_name}] Pida un protocolo o describa síntomas...")
        prompt = chip_prompt or user_input

        if prompt:
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            lista_imgs =[f.getvalue() for f in uploaded_files] if uploaded_files else[]

            with st.chat_message("assistant"):
                ph = st.empty()
                ph.markdown('<span style="font-family:Space Mono,monospace;font-size:0.7rem;color:var(--teal);">// Procesando...</span>', unsafe_allow_html=True)
                time.sleep(0.25)
                try:
                    respuesta_ia = modelo_vision.analizar_imagen_y_sintomas(lista_imagenes=lista_imgs, texto_doctor=prompt)
                except Exception as e:
                    respuesta_ia = f"⚠️ **Error en módulo CNN:** `{e}`"

                full_response = ""
                words = respuesta_ia.split()
                for i, word in enumerate(words):
                    full_response += word + " "
                    if i % 5 == 0 or i == len(words) - 1:
                        ph.markdown(full_response + "▌")
                        time.sleep(0.016)
                ph.markdown(full_response.strip())

            st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})
            st.session_state.total_consultas += 1

            if st.session_state.visita_id:
                try:
                    database.actualizar_visita(
                        visita_id=st.session_state.visita_id,
                        diagnostico_ia=full_response.strip()[:600],
                        tiene_imagen=bool(lista_imgs),
                    )
                except Exception: pass
            try:
                database.registrar_consulta(
                    doctor_nombre=st.session_state.doctor_name, paciente_nombre=st.session_state.patient_name,
                    pregunta_doctor=prompt, respuesta_ia=full_response.strip(), tiene_imagen=bool(lista_imgs),
                    visita_id=st.session_state.visita_id, paciente_id=st.session_state.patient_id,
                )
            except Exception: pass

# ────────────────────────────────────────────────────────────────────────
# REGISTRO, HISTORIAL Y DASHBOARD (Sin cambios, tal como los pediste)
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
                except Exception as e: st.error(f"Error: {e}")
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
                <div style="background:rgba(0,229,216,0.05);border:1px solid var(--glass-brd);border-radius:12px;padding:16px 18px;margin:8px 0;font-family:Space Mono;">
                    <div style="color:var(--teal);font-size:1.1rem;font-family:Syne;">{p['nombre_completo']}</div>
                    <div style="font-size:0.7rem;color:var(--text-muted);margin-top:5px;">CÉD: <span style="color:white">{p.get('cedula','—')}</span> | EDAD: <span style="color:white">{p.get('edad','—')}</span></div>
                    <div style="font-size:0.7rem;color:var(--text-muted);margin-top:5px;">ANTECEDENTES: <span style="color:white">{p.get('antecedentes','—')}</span></div>
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
