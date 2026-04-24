def generate_image(prompt: str, idx: int):
    # simulación reemplazable por API real
    prompt_hash = abs(hash(prompt)) % (10**8)
    return f"image_{idx}_{prompt_hash}.png"
