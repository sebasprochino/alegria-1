import os
import sys
import asyncio

# --- FIX: Windows Loop Policy for Subprocesses (Playwright Support) ---
# Debe estar al inicio absoluto ANTES de cualquier import de FastAPI/Uvicorn
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# ----------------------------------------------------------------------

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import importlib

# ─── FIX sys.path (Windows / uvicorn --reload) ───────────────────────────────
# Garantiza que tanto el proceso padre (pre-reloader) como el proceso hijo
# (worker) resuelvan los paquetes src.* desde el directorio /backend.
# Debe ejecutarse a nivel de módulo — NO sólo en __main__ — porque uvicorn
# importa este archivo antes de lanzar el StatReload worker.
_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)
# ─────────────────────────────────────────────────────────────────────────────

# Configuración de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ALEGRIA_OS_SERVER")
logger.info("🔥 [STARTUP] ALEGRIA OS Backend — REGENERADO")

# --- GHOST NODE PATTERN ---
class GhostNode:
    """
    Representa un módulo que falló al cargar.
    Permite que el sistema arranque en modo degradado.
    """
    def __init__(self, name, error):
        self.name = name
        self.error = str(error)
        self.status = "ghost"

    def __getattr__(self, method_name):
        def ghost_method(*args, **kwargs):
            logger.warning(f"👻 [GHOST] Intento de acceso a nodo muerto: {self.name}.{method_name}")
            return {"status": "degraded", "error": self.error, "node": self.name}
        return ghost_method

class NodeLoader:
    """
    Cargador dinámico de servicios para arquitectura resiliente.
    """
    def __init__(self):
        self.nodes = {}

    def load_node(self, node_name: str, module_path: str, class_name: str = None):
        try:
            # Intenta importar el módulo
            module = importlib.import_module(module_path)
            
            # Si se especifica una clase, intenta instanciarla (patrón Singleton simple)
            # Si no, guarda el módulo entero
            if class_name:
                service_class = getattr(module, class_name)
                # Asumimos que los servicios se pueden instanciar sin argumentos o manejan su propia init
                instance = service_class() 
                self.nodes[node_name] = instance
            else:
                self.nodes[node_name] = module
                
            logger.info(f"✅ [NODE] {node_name.upper()} cargado exitosamente desde {module_path}")
            return self.nodes[node_name]

        except ImportError as e:
            logger.error(f"❌ [FAIL] Error cargando {node_name}: {e}")
            self.nodes[node_name] = GhostNode(node_name, e)
            return self.nodes[node_name]
        except Exception as e:
            logger.error(f"❌ [FAIL] Error crítico en {node_name}: {e}")
            self.nodes[node_name] = GhostNode(node_name, e)
            return self.nodes[node_name]

# --- INICIALIZACIÓN DEL SISTEMA ---

# 1. Instanciamos el Loader
loader = NodeLoader()

# 2. Definición de la App FastAPI
app = FastAPI(
    title="ALEGRIA OS API",
    description="Backend del Sistema Operativo de Coherencia Creativa",
    version="2.0.0" # Actualizado según reporte de arquitectura
)

from src.services.audit_emitter import audit_emitter

@app.on_event("startup")
async def startup():
    await audit_emitter.start()

@app.on_event("shutdown")
async def shutdown():
    await audit_emitter.stop()

# 3. Configuración CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*" # Temporal para desarrollo, ajustar para producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Carga de Nodos Esenciales (Services)
# Ajustamos las rutas de importación según tu estructura de archivos 'src.services...'
nexus = loader.load_node("nexus", "src.services.nexus") 
# Nota: Si las clases tienen nombres específicos, ajustar aquí. 
# Por ahora cargamos el módulo para evitar errores si no conocemos el nombre exacto de la clase interna.

provider_registry = loader.load_node("provider_registry", "src.services.provider_registry")
radar = loader.load_node("radar", "src.services.radar")
anima = loader.load_node("anima", "src.services.anima")
developer = loader.load_node("developer", "src.services.developer")
brand = loader.load_node("brand", "src.services.brand_service")
motion = loader.load_node("motion", "src.services.motion_service", "MotionService")
connector_registry = loader.load_node("connector_registry", "src.services.connector_registry", "ConnectorRegistry")


