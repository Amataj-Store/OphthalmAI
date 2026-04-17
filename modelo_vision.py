"""
modelo_vision.py – Hospital Rísquez · OphthalmAI v3.9
Motor Conversacional Inteligente + Diagnóstico Diferencial Seguro (Medical Firewall)
"""

import random
import numpy as np
from PIL import Image
import io
import os

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(DIRECTORIO_ACTUAL, "modelo_oftalmologia.h5")

UMBRAL_CONFIANZA = 50.0 

cnn_model = None
clases_nombres = []
ERROR_CARGA = None  

if not os.path.exists(MODELO_PATH):
    ERROR_CARGA = f"⚠️ ERROR DE SISTEMA: No se encuentra el archivo del modelo en la ruta: `{MODELO_PATH}`. El sistema funciona en Modo Simulado."
else:
    try:
        import tensorflow as tf
        ruta_segura = os.path.normpath(MODELO_PATH)
        cnn_model = tf.keras.models.load_model(ruta_segura, compile=False)
        clases_nombres = ['sano', 'ulcera', 'uveitis']
    except Exception as e:
        ERROR_CARGA = f"⚠️ ERROR CARGANDO TENSORFLOW/MODELO en ruta `{ruta_segura}`: `{e}`. El sistema funciona en Modo Simulado."
        cnn_model = None

