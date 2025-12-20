import os
from pathlib import Path

# Código corregido para el Developer (Incluye carga de .env)
NEW_DEVELOPER_CODE = """import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno explícitamente desde la carpeta backend
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")

class AnimaDeveloper:
    def __init__(self):
        self.name = "Anima Developer"
        self.base_path = Path("src/services")

    async def generate_and_write(self, module_name: str, desc: str, tags: str) -> dict:
        
        if not api_key:
            return {"status": "error", "error": "No API Key found in .env"}

        system_instruction = f'''Eres Anima Developer, el ingeniero del sistema ALEGRIA.
        TU MISIÓN: Escribir el código Python completo y funcional para el módulo: {module_name}.
        REGLAS:
        1. Código moderno, robusto y limpio.
        2. Incluye manejo de errores.
        3. NO uses bloques de markdown (```). Solo código crudo.
        4. Si necesitas librerías externas, asume que el DependencyManager las instalará.'''
        
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=system_instruction)
            print(f"🧠 [DEV] Generando código para {module_name}...")
            
            response = await model.generate_content_async(desc)
            clean_code = response.text.replace("```python", "").replace("```", "").strip()
            
            # Escribir archivo
            filename = f"{module_name.lower()}.py"
            # Ajuste de ruta para asegurar que se guarde en src/services relativo al backend
            file_path = self.base_path / filename
            
            # Aseguramos que la ruta sea absoluta respecto a la ejecución
            if not file_path.is_absolute():
                # Estamos en backend/src/services/developer.py -> parents[1] es backend/src
                # Pero mejor usamos rutas relativas al script
                real_path = Path("backend/src/services") / filename
            else:
                real_path = file_path

            with open(real_path, "w", encoding="utf-8") as f:
                f.write(clean_code)
            
            return {"status": "success", "message": f"Módulo {module_name} creado.", "path": str(real_path)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

service = AnimaDeveloper()
"""

def patch_system():
    print("🔧 Ajustando conexiones neuronales (Leyendo .env)...")
    
    # 1. Reescribir developer.py con el fix de dotenv
    dev_path = Path("backend/src/services/developer.py")
    with open(dev_path, "w", encoding="utf-8") as f:
        f.write(NEW_DEVELOPER_CODE)
    
    print("✅ Developer actualizado para leer la clave.")
    print("---------------------------------------------")
    print("1. Cierra la ventana negra del servidor (anima_guardian) si está abierta.")
    print("2. Vuelve a ejecutar: .\\backend\\venv\\Scripts\\python.exe anima_guardian.py")
    print("3. Luego, en otra terminal, ejecuta de nuevo: despertar_nexus.py")

if __name__ == "__main__":
    patch_system()