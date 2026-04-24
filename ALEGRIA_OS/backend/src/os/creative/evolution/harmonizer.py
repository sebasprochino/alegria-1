from src.services.provider_registry import service as provider_registry

async def harmonize_fusion(alpha_outputs, state):
    """
    Refina y armoniza los componentes fusionados para asegurar una narrativa fluida.
    """
    script_art = alpha_outputs.get("generate_script", {})
    audio_art = alpha_outputs.get("generate_audio", {})
    
    script = script_art.get("value", "")
    audio_meta = audio_art.get("value", {})
    
    prompt = f"""
    Eres un Director Creativo. Debes refinar este guion para que armonice perfectamente 
    con las características del audio seleccionado.
    
    GUION ORIGINAL:
    {script}
    
    CARACTERÍSTICAS DEL AUDIO:
    {audio_meta}
    
    INSTRUCCIÓN:
    Ajusta el ritmo, el tono y la narrativa del guion para que no haya fricción. 
    Devuelve SOLO el guion procesado.
    """
    
    try:
        refined_script = await provider_registry.chat(
            messages=[{"role": "user", "content": prompt}],
            system="Eres un Director Creativo experto en ALEGR-IA OS."
        )
        
        # Actualizamos el componente en alpha_outputs
        alpha_outputs["generate_script"]["value"] = refined_script
        alpha_outputs["generate_script"]["status"] = "harmonized"
        
    except Exception as e:
        # Si falla el refinamiento, mantenemos el original (Sovereign Fallback)
        pass
        
    return alpha_outputs
