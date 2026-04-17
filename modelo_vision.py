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

# Umbral clínico: Si la CNN no está al menos 50% segura, no arriesga diagnóstico
UMBRAL_CONFIANZA = 50.0 

# ════════════════════════════════════════════════════════
# DIAGNÓSTICO DE CARGA DEL MODELO Y MANEJO DE ERRORES
# ════════════════════════════════════════════════════════
cnn_model = None
clases_nombres = []
ERROR_CARGA = None  # Aquí guardaremos el error si el modelo no carga

# 1. Verificar si el archivo .h5 existe en la carpeta
if not os.path.exists(MODELO_PATH):
    ERROR_CARGA = f"⚠️ ERROR DE SISTEMA: No se encuentra el archivo del modelo en la ruta: `{MODELO_PATH}`. El sistema funciona en Modo Simulado."
else:
    # 2. Si existe, intentar importar TensorFlow y cargarlo
    try:
        import tensorflow as tf
        cnn_model = tf.keras.models.load_model(MODELO_PATH)
        clases_nombres = ['sano', 'ulcera', 'uveitis']
    except Exception as e:
        ERROR_CARGA = f"⚠️ ERROR CARGANDO TENSORFLOW/MODELO: `{e}`. El sistema funciona en Modo Simulado."
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

    # 2. CONVERSACIÓN FLUIDA (Saludos, Gracias, etc.)
    if any(s in texto for s in ["gracias", "listo", "excelente", "perfecto", "ok", "mas nada"]):
        return "¿Desea registrar algo más en la evolución de este paciente, consultar un historial en el menú lateral, o finalizamos la consulta?"

    if any(s in texto for s in ["hola", "buenos", "buenas", "saludos"]):
        return "¡Saludos, Doctor! Especialidad: **Úlceras y Uveítis**. Puede pedirme un tratamiento directo, subir una foto, o describir los síntomas. ¿Qué desea hacer?"

    # 3. EVALUACIÓN DE IMÁGENES (Si hay fotos en el panel)
    if lista_imagenes:
        diagnosticos = []
        
        # Analizamos todas las imágenes subidas
        for i, img_bytes in enumerate(lista_imagenes):
            clase_detectada, prob = procesar_imagen_real(img_bytes)
            
            # Si TensorFlow no cargó o falló la predicción, usamos reglas según el texto (Simulado)
            if clase_detectada is None:
                if any(s in texto for s in SINTOMAS_ULCERA):
                    diagnosticos.append(f"Img {i+1}: Úlcera Corneal (Simulado)")
                elif any(s in texto for s in SINTOMAS_UVEITIS):
                    diagnosticos.append(f"Img {i+1}: Uveítis Anterior (Simulado)")
                else:
                    diagnosticos.append(f"Img {i+1}: Hallazgo indeterminado (Simulado)")
                    
            # Si TensorFlow sí cargó, evaluamos con UMBRAL DE CONFIANZA
            elif prob < UMBRAL_CONFIANZA:
                diagnosticos.append(f"Img {i+1}: ⚠️ Imagen dudosa (CNN: {prob:.1f}% - {clase_detectada})")
                
            # Si la CNN está segura
            else:
                if clase_detectada == 'ulcera':
                    diagnosticos.append(f"Img {i+1}: ⚠️ Úlcera Corneal (CNN: {prob:.1f}%)")
                elif clase_detectada == 'uveitis':
                    diagnosticos.append(f"Img {i+1}: 🔵 Uveítis Anterior (CNN: {prob:.1f}%)")
                else:
                    diagnosticos.append(f"Img {i+1}: ✅ Segmento Sano (CNN: {prob:.1f}%)")

        # Decidimos qué protocolo mostrar basado en el peor diagnóstico
        texto_diagnosticos = "\n".join(diagnosticos)
        protocolo_a_mostrar = ""
        
        # Si cualquier imagen dice úlcera, mostramos protocolo de úlcera (prioridad urgente)
        if any("úlcer" in d.lower() for d in diagnosticos):
            protocolo_a_mostrar = PROTOCOLO_ULCERA
        elif any("uveít" in d.lower() for d in diagnosticos):
            protocolo_a_mostrar = PROTOCOLO_UVEITIS
        else:
            protocolo_a_mostrar = "Sin alteraciones graves evidentes. Lágrimas artificiales si hay molestia."

        return f"🩺 **Impresión Diagnóstica:**\n{texto_diagnosticos}\n\n💊 **Orientación Terapéutica:**\n{protocolo_a_mostrar}{DISCLAIMER}{PREGUNTA_FINAL}"
    
    # 4. NO HAY IMÁGENES, pero el doctor describió síntomas
    else:
        puntaje_ulcera = sum(1 for s in SINTOMAS_ULCERA if s in texto)
        puntaje_uveitis = sum(1 for s in SINTOMAS_UVEITIS if s in texto)
        
        if puntaje_ulcera > 0 or puntaje_uveitis > 0:
            if puntaje_ulcera >= puntaje_uveitis:
                sospecha = "Úlcera Corneal / Queratitis"
                protocolo = PROTOCOLO_ULCERA
            else:
                sospecha = "Uveítis Anterior"
                protocolo = PROTOCOLO_UVEITIS
                
            return f"📝 **Orientación por Síntomas (Sin Imagen):**\nCon base en lo descrito, sospecha de **{sospecha}**.\n\n💊 **Orientación Terapéutica:**\n{protocolo}\n\n*Nota: Para probabilidad matemática, suba fotografías en el panel lateral.*{DISCLAIMER}{PREGUNTA_FINAL}"
        
        # Si no hay imágenes y no hay síntomas claros
        else:
            return "Para emitir una probabilidad diagnóstica de la Tesis, por favor suba las fotografías en el panel lateral, describa los síntomas del paciente, o solicite un protocolo específico."
