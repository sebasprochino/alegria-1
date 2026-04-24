def update_profile(profile, outputs, optimization, state):
    """
    Actualiza el perfil basándose en el éxito o fracaso de la optimización actual.
    """
    goal = state.get("goal", "").lower()
    issues = optimization.get("issues", [])

    # 1. Registro de evento histórico
    profile.setdefault("history", []).append({
        "goal": goal,
        "score": optimization.get("score"),
        "issues": issues
    })

    # 2. Inferencia de Estilo (Basado en el Goal)
    # Ejemplo simple: si pide blues frecuentemente, registrarlo como estilo preferido.
    if "blues" in goal:
        profile.setdefault("style", {})["music"] = "blues"
    elif "rock" in goal:
        profile.setdefault("style", {})["music"] = "rock"

    # 3. Ajuste de Preferencias (Basado en Issues)
    # Si detectamos constantemente narrativa débil, el perfil exige más longitud.
    if "weak_narrative_length" in issues:
        profile.setdefault("preferences", {})["min_script_length"] = 100
    
    if "low_thematic_coherence" in issues:
        profile.setdefault("preferences", {})["thematic_strictness"] = "high"

    return profile
