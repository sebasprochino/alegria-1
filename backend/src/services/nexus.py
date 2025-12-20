import logging
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
