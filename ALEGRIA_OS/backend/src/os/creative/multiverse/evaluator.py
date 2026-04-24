from src.os.creative.optimizer.scorer import score_output
from src.os.creative.optimizer.evaluator import evaluate
from src.os.creative.profile.scorer import score_profile_alignment

def evaluate_variant(outputs, state, profile):
    """
    Evalúa una variante sumando score técnico, cumplimiento creativo y afinidad de perfil.
    """
    # 1. Score Técnico (Completitud)
    technical_score = score_output(outputs, state.get("goal", ""))
    
    # 2. Evaluación de Issues (Penalización)
    evaluation = evaluate(outputs, state.get("goal", ""), state)
    penalty = len(evaluation.get("issues", [])) * 0.5
    
    # 3. Afinidad de Perfil
    affinity_score = score_profile_alignment(profile, state.get("goal", ""))
    
    final_score = technical_score - penalty + affinity_score
    
    return {
        "final_score": max(0, final_score),
        "details": {
            "technical": technical_score,
            "penalty": penalty,
            "affinity": affinity_score,
            "issues": evaluation.get("issues", [])
        }
    }
