import os
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
            model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025', system_instruction=system_instruction)
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
