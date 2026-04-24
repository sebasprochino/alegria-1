# ALEGR-IA OS — src/os/perception/vision/context.py

def infer_context(features):
    """
    Inferencia determinista basada en reglas métricas (OpenCV).
    Complementa el análisis cognitivo del LLM.
    """
    context = {}

    # Inferencia de iluminación
    brightness = features.get("brightness") or features.get("exposure_value", 127)
    if brightness < 80:
        context["lighting"] = "low_key"
    elif brightness > 180:
        context["lighting"] = "high_key"
    else:
        context["lighting"] = "normal"

    # Inferencia de estilo basado en contraste y complejidad
    contrast = features.get("contrast_value")
    if contrast is None:
        contrast_label = features.get("contrast", "medium")
        contrast = 75 if contrast_label == "high" else 50
    
    if contrast > 60:
        context["style"] = "dramatic"
    else:
        context["style"] = "soft"
    
    # Inferencia de composición (pasado desde extractor)
    context["composition_focus"] = features.get("composition", "centered")

    return context
