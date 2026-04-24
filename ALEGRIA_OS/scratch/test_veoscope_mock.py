
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
    _, buffer = cv2.imencode('.png', img)
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"

async def test_vision_pipeline_mocked():
    print("[TEST] Iniciando prueba de pipeline VeoScope (MOCK LLM)...")
    
    mock_llm_json = {
        "type": "pipeline",
        "mode": "veoscope",
        "input": { "source": "image", "path": "test_image.png" },
        "steps": [
            { "action": "vision.extract_features" },
            { "action": "vision.infer_context" },
            { "action": "vision.generate_prompt" },
            { "action": "vision.brand_suggestion" }
        ]
    }
    
    raw_result = {
        "raw": json.dumps(mock_llm_json),
        "modality": "vision",
        "source": "llm"
    }
    
    dummy_b64 = create_valid_test_image()
    
    file_metadata = {
        "name": "test_image.png",
        "type": "image/png",
        "data": dummy_b64
    }

    try:
        from src.core.rule_engine import service as rule_engine
        filtered = await rule_engine.filter_output(raw_result, mode="conversation")
        
        print("\n--- PASO 1: Procesamiento del Kernel (RuleEngine) ---")
        print(f"Status: {filtered.get('status')}")
        
        if filtered.get("type") == "pipeline":
             print("OK: Kernel detecto el pipeline estructurado correctamente.")
             pipeline = filtered["pipeline"]
             
             print("\n--- PASO 2: Ejecucion del Pipeline (Vision Executor) ---")
             from src.os.pipeline.vision_executor import run_vision_pipeline
             exec_result = await run_vision_pipeline(pipeline, file_metadata)
             
             print("\nOK: EJECUCION COMPLETADA CON EXITO")
             
             print("\n[RESULTADOS DEL ANALISIS VEO]:")
             output = exec_result["output"]
             if "features" in output:
                print(f"- Resolucion: {output['features'].get('resolution')}")
                print(f"- Brillo: {output['features'].get('brightness', 0):.2f}")
                print(f"- Dominantes: {', '.join(output['features'].get('dominant_colors', []))}")
             
             if "context" in output:
                print(f"- Iluminacion: {output['context']['lighting']}")
                print(f"- Estilo Inferido: {output['context']['style']}")
             
             if "prompt" in output:
                print(f"- Prompt Generado: {output['prompt'][:120]}...")
             
             if "brand" in output:
                print(f"- Sugerencia de Marca: {output['brand']['vibe']}")
             
             print("\n[TRAZA DE AUDITORIA]:")
             for step in exec_result["trace"]:
                 print(f"  > {step['step']}: {step['status']} {'(Error: '+step.get('message', '')+')' if step['status'] == 'error' else ''}")
        else:
             print("Error: El Kernel no proceso el JSON como pipeline.")

    except Exception as e:
        print(f"Error durante la prueba: {e}")

if __name__ == "__main__":
    asyncio.run(test_vision_pipeline_mocked())
