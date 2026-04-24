# ALEGR-IA OS — src/os/perception/vision/brand.py

def suggest_brand(features, context):
    """
    Propone directrices de marca basadas en el análisis visual.
    """
    return {
        "tone": context.get("style", "neutral"),
        "visual_identity": "cinematic" if context.get("lighting") == "low_key" else "clean",
        "target_medium": "digital content / high-end branding",
        "suggested_palette": features.get("dominant_colors", []),
        "vibe": "innovation" if features.get("sharpness") == "sharp" else "organic"
    }