# 5. Registro de Rutas (Routers) con Aislamiento de Fallos
def register_router(app, router, prefix, tags):
    """
    Registra un router garantizando idempotencia.
    El proceso padre y el worker hijo comparten el mismo objeto `app` en
    memoria durante el ciclo de reload, lo que causaba doble registro.
    Verificamos si el prefix ya está presente antes de incluir.
    """
    try:
        existing_prefixes = {r.path for r in app.routes if hasattr(r, "path")}
        if prefix in existing_prefixes:
            logger.debug(f"⏭️  [ROUTES] Router '{tags[0]}' ya registrado en {prefix} — omitiendo.")
            return
        app.include_router(router, prefix=prefix, tags=tags)
        logger.info(f"✅ [ROUTES] Router '{tags[0]}' registrado en {prefix}")
    except Exception as e:
        logger.error(f"❌ [ROUTES] Fallo al registrar {prefix}: {e}")

try:
    from src.routes import anima as anima_routes
    register_router(app, anima_routes.router, "/anima", ["Anima"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Anima: {e}")
    raise e

try:
    from src.routes import nexus as nexus_routes
    register_router(app, nexus_routes.router, "/nexus", ["Nexus"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Nexus: {e}")
    raise e

try:
    from src.routes import providers as provider_routes
    register_router(app, provider_routes.router, "/providers", ["Providers"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Providers: {e}")
    raise e

try:
    from src.routes import radar as radar_routes
    register_router(app, radar_routes.router, "/radar", ["Radar"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Radar: {e}")
    raise e

try:
    from src.routes import storage as storage_routes
    register_router(app, storage_routes.router, "/storage", ["Storage"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Storage: {e}")
    raise e

try:
    from src.routes import developer as developer_routes
    register_router(app, developer_routes.router, "/api/developer", ["Developer"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Developer: {e}")
    raise e

try:
    from src.routes import brand as brand_routes
    register_router(app, brand_routes.router, "/brand", ["Brand"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Brand: {e}")
    raise e

try:
    from src.routes import veoscope as veoscope_routes
    register_router(app, veoscope_routes.router, "/veoscope", ["Veoscope"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Veoscope: {e}")
    raise e

try:
    from src.routes import connectors as connectors_routes
    register_router(app, connectors_routes.router, "/connectors", ["Connectors"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Connectors: {e}")
    raise e

try:
    from src.routes import motion as motion_routes
    register_router(app, motion_routes.router, "/motion", ["Motion"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Motion: {e}")
    raise e

try:
    from src.routes import noticias as noticias_routes
    register_router(app, noticias_routes.router, "/noticias", ["Noticias"])
except Exception as e:
    logger.error(f"❌ [ROUTES ERROR] No se pudo cargar Noticias: {e}")
    raise e


# --- ENDPOINTS GLOBALES ---

@app.get("/")
async def root():
    """Health Check del Sistema Operativo."""
    return {
        "system": "ALEGRIA OS",
        "status": "operational",
        "version": "2.0.0",
        "architecture": "Outside-In",
        "sovereignty": "Active"
    }

@app.get("/status")
async def system_status():
    """
    Retorna el estado real de los nodos cargados.
    """
    status_report = {}
    for name, node in loader.nodes.items():
        if isinstance(node, GhostNode):
            status_report[name] = {"status": "ghost", "error": node.error}
        else:
            status_report[name] = {"status": "active"}
    
    return {
        "system": "running",
        "nodes": status_report
    }

# --- MIDDLEWARE & GLOBALS ---

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura cualquier error no controlado y lo entrega como JSON para evitar SyntaxError en el front."""
    logger.error(f"💥 [GLOBAL ERROR] {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": f"Error interno en el ALEGRIA OS: {str(exc)}",
            "path": request.url.path,
            "type": type(exc).__name__
        }
    )

# --- ARRANQUE INTELIGENTE ---

if __name__ == "__main__":
    # sys.path ya fue resuelto a nivel de módulo (ver bloque FIX al inicio).

    logger.info("🚀 Iniciando ALEGRIA OS Backend...")
    # Ejecutamos uvicorn
    uvicorn.run("src.server:app", host="0.0.0.0", port=8000, reload=True)