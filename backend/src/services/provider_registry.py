"""
ALEGR-IA Provider Registry
===========================
Registro central de proveedores LLM dinámicos.
Permite agregar, eliminar y seleccionar proveedores en runtime.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger("ALEGRIA_PROVIDERS")

# Ruta de persistencia
CONFIG_PATH = Path(__file__).parent.parent.parent / "provider_config.json"


@dataclass
class ProviderConfig:
    """Configuración de un proveedor."""
    name: str
    api_key: str
    endpoint: Optional[str] = None
    models: Optional[List[str]] = None
    is_active: bool = False
    is_local: bool = False  # Para Ollama


class ProviderRegistry:
    """
    Registro soberano de proveedores.
    
    ALEGR-IA no depende de ningún proveedor por defecto.
    Todo se agrega dinámicamente.
    """
    
    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}
        self.active_provider: Optional[str] = None
        self.active_model: Optional[str] = None
        self._load_config()
    
    def _load_config(self):
        """Carga configuración persistida."""
        try:
            if CONFIG_PATH.exists():
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                for name, cfg in data.get("providers", {}).items():
                    self.providers[name] = ProviderConfig(**cfg)
                self.active_provider = data.get("active_provider")
                self.active_model = data.get("active_model")
                logger.info(f"📦 Cargados {len(self.providers)} proveedores")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo cargar config: {e}")
    
    def _save_config(self):
        """Persiste configuración."""
        try:
            data = {
                "providers": {k: asdict(v) for k, v in self.providers.items()},
                "active_provider": self.active_provider,
                "active_model": self.active_model
            }
            CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
            logger.info("💾 Configuración guardada")
        except Exception as e:
            logger.error(f"❌ Error guardando config: {e}")
    
    def add_provider(self, name: str, api_key: str, 
                     endpoint: str = None, models: List[str] = None,
                     is_local: bool = False) -> dict:
        """Agrega un nuevo proveedor."""
        name_lower = name.lower()
        
        self.providers[name_lower] = ProviderConfig(
            name=name_lower,
            api_key=api_key,
            endpoint=endpoint,
            models=models or [],
            is_local=is_local
        )
        
        # Si es el primero, activarlo automáticamente
        if len(self.providers) == 1:
            self.active_provider = name_lower
            self.providers[name_lower].is_active = True
        
        self._save_config()
        logger.info(f"✅ Proveedor '{name_lower}' agregado")
        
        return {"status": "ok", "provider": name_lower}
    
    def remove_provider(self, name: str) -> dict:
        """Elimina un proveedor."""
        name_lower = name.lower()
        
        if name_lower not in self.providers:
            return {"status": "error", "message": f"Proveedor '{name}' no existe"}
        
        del self.providers[name_lower]
        
        if self.active_provider == name_lower:
            self.active_provider = None
            self.active_model = None
        
        self._save_config()
        return {"status": "ok", "message": f"Proveedor '{name}' eliminado"}
    
    def select_provider(self, name: str, model: str = None) -> dict:
        """Selecciona el proveedor activo."""
        name_lower = name.lower()
        
        if name_lower not in self.providers:
            return {"status": "error", "message": f"Proveedor '{name}' no configurado"}
        
        # Desactivar el anterior
        if self.active_provider and self.active_provider in self.providers:
            self.providers[self.active_provider].is_active = False
        
        # Activar el nuevo
        self.active_provider = name_lower
        self.active_model = model
        self.providers[name_lower].is_active = True
        
        self._save_config()
        logger.info(f"🎯 Proveedor activo: {name_lower}" + (f" modelo: {model}" if model else ""))
        
        return {
            "status": "ok",
            "active_provider": name_lower,
            "active_model": model
        }
    
    def get_active(self) -> Optional[dict]:
        """Retorna el proveedor y modelo activo."""
        if not self.active_provider:
            return None
        
        provider = self.providers.get(self.active_provider)
        if not provider:
            return None
        
        return {
            "provider": self.active_provider,
            "model": self.active_model,
            "api_key": provider.api_key,
            "endpoint": provider.endpoint,
            "is_local": provider.is_local
        }
    
    def list_providers(self) -> List[dict]:
        """Lista todos los proveedores configurados."""
        return [
            {
                "name": p.name,
                "is_active": p.is_active,
                "is_local": p.is_local,
                "models": p.models,
                "has_key": bool(p.api_key)
            }
            for p in self.providers.values()
        ]
    
    def get_provider_config(self, name: str) -> Optional[ProviderConfig]:
        """Obtiene configuración completa de un proveedor."""
        return self.providers.get(name.lower())


# Instancia global (requerida por NodeLoader)
service = ProviderRegistry()
