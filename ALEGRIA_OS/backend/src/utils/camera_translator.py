# backend/src/utils/camera_translator.py
"""
Camera Translator
=================
Convierte coordenadas espaciales (Rotate, Vertical, Zoom) en terminología 
cinematográfica profesional para inyección en prompts.
"""

def translate_camera_params(rotate: float, vertical: float, zoom: float) -> str:
    """
    Mapea valores numéricos a directivas de cámara.
    Rotate: 0-360 deg
    Vertical: -90 (zenith) a 90 (nadir) deg
    Zoom: 0.1 (FOV amplio) a 5.0 (Macro/Tele)
    """
    directives = []

    # 1. Ángulo Vertical (Pitch)
    if vertical <= -60:
        directives.append("Full Bird's eye view, top-down perspective")
    elif vertical <= -25:
        directives.append("High angle shot, looking down at subject")
    elif vertical >= 60:
        directives.append("Extreme low angle, worm's eye view, monumental scale")
    elif vertical >= 25:
        directives.append("Low angle shot, cinematic elevation")
    else:
        directives.append("Eye-level shot, neutral perspective")

    # 2. Rotación Horizontal (Yaw)
    # 0 = frontal, 90 = perfil derecho, 180 = espalda, 270 = perfil izquierdo
    rot = rotate % 360
    if 45 <= rot < 135:
        directives.append("Right side profile view")
    elif 135 <= rot < 225:
        directives.append("Back view shot, behind the subject")
    elif 225 <= rot < 315:
        directives.append("Left side profile view")
    else:
        # Frontal
        pass

    # 3. Zoom / Focal Length
    if zoom >= 2.5:
        directives.append("Macro detail, extreme close-up, telephoto compression")
    elif zoom >= 1.5:
        directives.append("Close-up shot, portrait framing")
    elif zoom <= 0.4:
        directives.append("Ultra-wide angle, fisheye effect, expansive landscape")
    elif zoom <= 0.7:
        directives.append("Wide angle lens, establishing shot")
    
    return ", ".join(directives)

if __name__ == "__main__":
    # Test simple
    print(translate_camera_params(0, 70, 0.5)) # Extreme low angle... Wide angle...
    print(translate_camera_params(180, -45, 2.0)) # Back view... High angle... Close-up...
