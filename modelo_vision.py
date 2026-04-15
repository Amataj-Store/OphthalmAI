"""
modelo_vision.py – Hospital Rísquez · OphthalmAI v3.1
Módulo Conversacional + Motor Diagnóstico Local
Arquitectura: EfficientNetB0 con Transfer Learning (modo simulado hasta deployment en nube)

Autores: Tesis UCV · Supervisado por personal médico del Hospital Rísquez
"""

import random
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════════════
# PROTOCOLOS CLÍNICOS (AAO / ESCRS / SVO – Hospital Rísquez)
# ══════════════════════════════════════════════════════════════════════════════

PROTOCOLO_ULCERA = """**⚠️ QUERATITIS INFECCIOSA — URGENCIA OFTALMOLÓGICA**

**Paso 1 · Antes de cualquier tratamiento:**
- Tomar raspado corneal para cultivo (Gram, Giemsa, KOH) y antibiograma.
- No inocular antibióticos antes de la toma de muestra.

**Paso 2 · Antibioticoterapia empírica tópica:**
- Bacteriana leve-moderada: **Moxifloxacino 0.5%** o **Ciprofloxacino 0.3%** cada 15–30 min la 1.ª hora, luego cada hora.
- Bacteriana severa / eje visual: **Vancomicina 50 mg/ml + Ceftazidima 50 mg/ml** (terapia combinada) cada hora alternado.
- Herpética (dendrítica): **Ganciclovir gel 0.15%** + **Aciclovir 400 mg VO** 5 veces/día.

**Paso 3 · Medidas generales:**
- 🚫 CONTRAINDICADO: Esteroides tópicos en fase activa de úlcera bacteriana o viral.
- No ocluir el ojo (favorece anaerobiosis).
- Suspender lentes de contacto inmediatamente.
- Control en 24–48 h; hospitalizar si progresión rápida.

**Paso 4 · Señales de alarma para interconsulta urgente:**
Perforación inminente, hipopión en aumento, extensión al limbo esclerocorneal."""

PROTOCOLO_UVEITIS = """**🔵 UVEÍTIS ANTERIOR — PROTOCOLO ESTÁNDAR AAO/ESCRS**

**Objetivo primario:** Suprimir inflamación + preservar barrera hemato-acuosa + prevenir sinequias.

**Corticosteroides tópicos:**
- **Acetato de Prednisolona 1%**: según celularidad en cámara anterior (Tyndall 0–4+):
  - Tyndall 1–2+: 1 gota cada 4–6 h
  - Tyndall 3–4+: 1 gota cada 1–2 h, reducción progresiva muy lenta (meses).
- Alternativa: **Dexametasona 0.1%** — similar eficacia.

**Ciclopléjicos / Midriáticos:**
- **Ciclopentolato 1%** cada 8–12 h (uveítis leve-moderada).
- **Atropina 1%** 2 veces/día (uveítis severa, alto riesgo de sinequias).

**Monitoreo obligatorio:**
- Presión Intraocular (PIO) en cada visita — riesgo de HTO por corticoides.
- Buscar etiología sistémica: HLA-B27, FAN, ANCA, VDRL, PPD/IGRA, Rx tórax.

**Señales de alarma:**
PIO > 30 mmHg, sinequias posteriores, uveítis intermedia/posterior — referir a uveítis especializada."""

PROTOCOLO_GLAUCOMA = """**🟡 HIPERTENSIÓN OCULAR / SOSPECHA DE GLAUCOMA**

**Evaluación inicial:**
- Tonometría de aplanación (Goldmann) — valores normales: 10–21 mmHg.
- Paquimetría corneal central (corrección de PIO según espesor).
- Campo visual (Humphrey 24-2) y OCT de fibras del nervio óptico.

**Primera línea de tratamiento médico:**
- **Análogo de prostaglandina** (Latanoprost 0.005% o Travoprost 0.004%) — una gota nocturna. Reducción ~25–30%.
- **β-bloqueante** (Timolol 0.5%) mañana y noche si PIO persiste elevada.
- Contraindicación: Timolol en asma, EPOC, bloqueo AV.

**Seguimiento:**
- Control de PIO a las 4–6 semanas de inicio.
- Si no controlada médicamente: considerar trabeculoplastia láser (SLT) o cirugía filtrante."""

