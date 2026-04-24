from src.os.pipeline.creative_steps import render_video_step
from .coherence import evaluate_coherence
from src.os.creative.director import CreativeDirector

async def synthesize_alpha(alpha_outputs, results, state):
    """
    Sintetiza la variante 'Alpha' realizando validación de coherencia, auditoría del CDM y renderizado final.
    """
    # 0. Creative Director Audit (Aesthetic Intelligence)
    director = CreativeDirector()
    # Inyectar dimensiones estéticas del preset actual en el estado si no existen
    score, cdm_issues, cdm_status = director.evaluate_variant(alpha_outputs)
    
    if cdm_status == "rejected":
        return {
            "status": "cdm_rejected",
            "reason": cdm_issues,
            "outputs": None
        }

    # 1. Coherence Gate
    coherence = evaluate_coherence(alpha_outputs, state)

    
    if not coherence["valid"]:
        # Fallback: Usar la mejor variante completa (Winner del Multiverso)
        from src.os.creative.multiverse.selector import select_best
        winner = select_best(results)
        
        return {
            "status": "fallback",
            "reason": coherence["issues"],
            "outputs": winner.get("output")
        }

    # 2. Harmonización (Opcional pero recomendado)
    from .harmonizer import harmonize_fusion
    alpha_outputs = await harmonize_fusion(alpha_outputs, state)

    # 3. Renderizado Final
    if "generate_images" in alpha_outputs and "generate_audio" in alpha_outputs:
        alpha_outputs["render_video"] = render_video_step(state, alpha_outputs)
        
    return {
        "status": "synthesized",
        "outputs": alpha_outputs,
        "coherence_log": coherence["issues"]
    }

