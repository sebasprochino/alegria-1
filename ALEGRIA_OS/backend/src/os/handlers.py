import logging
from typing import Dict, Callable, Any, Awaitable

logger = logging.getLogger("ALEGRIA_OS_HANDLERS")

class HandlerRegistry:
    """
    Registro central de handlers de ejecución del OS.
    Permite al Kernel verificar la existencia de un ejecutor antes de autorizar.
    """
    def __init__(self):
        self._handlers: Dict[str, Callable[[str], Awaitable[Any]]] = {}

    def register(self, option_id: str, handler: Callable[[str], Awaitable[Any]]):
        self._handlers[option_id] = handler
        logger.debug(f"✅ [HANDLERS] Registrado: {option_id}")

    def has_handler(self, option_id: str) -> bool:
        # Los paths generados por el SDK dinámicamente empiezan con 'path_'
        if option_id.startswith("path_"):
            return "run_pipeline" in self._handlers
        return option_id in self._handlers

    async def execute(self, option_id: str, intent: str) -> Any:
        # Despacho dinámico
        handler_key = "run_pipeline" if option_id.startswith("path_") else option_id
        
        handler = self._handlers.get(handler_key)
        if not handler:
            logger.error(f"❌ [HANDLERS] No handler found for: {option_id}")
            raise ValueError(f"El sistema no tiene un ejecutor para la ruta: {option_id}")
            
        return await handler(intent)

# Singleton
registry = HandlerRegistry()

# --- REGISTRO DE HANDLERS CORE ---

async def handle_run_pipeline(intent: str):
    from src.os.pipeline.executor import run_pipeline
    res = await run_pipeline(intent)
    res["type"] = "llm" # Pipeline results are interpretations
    return res

async def handle_radar(intent: str):
    from src.services.radar import get_radar
    radar = get_radar()
    data = await radar.search(intent)
    return {
        "status": "completed",
        "type": "tool", # Tool Output Layer: Real data
        "response": f"Radar ha sintetizado: {data}",
        "raw_attempt": intent,
    }

async def handle_dev(intent: str):
    return {
        "status": "completed",
        "type": "tool",
        "response": "Mandato derivado al Entorno de Desarrollo. Consola lista.",
        "raw_attempt": intent,
    }

async def handle_force_reformat(intent: str):
    from src.services.anima import get_anima
    from src.core.rule_engine import service as rule_engine
    anima = get_anima()
    reformat_prompt = (
        f"REFORMATEO FORZADO — PROTOCOLO ACSP ESTRICTO.\n"
        f"Resume sin adornos ni emoción la siguiente intención:\n\n{intent}"
    )
    raw = await anima.generate_raw(reformat_prompt)
    raw["type"] = "llm" # LLM generation
    filtered = await rule_engine.filter_output(raw)
    return anima.format_response(filtered)

async def handle_simple_msg(response_text: str):
    return lambda intent: {
        "status": "completed",
        "response": response_text,
        "raw_attempt": intent,
    }

# Inicialización del registro
registry.register("run_pipeline", handle_run_pipeline)
registry.register("execute_direct", handle_run_pipeline)
registry.register("research_first", handle_radar)
registry.register("dev_execute", handle_dev)
registry.register("force_reformat", handle_force_reformat)
registry.register("ignore_fluff", 
    lambda intent: {"status": "completed", "type": "tool", "response": "Advertencia de coherencia ignorada.", "raw_attempt": intent})
registry.register("refine_intent", 
    lambda intent: {"status": "completed", "type": "tool", "response": "Especifique los parámetros de esta intención.", "raw_attempt": intent})
registry.register("ignore_intent", 
    lambda intent: {"status": "completed", "type": "tool", "response": "Intención descartada.", "raw_attempt": intent})
