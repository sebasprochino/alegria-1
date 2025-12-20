from pathlib import Path
from datetime import datetime

BASE = Path(r"G:\ALEGRIA_OS\ALEGRIA_OS")
ANIMA_FILE = BASE / "frontend" / "src" / "anima" / "AnimaUI.tsx"
BACKUP_DIR = BASE / "frontend" / "src" / "anima" / "_backup"

CORRECT_CONTENT = """import { useEffect, useRef } from "react";

export default function AnimaUI({ messages }) {
  const lastSpoken = useRef(null);

  useEffect(() => {
    if (!messages || messages.length === 0) return;

    const last = messages[messages.length - 1];

    if (last.role !== "anima") return;
    if (last.content === lastSpoken.current) return;

    lastSpoken.current = last.content;

    if ("speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(last.content);
      u.lang = "es-AR";
      u.rate = 0.95;
      u.pitch = 1.05;
      window.speechSynthesis.speak(u);
    }
  }, [messages]);

  return (
    <div style={{
      position: "fixed",
      bottom: 12,
      right: 12,
      opacity: 0.6,
      fontSize: 12
    }}>
      🧠 Anima presente
    </div>
  );
}
"""

def log(msg):
    print(f"[ANIMA-FIX] {msg}")

def main():
    if not ANIMA_FILE.exists():
        log("❌ AnimaUI.tsx no encontrado. Abortando.")
        return

    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"AnimaUI_backup_{timestamp}.tsx"

    backup_file.write_text(ANIMA_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    log(f"Backup creado: {backup_file.name}")

    ANIMA_FILE.write_text(CORRECT_CONTENT, encoding="utf-8")
    log("AnimaUI.tsx corregido (auto-import eliminado)")

    log("✔ Corrección aplicada con dignidad")
    log("🔁 Reiniciá Vite para completar el rito")

if __name__ == "__main__":
    main()
