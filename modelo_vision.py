"""
modelo_vision.py – Hospital Rísquez · OphthalmAI v3.8
Motor Conversacional Inteligente + Umbrales Clínicos + NLP Anti-Bucle
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

SINTOMAS_UVEITIS = ["fotofobia", "dolor ocular", "ojo rojo", "vision borrosa", "miosis", "tyndall"]
SINTOMAS_ULCERA = ["secrecion", "lagrimeo", "dolor corneal", "mancha blanca", "hipopion", "queratitis"]

def analizar_imagen_y_sintomas(lista_imagenes: list, texto_doctor: str) -> str:
    texto = texto_doctor.lower().strip()
    
    # 1. PEDIR TRATAMIENTOS DIRECTAMENTE (SIN FOTO)
    if any(p in texto for p in ["tratamiento", "protocolo", "medicamento", "recet", "manejo"]):
        if "uveitis" in texto or "uveítis" in texto:
            return f"Claro, Doctor. Aquí tiene el manejo indicado:\n\n{PROTOCOLO_UVEITIS}{DISCLAIMER}"
        elif "ulcera" in texto or "úlcera" in texto or "queratitis" in texto:
            return f"Claro, Doctor. Aquí tiene el manejo de urgencia:\n\n{PROTOCOLO_ULCERA}{DISCLAIMER}"
        else:
            return "Por favor especifique de qué patología desea el protocolo: ¿Úlcera Corneal o Uveítis Anterior?"

    # 2. INTENCIÓN DE NAVEGACIÓN (Historial / Registro)
    if any(s in texto for s in ["historial", "ver historial", "expediente", "buscar paciente"]):
        return "¡Por supuesto! Para consultar expedientes previos, diríjase al menú lateral izquierdo y seleccione **📂 Historial**."
    if any(s in texto for s in ["registrar", "nuevo paciente", "registro", "crear paciente"]):
        return "Para ingresar un nuevo paciente al sistema, por favor diríjase a **📋 Registro** en el menú lateral."

    # 3. CONVERSACIÓN FLUIDA Y CIERRE (Anti-bucle)
    # Si el doctor quiere terminar, le indicamos el botón y cerramos el chat.
    if any(s in texto for s in ["terminar", "finalizar", "cerrar", "adios", "chao", "hasta luego", "me voy"]):
        return "¡Hasta luego, Doctor! Para guardar la sesión y liberar la memoria, presione **⏹ FINALIZAR CONSULTA** en el menú lateral."
    
    # Si agradece o da por terminado el tema
    if any(s in texto for s in ["gracias", "listo", "excelente", "perfecto", "ok", "mas nada", "ya", "entendido"]):
        return "¡A la orden! Si necesita algo más, puedo analizar otras fotos o buscar protocolos. Si terminamos, recuerde presionar **⏹ FINALIZAR CONSULTA**."
    
    if any(s in texto for s in ["hola", "buenos", "buenas", "saludos"]):
        return "¡Saludos, Doctor! Especialidad activa: **Úlceras y Uveítis**. ¿En qué le puedo ayudar hoy?"

    # 4. EVALUACIÓN DE IMÁGENES (Solo llega aquí si no fue conversación, navegación ni protocolo)
    if lista_imagenes:
        diagnosticos = []
        
        for i, img_bytes in enumerate(lista_imagenes):
            clase_detectada, prob = procesar_imagen_real(img_bytes)
            
            if clase_detectada is None:
                if any(s in texto for s in SINTOMAS_ULCERA):
                    diagnosticos.append(f"Img {i+1}: Úlcera Corneal (Simulado)")
                elif any(s in texto for s in SINTOMAS_UVEITIS):
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
    
    # 5. NO HAY IMÁGENES, pero el doctor describió síntomas
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
                
            return f"📝 **Orientación por Síntomas (Sin Imagen):**\nCon base en lo descrito, sospecha de **{sospecha}**.\n\n💊 **Orientación Terapéutica:**\n{protocolo}\n\n*Nota: Para probabilidad matemática, suba fotografías en el panel lateral.*{DISCLAIMER}"
        
        # 6. FALLBACK FINAL (Si no hay imágenes, ni síntomas, ni nada reconocible)
        return "Entendido, Doctor. Puede pedirme un protocolo médico directamente, describir síntomas del paciente, o subir fotografías al panel lateral para el análisis con IA. ¿Qué desea hacer?"
