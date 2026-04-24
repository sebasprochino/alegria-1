def generate_variants(requested_steps, state, n=3):
    """
    Genera n variantes de un plan de ejecución, ajustando parámetros de creatividad.
    """
    variants = []

    for i in range(n):
        # Creamos una copia profunda del estado para cada variante
        import copy
        variant_state = copy.deepcopy(state)
        variant_state["variant_id"] = i
        
        # Variación controlada de la temperatura creativa
        variant_state["temperature"] = min(1.0, 0.7 + (i * 0.1))
        
        variants.append({
            "id": i,
            "state": variant_state,
            "steps": requested_steps
        })

    return variants
