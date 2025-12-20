import logging
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
