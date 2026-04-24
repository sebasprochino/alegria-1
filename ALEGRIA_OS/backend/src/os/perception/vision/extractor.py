import cv2
import numpy as np
import base64

def load_image(path_or_b64):
    if len(path_or_b64) > 1000 or path_or_b64.startswith('data:'):
        # Es base64
        if ',' in path_or_b64:
            b64_data = path_or_b64.split(',', 1)[1]
        else:
            b64_data = path_or_b64
        img_data = base64.b64decode(b64_data)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    else:
        # Es path
        img = cv2.imread(path_or_b64)
        
    if img is None:
        raise ValueError("No se pudo cargar la imagen. Ruta inválida o formato base64 corrupto.")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def exposure_level(gray):
    mean = gray.mean()
    if mean < 80: return "low_key"
    if mean > 180: return "high_key"
    return "normal"

def contrast_level(gray):
    std = gray.std()
    if std < 30: return "low"
    if std > 70: return "high"
    return "medium"

def palette_type(hsv):
    h = hsv[:,:,0].flatten()
    if np.std(h) < 10: return "neutral"
    warm = np.mean((h < 30) | (h > 150))
    cool = np.mean((h >= 60) & (h <= 120))
    if warm > cool: return "warm"
    if cool > warm: return "cool"
    return "mixed"

def dominant_colors(img, k=5):
    pixels = img.reshape(-1, 3)
    Z = np.float32(pixels)
    _, labels, centers = cv2.kmeans(
        Z, k, None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
        10, cv2.KMEANS_RANDOM_CENTERS
    )
    centers = np.uint8(centers)
    return ["#%02x%02x%02x" % tuple(c) for c in centers]

def composition(img):
    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    ys, xs = np.where(edges > 0)
    if len(xs) == 0: return "centered"
    cx, cy = xs.mean() / w, ys.mean() / h
    if 0.3 < cx < 0.7 and 0.3 < cy < 0.7:
        return "centered"
    return "rule_of_thirds"

def sharpness(gray):
    var_lap = cv2.Laplacian(gray, cv2.CV_64F).var()
    if var_lap < 50: return "soft"
    if var_lap > 200: return "sharp"
    return "normal"

def edge_complexity(gray):
    edges = cv2.Canny(gray, 50, 150)
    density = edges.mean()
    if density < 10: return "low"
    if density > 40: return "high"
    return "medium"

def visual_density(edges):
    d = edges.mean()
    if d < 10: return "minimal"
    if d > 40: return "rich"
    return "balanced"

def extract_features(path):
    img = load_image(path)
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    edges = cv2.Canny(gray, 50, 150)

    return {
        "resolution": f"{w}x{h}",
        "brightness": float(gray.mean()),
        "exposure": exposure_level(gray),
        "contrast": contrast_level(gray),
        "color_palette": palette_type(hsv),
        "dominant_colors": dominant_colors(img, k=5),
        "composition": composition(img),
        "sharpness": sharpness(gray),
        "texture": "grainy" if gray.std() > 60 else "smooth",
        "visual_density": visual_density(edges),
        "edge_complexity": edge_complexity(gray)
    }
