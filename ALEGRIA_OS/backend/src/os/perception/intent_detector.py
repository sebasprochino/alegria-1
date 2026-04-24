import re
import logging

logger = logging.getLogger("ALEGRIA_INTENT_DETECTOR")

# 🔹 Palabras que indican intención real (para activar el SDK/Kernel)
INTENT_KEYWORDS = [
    "crear", "generar", "hacer", "construir", "creame",
    "quiero", "necesito", "armar",
    "diseñar", "producir", "ejecutar", "investigar",
    "analizar", "buscar", "busca", "buscame",
    "guardar", "guarda", "almacenar", "recordar", "recuerda"
]

# 🔹 Patrones de ejecución directa (para derivar al modo ejecución)
EXECUTION_PATTERNS = [
    r"^ejecutar",
    r"^usar opción",
    r"^opción \d+",
    r"^run",
]

# 🔹 Acciones directas mapeadas (Bypass de propuesta)
EXPLICIT_ACTION_MAP = {
    "ejecutar radar": "radar.search",
    "usar radar": "radar.search",
    "busca en radar": "radar.search",
    "buscar en radar": "radar.search",
    "radar": "radar.search",
    "search": "radar.search",
    "buscar": "radar.search",
    "busca": "radar.search",
    # ── Acciones visuales (DESACOPLADO: Ahora fluyen vía Pipeline VeoScope) ────
    # Se eliminan de aquí para permitir que Anima genere el pipeline JSON soberano.
    "veoscope": "visual.veoscope",
    # ── Otras acciones ────────────────────────────────────────────────────────
    "code": "developer.execute",
    "noticias": "news.clarin",
    "noticia": "news.clarin",
    "clarin": "news.clarin",
    "abrir": "system.navigate",
    "navegar": "system.navigate",
    "youtube": "system.navigate",
    "ver": "system.navigate",
}


def normalize(text: str) -> str:
    return text.lower().strip()


def get_explicit_action(text: str) -> str:
    """Retorna el ID de la acción si el comando es inequívoco."""
    t = normalize(text)
    for keyword, action_id in EXPLICIT_ACTION_MAP.items():
        if t.startswith(keyword):
            return action_id
    return None


def is_execution(text: str) -> bool:
    for pattern in EXECUTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def is_intention(text: str) -> bool:
    for word in INTENT_KEYWORDS:
        if word in text:
            return True
    return False


def detect_mode(text: str) -> str:
    """
    Clasifica el input en: conversation, intention, o execution.
    Alineado con ACSP v1.1 + Modality Router (visual markers → execution directa).
    """
    t = normalize(text)

    if not t:
        return "conversation"

    # 🔴 Ejecución directa (Bypass de propuesta si es inequívoco)
    if get_explicit_action(t):
        return "execution"

    # 🔴 Ejecución explícita (Comandos de control + marcadores visuales)
    if is_execution(t):
        return "execution"

    # 🟡 Intención (Activa el Pipeline Soberano)
    if is_intention(t):
        return "intention"

    # 🟢 Fallback natural: Conversación directa (No activa pipeline)
    return "conversation"
