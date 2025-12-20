import os
import subprocess
from pathlib import Path

# ==========================================
# 1. CÓDIGO LIMPIO PARA RADAR (Sin errores)
# ==========================================
RADAR_CODE = """import logging
from duckduckgo_search import DDGS

logger = logging.getLogger("ALEGRIA_RADAR")

class RadarSystem:
    def __init__(self):
        self.name = "Radar"
        
    def scan(self, query: str, max_results: int = 3):
        try:
            logger.info(f"📡 [RADAR] Escaneando: {query}")
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                
            if not results:
                return "Radar no encontró señales relevantes."
                
            summary = "--- REPORTE DE RADAR ---\\n"
            for i, r in enumerate(results, 1):
                summary += f"{i}. {r['title']}: {r['body']} (Fuente: {r['href']})\\n"
            return summary
            
        except Exception as e:
            logger.error(f"❌ [RADAR] Error de señal: {e}")
            return f"Error de Radar: {str(e)}"

service = RadarSystem()
"""

# ==========================================
# 2. CÓDIGO LIMPIO PARA ANIMA (Orquestador)
# ==========================================
ANIMA_CODE = """import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Configuración
logger = logging.getLogger("ALEGRIA_ANIMA")

# Cargar entorno
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(env_path)
api_key = os.getenv("GEMINI_API_KEY")

class AnimaChordata:
    def __init__(self):
        self.name = "Anima Chordata"
        self.nexus = None
        self.radar = None
        self.model_name = "gemini-2.0-flash-exp" # O el modelo que tengas disponible
        self.configure_ai()

    def configure_ai(self):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                self.model_name,
                system_instruction="Eres Anima, un SO vivo. Responde con identidad propia, breve y útil."
            )
        else:
            logger.warning("⚠️ [ANIMA] Sin API KEY. Lobotomizada.")
            self.model = None

    # Inyección de Dependencias (El Gateway llama a esto)
    def set_peers(self, nexus_node, radar_node):
        self.nexus = nexus_node
        self.radar = radar_node

    async def reply(self, user_text: str, context: dict = None):
        if not self.model:
            return "Error: No tengo API Key configurada en backend/.env"

        # 1. Pensamiento (Consultar Radar si es necesario)
        radar_info = ""
        if "buscar" in user_text.lower() or "investiga" in user_text.lower():
            if self.radar:
                radar_info = self.radar.service.scan(user_text)
            else:
                radar_info = "[Radar no disponible]"

        # 2. Construcción del Prompt
        full_prompt = f'''
        CONTEXTO DEL SISTEMA:
        {radar_info}
        
        USUARIO DICE:
        {user_text}
        '''

        # 3. Generación
        try:
            response = await self.model.generate_content_async(full_prompt)
            return response.text
        except Exception as e:
            return f"Error cognitivo: {str(e)}"

service = AnimaChordata()
"""

def reparar():
    print("🔧 INICIANDO REPARACIÓN QUIRÚRGICA DEL CEREBRO...")
    
    base_path = Path("backend/src/services")
    
    # 1. Reescribir Radar
    with open(base_path / "radar.py", "w", encoding="utf-8") as f:
        f.write(RADAR_CODE)
    print("✅ Radar.py reconstruido correctamente.")

    # 2. Reescribir Anima
    with open(base_path / "anima.py", "w", encoding="utf-8") as f:
        f.write(ANIMA_CODE)
    print("✅ Anima.py reconstruido correctamente.")

    # 3. Arreglar Nexus (Prisma Generate)
    print("🔄 Reparando Nexus (Generando Cliente Prisma)...")
    
    # Detectar rutas
    if os.name == 'nt':
        prisma_cmd = str(Path("backend/venv/Scripts/prisma"))
    else:
        prisma_cmd = str(Path("backend/venv/bin/prisma"))

    try:
        subprocess.run([prisma_cmd, "generate", "--schema=backend/prisma/schema.prisma"], check=True)
        print("✅ Cliente Prisma generado. Nexus ya puede leer.")
    except Exception as e:
        print(f"❌ Error generando Prisma: {e}")
        print("Intenta correr manualmente: backend\\venv\\Scripts\\prisma generate --schema=backend/prisma/schema.prisma")

    print("\n✨ REPARACIÓN COMPLETADA ✨")
    print("---------------------------------------")
    print("1. Cierra todas las ventanas negras (servidores).")
    print("2. Ejecuta tu script maestro: .\\backend\\venv\\Scripts\\python.exe iniciar_alegria.py")

if __name__ == "__main__":
    reparar()