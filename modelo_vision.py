"""
modelo_vision.py – Hospital Rísquez · OphthalmAI v3.3
Motor Conversacional + Diagnóstico (Restringido a Úlcera y Uveítis)
Arquitectura: EfficientNetB0 (Local/Cloud)
"""

import random
import numpy as np
from PIL import Image
import io
import os

# ==============================================================================
# CARGA DEL MODELO MATEMÁTICO REAL (TENSORFLOW)
# ==============================================================================
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
    """Abre los ojos de la IA de verdad."""
    if cnn_model is None:
        return None, 0.0
    try:
        img = Image.open(io.BytesIO(imagen_bytes)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        predicciones = cnn_model.predict(img_array, verbose=0)[0]
        indice_clase = np.argmax(predicciones)
        probabilidad = predicciones[indice_clase] * 100
        
        return clases_nombres[indice_clase], probabilidad
    except Exception:
        return None, 0.0

# ==============================================================================
# PROTOCOLOS MÉDICOS 
# ==============================================================================
PROTOCOLO_UVEITIS = """**🔵 UVEÍTIS ANTERIOR — Protocolo AAO/Hospital Rísquez**
- **Esteroides Tópicos:** Acetato de Prednisolona 1% (estándar de oro). Dosis según Tyndall, con reducción lenta.
- **Ciclopléjicos:** Ciclopentolato 1% o Atropina 1%. Previene sinequias.
- **Control PIO:** Riesgo de hipertensión ocular por esteroides.
⚠️ *Nota: Buscar etiología sistémica si es recurrente.*"""

PROTOCOLO_ULCERA = """**⚠️ QUERATITIS INFECCIOSA / ÚLCERA — URGENCIA OFTALMOLÓGICA**
- 🔴 **Crítico:** Tomar muestra para cultivo (Gram/Giemsa) *ANTES* de iniciar antibióticos.
- **Bacteriana Empírica:** Fluoroquinolonas 4ta gen. (Moxifloxacino) cada 15-30 min.
- **Herpética:** Ganciclovir en gel. *NUNCA usar esteroides en úlcera dendrítica*.
🚫 *Esteroides tópicos contraindicados en fase activa infecciosa.*"""

PROTOCOLO_SANO = """**✅ SEGMENTO ANTERIOR SANO / NORMAL**
- No se observan signos de Úlcera Corneal ni Uveítis Anterior.
- **Manejo:** Examen de rutina. Considerar lágrimas artificiales sin conservantes si el paciente refiere fatiga visual."""


def analizar_imagen_y_sintomas(lista_imagenes: list, texto_doctor: str) -> str:
    texto = texto_doctor.lower().strip()
    
    # 1. CONVERSACIÓN NATURAL
    if any(s in texto for s in["hola", "buenos", "buenas", "saludos"]):
        return "¡Saludos, Doctor! El sistema está restringido y especializado exclusivamente en **Úlceras Corneales** y **Uveítis**. ¿Subimos una foto?"
        
    if any(s in texto for s in["gracias", "mas nada", "listo", "excelente", "perfecto", "ok"]):
        return "¡A su orden, Doctor! Todo guardado. Estoy listo para la siguiente evaluación."

    # 2. EVALUACIÓN (ESTRICTA)
    if lista_imagenes:
        clase_detectada, prob = procesar_imagen_real(lista_imagenes[0])
        
        # Si la red neuronal de verdad (.h5) funcionó:
        if clase_detectada is not None:
            if clase_detectada == 'ulcera':
                diag = f"Úlcera Corneal / Queratitis (Precisión CNN: {prob:.1f}%)"
                trat = PROTOCOLO_ULCERA
            elif clase_detectada == 'uveitis':
                diag = f"Uveítis Anterior (Precisión CNN: {prob:.1f}%)"
                trat = PROTOCOLO_UVEITIS
            elif clase_detectada == 'sano':
                diag = f"Segmento Anterior Sano (Precisión CNN: {prob:.1f}%)"
                trat = PROTOCOLO_SANO
                
            estado = "✅ **Procesado con Modelo Real (EfficientNetB0)**"
            
        # Si tu laptop no tiene AVX (Modo Simulado por hardware):
        else:
            estado = "⚠️ **Modo Simulado** *(El modelo .h5 se activará en la nube)*"
            if "ulcera" in texto or "secrecion" in texto or "rojo" in texto:
                diag = "Úlcera Corneal (Simulado)"
                trat = PROTOCOLO_ULCERA
            elif "uveitis" in texto or "dolor" in texto or "fotofobia" in texto:
                diag = "Uveítis Anterior (Simulado)"
                trat = PROTOCOLO_UVEITIS
            else:
                diag = "Segmento Sano / Patología no detectada (Simulado)"
                trat = PROTOCOLO_SANO
                
        return f"🩺 **Análisis Completado:**\n{estado}\n\n**Impresión Diagnóstica:** {diag}\n\n💊 **Protocolo Terapéutico:**\n{trat}"
    
    else:
        return "Para emitir un criterio diagnóstico sobre Úlcera o Uveítis, necesito que por favor **suba las fotografías** en el panel lateral."
