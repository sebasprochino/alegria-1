import sys
import time
import subprocess
import threading
from pathlib import Path

def watcher():
    while True:
        # Aquí vigilamos la salud del sistema
        time.sleep(5)

def start_server():
    # Iniciamos el servidor con recarga automática
    cmd = [sys.executable, "-m", "uvicorn", "src.server:app", "--reload", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]
    print("⚡ [ANIMA GUARDIAN] Iniciando sistema...")
    subprocess.run(cmd)

if __name__ == "__main__":
    t = threading.Thread(target=watcher, daemon=True)
    t.start()
    start_server()
