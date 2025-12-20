from pathlib import Path
from datetime import datetime
import shutil

BASE = Path(r"G:\ALEGRIA_OS\ALEGRIA_OS")

ORIGEN = BASE / "src" / "AlegrIAAnimaV4.tsx"
DEST_DIR = BASE / "frontend" / "src" / "anima"
DESTINO = DEST_DIR / "AlegrIAAnimaV4.tsx"

BACKUP_DIR = BASE / "_backup_interfaz"

def log(msg):
    print(f"[INYECCION-ANIMA] {msg}")

def main():
    if not ORIGEN.exists():
        log("❌ No se encontró src/AlegrIAAnimaV4.tsx")
        return

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"AlegrIAAnimaV4_{timestamp}.tsx"

    shutil.copy2(ORIGEN, backup)
    log(f"Backup creado: {backup.name}")

    shutil.move(str(ORIGEN), str(DESTINO))
    log("Interfaz Maestra movida a frontend/src/anima/")

    log("✔ El frontend ahora puede ver a Anima")
    log("🔁 Reiniciá Vite")

if __name__ == "__main__":
    main()
