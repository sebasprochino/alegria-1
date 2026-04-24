def evaluate_coherence(components, state):
    """
    Valida que los componentes seleccionados para fusión puedan convivir armónicamente.
    """
    issues = []
    goal = state.get("goal", "").lower()

    script_art = components.get("generate_script", {})
    audio_art = components.get("generate_audio", {})
    
    script_val = script_art.get("value", "").lower() if isinstance(script_art, dict) else ""
    audio_val = audio_art.get("value", {}) if isinstance(audio_art, dict) else {}
    
    # 1. Validación de Mood (Ejemplo simple)
    # Si el guion es triste/melancólico y el audio es rápido/alegre, hay inconsistencia.
    sad_keywords = ["triste", "melancolía", "solo", "perdido", "blue", "melancholy"]
    is_sad_script = any(kw in script_val for kw in sad_keywords)
    
    # Supongamos que el audio artifact tiene metadata de tempo/mood
    audio_tempo = audio_val.get("tempo", "medium") 
    
    if is_sad_script and audio_tempo == "fast":
        issues.append("mood_rhythm_mismatch")

    # 2. Validación de Intención
    # Si el objetivo pide algo cinematográfico y las imágenes son tipo 'cartoon'.
    if "cinematic" in goal and "cartoon" in str(components.get("generate_images", "")):
        issues.append("aesthetic_intent_mismatch")

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }
