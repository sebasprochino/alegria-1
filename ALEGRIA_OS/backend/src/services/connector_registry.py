"""
PANEL DE CONECTORES — src/services/connector_registry.py
=========================================================
El único lugar donde el sistema sabe qué puede hacer y qué no.

REGLA DE ORO:
Si un conector no está activo, el sistema NO falla.
Simplemente no lo usa.

El panel no ejecuta. El panel no piensa. El panel declara presencia.

Integración ALEGRIA_OS:
 - Singleton accesible vía get_connector_registry()
 - Persiste en backend/data/connectors.json
 - Compatible con la consulta de VEOSCOPE y demás agentes:
       from src.services.connector_registry import get_connector_registry
       registry = get_connector_registry()
       if registry.is_available("vision"): ...

Author: Sebastián Fernández
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("CONNECTORS")


# ─── Enumeraciones ────────────────────────────────────────────────────────────


class ConnectorType(str, Enum):
    """Tipos de capacidades que un conector puede habilitar."""
    CHAT     = "chat"
    AUDIO    = "audio"
    VISION   = "vision"
    IMAGE    = "image"
    VIDEO    = "video"
    TOOLS    = "tools"
    MEMORY   = "memory"
    SEARCH   = "search"
    CALENDAR = "calendar"
    STORAGE  = "storage"
    PUBLISH  = "publish"


class ConnectorState(str, Enum):
    """Estados válidos de un conector."""
    ACTIVE   = "active"
    INACTIVE = "inactive"
    ERROR    = "error"


# ─── Dataclass ────────────────────────────────────────────────────────────────


@dataclass
class Connector:
    """
    Contrato mínimo de un conector.

    Campos:
      id          → Nombre lógico único (chat, vision, audio, …)
      tipo        → Qué habilita (ConnectorType)
      endpoint    → Dirección lógica o URL (local o externa)
      estado      → active / inactive / error
      notas       → Uso previsto, legible por humanos
      provider_id → Referencia al proveedor activo (opcional)
      created_at  → ISO timestamp de creación

    Nada más. Cualquier campo extra es sospechoso.
    """
    id:          str
    tipo:        ConnectorType
    endpoint:    str
    estado:      ConnectorState = ConnectorState.INACTIVE
    notas:       str = ""
    provider_id: Optional[str] = None
    created_at:  str = field(default_factory=lambda: datetime.now().isoformat())

    def is_active(self) -> bool:
        return self.estado == ConnectorState.ACTIVE


# ─── Registry ─────────────────────────────────────────────────────────────────


class ConnectorRegistry:
    """
    Panel de Conectores — Registro central de capacidades.

    El sistema lee de acá. Nada decide desde acá.

    Reglas constitucionales:
     - Ningún agente puede ASUMIR la existencia de un conector.
     - Todo agente DEBE consultar el Panel antes de actuar.
     - Si un conector no está activo, el sistema sigue operando.
    """

    # Ruta por defecto, anclade al directorio backend/
    _DEFAULT_PATH = (
        Path(__file__).resolve().parents[2] / "data" / "connectors.json"
    )

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._DEFAULT_PATH
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        self.connectors: Dict[str, Connector] = {}
        self._init_default_connectors()
        self._load_config()

        logger.info("🔌 [CONNECTORS] Panel de Conectores inicializado")

    # ─── Bootstrapping ────────────────────────────────────────────────────────

    def _init_default_connectors(self) -> None:
        """Inicializa el conjunto base de conectores en estado INACTIVE."""
        defaults = [
            Connector(id="chat",    tipo=ConnectorType.CHAT,    endpoint="/api/chat",
                      notas="Comunicación con LLMs"),
            Connector(id="audio",   tipo=ConnectorType.AUDIO,   endpoint="/api/audio",
                      notas="Procesamiento de audio"),
            Connector(id="vision",  tipo=ConnectorType.VISION,  endpoint="/veoscope/analyze",
                      notas="Análisis visual (VEOSCOPE)"),
            Connector(id="image",   tipo=ConnectorType.IMAGE,   endpoint="/api/image",
                      notas="Generación de imágenes"),
            Connector(id="video",   tipo=ConnectorType.VIDEO,   endpoint="/api/video",
                      notas="Procesamiento de video"),
            Connector(id="tools",   tipo=ConnectorType.TOOLS,   endpoint="/api/tools",
                      notas="Herramientas externas"),
            Connector(id="memory",  tipo=ConnectorType.MEMORY,  endpoint="/api/memory",
                      notas="Memoria persistente"),
            Connector(id="search",  tipo=ConnectorType.SEARCH,  endpoint="/api/search",
                      notas="Búsqueda web"),
            Connector(id="storage", tipo=ConnectorType.STORAGE, endpoint="/storage",
                      notas="Almacenamiento de archivos"),
            Connector(id="publish", tipo=ConnectorType.PUBLISH, endpoint="/api/publish",
                      notas="Publicación en canales externos"),
        ]
        for conn in defaults:
            self.connectors[conn.id] = conn

    # ─── Persistencia ─────────────────────────────────────────────────────────

    def _load_config(self) -> None:
        """Carga y fusiona el estado persistido sobre los defaults."""
        if not self.config_path.exists():
            return
        try:
            raw = json.loads(self.config_path.read_text(encoding="utf-8"))
            for conn_id, conn_data in raw.get("connectors", {}).items():
                # Normalizar enums (aceptar string o valor)
                conn_data["tipo"]   = ConnectorType(conn_data["tipo"])
                conn_data["estado"] = ConnectorState(conn_data["estado"])
                self.connectors[conn_id] = Connector(**conn_data)
            logger.debug(f"[CONNECTORS] {len(self.connectors)} conectores cargados.")
        except Exception as e:
            logger.warning(f"[CONNECTORS] Error cargando config: {e}. Usando defaults.")

    def _save_config(self) -> None:
        """Persiste el estado actual en JSON."""
        try:
            data = {
                "connectors": {
                    k: {
                        **asdict(v),
                        "tipo":   v.tipo.value,
                        "estado": v.estado.value,
                    }
                    for k, v in self.connectors.items()
                }
            }
            self.config_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"[CONNECTORS] Error guardando config: {e}")

    # ─── Consultas (API para agentes) ─────────────────────────────────────────

    def is_available(self, connector_id: str) -> bool:
        """
        Consulta principal de los agentes.
        Retorna True sólo si el conector existe Y está activo.
        """
        conn = self.connectors.get(connector_id)
        return conn is not None and conn.is_active()

    def get_connector(self, connector_id: str) -> Optional[Connector]:
        """Obtiene el objeto Connector, o None si no existe."""
        return self.connectors.get(connector_id)

    def get_endpoint(self, connector_id: str) -> Optional[str]:
        """Retorna el endpoint de un conector activo, o None."""
        conn = self.connectors.get(connector_id)
        return conn.endpoint if (conn and conn.is_active()) else None

    def list_active(self) -> List[Dict[str, Any]]:
        """Lista todos los conectores activos como dicts serializables."""
        return [
            {**asdict(c), "tipo": c.tipo.value, "estado": c.estado.value}
            for c in self.connectors.values()
            if c.is_active()
        ]

    def list_all(self) -> List[Dict[str, Any]]:
        """Lista todos los conectores (activos e inactivos) como dicts."""
        return [
            {**asdict(c), "tipo": c.tipo.value, "estado": c.estado.value}
            for c in self.connectors.values()
        ]

    # ─── Gestión (API para el Panel / Developer) ──────────────────────────────

    def activate(self, connector_id: str, provider_id: Optional[str] = None) -> Dict[str, Any]:
        """Activa un conector. Opcionalmente vincula al proveedor activo."""
        conn = self.connectors.get(connector_id)
        if not conn:
            return {"status": "error", "message": f"Conector '{connector_id}' no existe"}

        conn.estado = ConnectorState.ACTIVE
        if provider_id:
            conn.provider_id = provider_id

        self._save_config()
        logger.info(f"✅ [CONNECTORS] '{connector_id}' activado")
        return {"status": "ok", "connector": connector_id, "estado": "active"}

    def deactivate(self, connector_id: str) -> Dict[str, Any]:
        """Desactiva un conector."""
        conn = self.connectors.get(connector_id)
        if not conn:
            return {"status": "error", "message": f"Conector '{connector_id}' no existe"}

        conn.estado = ConnectorState.INACTIVE
        self._save_config()
        logger.info(f"⏸️  [CONNECTORS] '{connector_id}' desactivado")
        return {"status": "ok", "connector": connector_id, "estado": "inactive"}

    def add_connector(
        self,
        connector_id: str,
        tipo: str,
        endpoint: str,
        notas: str = "",
    ) -> Dict[str, Any]:
        """Agrega un nuevo conector personalizado."""
        if connector_id in self.connectors:
            return {"status": "error", "message": f"Conector '{connector_id}' ya existe"}

        try:
            tipo_enum = ConnectorType(tipo)
        except ValueError:
            validos = [t.value for t in ConnectorType]
            return {"status": "error", "message": f"Tipo '{tipo}' inválido. Válidos: {validos}"}

        self.connectors[connector_id] = Connector(
            id=connector_id, tipo=tipo_enum, endpoint=endpoint, notas=notas
        )
        self._save_config()
        logger.info(f"➕ [CONNECTORS] '{connector_id}' agregado")
        return {"status": "ok", "connector": connector_id}

    def remove_connector(self, connector_id: str) -> Dict[str, Any]:
        """Elimina un conector. Los conectores del sistema base no deberían eliminarse."""
        if connector_id not in self.connectors:
            return {"status": "error", "message": f"Conector '{connector_id}' no existe"}

        del self.connectors[connector_id]
        self._save_config()
        logger.info(f"➖ [CONNECTORS] '{connector_id}' eliminado")
        return {"status": "ok", "connector": connector_id}

    def update_endpoint(self, connector_id: str, endpoint: str) -> Dict[str, Any]:
        """Actualiza el endpoint de un conector existente."""
        conn = self.connectors.get(connector_id)
        if not conn:
            return {"status": "error", "message": f"Conector '{connector_id}' no existe"}

        conn.endpoint = endpoint
        self._save_config()
        return {"status": "ok", "connector": connector_id, "endpoint": endpoint}

    def clone_connector(self, source_id: str, new_id: str) -> Dict[str, Any]:
        """
        Clona un conector para pruebas.

        Patrón recomendado: clonar → probar → reemplazar si funciona.
        El clon empieza siempre INACTIVE.
        """
        source = self.connectors.get(source_id)
        if not source:
            return {"status": "error", "message": f"Conector '{source_id}' no existe"}

        if new_id in self.connectors:
            return {"status": "error", "message": f"Conector '{new_id}' ya existe"}

        self.connectors[new_id] = Connector(
            id=new_id,
            tipo=source.tipo,
            endpoint=source.endpoint,
            estado=ConnectorState.INACTIVE,
            notas=f"Clon de '{source_id}'",
        )
        self._save_config()
        logger.info(f"📋 [CONNECTORS] '{source_id}' clonado → '{new_id}'")
        return {"status": "ok", "source": source_id, "clone": new_id}

    def set_error(self, connector_id: str, reason: str = "") -> Dict[str, Any]:
        """Marca un conector en estado ERROR (para diagnóstico del sistema)."""
        conn = self.connectors.get(connector_id)
        if not conn:
            return {"status": "error", "message": f"Conector '{connector_id}' no existe"}

        conn.estado = ConnectorState.ERROR
        if reason:
            conn.notas = f"[ERROR] {reason}"
        self._save_config()
        logger.warning(f"❌ [CONNECTORS] '{connector_id}' marcado como ERROR: {reason}")
        return {"status": "ok", "connector": connector_id, "estado": "error"}


# ─── Singleton ────────────────────────────────────────────────────────────────

_registry_instance: Optional[ConnectorRegistry] = None


def get_connector_registry() -> ConnectorRegistry:
    """
    Acceso soberano al singleton del Panel de Conectores.

    Uso desde cualquier agente o servicio:
        from src.services.connector_registry import get_connector_registry
        registry = get_connector_registry()
        if registry.is_available("vision"):
            endpoint = registry.get_endpoint("vision")
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ConnectorRegistry()
    return _registry_instance
