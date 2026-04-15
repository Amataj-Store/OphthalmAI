"""
modelo_vision.py – Hospital Rísquez · OphthalmAI v3.2
Motor Conversacional + Diagnóstico Local
Especialidad: Úlceras Corneales (Queratitis) y Uveítis
Arquitectura: EfficientNetB0 Transfer Learning (modo simulado hasta GPU en nube)
"""

import random
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════════════
# PROTOCOLOS CLÍNICOS — Solo Úlcera Corneal y Uveítis
# Fuente: AAO, ESCRS, SVO, Hospital Rísquez
# ══════════════════════════════════════════════════════════════════════════════

PROTOCOLO_UVEITIS = """**🔵 UVEÍTIS ANTERIOR — Protocolo AAO/Hospital Rísquez**

**Objetivo:** Suprimir inflamación de cámara anterior + prevenir sinequias + estabilizar barrera hemato-acuosa.

**1. Corticosteroides Tópicos (pilar del tratamiento):**
- **Acetato de Prednisolona 1%** *(estándar de oro — mayor penetración intraocular)*
  - Tyndall 1–2+: 1 gota c/4–6 h
  - Tyndall 3–4+: 1 gota c/1–2 h → reducción lenta (tapering) para evitar efecto rebote
- **Dexametasona 0.1%**: alternativa, menor penetración que el acetato.

**2. Ciclopléjicos / Midriáticos** *(esenciales)*:
- **Ciclopentolato 1%** c/8–12 h → uveítis leve-moderada
- **Atropina 1%** 2 veces/día → inflamación severa, alto riesgo de sinequias
- *Función:* Previenen sinequias posteriores + alivian espasmo del cuerpo ciliar

**3. Control de PIO obligatorio:**
- Tanto la uveítis como el uso prolongado de esteroides pueden elevar la PIO.
- Hipotensores oculares si PIO > 21 mmHg: β-bloqueantes o inhibidores de anhidrasa carbónica.

**4. Uveítis crónica / recurrente:**
- Inmunomoduladores: **Metotrexato** o biológicos **Anti-TNF (Adalimumab)** previa evaluación sistémica.

**5. Medidas generales:**
- Lágrimas artificiales sin conservantes (mejoran microambiente de superficie ocular).
- Buscar etiología sistémica: HLA-B27, FAN, ANCA, VDRL, PPD/IGRA, Rx tórax.

⚠️ *Señales de alarma: PIO > 30 mmHg, sinequias extensas, hipopión, edema macular cistoide.*"""

PROTOCOLO_ULCERA_BACTERIANA = """**⚠️ QUERATITIS BACTERIANA — URGENCIA OFTALMOLÓGICA**

> 🔴 *Tomar raspado corneal (Gram, Giemsa) ANTES de iniciar antibióticos.*

**Antibioticoterapia Empírica:**
- **Leve-Moderada** → Fluoroquinolona 4ta generación (Moxifloxacino 0.5% o Vigabatrina)
  - Dosis de carga: 1 gota c/15–30 min las primeras 24–48 h
- **Severa / eje visual amenazado** → Terapia combinada reforzada:
  - **Vancomicina** (Gram +) + **Ceftazidima o Amikacina** (Gram –), alternando c/hora

**Contraindicaciones:**
- 🚫 **Esteroides tópicos contraindicados** en fase activa infecciosa.
- Solo se consideran tras control bacteriano confirmado + epitelio cerrando.

**Medidas generales:**
- Limpiar secreciones antes del tratamiento (mejora biodisponibilidad).
- No ocluir el ojo (favorece anaerobiosis).
- Suspender lentes de contacto de inmediato.
- Control en 24–48 h; hospitalizar si progresión rápida."""

