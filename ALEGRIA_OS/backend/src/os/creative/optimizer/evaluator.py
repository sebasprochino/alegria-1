from .creative_criteria import evaluate_style

def map_issue_to_step(issue):
    """Mapea un problema detectado al paso del pipeline que debe corregirlo."""
    mapping = {
        "missing_audio": "generate_audio",
        "missing_images": "generate_images",
        "missing_script": "generate_script",
        "weak_narrative_length": "generate_script",
        "low_thematic_coherence": "generate_script"
    }
    return mapping.get(issue)

def evaluate(outputs, goal, state):
    """
    Evalúa los outputs actuales frente al objetivo e intención creativa.
    """
    issues = []

    # Verificación Técnica (Presencia)
    if not outputs.get("generate_audio"):
        issues.append("missing_audio")

    if not outputs.get("generate_images"):
        issues.append("missing_images")
        
    if not outputs.get("generate_script"):
        issues.append("missing_script")

    # Verificación Creativa (Estilo)
    style_issues = evaluate_style(outputs, state)
    issues.extend(style_issues)

    return {
        "issues": issues,
        "needs_improvement": len(issues) > 0
    }

