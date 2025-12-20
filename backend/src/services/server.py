import sys
import importlib
import logging
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ALEGRIA_CORE")

# --- ARQUITECTURA DE NODOS RESILIENTES ---
class GhostNode:
    def __init__(self, name: str, error: str):
        self.name = name
        self.error = error
        self.is_ghost = True

    def __getattr__(self, method_name):
        def ghost_method(*args, **kwargs):
            logger.warning(
                f"👻 [GHOST] {self.name}.{method_name} no disponible. Error original: {self.error}"
            )
            return {
                "status": "degraded",
                "node": self.name,
                "error": self.error
            }
        return ghost_method


class NodeLoader:
    def __init__(self):
        self.nodes: Dict[str, Any] = {}

    def load(self, module_name: str, internal_name: str):
        try:
            module = importlib.import_module(f"src.services.{module_name}")
            importlib.reload(module)  # Recarga en caliente
            self.nodes[internal_name] = module
            logger.info(f"✅ [NODE UP] {internal_name.upper()} conectado.")
        except Exception as e:
            logger.error(f"❌ [NODE DOWN] Fallo {internal_name}: {e}")
            self.nodes[internal_name] = GhostNode(internal_name, str(e))


# --- INICIALIZACIÓN ---
app = FastAPI(title="ALEGRIA Anima OS v1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

system = NodeLoader()

# --- CARGA DE NODOS (ORDEN CRÍTICO) ---
system.load("developer", "developer")
system.load("dependency_manager", "dependencies")
system.load("world_gateway", "gateway")
system.load("nexus", "nexus")
system.load("radar", "radar")
system.load("anima", "anima")

# --- CONEXIÓN SINÁPTICA GATEWAY -> DEPENDENCIES ---
if (
    not getattr(system.nodes.get("gateway"), "is_ghost", True)
    and not getattr(system.nodes.get("dependencies"), "is_ghost", True)
):
    system.nodes["gateway"].service.set_dependency_manager(
        system.nodes["dependencies"]
    )

# --- MODELOS DE REQUEST ---
class CreateRequest(BaseModel):
    module_name: str
    description: str
    tech_tags: str = "python"


class ChatRequest(BaseModel):
    message: str


# --- ENDPOINTS BASE ---
@app.get("/")
def root():
    return {
        "status": "Operational",
        "system": "ALEGRIA Anima OS",
        "mode": "Genesis"
    }


@app.get("/system/status")
def status():
    return {
        k: ("broken" if getattr(v, "is_ghost", False) else "active")
        for k, v in system.nodes.items()
    }


# --- DEVELOPER ---
@app.post("/developer/create")
async def create_node(r: CreateRequest):
    dev = system.nodes.get("developer")
    if getattr(dev, "is_ghost", False):
        return {"error": "Developer is Ghost"}
    return await dev.service.generate_and_write(
        r.module_name, r.description, r.tech_tags
    )


# --- CHAT (SINAPSIS PRINCIPAL) ---
@app.post("/chat")
async def chat(r: ChatRequest):
    anima = system.nodes.get("anima")
    nexus = system.nodes.get("nexus")
    radar = system.nodes.get("radar")

    if getattr(anima, "is_ghost", False):
        return {"error": "Anima no disponible"}

    return await anima.service.respond(
        message=r.message,
        nexus=nexus,
        radar=radar
    )


# --- RADAR ---
@app.get("/radar/modelos-gratuitos")
def radar_modelos_gratuitos():
    radar = system.nodes.get("radar")
    if getattr(radar, "is_ghost", False):
        return {"error": "Radar no disponible"}
    return radar.service.descubrir_modelos_gratuitos()


# --- BOOT ---
if __name__ == "__main__":
    import uvicorn
    print("🚀 [ANIMA] Escuchando en toda la red local (0.0.0.0:8000)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
