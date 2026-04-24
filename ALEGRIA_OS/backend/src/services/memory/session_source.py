# src/services/memory/session_source.py

import time
from pathlib import Path

class SessionSourceStore:
    """
    SESIÓN INFINITA
    ---------------
    Contexto vivo + base de almacenamiento.
    """
    def __init__(self, base_path: str | Path | None = None):
        self.started_at = time.time()

        # 🔒 Path de runtime (FUERA de src/)
        if base_path is None:
            self.base_path = (
                Path(__file__).resolve()
                .parents[3]          # backend/
                / "data"
                / "session"
            )
        else:
            self.base_path = Path(base_path)

        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata = {}

        print(f"[SESSION_SOURCE] Store inicializado en: {self.base_path}")

    def set(self, key, value):
        self.metadata[key] = value

    def get(self, key, default=None):
        return self.metadata.get(key, default)

    # compatibilidad con os.stat / Path
    def __fspath__(self):
        return str(self.base_path)
