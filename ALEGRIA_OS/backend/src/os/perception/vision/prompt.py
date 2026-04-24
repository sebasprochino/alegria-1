# ALEGR-IA OS — src/os/perception/vision/prompt.py

def generate_prompt(features, context):
    """
    Construye un prompt técnico para generadores de IA (Midjourney/Flux)
    basado en los datos objetivos extraídos.
    """
    res = features.get("resolution", "unknown")
    lighting = context.get("lighting", "natural")
    style = context.get("style", "cinematic")
    colors = ", ".join(features.get("dominant_colors", []))
    
    prompt = f"""
Cinematic scene, high quality photography.
Resolution: {res}.
Lighting: {lighting} style.
Atmosphere: {style}.
Color Palette: {colors}.
Elements: {context.get('composition_focus', 'balanced composition')}.

Technical specs: professional cinematography, 8k, highly detailed, sharp focus.
"""
    return prompt.strip()