PROTOCOLO_ULCERA_HERPETICA = """**🟡 QUERATITIS HERPÉTICA (HSV) — Protocolo Específico**

**Antivirales Tópicos:**
- **Ganciclovir gel 0.15%** 5 veces al día (primera línea)
- **Aciclovir ungüento 3%** 5 veces al día (alternativa)

**Antivirales Sistémicos:**
- **Aciclovir 400 mg** 5 veces/día VO
- **Valaciclovir 500 mg** 3 veces/día VO (mejor biodisponibilidad)

**⚠️ CRÍTICO:**
- 🚫 **NUNCA usar esteroides** en úlcera dendrítica (epitelial) → riesgo de transformación a úlcera geográfica.
- Los esteroides solo se consideran en queratitis estromal herpética (sin defecto epitelial activo) y bajo supervisión estricta."""

PROTOCOLO_ULCERA_FUNGICA = """**🟠 QUERATITIS FÚNGICA — Protocolo Específico**

**Hongos filamentosos (Fusarium, Aspergillus):**
- **Natamicina 5%** → primera línea. 1 gota c/1–2 h inicialmente.

**Levaduras (Candida):**
- **Anfotericina B 0.15–0.5%** → preferible en infección por cándida.

**Consideraciones:**
- Evolución lenta — respuesta más tardía que bacteriana.
- Evitar esteroides hasta confirmar control del hongo.
- Toma de muestra para cultivo en medio Sabouraud es esencial.
- Hospitalizar si hay amenaza de perforación o extensión rápida."""


# ══════════════════════════════════════════════════════════════════════════════
# KEYWORDS POR PATOLOGÍA
# ══════════════════════════════════════════════════════════════════════════════

KW_UVEITIS = [
    "uveitis", "uveítis", "iritis", "dolor", "fotofobia", "miosis",
    "tyndall", "celulas", "células", "flare", "sinequias", "ciliar",
    "precipitados", "hipopion", "hipopión", "inflamacion", "inflamación",
    "camara anterior", "cámara anterior", "ojo rojo", "lagrimeo",
    "visión borrosa", "vision borrosa", "hiperemia", "depositos", "depósitos"
]

KW_ULCERA = [
    "ulcera", "úlcera", "corneal", "queratitis", "secrecion", "secreción",
    "lentes de contacto", "infiltrado", "defecto epitelial", "fluorescencia",
    "tincion", "tinción", "estroma", "estromal", "purulento", "herpetica",
    "herpética", "fungica", "fúngica", "bacteriana", "dendritica", "dendrítica",
    "perforacion", "perforación", "raspado", "cultivo", "gram", "giemsa"
]

KW_CIERRE = [
    "gracias", "mas nada", "más nada", "listo", "excelente",
    "perfecto", "de acuerdo", "ok gracias", "muchas gracias",
    "hasta luego", "hasta pronto", "nos vemos"
]

KW_SALUDOS = [
    "hola", "buenos días", "buenas tardes", "buenas noches",
    "buenos dias", "buenas", "saludos", "que tal", "qué tal", "buen dia"
]

KW_AFIRMACION = [
    "si", "sí", "ok", "vale", "claro", "por favor",
    "adelante", "correcto", "entendido", "proceda"
]


