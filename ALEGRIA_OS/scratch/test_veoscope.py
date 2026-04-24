
import asyncio
import os
import sys
import json
import logging

# Configurar path para importar desde src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Mock de logging para evitar ruido excesivo
logging.basicConfig(level=logging.INFO)

async def test_vision_pipeline():
    print("[TEST] Iniciando prueba de pipeline VeoScope...")
    
    # Simular una imagen base64 (una imagen pequeña de 1x1 pixel negro para el test)
    dummy_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    from src.services.anima import get_anima
    anima = get_anima()
    
    print("\n--- PASO 1: Generacion de Pipeline (Anima) ---")
    message = "[Análisis VEO Requerido] Analiza esta imagen y sugereme branding."
    file_metadata = {
        "name": "test_image.png",
        "type": "image/png",
        "data": dummy_b64
    }
    
    try:
        # Cargamos las variables de entorno para que el adapter tenga la API KEY
        from dotenv import load_dotenv
        load_dotenv("backend/.env")
        
        raw_result = await anima.generate_raw(message, file_metadata)
        print(f"RAW Result Modality: {raw_result.get('modality')}")
        
        # 2. Simular el filtrado del RuleEngine
        from src.core.rule_engine import service as rule_engine
        filtered = await rule_engine.filter_output(raw_result, mode="conversation")
        
        print("\n--- PASO 2: Resultado del Kernel (RuleEngine) ---")
        print(f"Status: {filtered.get('status')}")
        print(f"Type: {filtered.get('type')}")
        
        if filtered.get("type") == "pipeline":
             print("Pipeline correctamente detectado por el Kernel.")
             pipeline = filtered["pipeline"]
             print(json.dumps(pipeline, indent=2))
             
             # 3. Simular Ejecucion del Pipeline
             print("\n--- PASO 3: Ejecucion del Pipeline (Vision Executor) ---")
             from src.os.pipeline.vision_executor import run_vision_pipeline
             exec_result = await run_vision_pipeline(pipeline, file_metadata)
             
             print("Ejecucion completada.")
             print(json.dumps(exec_result, indent=2))
        else:
             print("El Kernel no detecto un pipeline. Respuesta cruda:")
             print(raw_result.get('raw'))

    except Exception as e:
        print(f"Error durante la prueba: {e}")

if __name__ == "__main__":
    asyncio.run(test_vision_pipeline())
