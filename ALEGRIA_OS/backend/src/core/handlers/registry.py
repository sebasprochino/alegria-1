import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ALEGRIA_HANDLER_REGISTRY")

# HANDLER_REGISTRY: El mapa soberano de capacidades del sistema.
# Mapea un ID de acción a su configuración y ruta de ejecución.
HANDLER_REGISTRY = {
    "radar.search": {
        "enabled": True,
        "handler": "src.os.actions.registry.tool_radar_search",
        "name": "Búsqueda en Radar",
        "description": "Busca información en tiempo real en internet."
    },
    "file.save": {
        "enabled": True,
        "handler": "src.os.actions.registry.tool_file_save",
        "name": "Guardar Archivo",
        "description": "Escribe contenido en un archivo del sistema."
    },
    "visual.analyze": {
        "enabled": True,
        "handler": "src.os.actions.registry.tool_analyze_visual",
        "name": "Análisis Visual",
        "description": "Analiza imágenes usando modelos de visión."
    },
    "system.navigate": {
        "enabled": True,
        "handler": "src.os.actions.registry.tool_system_navigate",
        "name": "Navegación Soberana",
        "description": "Abre un sitio web o nodo de contenido (YouTube) en el explorador interno."
    },
    "news.clarin": {
        "enabled": True,
        "handler": "src.os.actions.registry.tool_clarin_news",
        "name": "Clarín News Sensor",
        "description": "Sonda especializada en noticias de Clarín (RSS Trusted Source)."
    },
    "developer.execute": {
        "enabled": True,
        "handler": "src.os.pipeline.executor.run_pipeline",  # Por ahora el pipeline completo
        "name": "Entorno de Desarrollo",
        "description": "Ejecuta mandatos complejos en el entorno de desarrollo."
    },
    "visual.veoscope": {
        "enabled": True,
        "handler": "src.os.actions.registry.tool_visual_veoscope",
        "name": "VeoScope Engine",
        "description": "Análisis clínico audiovisual (Ojo Clínico) de ALEGR-IA."
    },
    "brand.update": {
        "enabled": True,
        "handler": "src.os.actions.registry.tool_brand_update",
        "name": "Brand Update",
        "description": "Actualiza la identidad de una marca en el Studio."
    }
}

def get_handler(action: str) -> Optional[Dict[str, Any]]:
    """Recupera la configuración de un handler por su ID."""
    return HANDLER_REGISTRY.get(action)

def handler_exists(action: str) -> bool:
    """Verifica si un handler existe y está habilitado."""
    h = get_handler(action)
    return h is not None and h.get("enabled", False)

def list_handlers() -> Dict[str, str]:
    """Lista todos los handlers habilitados para el Planner."""
    return {k: v["description"] for k, v in HANDLER_REGISTRY.items() if v["enabled"]}
