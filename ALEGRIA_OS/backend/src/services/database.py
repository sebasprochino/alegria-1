import logging
from prisma import Prisma

logger = logging.getLogger("ALEGRIA_DB")

class DatabaseService:
    def __init__(self):
        import os
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        db_path = os.path.join(backend_dir, 'dev.db')
        # Utilizamos url con slash según el formato prisma file: (ej file:C:/...) o file:./...
        # En windows la barra invertida puede causar problemas con url, se reemplazan manual.
        self.db_url = f"file:{db_path.replace(chr(92), '/')}"
        self.db = None
        self.connected = False

    async def connect(self):
        if not self.connected:
            try:
                if self.db is None:
                    # Instanciación diferida para evitar errores de Client not generated al importar
                    from prisma import Prisma
                    self.db = Prisma(datasource={'url': self.db_url})
                
                await self.db.connect()
                self.connected = True
                logger.info("✅ [DB] Conexión establecida con SQLite.")
            except Exception as e:
                logger.error(f"❌ [DB] Error conectando o instanciando Prisma: {e}")
                self.connected = False


    async def disconnect(self):
        if self.connected:
            await self.db.disconnect()
            self.connected = False

    # Métodos utilitarios
    async def create_log(self, module, code, msg):
        try:
            if not self.connected:
                await self.connect()
                
            if self.connected:
                await self.db.codingerror.create(data={
                    'moduleName': module,
                    'badCode': code,
                    'errorMsg': msg
                })
        except Exception as e:
            logger.warning(f"⚠️ [PRISMA] Error en create_log (skip): {e}")
            pass


service = DatabaseService()