def procesar_imagen_real(imagen_bytes):
    if cnn_model is None: 
        return None, 0.0
    try:
        img = Image.open(io.BytesIO(imagen_bytes)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        predicciones = cnn_model.predict(img_array, verbose=0)[0]
        indice_clase = np.argmax(predicciones)
        prob = predicciones[indice_clase] * 100
        return clases_nombres[indice_clase], prob
    except Exception:
        return None, 0.0

PROTOCOLO_UVEITIS = """**🔵 PROTOCOLO: UVEÍTIS ANTERIOR (No Infecciosa)**
*Objetivo: Suprimir inflamación y evitar sinequias posteriores.*
- **Esteroides Tópicos (Pilar):** Acetato de Prednisolona 1% (Estándar de oro por alta penetración). Dosis de carga: 1 gota/hora en severos, luego reducción paulatina (tapering) para evitar rebote. *Alternativa:* Dexametasona 0.1% (menor penetración).
- **Ciclopléjicos/Midriáticos:** Ciclopentolato 1% o Atropina 1% (reservar para inflamaciones intensas por su larga duración). Previene sinequias y alivia espasmo ciliar.
- **Inmunomoduladores (Casos Crónicos/Recurrentes):** Si falla esteroide, evaluar Metotrexato o biológicos (Anti-TNF como Adalimumab) previa valoración sistémica.
- ⚠️ **Control de PIO:** Monitorizar por riesgo de hipertensión secundaria a esteroides. Usar hipotensores si es necesario (Beta-bloqueantes/ICA)."""

PROTOCOLO_ULCERA = """**⚠️ PROTOCOLO: ÚLCERA CORNEAL / QUERATITIS INFECCIOSA**
*Urgencia Oftalmológica. El manejo depende de la etiología.*
🔴 **PASO 1 (CRÍTICO):** Toma de muestra para Cultivo y Frotis (Gram/Giemsa) **ANTES** de la primera gota de antibiótico. Limpiar secreciones previamente para asegurar biodisponibilidad del fármaco.

**A. Queratitis Bacteriana (Empírica):**
- **Monoterapia:** Fluoroquinolonas 4ta gen (Moxifloxacino) c/15-30 min (dosis carga 24-48h).
- **Terapia Reforzada (Amenaza eje visual):** Vancomicina (Gram +) + Ceftazidima o Amikacina (Gram -) alternados cada hora.
- 🚫 **Esteroides:** CONTRAINDICADOS en fase activa. Solo considerar cuando el epitelio esté cerrando y la bacteria controlada.

**B. Queratitis Herpética (Viral - HSV):**
- **Tópicos:** Ganciclovir gel (5 veces/día) o Aciclovir ungüento.
- **Sistémicos:** Aciclovir 400mg (5 veces/día) o Valaciclovir 500mg (3 veces/día).
- 🚫 **NUNCA** usar esteroides en úlcera dendrítica (epitelial), riesgo de úlcera geográfica.

**C. Queratitis Fúngica:**
- **Elección:** Natamicina 5% (hongos filamentosos).
- **Alternativa:** Anfotericina B 0.15-0.5% (Candida/levaduras).

💡 **Soporte:** Lágrimas artificiales sin conservantes para reepitelización. Control estricto de PIO."""

DISCLAIMER = "\n\n*⚠️ OphthalmAI es un sistema de apoyo. Confirmar siempre con lámpara de hendidura y criterio clínico.*"

# ── LISTADOS CLÍNICOS SEGÚN ACADEMIA AMERICANA DE OFTALMOLOGÍA ──

# Síntomas que apuntan FUERTEMENTE a Úlcera Corneal
SINTOMAS_CLAVE_ULCERA = ["secrecion", "secreción", "secreción ocular", "lagrimeo", "mancha blanca", "hipopion", "queratitis", "cuerpo extraño"]

# Síntomas que apuntan FUERTEMENTE a Uveítis Anterior
SINTOMAS_CLAVE_UVEITIS = ["fotofobia", "fotofobia severa", "vision borrosa", "miosis", "tyndall", "dolor profundo"]

# Síntomas AMBIGUOS (Comunes en AMBAS patologías - ¡PROHIBIDO RECETAR SOLO CON ESTO!)
SINTOMAS_AMBIGUOS = ["ojo rojo", "rojeza", "dolor", "dolor ocular", "ardor", "inflamacion", "ojo irritado"]


def analizar_imagen_y_sintomas(lista_imagenes: list, texto_doctor: str) -> str:
    texto = texto_doctor.lower().strip()
    
    # 1. PEDIR TRATAMIENTOS DIRECTAMENTE
    if any(p in texto for p in ["tratamiento", "protocolo", "medicamento", "recet", "manejo"]):
        if "uveitis" in texto or "uveítis" in texto:
            return f"Claro, Doctor. Aquí tiene el manejo indicado:\n\n{PROTOCOLO_UVEITIS}{DISCLAIMER}"
        elif "ulcera" in texto or "úlcera" in texto or "queratitis" in texto:
            return f"Claro, Doctor. Aquí tiene el manejo de urgencia:\n\n{PROTOCOLO_ULCERA}{DISCLAIMER}"
        else:
            return "Por favor especifique de qué patología desea el protocolo: ¿Úlcera Corneal o Uveítis Anterior?"

    # 2. INTENCIÓN DE NAVEGACIÓN
    if any(s in texto for s in ["historial", "ver historial", "expediente", "buscar paciente"]):
        return "¡Por supuesto! Para consultar expedientes previos, diríjase al menú lateral izquierdo y seleccione **📂 Historial**."
    if any(s in texto for s in ["registrar", "nuevo paciente", "registro", "crear paciente"]):
        return "Para ingresar un nuevo paciente al sistema, por favor diríjase a **📋 Registro** en el menú lateral."

    # 3. CONVERSACIÓN FLUIDA Y CIERRE
    if any(s in texto for s in ["terminar", "finalizar", "cerrar", "adios", "chao", "hasta luego", "me voy"]):
        return "¡Hasta luego, Doctor! Para guardar la sesión y liberar la memoria, presione **⏹ FINALIZAR CONSULTA** en el menú lateral."
    if any(s in texto for s in ["gracias", "listo", "excelente", "perfecto", "ok", "mas nada", "ya", "entendido"]):
        return "¡A la orden! Si necesita algo más, puedo analizar otras fotos o buscar protocolos. Si terminamos, recuerde presionar **⏹ FINALIZAR CONSULTA**."
    if any(s in texto for s in ["hola", "buenos", "buenas", "saludos"]):
        return "¡Saludos, Doctor! Especialidad activa: **Úlceras y Uveítis**. ¿En qué le puedo ayudar hoy?"

    # 4. EVALUACIÓN DE IMÁGENES (CNN)
    if lista_imagenes:
        diagnosticos = []
        for i, img_bytes in enumerate(lista_imagenes):
            clase_detectada, prob = procesar_imagen_real(img_bytes)
            if clase_detectada is None:
                if any(s in texto for s in SINTOMAS_CLAVE_ULCERA):
                    diagnosticos.append(f"Img {i+1}: Úlcera Corneal (Simulado)")
                elif any(s in texto for s in SINTOMAS_CLAVE_UVEITIS):
                    diagnosticos.append(f"Img {i+1}: Uveítis Anterior (Simulado)")
                else:
                    diagnosticos.append(f"Img {i+1}: Hallazgo indeterminado (Simulado)")
            elif prob < UMBRAL_CONFIANZA:
                diagnosticos.append(f"Img {i+1}: ⚠️ Imagen dudosa (CNN: {prob:.1f}% - {clase_detectada})")
            else:
                if clase_detectada == 'ulcera':
                    diagnosticos.append(f"Img {i+1}: ⚠️ Úlcera Corneal (CNN: {prob:.1f}%)")
                elif clase_detectada == 'uveitis':
                    diagnosticos.append(f"Img {i+1}: 🔵 Uveítis Anterior (CNN: {prob:.1f}%)")
                else:
                    diagnosticos.append(f"Img {i+1}: ✅ Segmento Sano (CNN: {prob:.1f}%)")

        texto_diagnosticos = "\n".join(diagnosticos)
        protocolo_a_mostrar = ""
        if any("úlcer" in d.lower() for d in diagnosticos):
            protocolo_a_mostrar = PROTOCOLO_ULCERA
        elif any("uveít" in d.lower() for d in diagnosticos):
            protocolo_a_mostrar = PROTOCOLO_UVEITIS
        else:
            protocolo_a_mostrar = "Sin alteraciones graves evidentes. Lágrimas artificiales si hay molestia."

        return f"🩺 **Impresión Diagnóstica:**\n{texto_diagnosticos}\n\n💊 **Orientación Terapéutica:**\n{protocolo_a_mostrar}{DISCLAIMER}"
    
    # 5. DIAGNÓSTICO DIFERENCIAL POR SÍNTOMAS (SIN IMAGEN - MEDICAL FIREWALL)
    else:
        puntaje_ulcera = sum(1 for s in SINTOMAS_CLAVE_ULCERA if s in texto)
        puntaje_uveitis = sum(1 for s in SINTOMAS_CLAVE_UVEITIS if s in texto)
        es_ambiguo = any(s in texto for s in SINTOMAS_AMBIGUOS)
        
        # Caso A: Síntoma específico de Úlcera
        if puntaje_ulcera > 0 and puntaje_uveitis == 0:
            return f"📝 **Orientación por Síntomas (Sin Imagen):**\nCon base en lo descrito, alta sospecha de **Úlcera Corneal / Queratitis Infecciosa**.\n\n💊 **Orientación Terapéutica:**\n{PROTOCOLO_ULCERA}\n\n*Nota: Confirme con fotografía en el panel lateral.*{DISCLAIMER}"
            
        # Caso B: Síntoma específico de Uveítis
        elif puntaje_uveitis > 0 and puntaje_ulcera == 0:
            return f"📝 **Orientación por Síntomas (Sin Imagen):**\nCon base en lo descrito, alta sospecha de **Uveítis Anterior**.\n\n💊 **Orientación Terapéutica:**\n{PROTOCOLO_UVEITIS}\n\n*Nota: Confirme con fotografía en el panel lateral.*{DISCLAIMER}"
            
        # Caso C: SÍNTOMA AMBIGUO (El sistema NO receta, actúa como Firewall de seguridad)
        elif es_ambiguo:
            return ("⚠️ **Diagnóstico Diferencial (Requiere más datos):**\n"
                    "El síntoma descrito (*ojo rojo, dolor o ardor*) es común en **ambas patologías**. "
                    "Recetar a ciegas puede ser peligroso (ej. dar esteroides si es úlcera). Para diferenciar de forma segura:\n\n"
                    "🔹 Si asocia **secreción ocular, lagrimeo o sensación de cuerpo extraño**, sospechamos **Úlcera Corneal**.\n"
                    "🔹 Si asocia **fotofobia severa o visión borrosa**, sospechamos **Uveítis Anterior**.\n\n"
                    "*Por favor, especifique si presenta alguno de estos síntomas clave, o suba una fotografía para análisis matemático.*")
                    
        # Caso D: Mixto o sin datos suficientes
        else:
            return "Entendido, Doctor. Para emitir un diagnóstico preciso, describa síntomas específicos (fotofobia, secreción) o suba fotografías al panel lateral para el análisis con IA."
