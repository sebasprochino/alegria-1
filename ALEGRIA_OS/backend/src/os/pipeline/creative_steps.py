from src.integrations.audio.suno import generate_music
from src.integrations.image.sd import generate_image
from src.integrations.video.ffmpeg import render_video

def wrap_artifact(art_type, value):
    """Estandariza el formato de los artefactos producidos."""
    return {
        "type": art_type,
        "value": value
    }

def generate_script_step(state, outputs):
    """Genera el guion basado en el objetivo."""
    val = state.get("goal") or "Guion generado por defecto"
    return wrap_artifact("text", val)

def generate_audio_step(state, outputs):
    """Genera música/audio basado en el guion."""
    script_data = outputs.get("generate_script", {})
    script = script_data.get("value", "") if isinstance(script_data, dict) else ""
    res = generate_music(script)
    return wrap_artifact("audio", res)

def generate_images_step(state, outputs):
    """Genera una serie de imágenes basadas en el guion."""
    script_data = outputs.get("generate_script", {})
    script = script_data.get("value", "") if isinstance(script_data, dict) else ""
    images = [generate_image(script, i) for i in range(3)]
    return wrap_artifact("image_list", images)

def render_video_step(state, outputs):
    """Renderiza el video final usando imágenes y audio."""
    images_data = outputs.get("generate_images", {})
    audio_data = outputs.get("generate_audio", {})
    
    images = images_data.get("value", []) if isinstance(images_data, dict) else []
    audio_val = audio_data.get("value", {}) if isinstance(audio_data, dict) else {}
    audio_file = audio_val.get("file") if isinstance(audio_val, dict) else audio_val
    
    video_file = render_video(images, audio_file)
    return wrap_artifact("video", video_file)


# Mapeo para el registro
CREATIVE_STEPS = {
    "generate_script": generate_script_step,
    "generate_audio": generate_audio_step,
    "generate_images": generate_images_step,
    "render_video": render_video_step
}
