"""
ALEGR-IA Server
===============
API principal del sistema operativo ALEGR-IA.
Sistema de proveedores dinámicos.
"""

import sys
import importlib
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ALEGRIA_CORE")


# --- ARQUITECTURA DE NODOS RESILIENTES ---
class GhostNode:
    """Nodo fantasma para manejar fallos gracefully."""
    
    def __init__(self, name: str, error: str):
        self.name = name
        self.error = error
        self.is_ghost = True

    def __getattr__(self, method_name):
        def ghost_method(*args, **kwargs):
            logger.warning(
                f"👻 [GHOST] {self.name}.{method_name} no disponible. Error: {self.error}"
            )
            return {
                "status": "degraded",
                "node": self.name,
                "error": self.error
            }
        return ghost_method


class NodeLoader:
    """Cargador dinámico de nodos del sistema."""
    
    def __init__(self):
        self.nodes: Dict[str, Any] = {}

    def load(self, module_name: str, internal_name: str):
        try:
            module = importlib.import_module(f"src.services.{module_name}")
            importlib.reload(module)
            self.nodes[internal_name] = module
            logger.info(f"✅ [NODE UP] {internal_name.upper()} conectado.")
        except Exception as e:
            logger.error(f"❌ [NODE DOWN] Fallo {internal_name}: {e}")
            self.nodes[internal_name] = GhostNode(internal_name, str(e))


# --- INICIALIZACIÓN ---
app = FastAPI(title="ALEGRIA Anima OS v2.0 - Soberano")

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
system.load("provider_registry", "providers")  # NUEVO
system.load("anima", "anima")

# --- CONEXIÓN SINÁPTICA ---
# Gateway -> Dependencies
if (
    not getattr(system.nodes.get("gateway"), "is_ghost", True)
    and not getattr(system.nodes.get("dependencies"), "is_ghost", True)
):
    system.nodes["gateway"].service.set_dependency_manager(
        system.nodes["dependencies"]
    )

# Anima -> ProviderRegistry
if (
    not getattr(system.nodes.get("anima"), "is_ghost", True)
    and not getattr(system.nodes.get("providers"), "is_ghost", True)
):
    system.nodes["anima"].service.set_provider_registry(
        system.nodes["providers"].service
    )


# --- MODELOS DE REQUEST ---
class CreateRequest(BaseModel):
    module_name: str
    description: str
    tech_tags: str = "python"


class ChatRequest(BaseModel):
    message: str


class AddProviderRequest(BaseModel):
    provider: str
    api_key: str
    model: Optional[str] = None
    endpoint: Optional[str] = None


class SelectProviderRequest(BaseModel):
    provider: str
    model: Optional[str] = None


# --- ENDPOINTS BASE ---
@app.get("/")
def root():
    return {
        "status": "Operational",
        "system": "ALEGRIA Anima OS v2.0",
        "mode": "Soberano",
        "message": "Sistema independiente de proveedor"
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
        raise HTTPException(status_code=503, detail="Developer no disponible")
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
        raise HTTPException(status_code=503, detail="Anima no disponible")

    return await anima.service.respond(
        message=r.message,
        nexus=nexus,
        radar=radar
    )


# --- PROVEEDORES DINÁMICOS ---
@app.get("/providers")
def list_providers():
    """Lista proveedores configurados."""
    providers = system.nodes.get("providers")
    if getattr(providers, "is_ghost", False):
        return {"providers": [], "error": "Registry no disponible"}
    return {"providers": providers.service.list_providers()}


@app.get("/providers/active")
def get_active_provider():
    """Retorna el proveedor activo."""
    providers = system.nodes.get("providers")
    if getattr(providers, "is_ghost", False):
        return {"active": None, "error": "Registry no disponible"}
    
    active = providers.service.get_active()
    if active:
        # No exponer la API key completa
        active["api_key"] = "***" + active["api_key"][-4:] if active.get("api_key") else None
    return {"active": active}


@app.post("/providers/add")
def add_provider(r: AddProviderRequest):
    """Agrega un nuevo proveedor."""
    providers = system.nodes.get("providers")
    if getattr(providers, "is_ghost", False):
        raise HTTPException(status_code=503, detail="Registry no disponible")
    
    result = providers.service.add_provider(
        name=r.provider,
        api_key=r.api_key,
        endpoint=r.endpoint,
        models=[r.model] if r.model else None,
        is_local=(r.provider.lower() == "ollama")
    )
    
    # Refrescar Anima
    anima = system.nodes.get("anima")
    if not getattr(anima, "is_ghost", False):
        anima.service._refresh_adapter()
    
    return result


@app.post("/providers/select")
def select_provider(r: SelectProviderRequest):
    """Selecciona el proveedor activo."""
    providers = system.nodes.get("providers")
    if getattr(providers, "is_ghost", False):
        raise HTTPException(status_code=503, detail="Registry no disponible")
    
    result = providers.service.select_provider(r.provider, r.model)
    
    # Refrescar Anima
    anima = system.nodes.get("anima")
    if not getattr(anima, "is_ghost", False):
        anima.service._refresh_adapter()
    
    return result


@app.delete("/providers/{provider_name}")
def remove_provider(provider_name: str):
    """Elimina un proveedor."""
    providers = system.nodes.get("providers")
    if getattr(providers, "is_ghost", False):
        raise HTTPException(status_code=503, detail="Registry no disponible")
    
    return providers.service.remove_provider(provider_name)


# --- RADAR ---
@app.get("/radar/modelos-gratuitos")
def radar_modelos_gratuitos():
    """Descubre modelos gratuitos."""
    radar = system.nodes.get("radar")
    if getattr(radar, "is_ghost", False):
        return {"error": "Radar no disponible", "models": []}
    return radar.service.descubrir_modelos_gratuitos()


@app.get("/radar/providers")
def radar_discover_providers():
    """Descubre proveedores disponibles via RADAR."""
    radar = system.nodes.get("radar")
    if getattr(radar, "is_ghost", False):
        return {"error": "Radar no disponible", "providers": []}
    
    # Lista de proveedores conocidos con info
    known_providers = [
        {
            "name": "groq",
            "display_name": "Groq Cloud",
            "description": "Modelos LLM ultrarrápidos, tier gratuito generoso",
            "free_tier": True,
            "models": [
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "mixtral-8x7b-32768",
                "gemma2-9b-it"
            ],
            "signup_url": "https://console.groq.com"
        },
        {
            "name": "openai",
            "display_name": "OpenAI",
            "description": "GPT-4, GPT-3.5 y más",
            "free_tier": False,
            "models": [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ],
            "signup_url": "https://platform.openai.com"
        },
        {
            "name": "gemini",
            "display_name": "Google Gemini",
            "description": "Gemini Pro y Flash, tier gratuito disponible",
            "free_tier": True,
            "models": [
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash",
                "gemini-1.5-pro"
            ],
            "signup_url": "https://aistudio.google.com"
        },
        {
            "name": "ollama",
            "display_name": "Ollama (Local)",
            "description": "Modelos locales, sin API key requerida",
            "free_tier": True,
            "is_local": True,
            "models": [
                "llama3.2",
                "mistral",
                "mixtral",
                "phi3"
            ],
            "signup_url": "https://ollama.ai"
        }
    ]
    
    return {
        "status": "ok",
        "providers": known_providers
    }


# --- BOOT ---
if __name__ == "__main__":
    import uvicorn
    print("🚀 [ALEGR-IA] Sistema Soberano iniciando en 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
