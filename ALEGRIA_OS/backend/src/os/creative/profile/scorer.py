def score_profile_alignment(profile, goal):
    """
    Evalúa qué tan alineado está un objetivo con el perfil aprendido.
    """
    score = 0
    goal_lower = goal.lower()
    
    style = profile.get("style", {})
    if style.get("music") and style.get("music") in goal_lower:
        score += 1
        
    # Podemos añadir más criterios de alineación aquí
    
    return score
