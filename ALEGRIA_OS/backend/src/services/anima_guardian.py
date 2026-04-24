# -------------------------------------------------------------------------
# ALEGR-IA OS — Sistema Operativo de Coherencia Creativa
# Copyright (c) 2025 Sebastián Fernández & Antigravity AI.
# Todos los derechos reservados.
#
# Este código es CONFIDENCIAL y PROPIETARIO.
# Su copia, distribución o modificación no autorizada está penada por la ley.
# -------------------------------------------------------------------------

import sys
import time
import subprocess
import threading
import urllib.request
import os
from pathlib import Path

# Forzar UTF-8 en consola Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# --- CONFIGURACIÓN ---
BACKEND_DIR = Path("backend")
VENV_PYTHON = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
HOST = "0.0.0.0"
PORT = 8000
HEALTH_URL = f"http://localhost:{PORT}/"

def get_python_executable():
    """Busca el Python del entorno virtual, si no usa el del sistema."""
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable

def watcher():
    """Vigila que el sistema responda."""
    print("👀 [GUARDIAN] Vigilante activo...")
    while True:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as response:
                if response.getcode() == 200:
                    # Sistema OK
                    pass
        except urllib.error.URLError:
            # Es normal al inicio o si se cae
            pass
        except Exception as e:
            print(f"⚠️ [GUARDIAN] Error de vigilancia: {e}")
        
        time.sleep(10)

def start_server():
    """Inicia el servidor Uvicorn."""
    python_exe = get_python_executable()
    print(f"⚡ [ANIMA GUARDIAN] Iniciando sistema con: {python_exe}")
    
    # Comando para iniciar uvicorn respetando la estructura de paquetes
    # Ejecutamos desde la raíz, apuntando a backend como app-dir
    # Esto permite que 'src.server' y 'src.services' se importen correctamente
    cmd = [
        python_exe, "-m", "uvicorn", 
        "src.server:app", 
        "--reload", 
        "--app-dir", "backend", 
        "--host", HOST, 
        "--port", str(PORT)
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 [ANIMA GUARDIAN] Deteniendo sistema...")

if __name__ == "__main__":
    # Iniciar vigilante en hilo secundario
    t = threading.Thread(target=watcher, daemon=True)
    t.start()
    
    start_server()
