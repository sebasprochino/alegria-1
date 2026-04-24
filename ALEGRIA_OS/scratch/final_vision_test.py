
import asyncio
import os
import sys
import json
import logging
import base64
import numpy as np
import cv2

# Configurar path para importar desde src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Mock de logging para evitar ruido excesivo
logging.basicConfig(level=logging.INFO)

def create_valid_test_image():
    # Crear una imagen azul de 100x100
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:] = [255, 0, 0] # BGR Azul
    
    # Guardar en disco para que tool_analyze_visual la lea
    path = "scratch/test_vision_real.png"
    os.makedirs("scratch", exist_ok=True)
    cv2.imwrite(path, img)
    return path

async def test_real_vision_cascade():
    print("[TEST] Iniciando prueba real de cascada de vision 2026...")
    
    # 0. Cargar .env
    from dotenv import load_dotenv
    load_dotenv("backend/.env")
    
    # 1. Crear imagen real
    path = create_valid_test_image()
    print(f"Imagen creada en: {path}")
    
    # 2. Importar el registro de herramientas
    from src.os.actions.registry import tool_analyze_visual
    
    # 3. Ejecutar herramienta con el nuevo modelo configurado
    query = f"Local Path: {path}"
    print(f"Ejecutando tool_analyze_visual con query: {query}")
    
    try:
        # Esto intentará Gemini 2.5 -> Llama 4 Scout -> OpenAI
        result = await tool_analyze_visual(query)
        
        print("\n--- RESULTADO DE LA VISION ---")
        print(result)
        
        if "data:image" not in result and "Error" not in result:
             print("\nOK: La cascada funciono y un LLM respondio.")
        else:
             print("\nAVISO: Probablemente devolvio el fallback de OpenCV o un error.")
             
    except Exception as e:
        print(f"Error fatal: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_vision_cascade())
