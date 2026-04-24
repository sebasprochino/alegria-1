from .scorer import score_output
from .evaluator import evaluate, map_issue_to_step

MIN_SCORE = 3

def optimize(outputs, goal, state):
    """
    Coordina la evaluación y decide si el output es aceptable o requiere mejora quirúrgica.
    """
    score = score_output(outputs, goal)
    evaluation = evaluate(outputs, goal, state)

    state["optimization"] = {
        "score": score,
        "issues": evaluation["issues"],
        "threshold": MIN_SCORE
    }

    # Si el score es sufiente y no hay issues críticos técnicos, aceptamos
    if score >= MIN_SCORE and not evaluation["needs_improvement"]:
        return {
            "action": "accept",
            "outputs": outputs
        }

    # Decidir qué pasos específicos re-ejecutar (mejora quirúrgica)
    steps_to_fix = list(set([map_issue_to_step(i) for i in evaluation["issues"] if map_issue_to_step(i)]))

    return {
        "action": "improve",
        "issues": evaluation["issues"],
        "steps_to_fix": steps_to_fix
    }

