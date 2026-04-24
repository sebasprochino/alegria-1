def get_default_profile():
    """Retorna el perfil creativo base para un nuevo hilo u operador."""
    return {
        "style": {},
        "preferences": {
            "min_script_length": 50,
            "image_count": 3
        },
        "history": [],
        "version": "1.0"
    }

def prune_profile(profile):
    """Limpia el historial para evitar deriva y exceso de tokens."""
    if "history" in profile:
        profile["history"] = profile["history"][-20:]
    return profile
