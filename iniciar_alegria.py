import subprocess
import time
import os
import sys

# --- CONFIGURACIÓN ---
PORTS_TO_CLEAN = [8000, 5173]
BACKEND_SCRIPT = r".\backend\venv\Scripts\python.exe anima_guardian.py"
FRONTEND_DIR = "frontend"
FRONTEND_CMD = "npm run dev"

def kill_port(port):
    """Detecta y elimina procesos ocupando un puerto específico en Windows."""
    print(f"🔍 Escaneando puerto {port}...", end=" ")
    try:
        # Busca el PID del proceso que usa el puerto
        cmd = f"netstat -ano | findstr :{port}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if not result.stdout:
            print("✅ Libre.")
            return

        # Extraer PIDs únicos
        pids = set()
        for line in result.stdout.strip().split('\n'):
            parts = line.split()
            # El formato de netstat suele ser: PROTO IP:PORT IP:PORT ESTADO PID
            # Buscamos que la IP local contenga el puerto exacto (ej :8000)
            if len(parts) >= 5 and f":{port}" in parts[1]:
                pids.add(parts[-1])

        if not pids:
            print("✅ Libre (Falso positivo).")
            return

        print(f"⚠️ Ocupado por PIDs: {', '.join(pids)}")
        for pid in pids:
            if pid != "0": # Ignorar System Idle
                print(f"   🧹 Matando proceso {pid}...", end=" ")
                subprocess.run(f"taskkill /PID {pid} /F", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("💀 Hecho.")
                
    except Exception as e:
        print(f"❌ Error limpiando puerto: {e}")

def start_system():
    print("\n🚀 INICIANDO SECUENCIA DE ARRANQUE ALEGRIA OS...\n")
    
    # 1. LIMPIEZA DE TERRENO
    for port in PORTS_TO_CLEAN:
        kill_port(port)
    
    time.sleep(1) # Un respiro para el sistema
    
    # 2. INICIAR CEREBRO (BACKEND)
    print("\n🧠 Despertando a Anima (Backend)...")
    # 'start' abre una nueva ventana de CMD independiente
    subprocess.Popen(f'start "ALEGRIA - CEREBRO" {BACKEND_SCRIPT}', shell=True)
    
    # 3. INICIAR ROSTRO (FRONTEND)
    print("🎨 Encendiendo Interfaz Visual...")
    # Entra a la carpeta frontend y ejecuta npm
    cmd_frontend = f'cd {FRONTEND_DIR} && {FRONTEND_CMD}'
    subprocess.Popen(f'start "ALEGRIA - VISUAL" cmd /k "{cmd_frontend}"', shell=True)

    print("\n✨ SISTEMA LANZADO.")
    print("Se han abierto 2 ventanas nuevas. Puedes cerrar esta.")

if __name__ == "__main__":
    start_system()