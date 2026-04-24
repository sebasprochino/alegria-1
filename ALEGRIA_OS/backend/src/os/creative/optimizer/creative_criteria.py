def evaluate_style(outputs, state):
    """
    Evalúa el estilo, coherencia y narrativa del contenido generado.
    """
    goal = state.get("goal", "").lower()
    style_flags = []

    # 1. Validación de concordancia de estilo musical
    if "blues" in goal:
        # Aquí se podría integrar un análisis real del archivo de audio en el futuro
        style_flags.append("musical_style_match_blues")
    
    # 2. Evaluación narrativa (Guion)
    script_art = outputs.get("generate_script")
    if script_art and script_art.get("type") == "text":
        text = script_art.get("value", "")
        if len(text) < 50:
            style_flags.append("weak_narrative_length")
        
        # Búsqueda de palabras clave del objetivo en el guion
        keywords = goal.split()
        matches = [kw for kw in keywords if kw in text.lower()]
        if len(matches) < len(keywords) / 2:
            style_flags.append("low_thematic_coherence")

    return style_flags
