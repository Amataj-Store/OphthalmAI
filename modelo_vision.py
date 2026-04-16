"""
modelo_vision.py – Hospital Rísquez · OphthalmAI v3.4
Motor Conversacional Inteligente + Preguntas Finales + Protocolos Directos
"""

import random
import numpy as np
from PIL import Image
import io
import os

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(DIRECTORIO_ACTUAL, "modelo_oftalmologia.h5")

try:
    import tensorflow as tf
    if os.path.exists(MODELO_PATH):
        cnn_model = tf.keras.models.load_model(MODELO_PATH)
        clases_nombres =['sano', 'ulcera', 'uveitis']
    else:
        cnn_model = None
except Exception:
    cnn_model = None

def procesar_imagen_real(imagen_bytes):
    if cnn_model is None: return None, 0.0
    try:
        img = Image.open(io.BytesIO(imagen_bytes)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        predicciones = cnn_model.predict(img_array, verbose=0)[0]
        indice_clase = np.argmax(predicciones)
        return clases_nombres[indice_clase], predicciones[indice_clase] * 100
    except:
        return None, 0.0

PROTOCOLO_UVEITIS = """**🔵 PROTOCOLO: UVEÍTIS ANTERIOR**
- **Esteroides Tópicos:** Acetato de Prednisolona 1% (estándar de oro). Dosis según grado celular (Tyndall). Reducción paulatina.
- **Ciclopléjicos/Midriáticos:** Ciclopentolato 1% o Atropina 1% para prevenir sinequias posteriores y dolor.
- **Control de PIO:** Evaluar presión intraocular por riesgo de hipertensión secundaria a esteroides."""

PROTOCOLO_ULCERA = """**⚠️ PROTOCOLO: ÚLCERA CORNEAL / QUERATITIS INFECCIOSA**
- 🔴 **Toma de Muestra:** Cultivo y frotis (Gram/Giemsa) *ANTES* de la primera gota de antibiótico.
- **Tratamiento Empírico (Bacteriana):** Fluoroquinolonas 4ta generación (Moxifloxacino) c/15-30 min.
- **Tratamiento Reforzado:** Vancomicina + Ceftazidima alternados cada hora.
- 🚫 **Contraindicación Absoluta:** No usar esteroides en fase activa infecciosa."""

PREGUNTA_FINAL = "\n\n*Evaluación registrada. Doctor, ¿qué desea hacer ahora? ¿Analizar otro síntoma, registrar la evolución arriba o consultar otro historial en el menú lateral?*"

def analizar_imagen_y_sintomas(lista_imagenes: list, texto_doctor: str) -> str:
    texto = texto_doctor.lower().strip()
    
    # 1. PEDIR TRATAMIENTOS DIRECTAMENTE (SIN FOTO)
    if "tratamiento" in texto or "protocolo" in texto or "medicamento" in texto or "que le receto" in texto:
        if "uveitis" in texto or "uveítis" in texto:
            return f"Claro, Doctor. Aquí tiene el manejo indicado:\n\n{PROTOCOLO_UVEITIS}{PREGUNTA_FINAL}"
        elif "ulcera" in texto or "úlcera" in texto or "queratitis" in texto:
            return f"Claro, Doctor. Aquí tiene el manejo de urgencia:\n\n{PROTOCOLO_ULCERA}{PREGUNTA_FINAL}"
        else:
            return "Por favor especifique de qué patología desea el protocolo: ¿Úlcera Corneal o Uveítis Anterior?"

    # 2. CONVERSACIÓN FLUIDA (Saludos, Gracias, etc.)
    if any(s in texto for s in["gracias", "listo", "excelente", "perfecto", "ok", "mas nada"]):
        return "¿Desea registrar algo más en la evolución de este paciente, consultar un historial en el menú lateral, o finalizamos la consulta?"

    if any(s in texto for s in["hola", "buenos", "buenas", "saludos"]):
        return "¡Saludos, Doctor! Especialidad: **Úlceras y Uveítis**. Puede pedirme un tratamiento directo, subir una foto, o describir los síntomas. ¿Qué desea hacer?"

    # 3. EVALUACIÓN DE IMÁGENES
    if lista_imagenes:
        clase_detectada, prob = procesar_imagen_real(lista_imagenes[0])
        
        if clase_detectada is not None:
            if clase_detectada == 'ulcera':
                diag, trat = f"Úlcera Corneal (CNN: {prob:.1f}%)", PROTOCOLO_ULCERA
            elif clase_detectada == 'uveitis':
                diag, trat = f"Uveítis Anterior (CNN: {prob:.1f}%)", PROTOCOLO_UVEITIS
            else:
                diag, trat = f"Segmento Sano (CNN: {prob:.1f}%)", "Sin alteraciones graves evidentes. Lágrimas artificiales si hay molestia."
        else:
            if "ulcera" in texto or "secrecion" in texto or "rojo" in texto:
                diag, trat = "Úlcera Corneal (Simulado)", PROTOCOLO_ULCERA
            elif "uveitis" in texto or "dolor" in texto or "fotofobia" in texto:
                diag, trat = "Uveítis Anterior (Simulado)", PROTOCOLO_UVEITIS
            else:
                diag, trat = "Hallazgos no detectados (Simulado)", "Requiere evaluación con lámpara de hendidura."
                
        return f"🩺 **Impresión Diagnóstica:** {diag}\n\n💊 **Orientación Terapéutica:**\n{trat}{PREGUNTA_FINAL}"
    
    else:
        return "Para emitir una probabilidad diagnóstica de la Tesis, por favor suba las fotografías en el panel lateral, o si solo requiere revisar el texto, solicite el protocolo específico."
