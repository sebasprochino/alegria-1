import sys
import subprocess
from pathlib import Path

class DependencyManager:
    def __init__(self):
        self.req_path = Path("requirements.txt")
        self.python_exec = sys.executable

    def install(self, package_name: str):
        print(f"📦 [DEP] Instalando {package_name}...")
        try:
            # Primero nos aseguramos de que pip esté actualizado
            subprocess.run([self.python_exec, "-m", "pip", "install", "--upgrade", "pip"], check=False)
            
            # Instalamos el paquete
            subprocess.run([self.python_exec, "-m", "pip", "install", package_name], check=True)
            
            # Registrar en requirements
            with open(self.req_path, "a") as f: f.write(f"\n{package_name}")
            return {"status": "success", "pkg": package_name}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def execute(self, action, params):
        if action == "install_tool": return self.install(params['query'])
        return {"error": "Unknown action"}

service = DependencyManager()
