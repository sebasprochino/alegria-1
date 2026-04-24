import hash_lib

def generate_music(prompt: str):
    # simulación reemplazable por API real
    # Usamos hashes deterministas para la simulación
    prompt_hash = abs(hash(prompt)) % (10**8)
    return {
        "file": f"music_{prompt_hash}.mp3",
        "duration": 30,
        "provider": "suno_sim"
    }