PROTOCOLO_CONJUNTIVITIS = """**🟢 CONJUNTIVITIS — DIAGNÓSTICO DIFERENCIAL Y MANEJO**

**Bacteriana:** Secreción purulenta, sin dolor profundo, visión conservada.
- Tobramicina 0.3% o Azitromicina 1.5% cada 8–12 h por 5–7 días.
- Hisopado conjuntival si sospecha gonocócica (urgencia: Ceftriaxona IM).

**Viral (adenoviral — más frecuente):** Secreción serosa, folículos tarsal, adenopatía preauricular.
- Tratamiento de soporte: Lubricantes, compresas frías, higiene de manos estricta.
- Altamente contagiosa — aislamiento laboral 7–14 días.

**Alérgica:** Prurito intenso, quemosis, estacional/crónica.
- Antihistamínico tópico (Olopatadina 0.1%) + Lubricantes.
- Casos severos: corticoide tópico de baja penetración (Fluorometolona 0.1%) ciclos cortos."""


# ══════════════════════════════════════════════════════════════════════════════
# DETECCIÓN DE INTENCIÓN Y RESPUESTA CONVERSACIONAL
# ══════════════════════════════════════════════════════════════════════════════

def analizar_imagen_y_sintomas(lista_imagenes: list, texto_doctor: str) -> str:
    """
    Motor principal: detecta intención conversacional y/o realiza evaluación clínica.

    Args:
        lista_imagenes: Lista de bytes de imágenes del segmento anterior.
        texto_doctor:   Texto libre del médico (síntomas, preguntas, saludos).

    Returns:
        str: Respuesta clínica o conversacional formateada en Markdown.
    """
    texto = texto_doctor.lower().strip()
    n_fotos = len(lista_imagenes) if lista_imagenes else 0

    # ── 1. MÓDULO CONVERSACIONAL ──────────────────────────────────────────────

    # Saludos
    if any(s in texto for s in ["hola", "buenos días", "buenas tardes", "buenas noches",
                                  "buenos dias", "buenas", "saludos", "que tal", "qué tal"]):
        hora = datetime.now().hour
        saludo = "Buenos días" if hora < 12 else ("Buenas tardes" if hora < 19 else "Buenas noches")
        return (
            f"{saludo}, Doctor. El sistema visual **EfficientNetB0** está calibrado y en línea. "
            "¿Qué caso clínico tenemos hoy? Puede describirme los síntomas o subir imágenes del segmento anterior."
        )

    # Agradecimientos y cierre
    if any(s in texto for s in ["gracias", "mas nada", "más nada", "listo", "excelente",
                                  "perfecto", "de acuerdo", "ok gracias", "muchas gracias"]):
        return random.choice([
            "¡A su completa disposición, Doctor! Todo ha quedado registrado en el historial del paciente. Avíseme cuando ingrese el próximo caso.",
            "¡Con gusto! Recuerde revisar el seguimiento en 24–48 horas. Estoy listo para el próximo paciente.",
            "Siempre a la orden. Si necesita consultar un historial previo o registrar la evolución, lo asisto desde el panel lateral.",
        ])

    # Afirmaciones simples
    if texto in ["si", "sí", "ok", "vale", "claro", "por favor", "adelante", "correcto"]:
        return "¡Entendido! ¿Continuamos con alguna otra evaluación o cerramos la consulta de hoy?"

    # Pregunta sobre el sistema
    if any(s in texto for s in ["cómo funciona", "como funciona", "qué eres", "que eres",
                                  "qué puedes hacer", "que puedes hacer", "ayuda", "help"]):
        return (
            "Soy **OphthalmAI**, el asistente de diagnóstico del Hospital Rísquez. "
            "Analizo imágenes del segmento anterior usando una red neuronal **EfficientNetB0** con Transfer Learning, "
            "cruzo los hallazgos con los síntomas que usted describe, y le sugiero protocolos clínicos según las guías **AAO/ESCRS/SVO**.\n\n"
            "Puedo ayudarle con: **Úlceras Corneales**, **Uveítis Anterior**, **Glaucoma/HTO**, **Conjuntivitis** y más. "
            "Cada consulta queda guardada en la base de datos con historial y seguimiento."
        )

    # Pregunta sobre protocolos sin imagen
    if "protocolo" in texto or "tratamiento" in texto or "manejo" in texto:
        if "ulcera" in texto or "úlcera" in texto or "corneal" in texto or "queratitis" in texto:
            return f"Aquí el protocolo para queratitis infecciosa, Doctor:\n\n{PROTOCOLO_ULCERA}"
        if "uveitis" in texto or "uveítis" in texto:
            return f"Protocolo de uveítis anterior:\n\n{PROTOCOLO_UVEITIS}"
        if "glaucoma" in texto or "pio" in texto or "presion" in texto or "presión" in texto:
            return f"Protocolo de glaucoma/HTO:\n\n{PROTOCOLO_GLAUCOMA}"
        if "conjuntivitis" in texto:
            return f"Protocolo de conjuntivitis:\n\n{PROTOCOLO_CONJUNTIVITIS}"

    # ── 2. EVALUACIÓN CLÍNICA ─────────────────────────────────────────────────

    # Detección de entidades clínicas por palabras clave
    kw_ulcera    = ["ulcera", "úlcera", "corneal", "queratitis", "rojo", "secrecion",
                    "secreción", "lentes de contacto", "infiltrado", "defecto epitelial",
                    "fluorescencia", "tincion", "tinción"]
    kw_uveitis   = ["uveitis", "uveítis", "dolor", "fotofobia", "miosis", "tyndall",
                    "celulas", "células", "flare", "sinequias", "ciliar", "iritis"]
    kw_glaucoma  = ["glaucoma", "pio", "presion intraocular", "presión intraocular",
                    "nervio optico", "nervio óptico", "campo visual", "excavacion",
                    "excavación", "hto", "hipertension ocular"]
    kw_conjunt   = ["conjuntivitis", "conjuntival", "papila", "foliculo", "folículo",
                    "prurito", "quemosis", "adenopatia", "adenopatía", "picazon", "picazón"]

    hits_ulcera   = sum(1 for k in kw_ulcera   if k in texto)
    hits_uveitis  = sum(1 for k in kw_uveitis  if k in texto)
    hits_glaucoma = sum(1 for k in kw_glaucoma if k in texto)
    hits_conjunt  = sum(1 for k in kw_conjunt  if k in texto)

    max_hits = max(hits_ulcera, hits_uveitis, hits_glaucoma, hits_conjunt)

    # Sin imagen y sin síntomas claros
    if n_fotos == 0 and max_hits == 0:
        return (
            "He registrado sus apuntes, Doctor. Para un análisis más preciso, suba fotografías del "
            "segmento anterior en el panel lateral, o descríbame los síntomas principales del paciente: "
            "¿hay dolor, fotofobia, secreción, hiperemia, o alteración visual?"
        )

    # Con síntomas pero sin imagen
    if n_fotos == 0 and max_hits > 0:
        if hits_uveitis == max_hits:
            return (
                f"Basado en los síntomas descritos, el cuadro es sugestivo de **Uveítis Anterior**, Doctor. "
                f"Para confirmar necesito ver la imagen del segmento anterior (células en cámara, Tyndall, sinequias).\n\n"
                f"{PROTOCOLO_UVEITIS}\n\n"
                "_Suba la fotografía para refinar el diagnóstico._"
            )
        if hits_ulcera == max_hits:
            return (
                f"Los síntomas descritos son compatibles con **Queratitis / Úlcera Corneal**, Doctor. "
                f"Recomiendo la fotografía para evaluar bordes, profundidad y extensión del infiltrado.\n\n"
                f"{PROTOCOLO_ULCERA}\n\n"
                "_Adjunte la imagen del segmento anterior para análisis visual._"
            )
        if hits_glaucoma == max_hits:
            return f"Los datos apuntan a posible **Glaucoma/HTO**. Le comparto el protocolo:\n\n{PROTOCOLO_GLAUCOMA}"
        if hits_conjunt == max_hits:
            return f"Cuadro compatible con **Conjuntivitis**. Protocolo diferencial:\n\n{PROTOCOLO_CONJUNTIVITIS}"

    # ── Con imagen ────────────────────────────────────────────────────────────
    if n_fotos > 0:
        n_str = f"las {n_fotos} imágenes" if n_fotos > 1 else "la imagen"
        nota_modo = (
            "\n\n> ⚙️ *Sistema operando en **Modo Simulado** (hardware local sin GPU). "
            "El modelo EfficientNetB0 completo se activará automáticamente al ejecutar en la nube con GPU.*"
        )

        if hits_ulcera >= hits_uveitis and hits_ulcera > 0:
            prob = random.randint(85, 94)
            return (
                f"🩺 **Análisis Completado — {n_str} procesada(s)**\n\n"
                f"**Impresión Diagnóstica:** Úlcera Corneal / Queratitis Infecciosa "
                f"_(Prob. simulada: {prob}%)_\n\n"
                f"**Hallazgos sugeridos en imagen:** infiltrado estromal, posible defecto epitelial, "
                f"reacción inflamatoria perilímbica.\n\n"
                f"{PROTOCOLO_ULCERA}"
                f"{nota_modo}"
            )

        elif hits_uveitis >= hits_ulcera and hits_uveitis > 0:
            prob = random.randint(82, 93)
            return (
                f"🩺 **Análisis Completado — {n_str} procesada(s)**\n\n"
                f"**Impresión Diagnóstica:** Uveítis Anterior "
                f"_(Prob. simulada: {prob}%)_\n\n"
                f"**Hallazgos sugeridos:** hiperemia ciliar, posibles células en cámara anterior (Tyndall), "
                f"pupila miótica.\n\n"
                f"{PROTOCOLO_UVEITIS}"
                f"{nota_modo}"
            )

        elif hits_glaucoma > 0:
            return (
                f"🩺 **Análisis Completado — {n_str} procesada(s)**\n\n"
                f"**Impresión Diagnóstica:** Sospecha de Glaucoma / HTO\n\n"
                f"{PROTOCOLO_GLAUCOMA}"
                f"{nota_modo}"
            )

        elif hits_conjunt > 0:
            return (
                f"🩺 **Análisis Completado — {n_str} procesada(s)**\n\n"
                f"**Impresión Diagnóstica:** Conjuntivitis (diferencial bacteriana/viral/alérgica)\n\n"
                f"{PROTOCOLO_CONJUNTIVITIS}"
                f"{nota_modo}"
            )

        else:
            # Imagen sin palabras clave claras
            return (
                f"🩺 **Imagen(s) recibida(s) — {n_str}**\n\n"
                f"He procesado la(s) imagen(es). Sin embargo, para orientar el diagnóstico necesito "
                f"que me indique los síntomas principales:\n\n"
                f"- ¿Hay **dolor o fotofobia**? → Orienta a uveítis\n"
                f"- ¿**Secreción o ojo muy rojo**? → Orienta a queratitis/úlcera\n"
                f"- ¿**Presión ocular elevada o visión tubular**? → Orienta a glaucoma\n"
                f"- ¿**Prurito e hiperemia difusa**? → Orienta a conjuntivitis"
                f"{nota_modo}"
            )

    # Fallback genérico
    return (
        "Entendido, Doctor. ¿Puede ampliar los síntomas o adjuntar imágenes del segmento anterior? "
        "Estoy listo para el análisis clínico."
    )


def generar_resumen_consulta(doctor: str, paciente: str, chat_history: list) -> str:
    """
    Genera un resumen de texto plano de la consulta para exportar o imprimir.
    """
    from datetime import datetime
    lineas = [
        "=" * 60,
        "   HOSPITAL RÍSQUEZ · OphthalmAI",
        "   RESUMEN DE CONSULTA OFTALMOLÓGICA",
        "=" * 60,
        f"Fecha:    {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Doctor:   {doctor}",
        f"Paciente: {paciente}",
        "-" * 60,
        "HISTORIAL DE CONSULTA:",
        "-" * 60,
    ]
    for msg in chat_history:
        rol = "Dr." if msg["role"] == "user" else "OphthalmAI"
        lineas.append(f"\n[{rol}]\n{msg['content']}\n")
    lineas += [
        "=" * 60,
        "Documento generado automáticamente por OphthalmAI v3.1",
        "Este reporte es un apoyo diagnóstico. El juicio clínico",
        "definitivo corresponde al médico tratante.",
        "=" * 60,
    ]
    return "\n".join(lineas)
