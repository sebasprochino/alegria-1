# ALEGR-IA OS — src/os/pipeline/vision_executor.py

import logging
from src.os.perception.vision.extractor import extract_features
from src.os.perception.vision.context import infer_context
from src.os.perception.vision.prompt import generate_prompt
from src.os.perception.vision.brand import suggest_brand

logger = logging.getLogger("ALEGRIA_VISION_EXECUTOR")

async def run_vision_pipeline(pipeline_req: dict, file_metadata: dict = None):
    """
    Ejecuta un pipeline estructurado de visión (VeoScope).
    Formato esperado:
    {
      "type": "pipeline",
      "mode": "veoscope",
      "input": {"path": "..." },
      "steps": [{"action": "vision.extract_features"}, ...]
    }
    """
    # Si hay metadata con data (base64), priorizamos eso sobre el path del pipeline
    image_source = pipeline_req.get("input", {}).get("path", "image.jpg")
    
    if file_metadata and file_metadata.get("data"):
        image_source = file_metadata["data"]
    elif not image_source or image_source == "<image_path>":
        raise ValueError("No se proporcionó origen de imagen (path o base64).")

    state = {}
    trace = []

    logger.info(f"⚙️ [VISION_EXECUTOR] Ejecutando pipeline. Source type: {'base64' if image_source.startswith('data:') else 'path'}")

    for step in pipeline_req.get("steps", []):
        action = step.get("action")
        logger.info(f"🔹 Ejecutando paso: {action}")
        
        try:
            if action == "vision.extract_features":
                state["features"] = extract_features(image_source)
                trace.append({"step": action, "status": "ok"})

            elif action == "vision.infer_context":
                if "features" not in state:
                    state["features"] = extract_features(image_source)
                state["context"] = infer_context(state["features"])
                trace.append({"step": action, "status": "ok"})

            elif action == "vision.generate_prompt":
                if "features" not in state:
                    state["features"] = extract_features(image_source)
                if "context" not in state:
                    state["context"] = infer_context(state["features"])
                state["prompt"] = generate_prompt(state["features"], state["context"])
                trace.append({"step": action, "status": "ok"})

            elif action == "vision.brand_suggestion":
                if "features" not in state:
                    state["features"] = extract_features(image_source)
                if "context" not in state:
                    state["context"] = infer_context(state["features"])
                state["brand"] = suggest_brand(state["features"], state["context"])
                trace.append({"step": action, "status": "ok"})
            
            else:
                logger.warning(f"⚠️ Acción desconocida: {action}")
                trace.append({"step": action, "status": "unknown"})

        except Exception as e:
            logger.error(f"❌ Error en paso {action}: {e}")
            trace.append({"step": action, "status": "error", "message": str(e)})

    return {
        "status": "success",
        "output": state,
        "trace": trace,
        "type": "vision_result"
    }
