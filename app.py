"""
app.py – Hospital Rísquez · OphthalmAI v3.4
Diseño Arena.site (Clean UI, Grid, Ojo Realista Central)
"""

import streamlit as st
import time
import database
import modelo_vision

st.set_page_config(
    page_title="OphthalmAI · Hospital Rísquez",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CSS INMERSIVO (Estilo Arena.site exacto)
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

/* Fondo de cuadrícula (Grid) estilo Arena */
[data-testid="stAppViewContainer"] {
    background-color: var(--void) !important;
    background-image: 
        linear-gradient(rgba(0, 229, 216, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 229, 216, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    color: var(--text-main) !important;
    font-family: 'DM Sans', sans-serif;
}[data-testid="stSidebar"] {
    background: var(--navy-mid) !important;
    border-right: 1px solid var(--glass-brd) !important;
}

/* LOGO SIMPLE SIN OJO PEQUEÑO */
.sidebar-logo { text-align:center; padding:20px 16px; border-bottom:1px solid var(--glass-brd); margin-bottom:10px; }
.logo-title { font-family:'Syne',sans-serif; font-weight:800; font-size:1.5rem; color:var(--text-main); letter-spacing:1px; }
.logo-title span { color:var(--teal); }
.logo-sub { font-family:'Space Mono',monospace; font-size:0.6rem; color:var(--text-muted); letter-spacing:2.5px; text-transform:uppercase; margin-top:2px; }

/* CONTENEDOR CENTRAL ESTILO ARENA (Con esquinas de mira láser) */
.welcome-screen {
    position: relative;
    text-align: center; 
    padding: 100px 20px;
    background: radial-gradient(circle at center, rgba(0,229,216,0.08) 0%, transparent 60%);
    border: 1px solid rgba(0,229,216,0.05);
    margin-top: 40px;
}
/* Las 4 esquinas del contenedor */
.welcome-screen::before { content:''; position:absolute; top:0; left:0; width:40px; height:40px; border-top:2px solid var(--teal); border-left:2px solid var(--teal); opacity:0.6; }
.welcome-screen::after { content:''; position:absolute; bottom:0; right:0; width:40px; height:40px; border-bottom:2px solid var(--teal); border-right:2px solid var(--teal); opacity:0.6; }
.ws-tr { position:absolute; top:0; right:0; width:40px; height:40px; border-top:2px solid var(--teal); border-right:2px solid var(--teal); opacity:0.6; }
.ws-bl { position:absolute; bottom:0; left:0; width:40px; height:40px; border-bottom:2px solid var(--teal); border-left:2px solid var(--teal); opacity:0.6; }

/* El Ojo Realista Central */
.realistic-eye {
    width: 250px; /* OJO GIGANTE */
    height: auto;
    margin: 0 auto 30px auto;
    border-radius: 50%;
    filter: drop-shadow(0 0 30px rgba(0,229,216,0.5)) drop-shadow(0 0 60px rgba(0,207,255,0.2));
    animation: float-eye 6s ease-in-out infinite;
}
@keyframes float-eye {
    0% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-10px) scale(1.02); }
    100% { transform: translateY(0px) scale(1); }
}

.welcome-screen h2 { font-family:'Syne',sans-serif!important; font-weight:800; font-size:2rem; color:var(--text-main)!important; margin:0 0 8px!important; }
.welcome-screen p { color:var(--text-muted); font-size:1rem; max-width:500px; margin:0 auto; line-height:1.8; }

/* HEADER SUPERIOR LIMPIO */
.hud-header{display:flex;align-items:center;padding:10px 0 20px;border-bottom:1px solid var(--glass-brd);margin-bottom:20px;}
.hud-title h1{font-family:'Syne',sans-serif!important;font-weight:800!important;font-size:1.8rem!important;color:var(--text-main)!important;margin:0!important;}
.hud-title h1 em{font-style:normal;color:var(--teal);}
.hud-meta{margin-left:auto;text-align:right;font-family:'Space Mono',monospace;font-size:0.6rem;color:var(--text-muted);}

/* ESTILOS GENERALES (Botones, Inputs, Chat) */
[data-testid="stSidebar"] label, .stTextInput label {font-family:'Space Mono',monospace!important;font-size:0.62rem!important;color:var(--text-muted)!important;text-transform:uppercase;}[data-testid="stSidebar"] input, .stTextInput input, textarea {background:rgba(5,10,20,0.9)!important;color:var(--teal)!important;border:1px solid var(--glass-brd)!important;border-radius:8px!important;}
.stButton>button {background:transparent!important;color:var(--teal)!important;font-family:'Syne',sans-serif!important;font-weight:700!important;border:1px solid var(--teal)!important;border-radius:8px!important;}
.stButton>button:hover {background:var(--teal)!important;color:var(--void)!important;box-shadow:0 0 20px rgba(0,229,216,0.4)!important;}
[data-testid="stChatMessage"]{background:var(--panel)!important;border:1px solid var(--glass-brd)!important;border-radius:12px!important;backdrop-filter:blur(12px);}
[data-testid="stImage"] img{border-radius:10px!important;border:1px solid var(--glass-brd)!important;}[data-testid="stFileUploader"]{background:rgba(5,10,20,0.8)!important;border:1px dashed var(--glass-brd)!important;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# INICIALIZACIÓN
# ──────────────────────────────────────────────────────────────────────────────
database.init_db()

defaults = {
    "messages":[], "session_active": False, "doctor_name": "",
    "patient_name": "", "session_idx": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR (Sin ojos pequeños)
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-title">Ophthalm<span>AI</span></div>
        <div class="logo-sub">Hospital Rísquez · Caracas</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-family:Space Mono; font-size:0.6rem; color:var(--teal); margin:15px 0 5px;">// DATOS DE LA CONSULTA</div>', unsafe_allow_html=True)
    doctor_input  = st.text_input("Nombre del Doctor", value=st.session_state.doctor_name, disabled=st.session_state.session_active)
    patient_input = st.text_input("Paciente", value=st.session_state.patient_name, disabled=st.session_state.session_active)

    if not st.session_state.session_active:
        if st.button("▶ INICIAR SESIÓN"):
            if doctor_input.strip() and patient_input.strip():
                st.session_state.doctor_name = doctor_input.strip()
                st.session_state.patient_name = patient_input.strip()
                st.session_state.session_active = True
                st.session_state.messages =[]
                st.session_state.messages.append({"role": "assistant", "content": f"Bienvenido, **Dr. {doctor_input.strip()}**. Especialidad activa: **Úlceras Corneales** y **Uveítis**.\n\n¿Desea ingresar síntomas, subir fotografías, o solicitar un protocolo de tratamiento?"})
                st.rerun()
            else:
                st.error("Complete los campos.")
    else:
        if st.button("⏹ FINALIZAR CONSULTA"):
            for k, v in defaults.items():
                if k != "session_idx": st.session_state[k] = v
            st.session_state.session_idx += 1
            st.rerun()

    if st.session_state.session_active:
        st.markdown('<div style="font-family:Space Mono; font-size:0.6rem; color:var(--teal); margin:15px 0 5px;">// IMÁGENES DEL SEGMENTO ANTERIOR</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Fotografías", type=["jpg","jpeg","png"], accept_multiple_files=True,
            label_visibility="collapsed", key=f"up_{st.session_state.session_idx}" 
        )
        if uploaded_files:
            cols = st.columns(min(len(uploaded_files), 2))
            for i, f in enumerate(uploaded_files): cols[i % 2].image(f, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN AREA
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hud-header">
    <div class="hud-title"><h1>Ophthalm<em>AI</em></h1></div>
    <div class="hud-meta">EfficientNetB0 · v3.4</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.session_active:
    # URL de un ojo realista impresionante y tecnológico
    OJO_REALISTA_URL = "https://images.unsplash.com/photo-1542282088-fe8426682b8f?auto=format&fit=crop&w=500&q=80"
    
    st.markdown(f"""
    <div class="welcome-screen">
        <div class="ws-tr"></div><div class="ws-bl"></div>
        <img src="{OJO_REALISTA_URL}" class="realistic-eye">
        <h2>OphthalmAI en espera</h2>
        <p>Sistema diagnóstico asistido por Red Neuronal. Procesamiento 100% local.<br>Inicie sesión en el panel lateral para comenzar.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(f"[Dr. {st.session_state.doctor_name}] Escriba síntomas, pida un protocolo, o analice fotos...")

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
                respuesta_ia = f"⚠️ Error: `{e}`"

            full_response = ""
            for chunk in respuesta_ia.split():
                full_response += chunk + " "
                ph.markdown(full_response + "▌")
                time.sleep(0.02)
            ph.markdown(full_response.strip())

        st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})