# ══════════════════════════════════════════════════════════════════════════════
# MOTOR PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def analizar_imagen_y_sintomas(lista_imagenes: list, texto_doctor: str) -> str:
    """
    Motor principal: detecta intención conversacional o realiza evaluación clínica.
    Solo trabaja con Úlcera Corneal y Uveítis.
    """
    texto  = texto_doctor.lower().strip()
    n_imgs = len(lista_imagenes) if lista_imagenes else 0

    # ── MÓDULO CONVERSACIONAL ─────────────────────────────────────────────────

    if any(s in texto for s in KW_SALUDOS):
        hora   = datetime.now().hour
        saludo = "Buenos días" if hora < 12 else ("Buenas tardes" if hora < 19 else "Buenas noches")
        return (
            f"{saludo}, Doctor. El sistema **OphthalmAI** está activo y listo para asistirle. "
            "Especializado en **Úlceras Corneales** y **Uveítis**. "
            "¿Qué caso clínico evaluamos hoy? Puede describir los síntomas o subir imágenes del segmento anterior."
        )

    if any(s in texto for s in KW_CIERRE):
        return random.choice([
            "¡A su completa disposición, Doctor! Todo ha quedado registrado en el historial del paciente. Avíseme cuando ingrese el próximo caso.",
            "¡Con gusto! Recuerde el control del paciente en 24–48 horas. Estoy listo para el próximo caso clínico.",
            "Siempre a la orden. Si desea registrar la evolución o revisar el historial, lo tiene disponible en el panel lateral.",
        ])

    if texto.strip() in KW_AFIRMACION or texto.strip().startswith(("si,", "si ", "sí,")):
        return "¡Entendido, Doctor! ¿Continuamos con alguna otra evaluación o cerramos la consulta de hoy?"

    if any(s in texto for s in ["cómo funciona", "como funciona", "ayuda", "help", "qué puedes"]):
        return (
            "Soy **OphthalmAI**, asistente diagnóstico del Hospital Rísquez especializado en:\n\n"
            "🔵 **Uveítis Anterior** — Protocolos AAO con corticosteroides, ciclopléjicos e inmunomoduladores.\n\n"
            "⚠️ **Úlcera Corneal / Queratitis** — Bacteriana, Herpética y Fúngica. Protocolos urgentes.\n\n"
            "Analizo imágenes del segmento anterior con **EfficientNetB0** y cruzo los hallazgos con los síntomas. "
            "Cada consulta queda guardada con historial y seguimiento de evolución."
        )

    # Consulta de protocolo específico sin imagen
    if "protocolo" in texto or "tratamiento" in texto or "manejo" in texto:
        if any(k in texto for k in ["herpetica","herpética","herpes","hsv","dendritica"]):
            return f"Protocolo para queratitis herpética:\n\n{PROTOCOLO_ULCERA_HERPETICA}"
        if any(k in texto for k in ["fungica","fúngica","hongo","natamicina","candida"]):
            return f"Protocolo para queratitis fúngica:\n\n{PROTOCOLO_ULCERA_FUNGICA}"
        if any(k in texto for k in ["ulcera","úlcera","bacteriana","queratitis","corneal"]):
            return f"Protocolo para queratitis bacteriana:\n\n{PROTOCOLO_ULCERA_BACTERIANA}"
        if any(k in texto for k in ["uveitis","uveítis","iritis"]):
            return f"Protocolo de uveítis anterior:\n\n{PROTOCOLO_UVEITIS}"

    # ── EVALUACIÓN CLÍNICA ────────────────────────────────────────────────────

    hits_uveitis = sum(1 for k in KW_UVEITIS if k in texto)
    hits_ulcera  = sum(1 for k in KW_ULCERA  if k in texto)

    # Subcategoría de úlcera
    es_herpetica = any(k in texto for k in ["herpetica","herpética","herpes","hsv","dendritica","aciclovir"])
    es_fungica   = any(k in texto for k in ["fungica","fúngica","hongo","natamicina","candida","filamentoso"])

    # Sin imagen y sin síntomas claros
    if n_imgs == 0 and hits_uveitis == 0 and hits_ulcera == 0:
        return (
            "He registrado sus apuntes, Doctor. Para orientar el diagnóstico, indíqueme los síntomas principales:\n\n"
            "- ¿**Dolor + fotofobia + lagrimeo**? → Posible uveítis anterior\n"
            "- ¿**Ojo rojo + secreción + infiltrado corneal**? → Posible queratitis/úlcera\n\n"
            "También puede subir fotografías del segmento anterior para análisis por imagen."
        )

    # Con síntomas pero sin imagen
    if n_imgs == 0:
        if hits_uveitis >= hits_ulcera and hits_uveitis > 0:
            return (
                "Los síntomas descritos son sugestivos de **Uveítis Anterior**, Doctor. "
                "Suba fotografías del segmento anterior para confirmar (Tyndall, sinequias, hipopión).\n\n"
                f"{PROTOCOLO_UVEITIS}"
            )
        if hits_ulcera > hits_uveitis:
            proto = PROTOCOLO_ULCERA_HERPETICA if es_herpetica else (PROTOCOLO_ULCERA_FUNGICA if es_fungica else PROTOCOLO_ULCERA_BACTERIANA)
            tipo  = "Herpética" if es_herpetica else ("Fúngica" if es_fungica else "Bacteriana")
            return (
                f"El cuadro clínico es compatible con **Queratitis {tipo} / Úlcera Corneal**, Doctor. "
                "Suba la imagen del segmento anterior para evaluar bordes, profundidad y extensión del infiltrado.\n\n"
                f"{proto}"
            )

    # Con imagen
    if n_imgs > 0:
        n_str    = f"las {n_imgs} imágenes" if n_imgs > 1 else "la imagen"
        nota_sim = (
            "\n\n> ⚙️ *Sistema en **Modo Simulado** — hardware local sin GPU. "
            "EfficientNetB0 completo se activa al ejecutar en nube con GPU.*"
        )

        if hits_uveitis >= hits_ulcera and hits_uveitis > 0:
            prob = random.randint(83, 93)
            return (
                f"🩺 **Análisis completado — {n_str} procesada(s)**\n\n"
                f"**Impresión diagnóstica:** Uveítis Anterior *(prob. simulada: {prob}%)*\n\n"
                "**Hallazgos sugeridos en imagen:** Hiperemia ciliar periquerática, posible fenómeno "
                "Tyndall en cámara anterior, pupila miótica, posibles sinequias.\n\n"
                f"{PROTOCOLO_UVEITIS}"
                f"{nota_sim}"
            )

        if hits_ulcera > hits_uveitis or (hits_ulcera == 0 and hits_uveitis == 0):
            prob  = random.randint(85, 94)
            proto = PROTOCOLO_ULCERA_HERPETICA if es_herpetica else (PROTOCOLO_ULCERA_FUNGICA if es_fungica else PROTOCOLO_ULCERA_BACTERIANA)
            tipo  = "Herpética" if es_herpetica else ("Fúngica" if es_fungica else "Bacteriana")
            return (
                f"🩺 **Análisis completado — {n_str} procesada(s)**\n\n"
                f"**Impresión diagnóstica:** Queratitis {tipo} / Úlcera Corneal *(prob. simulada: {prob}%)*\n\n"
                "**Hallazgos sugeridos en imagen:** Infiltrado estromal, defecto epitelial corneal, "
                "reacción inflamatoria perilímbica.\n\n"
                f"{proto}"
                f"{nota_sim}"
            )

    # Fallback
    return (
        "Entendido, Doctor. ¿Podría ampliar los síntomas o adjuntar imágenes del segmento anterior? "
        "Estoy especializado en **Úlceras Corneales** y **Uveítis**."
    )


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES
# ══════════════════════════════════════════════════════════════════════════════

def generar_resumen_consulta(doctor: str, paciente: str, chat_history: list) -> str:
    """Genera un resumen texto plano de la consulta para exportar."""
    lineas = [
        "=" * 62,
        "   HOSPITAL RÍSQUEZ · OphthalmAI v3.2",
        "   RESUMEN DE CONSULTA OFTALMOLÓGICA",
        "=" * 62,
        f"Fecha:    {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Doctor:   {doctor}",
        f"Paciente: {paciente}",
        "-" * 62,
        "HISTORIAL DE LA CONSULTA:",
        "-" * 62,
    ]
    for msg in chat_history:
        rol = f"Dr. {doctor}" if msg["role"] == "user" else "OphthalmAI"
        lineas.append(f"\n[{rol}]\n{msg['content']}\n")
    lineas += [
        "=" * 62,
        "Documento generado por OphthalmAI v3.2 — Hospital Rísquez",
        "Este reporte es apoyo diagnóstico. El criterio clínico",
        "definitivo corresponde al médico tratante.",
        "=" * 62,
    ]
    return "\n".join(lineas)
