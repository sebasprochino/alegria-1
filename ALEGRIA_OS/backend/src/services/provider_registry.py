"""
REGISTRO DE PROVEEDORES — src/services/provider_registry.py
============================================================
Los proveedores NO son parte del sistema.
Son recursos intercambiables conectados a través de contratos abstractos.

El sistema no depende de ellos, los utiliza cuando conviene.

Para ALEGR-IA:
 - "OpenAI" no existe
 - "Gemini" no existe
 - "Claude" no existe

Solo existe: Conector CHAT, Conector IMAGE, etc.

────────────────────────────────────────────────────────────
SECCIÓN A: Arquitectura limpia (nueva)
SECCIÓN B: Capa de integración — métodos requeridos por el
           sistema existente (anima, developer, veoscanner…)
           Estos métodos DELEGAN a la arquitectura limpia y
           NO dupliquen lógica.
────────────────────────────────────────────────────────────

Author: Sebastián Fernández
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("PROVIDERS")

# ─── SECCIÓN A: Arquitectura limpia ──────────────────────────────────────────


class ProviderType(str, Enum):
    """Tipos de proveedores soportados. Hereda str para serialización directa."""
    OPENAI      = "openai"
    ANTHROPIC   = "anthropic"
    GEMINI      = "gemini"
    GROQ        = "groq"
    OLLAMA      = "ollama"
    CLAUDE      = "claude"        # alias legacy para anthropic
    FIREWORKS   = "fireworks"
    HUGGINGFACE = "huggingface"
    CUSTOM      = "custom"


@dataclass
class Provider:
    """
    Configuración de un proveedor.

    El proveedor es un DETALLE DE IMPLEMENTACIÓN,
    no una entidad del sistema.
    """
    id:            str
    provider_type: ProviderType
    alias:         str
    api_key:       str = ""
    endpoint:      Optional[str] = None
    models:        List[str] = field(default_factory=list)
    is_active:     bool = False
    is_local:      bool = False
    priority:      int = 10
    timeout_ms:    int = 30000
    created_at:    str = field(default_factory=lambda: datetime.now().isoformat())


class ProviderRegistry:
    """
    Registro de Proveedores.

    Los proveedores viven DEBAJO de los conectores.
    Los agentes NUNCA hablan directamente con proveedores.

    Flujo correcto:
        Agente → Conector → Proveedor activo

    El proveedor puede cambiar sin que el agente se entere.
    """

    # Mapeo: ProviderType → (ENV_VAR, modelo_default)
    ENV_VARS: Dict[ProviderType, tuple] = {
        ProviderType.GROQ:      ("GROQ_API_KEY",      "llama-3.3-70b-versatile"),
        ProviderType.OPENAI:    ("OPENAI_API_KEY",     "gpt-4o-mini"),
        ProviderType.GEMINI:    ("GEMINI_API_KEY",     "gemini-2.0-flash-exp"),
        ProviderType.ANTHROPIC: ("ANTHROPIC_API_KEY",  "claude-3-5-sonnet-20241022"),
        ProviderType.CLAUDE:    ("ANTHROPIC_API_KEY",  "claude-3-5-sonnet-20241022"),
    }

    # Ancla de path al directorio backend/ (independiente del cwd)
    _DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "providers.json"

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._DEFAULT_PATH
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        self.providers: Dict[str, Provider] = {}
        self.active_provider_id: Optional[str] = None
        self.active_model: Optional[str] = None

        self._load_config()
        self._inject_env_vars()

        logger.info(f"🔌 [PROVIDERS] Registro inicializado: {len(self.providers)} proveedores")

    # ─── Persistencia ─────────────────────────────────────────────────────────

    def _load_config(self) -> None:
        """Carga el estado persistido, con migración automática desde el formato legacy."""
        if not self.config_path.exists():
            # Intentar migrar desde la ruta legacy (backend/provider_config.json)
            legacy = Path(__file__).resolve().parents[2] / "provider_config.json"
            if legacy.exists():
                self._migrate_legacy(legacy)
            return

        try:
            raw = json.loads(self.config_path.read_text(encoding="utf-8"))

            for prov_data in raw.get("providers", {}).values():
                # Normalizar: acepta tanto dict (nuevo) como formato legacy
                prov_data = dict(prov_data)  # copia defensiva

                # Migrar campos legacy
                if "provider_type" not in prov_data and "name" in prov_data:
                    prov_data["provider_type"] = prov_data.pop("name", "custom")
                if "id" not in prov_data:
                    prov_data["id"] = str(uuid.uuid4())
                if "alias" not in prov_data:
                    prov_data["alias"] = prov_data["provider_type"].capitalize()

                # Convertir enum (acepta str o valor ya normalizado)
                try:
                    prov_data["provider_type"] = ProviderType(
                        str(prov_data["provider_type"]).lower()
                    )
                except ValueError:
                    prov_data["provider_type"] = ProviderType.CUSTOM

                # Eliminar campos que no pertenecen al dataclass
                known = {f.name for f in Provider.__dataclass_fields__.values()}
                prov_data = {k: v for k, v in prov_data.items() if k in known}

                self.providers[prov_data["id"]] = Provider(**prov_data)

            self.active_provider_id = raw.get("active_provider_id")
            self.active_model       = raw.get("active_model")

            # Compat legacy: active_provider era el type string, no un id
            if not self.active_provider_id and raw.get("active_provider"):
                for pid, p in self.providers.items():
                    if p.provider_type.value == raw["active_provider"]:
                        self.active_provider_id = pid
                        break

            logger.debug(f"[PROVIDERS] {len(self.providers)} proveedores cargados.")
        except Exception as e:
            logger.warning(f"[PROVIDERS] Error cargando config: {e}. Se usarán env vars.")

    def _migrate_legacy(self, legacy_path: Path) -> None:
        """Migra el formato legacy (provider_config.json) al nuevo formato."""
        try:
            raw = json.loads(legacy_path.read_text(encoding="utf-8"))
            for key, cfg in raw.get("providers", {}).items():
                new_id = cfg.get("id") or str(uuid.uuid4())
                ptype  = cfg.get("provider_type") or cfg.get("name", key)
                try:
                    ptype_enum = ProviderType(str(ptype).lower())
                except ValueError:
                    ptype_enum = ProviderType.CUSTOM

                self.providers[new_id] = Provider(
                    id=new_id,
                    provider_type=ptype_enum,
                    alias=cfg.get("alias", ptype.capitalize()),
                    api_key=cfg.get("api_key", ""),
                    endpoint=cfg.get("endpoint"),
                    models=cfg.get("models", []),
                    is_active=cfg.get("is_active", False),
                    is_local=cfg.get("is_local", False),
                    priority=cfg.get("priority", 10),
                    timeout_ms=cfg.get("timeout_ms", 30000),
                )

            self.active_provider_id = raw.get("active_provider_id")
            self.active_model       = raw.get("active_model")
            logger.info("[PROVIDERS] Migración desde legacy completada.")
        except Exception as e:
            logger.warning(f"[PROVIDERS] Error migrando legacy: {e}")

    def _save_config(self) -> None:
        """Persiste el estado actual."""
        try:
            data = {
                "providers": {
                    k: {
                        **asdict(v),
                        "provider_type": v.provider_type.value,
                    }
                    for k, v in self.providers.items()
                },
                "active_provider_id": self.active_provider_id,
                "active_model":       self.active_model,
            }
            self.config_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"[PROVIDERS] Error guardando config: {e}")

    def _inject_env_vars(self) -> None:
        """Inyecta proveedores detectados en variables de entorno."""
        for prov_type, (env_var, default_model) in self.ENV_VARS.items():
            # Claude y Anthropic comparten la misma key — evitar duplicados
            if prov_type == ProviderType.CLAUDE:
                continue

            raw_key = os.getenv(env_var)
            if not raw_key:
                continue
            api_key = raw_key.strip()

            # Evitar duplicados por clave O por tipo+key
            exists = any(
                (p.provider_type == prov_type and p.api_key == api_key)
                or (p.api_key == api_key)
                for p in self.providers.values()
            )
            if exists:
                continue

            new_id = str(uuid.uuid4())
            self.providers[new_id] = Provider(
                id=new_id,
                provider_type=prov_type,
                alias=f"{prov_type.value.capitalize()} (env)",
                api_key=api_key,
                models=[default_model],
                is_active=True,
            )

            if not self.active_provider_id:
                self.active_provider_id = new_id
                self.active_model = default_model

            logger.info(f"📌 [PROVIDERS] '{prov_type.value}' inyectado desde {env_var}")

    # ─── Consultas ────────────────────────────────────────────────────────────

    def get_active(self) -> Optional[Provider]:
        """Retorna el Provider activo, o None."""
        if self.active_provider_id and self.active_provider_id in self.providers:
            return self.providers[self.active_provider_id]
        return None

    def get_active_config(self) -> Optional[Dict[str, Any]]:
        """
        Retorna la configuración del proveedor activo como dict listo para adapters.
        Clave para VEOSCOPE y demás agentes que consultan el provider activo.
        """
        p = self.get_active()
        if not p:
            return None
        return {
            "provider_type": p.provider_type.value,
            "api_key":       p.api_key,
            "model":         self.active_model or (p.models[0] if p.models else None),
            "models":        p.models,
            "endpoint":      p.endpoint,
            "timeout_ms":    p.timeout_ms,
            "alias":         p.alias,
        }

    def list_providers(self) -> List[Dict[str, Any]]:
        """Lista todos los proveedores (para el panel de UI)."""
        return [
            {
                "id":            p.id,
                "provider_type": p.provider_type.value,
                "alias":         p.alias,
                "is_active":     p.id == self.active_provider_id,
                "model":         p.models[0] if p.models else None,
                "is_local":      p.is_local,
                "has_key":       bool(p.api_key),
                "priority":      p.priority,
            }
            for p in self.providers.values()
        ]

    def get_cascade_configs(self) -> List[Dict[str, Any]]:
        """
        Configuraciones para la Cascada de Inteligencia, ordenadas por prioridad.
        Retorna dicts (no instancias de adapter) — la cascada construye sus propios adapters.
        """
        active = sorted(
            [p for p in self.providers.values() if p.is_active],
            key=lambda p: p.priority,
        )
        return [
            {
                "provider_type": p.provider_type.value,
                "api_key":       p.api_key,
                "model":         p.models[0] if p.models else None,
                "endpoint":      p.endpoint,
                "timeout_ms":    p.timeout_ms,
                "alias":         p.alias,
            }
            for p in active
        ]

    # ─── Gestión ──────────────────────────────────────────────────────────────

    def add_provider(
        self,
        provider_type: str,
        api_key: str,
        alias: Optional[str] = None,
        endpoint: Optional[str] = None,
        models: Optional[List[str]] = None,
        is_local: bool = False,
    ) -> Dict[str, Any]:
        """Agrega un nuevo proveedor."""
        try:
            prov_type = ProviderType(provider_type.lower())
        except ValueError:
            return {"status": "error", "message": f"Tipo '{provider_type}' no soportado"}

        if not alias:
            count = sum(1 for p in self.providers.values() if p.provider_type == prov_type)
            alias = f"{provider_type.capitalize()} {count + 1}" if count else provider_type.capitalize()

        new_id = str(uuid.uuid4())
        self.providers[new_id] = Provider(
            id=new_id,
            provider_type=prov_type,
            alias=alias,
            api_key=api_key,
            endpoint=endpoint,
            models=models or [],
            is_local=is_local,
            is_active=True,
        )

        if not self.active_provider_id:
            self.active_provider_id = new_id
            if models:
                self.active_model = models[0]

        self._save_config()
        logger.info(f"➕ [PROVIDERS] '{alias}' agregado")
        return {"status": "ok", "id": new_id, "message": f"{alias} configurado."}

    def select_provider(self, provider_id: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Selecciona el proveedor activo."""
        if provider_id not in self.providers:
            return {"status": "error", "message": "Proveedor no existe"}
        self.active_provider_id = provider_id
        if model:
            self.active_model = model
        self._save_config()
        return {"status": "ok"}

    def remove_provider(self, provider_id: str) -> Dict[str, Any]:
        """Elimina un proveedor. Si era el activo, selecciona el siguiente disponible."""
        if provider_id not in self.providers:
            return {"status": "error", "message": "Proveedor no existe"}

        del self.providers[provider_id]

        if self.active_provider_id == provider_id:
            self.active_provider_id = next(iter(self.providers.keys()), None)
            # Reintentar inyección de env vars si quedamos sin activo
            if not self.active_provider_id:
                self._inject_env_vars()

        self._save_config()
        return {"status": "ok"}

    def toggle_provider(self, provider_id: str, active: bool) -> Dict[str, Any]:
        """Activa o desactiva un proveedor de la cascada."""
        if provider_id not in self.providers:
            return {"status": "error", "message": "Proveedor no existe"}
        self.providers[provider_id].is_active = active
        self._save_config()
        return {"status": "ok"}

    # ─── SECCIÓN B: Capa de integración (compat sistema existente) ────────────
    #
    # Estos métodos fueron requeridos por:
    #   anima.py, anima_service.py, developer.py, veoscanner.py,
    #   routes/providers.py, routes/anima.py, routes/routes_anima.py,
    #   os/pipeline/planner.py, os/pipeline/detective.py,
    #   os/creative/evolution/harmonizer.py, os/actions/registry.py
    #
    # NO duplican lógica nueva: delegan a los métodos de la Sección A
    # o a los adapters del SDK existente.
    # ─────────────────────────────────────────────────────────────────────────

    def get_active_provider_config(self) -> Optional[Dict[str, Any]]:
        """
        Alias de get_active_config() para compatibilidad con anima_service.py.
        """
        return self.get_active_config()

    def get_adapter_instance(self):
        """
        Retorna una instancia del adaptador activo lista para usar.
        Usado por developer.py y otros servicios que necesitan un adapter directo.
        """
        p = self.get_active()
        if not p:
            return None
        try:
            from src.services.llm_adapters import get_adapter as _get_adapter_class
            AdapterClass = _get_adapter_class(p.provider_type.value)
            if not AdapterClass:
                return None
            return AdapterClass(
                api_key=p.api_key,
                model=self.active_model or (p.models[0] if p.models else None),
                endpoint=p.endpoint,
            )
        except Exception as e:
            logger.warning(f"[PROVIDERS] Error creando adapter: {e}")
            return None

    def get_adapter(self, provider: str, model: Optional[str] = None):
        """
        Busca y retorna un adaptador instanciado por su tipo (ej: 'groq').
        Usado por veoscanner.py y el registry de acciones.
        """
        target = provider.lower()
        for p in self.providers.values():
            if p.provider_type.value == target and p.api_key:
                try:
                    from src.services.llm_adapters import get_adapter as _get_adapter_class
                    AdapterClass = _get_adapter_class(target)
                    if AdapterClass:
                        return AdapterClass(
                            api_key=p.api_key,
                            model=model or (p.models[0] if p.models else None),
                            endpoint=p.endpoint,
                        )
                except Exception as e:
                    logger.warning(f"[PROVIDERS] Error instanciando adapter '{target}': {e}")
        return None

    def get_cascade_providers(self) -> List[Any]:
        """
        Retorna instancias de adapters activos ordenadas por prioridad.
        Usado por la Cascada de Inteligencia (provider_cascade.py).
        """
        active = sorted(
            [p for p in self.providers.values() if p.is_active],
            key=lambda p: p.priority,
        )
        adapters = []
        for p in active:
            try:
                from src.services.llm_adapters import get_adapter as _get_adapter_class
                AdapterClass = _get_adapter_class(p.provider_type.value)
                if AdapterClass:
                    adapter = AdapterClass(
                        api_key=p.api_key,
                        model=p.models[0] if p.models else None,
                        endpoint=p.endpoint,
                    )
                    # Inyectar metadatos para la cascada
                    adapter.name        = p.alias
                    adapter.provider_id = p.id
                    adapter.priority    = p.priority
                    adapter.timeout_ms  = p.timeout_ms
                    adapters.append(adapter)
            except Exception as e:
                logger.warning(f"[PROVIDERS] Error cargando adapter '{p.alias}': {e}")
        return adapters

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        model: Optional[str] = None,
        modality: Optional[str] = "text",
        **kwargs,
    ) -> str:
        """
        Punto de entrada para conversar con la IA.
        Usa la Cascada de Inteligencia para garantizar resiliencia.
        Mantenido para compatibilidad con anima, planner, detective, harmonizer.
        """
        from src.services.provider_cascade import ProviderCascade
        from src.services.ethical_guard import service as ethical_guard

        adapters = self.get_cascade_providers()

        # --- FILTRADO POR MODALIDAD ---
        if modality == "vision":
            # Si es visión, priorizamos los que tienen 'vision' en el nombre del modelo
            # o pertenecen a gemini/openai (que usualmente soportan visión en sus modelos flash/4o)
            adapters = [
                a for a in adapters 
                if any(kw in str(getattr(a, 'model', '')).lower() for kw in ["vision", "flash", "4o", "gemini"])
            ]

        # --- PREFERENCIA DE MODELO (No exclusividad) ---
        # En lugar de filtrar y dejar solo uno, reordenamos para poner el preferido primero.
        if model and adapters:
            preferred = []
            others = []
            for a in adapters:
                if getattr(a, "model", None) == model:
                    preferred.append(a)
                else:
                    others.append(a)
            
            if preferred:
                adapters = preferred + others
            else:
                # Si no hay match exacto, intentar match parcial por nombre de proveedor
                for a in adapters:
                    p_name = getattr(a, "provider_name", "").lower()
                    if p_name and p_name in model.lower():
                        a.model = model
                        preferred.append(a)
                
                if preferred:
                    adapters = preferred + [a for a in others if a not in preferred]

        if not adapters:
            raise RuntimeError(
                f"No hay proveedores de IA activos"
                + (f" para el modelo '{model}'" if model else "")
            )

        # Preparar prompt
        last_msg = messages[-1]["content"] if messages else ""
        is_multimodal = isinstance(last_msg, list)

        full_prompt = last_msg
        if not is_multimodal and len(messages) > 1:
            history = "\n".join(
                f"{m['role'].upper()}: {m['content']}" for m in messages[:-1]
            )
            full_prompt = f"Historial previo:\n{history}\n\nUSUARIO: {last_msg}"

        cascade = ProviderCascade(providers=adapters, validator=ethical_guard)
        context = {
            "prompt":      full_prompt,
            "system":      system,
            "messages":    messages,
            "temperature": kwargs.get("temperature", 0.7),
        }
        
        try:
            response = await cascade.run(context)
            
            # --- POST-EJECUCIÓN: Auditoría de Fallos para Auto-Disable ---
            if cascade.failed_providers:
                # Si hubo fallos antes del éxito, analizamos si son críticos
                for fail in cascade.failed_providers:
                    err = fail["error"].lower()
                    pid = fail["id"]
                    # 401: Unauthorized, 429: Rate Limit / Billing
                    is_critical = any(kw in err for kw in ["401", "429", "invalid api key", "billing_hard_limit"])
                    
                    if is_critical and pid in self.providers:
                        logger.warning(f"🛡️ [PROVIDERS] Auto-disabling fallido por error crítico: {pid} ({err})")
                        self.providers[pid].is_active = False
                
                # Persistir cambios si hubo desactivaciones
                self._save_config()
                
            return response
            
        except Exception as e:
            # Si TODA la cascada falló, intentamos desactivar el último también si es crítico
            logger.error(f"💀 [PROVIDERS] Fallo catastrófico en cascada: {e}")
            raise e

    async def discover_and_update_models(self, provider_id: Optional[str] = None) -> Dict[str, Any]:
        """Usa Radar para descubrir nuevos modelos. Mantiene compat con provider_registry v1."""
        try:
            from src.services.radar import service as radar_service
            target_type = None
            if provider_id and provider_id in self.providers:
                target_type = self.providers[provider_id].provider_type.value

            findings = radar_service.descubrir_modelos_gratuitos(target_type)
            updated = False
            if findings.get("status") == "ok":
                for finding in findings.get("findings", []):
                    p_type = finding["provider"]
                    new_models = finding.get("models", [])
                    for p in self.providers.values():
                        if p.provider_type.value == p_type:
                            for m in new_models:
                                if m not in p.models:
                                    p.models.append(m)
                                    updated = True
            if updated:
                self._save_config()
            return {"status": "ok", "updated": updated}
        except Exception as e:
            logger.warning(f"[PROVIDERS] Error en discover_and_update_models: {e}")
            return {"status": "error", "message": str(e)}


# ─── Singletons y aliases ─────────────────────────────────────────────────────

# Singleton principal (nueva API)
_registry_instance: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    """
    Acceso soberano al singleton del Registro de Proveedores.

    Uso preferido (nueva arquitectura):
        from src.services.provider_registry import get_provider_registry
        registry = get_provider_registry()
        config = registry.get_active_config()
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ProviderRegistry()
    return _registry_instance


# ── Aliases de compatibilidad backward ────────────────────────────────────────
# Todos los módulos existentes que hacen:
#   from src.services.provider_registry import service as provider_registry
#   from .provider_registry import get_registry
#   from src.services.provider_registry import provider_registry
# siguen funcionando sin cambios.

service           = get_provider_registry()   # compat: developer, anima, routes, planner, etc.
provider_registry = service                   # compat: veoscope_entity.py, routes/anima.py
get_registry      = get_provider_registry     # compat: veoscanner.py