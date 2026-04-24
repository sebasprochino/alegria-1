def select_best(variant_results):
    """
    Selecciona la mejor variante basada en el score más alto.
    """
    best = None
    best_score = -1

    for result in variant_results:
        score = result.get("eval", {}).get("final_score", 0)
        if score > best_score:
            best = result
            best_score = score

    return best
