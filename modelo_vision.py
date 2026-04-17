"""
modelo_vision.py – Hospital Rísquez · OphthalmAI v3.8
Motor Conversacional Inteligente + Umbrales Clínicos + Diagnóstico de Carga
"""

import random
import numpy as np
from PIL import Image
import io
import os

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(DIRECTORIO_ACTUAL, "modelo_oftalmologia.h5")

# Umbral clínico
UMBRAL_CONFIANZA = 50.0 

# ════════════════════════════════════════════════════════
# DIAGNÓSTICO DE CARGA DEL MODELO Y MANEJO DE ERRORES
# ════════════════════════════════════════════════════════
cnn_model = None
clases_nombres = []
ERROR_CARGA = None  

if not os.path.exists(MODELO_PATH):
    ERROR_CARGA = f"⚠️ ERROR DE SISTEMA: No se encuentra el archivo en la ruta: `{MODELO_PATH}`"
else:
    try:
        import tensorflow as tf
        
        # TRUCO 1: Normalizar la ruta por si hay espacios o caracteres en español
        # que a h5py le cuesta leer en Windows/Linux
        ruta_segura = os.path.normpath(MODELO_PATH)
        
        # TRUCO 2: Cargar sin compilar. Evita errores de metadatos de entrenamiento
        # que suelen variar entre Colab y Local/Cloud.
        cnn_model = tf.keras.models.load_model(ruta_segura, compile=False)
        
        clases_nombres = ['sano', 'ulcera', 'uveitis']
        
    except Exception as e:
        # Si aún falla, capturamos el error exacto con la ruta que intentó usar
        ERROR_CARGA = f"⚠️ ERROR CARGANDO TENSORFLOW/MODELO en ruta `{ruta_segura}`: `{e}`"
        cnn_model = None
# ════════════════════════════════════════════════════════


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

PROTOCOLO_UVEITIS = """**🔵 PROTOCOLO: UVEÍTIS ANTERIOR**
- **Esteroides Tópicos:** Acetato de Prednisolona 1% (estándar de oro). Dosis según grado celular (Tyndall). Reducción paulatina.
- **Ciclopléjicos/Midriáticos:** Ciclopentolato 1% o Atropina 1% para prevenir sinequias posteriores y dolor.
- **Control de PIO:** Evaluar presión intraocular por riesgo de hipertensión secundaria a esteroides."""

PROTOCOLO_ULCERA = """**⚠️ PROTOCOLO: ÚLCERA CORNEAL / QUERATITIS INFECCIOSA**
- 🔴 **Toma de Muestra:** Cultivo y frotis (Gram/Giemsa) *ANTES* de la primera gota de antibiótico.
- **Tratamiento Empírico (Bacteriana):** Fluoroquinolonas 4ta generación (Moxifloxacino) c/15-30 min.
- **Tratamiento Reforzado:** Vancomicina + Ceftazidima alternados cada hora.
- 🚫 **Contraindicación Absoluta:** No usar esteroides en fase activa infecciosa."""

DISCLAIMER = "\n\n*⚠️ OphthalmAI es un sistema de apoyo. Confirmar siempre con lámpara de hendidura y criterio clínico.*"
PREGUNTA_FINAL = "\n\n*Doctor, ¿qué desea hacer ahora? ¿Analizar otro síntoma, registrar la evolución o consultar un historial?*"

# Reglas de síntomas para cuando NO hay imagen
SINTOMAS_UVEITIS = ["fotofobia", "dolor ocular", "ojo rojo", "vision borrosa", "miosis", "tyndall"]
SINTOMAS_ULCERA = ["secrecion", "lagrimeo", "dolor corneal", "mancha blanca", "hipopion", "queratitis"]

def analizar_imagen_y_sintomas(lista_imagenes: list, texto_doctor: str) -> str:
    texto = texto_doctor.lower().strip()
    
        # 1. PEDIR TRATAMIENTOS DIRECTAMENTE (SIN FOTO)
    if any(p in texto for p in ["tratamiento", "protocolo", "medicamento", "recet", "manejo"]):
        if "uveitis" in texto or "uveítis" in texto:
            return f"Claro, Doctor. Aquí tiene el manejo indicado:\n\n{PROTOCOLO_UVEITIS}{DISCLAIMER}{PREGUNTA_FINAL}"
        elif "ulcera" in texto or "úlcera" in texto or "queratitis" in texto:
            return f"Claro, Doctor. Aquí tiene el manejo de urgencia:\n\n{PROTOCOLO_ULCERA}{DISCLAIMER}{PREGUNTA_FINAL}"
        else:
            return "Por favor especifique de qué patología desea el protocolo: ¿Úlcera Corneal o Uveítis Anterior?"

    # 2. INTENCIÓN DE NAVEGACIÓN (Historial / Registro)
    if any(s in texto for s in ["historial", "ver historial", "expediente", "buscar paciente"]):
        return "¡Por supuesto! Para consultar expedientes previos, diríjase al menú lateral izquierdo y seleccione **📂 Historial**. ¿Le ayudo con algo más en este chat?"
    if any(s in texto for s in ["registrar", "nuevo paciente", "registro", "crear paciente"]):
        return "Para ingresar un nuevo paciente al sistema, por favor diríjase a **📋 Registro** en el menú lateral. ¿Hay algo más en lo que pueda asistirle aquí?"

    # 3. CONVERSACIÓN FLUIDA (Saludos, Despedidas, Agradecimientos)
    if any(s in texto for s in ["gracias", "listo", "excelente", "perfecto", "ok", "mas nada", "chao", "hasta luego"]):
        return "¡A la orden, Doctor! Estoy aquí para asistirle. ¿Desea evaluar otro síntoma, subir una nueva fotografía, o finalizamos la consulta?"
    
    if any(s in texto for s in ["hola", "buenos", "buenas", "saludos"]):
        return "¡Saludos, Doctor! Especialidad activa: **Úlceras y Uveítis**. ¿En qué le puedo ayudar hoy? Puede pedirme un tratamiento, subir una foto, o describir los síntomas."

    # 4. SI DICE SÍNTOMAS PERO NO HAY FOTOS (Evita el bucle de "suba una foto")
    if not lista_imagenes:
        puntaje_ulcera = sum(1 for s in SINTOMAS_ULCERA if s in texto)
        puntaje_uveitis = sum(1 for s in SINTOMAS_UVEITIS if s in texto)
        
        if puntaje_ulcera > 0 or puntaje_uveitis > 0:
            if puntaje_ulcera >= puntaje_uveitis:
                sospecha = "Úlcera Corneal / Queratitis"
                protocolo = PROTOCOLO_ULCERA
            else:
                sospecha = "Uveítis Anterior"
                protocolo = PROTOCOLO_UVEITIS
                
            return f"📝 **Orientación por Síntomas (Sin Imagen):**\nCon base en lo descrito, sospecha de **{sospecha}**.\n\n💊 **Orientación Terapéutica:**\n{protocolo}\n\n*Nota: Para probabilidad matemática con la IA, suba fotografías en el panel lateral.*{DISCLAIMER}{PREGUNTA_FINAL}"
        
        # Si no hay imágenes y no hay síntomas claros (Fallback más amigable)
        return "Entendido, Doctor. Puede pedirme un protocolo médico directamente, describir síntomas del paciente, o subir fotografías al panel lateral para el análisis con IA. ¿Qué desea hacer?"
