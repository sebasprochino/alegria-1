def score_output(outputs, goal):
    """
    Calcula una métrica objetiva de completitud y calidad base usando artefactos estandarizados.
    """
    score = 0

    # 1. Guion / Texto
    script = outputs.get("generate_script")
    if script and script.get("type") == "text":
        score += 1

    # 2. Audio
    audio = outputs.get("generate_audio")
    if audio and audio.get("type") == "audio":
        score += 1

    # 3. Imágenes
    images_art = outputs.get("generate_images")
    if images_art and images_art.get("type") == "image_list":
        images = images_art.get("value", [])
        if len(images) >= 3:
            score += 1

    # 4. Video (Resultado final)
    video = outputs.get("render_video")
    if video and video.get("type") == "video":
        score += 2

    return score

