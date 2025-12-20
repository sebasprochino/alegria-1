import importlib
import logging
import asyncio

logger = logging.getLogger("ALEGRIA_GATEWAY")

class UniversalAdapter:
    def __init__(self, name):
        self.name = name
        self.module = None
        self.status = "disconnected"
    def connect(self):
        try:
            self.module = importlib.import_module(self.name)
            self.status = "connected"
            return True
        except ImportError: return False
    def execute(self, func, **kwargs):
        f = getattr(self.module, func)
        if asyncio.iscoroutinefunction(f): return asyncio.run(f(**kwargs))
        return f(**kwargs)

class WorldGateway:
    def __init__(self):
        self.adapters = {}
        self.dep_manager = None
    
    def set_dependency_manager(self, node): self.dep_manager = node

    async def ensure_capability(self, package):
        if package in self.adapters: return True
        adapter = UniversalAdapter(package)
        if adapter.connect():
            self.adapters[package] = adapter
            return True
        
        logger.warning(f"⚠️ [GATEWAY] Falta {package}. Iniciando auto-instalación...")
        if self.dep_manager:
            res = self.dep_manager.service.execute("install_tool", {"query": package})
            if res['status'] == 'success' and adapter.connect():
                self.adapters[package] = adapter
                logger.info(f"🚀 [GATEWAY] {package} instalado y cargado.")
                return True
        return False

    async def use(self, pkg, func, **kwargs):
        if await self.ensure_capability(pkg):
            return self.adapters[pkg].execute(func, **kwargs)
        return {"error": "Capability missing"}

service = WorldGateway()
