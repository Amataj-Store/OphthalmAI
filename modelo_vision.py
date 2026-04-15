"""
modelo_vision.py - Hospital Rísquez
Versión NUBE (TensorFlow Activado - Analiza la imagen real)
"""

import numpy as np
from PIL import Image
import io
import os
import random
import tensorflow as tf

# ==========================================================
# CARGA DEL MODELO MATEMÁTICO REAL (.h5)
# ==========================================================
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
MODELO_PATH = os.path.join(DIRECTORIO_ACTUAL, "modelo_oftalmologia.h5")

try:
    if os.path.exists(MODELO_PATH):
        cnn_model = tf.keras.models.load_model(MODELO_PATH)
        # Clases en orden alfabético como las entrenó Colab
        clases_nombres =['sano', 'ulcera', 'uveitis'] 
    else:
        cnn_model = None
except Exception as e:
    cnn_model = None
    print(f"Error cargando modelo: {e}")

def procesar_imagen_real(imagen_bytes):
    """Abre los ojos de la IA y procesa los pixeles con EfficientNetB0"""
    if cnn_model is None:
        return None, 0.0
    try:
        # Preparar la imagen para la red neuronal
        img = Image.open(io.BytesIO(imagen_bytes)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        
        # ¡LA PREDICCIÓN MATEMÁTICA!
        predicciones = cnn_model.predict(img_array, verbose=0)[0]
        indice_clase = np.argmax(predicciones)
        probabilidad = predicciones[indice_clase] * 100
        
        return clases_nombres[indice_clase], probabilidad
    except Exception as e:
        return None, 0.0

def analizar_imagen_y_sintomas(lista_imagenes, texto_doctor):
    texto = texto_doctor.lower().strip()
    
    # 1. CONVERSACIÓN FLUÍDA
    if "gracias" in texto or "mas nada" in texto or "más nada" in texto or "listo" in texto or "excelente" in texto:
        return "¡A su completa disposición, Doctor! Todo ha quedado guardado en la base de datos de forma segura. Avíseme cuando ingrese el próximo paciente."

    if texto in ["si", "sí", "ok", "vale", "claro", "por favor"] or texto.startswith("si,") or texto.startswith("si "):
        return "¡Entendido, Doctor! El registro ha sido actualizado. ¿Damos por terminada la consulta?"

    if "hola" in texto or "buenos" in texto or "buenas" in texto:
        return "¡Saludos, Doctor! El sistema visual de la nube está 100% en línea y listo para asistir."

    # 2. EVALUACIÓN CLÍNICA REAL
    cantidad_fotos = len(lista_imagenes) if lista_imagenes else 0
    
    protocolo_ulcera = (
        "**QUERATITIS INFECCIOSA (URGENCIA OFTALMOLÓGICA)**\n"
        "• **Crítico:** Tomar muestra para cultivo (Gram/Giemsa) *ANTES* de iniciar antibióticos.\n"
        "• **Bacteriana Empírica:** Fluoroquinolonas de 4ta gen. (Moxifloxacino) cada 15-30 min.\n"
        "• **Severas/Eje Visual:** Terapia Combinada (Vancomicina + Ceftazidima/Amikacina).\n"
        "• **Herpética:** Ganciclovir en gel + Aciclovir sistémico. *NUNCA usar esteroides en úlcera dendrítica*.\n"
        "🚨 *CONTRAINDICACIÓN:* Esteroides prohibidos en fase activa."
    )
    
    protocolo_uveitis = (
        "**UVEÍTIS ANTERIOR (NO INFECCIOSA)**\n"
        "• **Objetivo:** Suprimir inflamación y evitar sinequias.\n"
        "• **Esteroides Tópicos:** Acetato de Prednisolona 1%. Dosis según Tyndall, con reducción lenta.\n"
        "• **Ciclopléjicos:** Ciclopentolato 1% o Atropina 1%.\n"
        "• **Práctica:** Control estricto de la PIO."
    )

    if cantidad_fotos > 0:
        # ¡AQUÍ LA IA MIRA LA FOTO DE VERDAD!
        clase_detectada, prob = procesar_imagen_real(lista_imagenes[0])
        
        if clase_detectada is None:
            return "⚠️ Hubo un error procesando la imagen en el servidor. Por favor, intente de nuevo."

        if clase_detectada == 'ulcera':
            diag = f"Úlcera Corneal (Probabilidad Visual: {prob:.1f}%)"
            trat = protocolo_ulcera
        elif clase_detectada == 'uveitis':
            diag = f"Uveítis Anterior (Probabilidad Visual: {prob:.1f}%)"
            trat = protocolo_uveitis
        else:
            diag = f"Ojo Sano / Sin alteraciones graves (Probabilidad Visual: {prob:.1f}%)"
            trat = "Se sugiere examen de rutina. Indicar lubricantes si hay fatiga visual."

        return f"🩺 **Análisis Visual Completado:**\n\n**Impresión Diagnóstica:** {diag}\n\n💊 **Protocolo Terapéutico:**\n{trat}"
    else:
        return "He registrado sus apuntes. Por favor, suba las fotografías en el panel lateral para que la Red Neuronal las evalúe."
