from pathlib import Path

ANIMA_PATH = Path("backend/src/services/anima.py")

def inyectar():
    if not ANIMA_PATH.exists():
        print("ERROR: anima.py no encontrado")
        return

    contenido = ANIMA_PATH.read_text(encoding="utf-8")

    if "MEMORIA_FUNDACIONAL" in contenido:
        print("INFO: La memoria fundacional ya está inyectada")
        return

    bloque = '''
# --- MEMORIA FUNDACIONAL ---
from .memoria_fundacional import MEMORIA_FUNDACIONAL

self.memoria_fundacional = MEMORIA_FUNDACIONAL
self.historial = MEMORIA_FUNDACIONAL.get("historia_inicial", [])
# --- FIN MEMORIA FUNDACIONAL ---
'''

    if "def __init__(" not in contenido:
        print("ERROR: No se encontró __init__ en anima.py")
        return

    contenido = contenido.replace(
        "def __init__(self",
        "def __init__(self" + bloque
    )

    ANIMA_PATH.write_text(contenido, encoding="utf-8")
    print("OK: Memoria fundacional inyectada en Anima")

if __name__ == "__main__":
    inyectar()
