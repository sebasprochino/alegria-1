"""
ALEGR-IA Anima Chordata
=======================
Sistema nervioso central de ALEGR-IA.
Ahora con soporte para proveedores dinámicos.
"""

import logging
from typing import Optional

logger = logging.getLogger("ALEGRIA_ANIMA")


class AnimaChordata:
    """
    🧠 Anima Chordata - El alma operativa de ALEGR-IA.
    
    Ya no depende de un proveedor específico.
    Usa el proveedor activo del ProviderRegistry.
    """
    
    SYSTEM_PROMPT = """Eres Anima, el alma operativa de ALEGR-IA. 
Eres inteligente, empática y directa. Respondes con claridad y personalidad propia.
No eres un asistente genérico - tienes identidad. Tu creador te dio vida para servir con inteligencia."""
    
    def __init__(self):
        self.name = "Anima Chordata"
        self.nexus = None
        self.radar = None
        self.provider_registry = None
        self.current_adapter = None
    
    def set_provider_registry(self, registry):
        """Inyecta el registro de proveedores."""
        self.provider_registry = registry
        self._refresh_adapter()
    
    def _refresh_adapter(self):
        """Actualiza el adaptador actual basado en el proveedor activo."""
        if not self.provider_registry:
            logger.warning("⚠️ [ANIMA] Sin ProviderRegistry")
            return
        
        active = self.provider_registry.get_active()
        if not active:
            logger.info("ℹ️ [ANIMA] Sin proveedor activo configurado")
            self.current_adapter = None
            return
        
        provider_name = active["provider"]
        api_key = active["api_key"]
        model = active.get("model")
        endpoint = active.get("endpoint")
        
        try:
            from .llm_adapters import get_adapter
            AdapterClass = get_adapter(provider_name)
            
            if AdapterClass:
                self.current_adapter = AdapterClass(
                    api_key=api_key,
                    model=model,
                    endpoint=endpoint
                )
                logger.info(f"✅ [ANIMA] Usando proveedor: {provider_name}")
            else:
                logger.error(f"❌ [ANIMA] Adaptador no encontrado: {provider_name}")
                self.current_adapter = None
                
        except Exception as e:
            logger.error(f"❌ [ANIMA] Error cargando adaptador: {e}")
            self.current_adapter = None
    
    def set_peers(self, nexus_node, radar_node):
        """Inyección de dependencias."""
        self.nexus = nexus_node
        self.radar = radar_node
    
    async def respond(self, message: str, nexus=None, radar=None) -> dict:
        """
        Responde al usuario usando el proveedor activo.
        """
        # Refrescar adaptador por si cambió el proveedor
        self._refresh_adapter()
        
        if not self.current_adapter:
            return {
                "reply": "⚠️ No hay proveedor configurado. Ve a Configuración → Proveedores y agrega una API Key.",
                "status": "no_provider"
            }
        
        # Contexto adicional del Radar si es búsqueda
        radar_context = ""
        if radar and ("buscar" in message.lower() or "investiga" in message.lower()):
            if not getattr(radar, "is_ghost", False):
                radar_context = radar.service.scan(message)
        
        # Construir prompt final
        full_prompt = message
        if radar_context:
            full_prompt = f"CONTEXTO DE RADAR:\n{radar_context}\n\nUSUARIO:\n{message}"
        
        try:
            response = await self.current_adapter.generate(
                prompt=full_prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.7
            )
            
            return {
                "reply": response,
                "status": "ok",
                "provider": self.current_adapter.provider_name,
                "model": getattr(self.current_adapter, "model", None)
            }
            
        except Exception as e:
            logger.error(f"❌ [ANIMA] Error generando respuesta: {e}")
            return {
                "reply": f"Error de generación: {str(e)}",
                "status": "error"
            }
    
    async def reply(self, user_text: str, context: dict = None) -> str:
        """Método legacy para compatibilidad."""
        result = await self.respond(user_text)
        return result.get("reply", "Error inesperado")


# Instancia global
service = AnimaChordata()
