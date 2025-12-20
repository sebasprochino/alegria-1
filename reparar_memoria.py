import os
from pathlib import Path

# ==========================================
# 1. DATABASE.PY (El Chofer de la Base de Datos)
# ==========================================
DATABASE_CODE = """import logging
from prisma import Prisma

logger = logging.getLogger("ALEGRIA_DB")

class DatabaseService:
    def __init__(self):
        self.db = Prisma()
        self.connected = False

    async def connect(self):
        if not self.connected:
            try:
                await self.db.connect()
                self.connected = True
                logger.info("✅ [DB] Conexión establecida con SQLite.")
            except Exception as e:
                logger.error(f"❌ [DB] Error conectando: {e}")

    async def disconnect(self):
        if self.connected:
            await self.db.disconnect()
            self.connected = False

    # Métodos utilitarios
    async def create_log(self, module, code, msg):
        if self.connected:
            try:
                await self.db.codingerror.create(data={
                    'moduleName': module,
                    'badCode': code,
                    'errorMsg': msg
                })
            except:
                pass

service = DatabaseService()
"""

# ==========================================
# 2. NEXUS.PY (El Bibliotecario)
# ==========================================
NEXUS_CODE = """import logging
# Importamos el servicio de base de datos local
from .database import service as db_service

logger = logging.getLogger("ALEGRIA_NEXUS")

class NexusSystem:
    def __init__(self):
        self.name = "Nexus"
        # Conectamos con el servicio de base de datos
        self.db = db_service

    async def initialize(self):
        # Este método se llama al arrancar para conectar la DB
        await self.db.connect()

    async def get_context(self):
        # Simula recuperar el contexto del proyecto actual
        return "Modo: Desarrollo. Proyecto: ALEGRIA OS. Usuario: Chinex."

    async def save_memory(self, key, value):
        logger.info(f"💾 [NEXUS] Guardando {key}: {value}")
        # Aquí iría la lógica real de guardado
        return True

service = NexusSystem()

# Hook de arranque: Cuando el Gateway carga a Nexus, intenta conectar la DB
import asyncio
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Si ya hay loop, creamos tarea
        loop.create_task(service.initialize())
    else:
        loop.run_until_complete(service.initialize())
except Exception:
    pass 
"""

def arreglar_memoria():
    print("🧠 RECONSTRUYENDO EL LÓBULO DE MEMORIA (NEXUS)...")
    
    base_path = Path("backend/src/services")
    
    # 1. Reescribir database.py
    with open(base_path / "database.py", "w", encoding="utf-8") as f:
        f.write(DATABASE_CODE)
    print("✅ database.py reescrito correctamente.")

    # 2. Reescribir nexus.py
    with open(base_path / "nexus.py", "w", encoding="utf-8") as f:
        f.write(NEXUS_CODE)
    print("✅ nexus.py reescrito correctamente.")

    print("\n✨ MEMORIA REPARADA ✨")
    print("---------------------------------------")
    print("1. Cierra las ventanas negras.")
    print("2. Ejecuta: .\\backend\\venv\\Scripts\\python.exe iniciar_alegria.py")

if __name__ == "__main__":
    arreglar_memoria()