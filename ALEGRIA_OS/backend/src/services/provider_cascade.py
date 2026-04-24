import logging
import asyncio
from typing import List, Dict, Any, Protocol, Optional, Union

logger = logging.getLogger("ALEGRIA_CASCADE")

class LLMProviderInterface(Protocol):
    """
    Contrato de Proveedor (lo que TODO modelo debe cumplir).
    """
    name: str
    priority: int
    timeout_ms: int

    async def generate(self, prompt: str, system: str = None, temperature: float = 0.7) -> str:
        ...

class ProviderCascade:
    """
    Cascada de Inteligencia.
    Itera sobre proveedores ordenados por prioridad hasta obtener una respuesta válida.
    """
    def __init__(self, providers: List[Any], validator: Any = None):
        """
        Args:
            providers: Lista de objetos que cumplen con LLMProviderInterface (o duck typing)
            validator: Objeto con método validate_response(str) -> bool
        """
        self.providers = sorted(providers, key=lambda p: getattr(p, 'priority', 999))
        self.validator = validator
        self.last_used_provider_name: Optional[str] = None
        self.failed_providers: List[Dict[str, Any]] = [] # Track: [{"id": pid, "error": str}]

    async def run(self, context: Dict[str, Any]) -> str:
        """
        Ejecuta la cascada con el contexto dado.
        """
        last_error = None
        self.last_used_provider_name = None
        
        if not self.providers:
            raise RuntimeError("❌ [CASCADE] No hay proveedores disponibles en la cascada.")

        for provider in self.providers:
            provider_name = getattr(provider, 'name', 'Unknown')
            priority = getattr(provider, 'priority', 999)
            
            try:
                logger.info(f"🌊 [CASCADE] Intentando con proveedor: {provider_name} (Prioridad {priority})")
                
                # Timeout handling (Micro-optimización: 8s max para failover rápido)
                timeout_ms = min(getattr(provider, 'timeout_ms', 8000), 8000)
                timeout_sec = timeout_ms / 1000.0

                
                # Extraer parámetros del contexto
                prompt = context.get("prompt")
                system = context.get("system")
                temperature = context.get("temperature", 0.7)
                
                if not prompt:
                    raise ValueError("Contexto sin prompt")

                # Ejecutar generación con timeout
                response = await asyncio.wait_for(
                    provider.generate(
                        prompt=prompt,
                        system=system,
                        temperature=temperature
                    ),
                    timeout=timeout_sec
                )
                
                # Validar respuesta
                if await self._is_valid(response):
                    logger.info(f"✅ [CASCADE] Respuesta válida de {provider_name}")
                    self.last_used_provider_name = provider_name
                    return response
                else:
                    logger.warning(f"⚠️ [CASCADE] Respuesta de {provider_name} rechazada por validación ética/semántica.")
                    last_error = "Validación fallida"
                    
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ [CASCADE] Timeout con {provider_name} ({timeout_ms}ms)")
                pid = getattr(provider, 'provider_id', None)
                if pid: self.failed_providers.append({"id": pid, "error": "Timeout"})
                last_error = "Timeout"
            except Exception as e:
                logger.error(f"❌ [CASCADE] Error con {provider_name}: {e}")
                pid = getattr(provider, 'provider_id', None)
                if pid: self.failed_providers.append({"id": pid, "error": str(e)})
                last_error = str(e)
                continue
        
        # ⚠️ fallback soberano
        logger.warning("🚨 [CASCADE] Fallo catastrófico: Ningún proveedor respondió. Activando fallback.")
        return "Sistema operativo activo. Los proveedores externos no están disponibles en este momento."


    async def _is_valid(self, response: str) -> bool:
        """
        Validación NO técnica.
        """
        if not response or not response.strip():
            return False
            
        if self.validator:
            if hasattr(self.validator, "validate_response"):
                return await self.validator.validate_response(response)
            
        return True
