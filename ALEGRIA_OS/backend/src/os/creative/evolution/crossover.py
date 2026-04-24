def crossover_variants(results):
    """
    Realiza un cruce genético de los mejores componentes de cada variante.
    'results' es una lista de diccionarios con la evaluación y los outputs de cada variante.
    """
    alpha_outputs = {}
    fusion_trace = []

    # Buscamos el mejor componente por cada paso del pipeline
    steps = ["generate_script", "generate_audio", "generate_images"]
    
    for step in steps:
        best_component = None
        best_component_score = -1
        variant_origin = None
        
        for r in results:
            # Puntuamos el componente individualmente (puedes sofisticarlo)
            outputs = r.get("output", {})
            if step in outputs:
                # El score del componente aquí lo simplificamos al score total de la variante
                # pero en un sistema real, cada artefacto tendría su propia nota de calidad.
                score = r.get("eval", {}).get("final_score", 0)
                if score > best_component_score:
                    best_component_score = score
                    best_component = outputs[step]
                    variant_origin = r["id"]
        
        if best_component:
            alpha_outputs[step] = best_component
            fusion_trace.append({
                "step": step,
                "winner_variant": variant_origin,
                "score": best_component_score
            })

    return alpha_outputs, fusion_trace
