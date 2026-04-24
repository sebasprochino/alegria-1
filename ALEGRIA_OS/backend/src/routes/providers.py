# Provider Routes - Exposición HTTP del ProviderRegistry
from fastapi import APIRouter
from src.services.provider_registry import service as provider_service

router = APIRouter(tags=["providers"])


@router.get("")
def list_providers():
    """Lista todos los proveedores configurados."""
    return {"providers": provider_service.list_providers()}


@router.get("/active")
def get_active_provider():
    """Retorna el proveedor activo actual."""
    active = provider_service.get_active()
    return {"active": active}


@router.post("/add")
async def add_provider(payload: dict):
    """Agrega un nuevo proveedor."""
    model = payload.get("model")
    return await provider_service.add_provider(
        provider_type=payload.get("provider"),
        api_key=payload.get("api_key"),
        alias=payload.get("alias"),
        models=[model] if model else [],
        endpoint=payload.get("endpoint"),
        is_local=payload.get("is_local", False)
    )


@router.post("/select")
def select_provider(payload: dict):
    """Selecciona un proveedor y opcionalmente un modelo."""
    provider_id = payload.get("id") or payload.get("provider")  # Compatibilidad
    model = payload.get("model")
    return provider_service.select_provider(provider_id, model)


@router.post("/refresh")
async def refresh_models(payload: dict = None):
    """Actualiza la lista de modelos usando Radar."""
    provider_id = payload.get("id") if payload else None
    return await provider_service.discover_and_update_models(provider_id)


@router.post("/toggle")
def toggle_provider(payload: dict):
    """Activa o desactiva un proveedor de la cascada pool."""
    provider_id = payload.get("id")
    active = payload.get("active", True)
    return provider_service.toggle_provider(provider_id, active)


@router.patch("/{provider_id}/priority")
def update_priority(provider_id: str, payload: dict):
    """Actualiza la prioridad de un proveedor (menor = más prioritario)."""
    priority = payload.get("priority", 10)
    if provider_id not in provider_service.providers:
        return {"status": "error", "message": "Proveedor no existe"}
    
    provider_service.providers[provider_id].priority = int(priority)
    provider_service._save_config()
    return {"status": "ok", "priority": priority}


@router.delete("/{provider_id}")
def remove_provider(provider_id: str):
    """Elimina un proveedor."""
    return provider_service.remove_provider(provider_id)
