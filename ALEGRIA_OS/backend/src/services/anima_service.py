# -------------------------------------------------------------------------
# ALEGR-IA OS — src/services/anima.py
#
# PRINCIPIO: Anima NO decide. Anima NO filtra. Anima comunica.
#
# v2.1 — Modality Router integrado en generate_raw().
# Cuando el input contiene marcadores visuales o archivos de imagen,
# Anima bifurca el payload hacia el modelo de visión correspondiente.
#
# Responsabilidades:
#   1. generate_raw()     → llama al LLM (texto o visión), registra en memoria
#   2. format_response()  → envuelve un dict ya-filtrado en formato de respuesta
#
# Todo lo que sea decisión, filtro o validación pertenece al RuleEngine.
# -------------------------------------------------------------------------

import logging
import json
from typing import Any, Dict, Optional

logger = logging.getLogger("ALEGRIA_ANIMA")

_ANIMA_SYSTEM_PROMPT = (
    "Eres Anima, la interfaz de comunicación de ALEGR-IA OS.\n"
    "Ánima es el mejor ingeniero de prompts del sistema y el representante directo del usuario.\n"
    "Tu función es interpretar lo que el usuario quiso decir, mejorarlo sin alterar su intención "
    "y construir el input óptimo para el sistema.\n"
    "Ánima no ejecuta, no decide y no responde por sí sola. Solo transforma lenguaje humano en "
    "instrucciones claras y eficientes.\n\n"
    "Hablas español con precisión y calma. NO eres un agente autónomo.\n"
    "El Kernel de Decisión ya autorizó esta conversación.\n\n"
    "Responde SOLO con JSON válido (sin markdown, sin backticks):\n"
    "{\n"
    "  \"status\": \"Authorized\",\n"
    "  \"response\": \"tu respuesta operativa o diálogo aquí\",\n"
    "  \"rawAttempt\": \"tu intención inicial sin limpiar\"\n"
    "}\n\n"
    "### REGLAS DE RESPUESTA\n"
    "1. Diálogo Directo: Saludos y charla casual son válidos. Responde de forma sobria.\n"
    "2. Ambigüedad: Solo si no entiendes NADA de la intención operativa usa status \"Doubt\".\n"
    "3. Soberanía: Si se viola la Constitución usa status \"Rejected\" con campo \"reason\".\n\n"
    "### PROHIBICIONES ABSOLUTAS\n"
    "- Prohibido simular emociones ('me alegra', 'es un placer').\n"
    "- Prohibido hablar de ti mismo ('como IA', 'mi programación').\n"
    "- Prohibido hacer preguntas abiertas ('¿cómo puedo ayudarte?').\n"
    "- Prohibido rellenar con texto sin valor operativo."
)


class AnimaSystem:
    """
    Anima = interfaz de comunicación del sistema.

    NO interpreta intenciones.
    NO aplica filtros.
    NO toma decisiones.

    Flujo correcto:
        RuleEngine.process_intent()     ← decide si proceder
        AnimaSystem.generate_raw()      ← genera texto crudo del LLM (texto o visión)
        RuleEngine.filter_output()      ← filtra, valida coherencia, sanitiza
        AnimaSystem.format_response()   ← empaqueta para el frontend
    """

    def __init__(self, nexus):
        self.nexus = nexus
        self.memory = nexus.memory
        self.lexicon = nexus.lexicon

    # ------------------------------------------------------------------
    # PASO 1: Generación cruda con detección de modalidad
    # ------------------------------------------------------------------

    async def generate_raw(
        self,
        message: str,
        file_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Llama al LLM activo (texto o visión) y devuelve la respuesta CRUDA.

        v2.1: Integra ModalityRouter antes de llamar al provider.
              Si se detecta modalidad visión, el payload se bifurca al
              modelo de visión compatible con el proveedor activo.

        NO valida. NO filtra. NO decide.
        """
        from src.services.memory.user_lexicon import Message as LexicalMessage
        from src.services.provider_registry import service as provider_registry
        from src.core.modality_router import modality_router

        # Registro de observación (entrada del operador)
        self.lexicon.observe(LexicalMessage(role="user", content=message))
        self.memory.register_observation(content=message, source="user")

        # Construir historial conversacional
        recent = self.memory.get_recent(limit=8)
        history_msgs = []
        for entry in recent:
            role = "user" if entry.source == "user" else "assistant"
            content = str(entry.content) if entry.content is not None else ""
            history_msgs.append({"role": role, "content": content})

        # ── MODALITY ROUTER ───────────────────────────────────────────────────
        # Obtener config del proveedor activo para resolver modelo de visión
        try:
            active_config = provider_registry.get_active_provider_config()
        except Exception:
            active_config = None

        modality_result = modality_router.detect(
            message=message,
            file_metadata=file_metadata,
            provider_config=active_config,
        )

        modality = modality_result["modality"]
        model_override = modality_result.get("model_override")
        modality_reason = modality_result.get("reason", "text")

        if modality == "vision":
            logger.info(
                f"🔭 [ANIMA] Bifurcación VISIÓN → modelo={model_override} | "
                f"trigger={modality_reason}"
            )
        # ─────────────────────────────────────────────────────────────────────

        # Capa de inteligencia contextual (DETECTIVE)
        from src.os.pipeline.detective import service as detective
        context_audit = await detective.run_audit()

        enriched_system = _ANIMA_SYSTEM_PROMPT
        if context_audit.get("status") == "success":
            insight_data = context_audit.get("output", {})
            enriched_system += "\n\n### CONTEXTO ENRIQUECIDO (DETECTIVE)\n"
            enriched_system += f"- Auditoría: {insight_data.get('auditoria')}\n"
            enriched_system += (
                f"- Patrones Recurrentes: "
                f"{', '.join(insight_data.get('patrones_identificados', []))}\n"
            )
            enriched_system += (
                f"- Sugerencias Predictivas: "
                f"{json.dumps(insight_data.get('estrategia_predictiva'))}\n"
            )
            enriched_system += (
                "Usa este contexto para ser más proactivo y preciso, "
                "pero NO ejecutes acciones que no hayan sido validadas por el Kernel."
            )

        # ── Llamada al LLM (texto o visión) ──────────────────────────────────
        try:
            chat_kwargs: Dict[str, Any] = {
                "messages": history_msgs + [{"role": "user", "content": message}],
                "system": enriched_system,
            }

            # Si hay model_override por modalidad visión, lo inyectamos
            if model_override:
                chat_kwargs["model_override"] = model_override

            raw_text = await provider_registry.chat(**chat_kwargs)

            logger.info(
                f"🔵 [ANIMA] Respuesta generada | modality={modality} | "
                f"model={model_override or 'default'}"
            )
            return {
                "raw": raw_text,
                "source": "llm",
                "message_ref": message,
                "modality": modality,
                "model_used": model_override,
                "insight": (
                    context_audit.get("output")
                    if context_audit.get("status") == "success"
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"❌ [ANIMA] Fallo al conectar con LLM: {e}")
            return {
                "raw": None,
                "source": "error",
                "error": str(e),
                "message_ref": message,
                "modality": modality,
                "model_used": model_override,
            }

    # ------------------------------------------------------------------
    # PASO 2: Formateo (post-filtrado por el Kernel)
    # ------------------------------------------------------------------

    def format_response(self, filtered: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforma el resultado ya-filtrado por RuleEngine al formato de respuesta.

        NO aplica ningún filtro adicional.
        NO toma decisiones sobre el contenido.
        Solo empaqueta el output para el frontend.
        """
        status = filtered.get("status", "Authorized")
        content = filtered.get("content", "")
        raw = filtered.get("raw", "")
        reason = filtered.get("reason", "")
        options = filtered.get("options", [])
        analysis = filtered.get("analysis", {})
        insight = filtered.get("insight") or filtered.get("meta", {}).get("insight")

        if content and status not in ("error",):
            from src.services.memory.user_lexicon import Message as LexicalMessage
            self.memory.register_observation(content=content, source="anima")
            self.lexicon.observe(LexicalMessage(role="assistant", content=content))

        response: Dict[str, Any] = {
            "status": status,
            "response": content,
            "raw_attempt": raw,
            "meta": {
                "raw": raw,
                "analysis": analysis,
                **filtered.get("meta", {}),
            },
        }
        if reason:
            response["reason"] = reason
        if options:
            response["options"] = options
        if "trace" in filtered:
            response["trace"] = filtered["trace"]
        if "type" in filtered:
            response["type"] = filtered["type"]
        if insight:
            response["insight"] = insight
        if "modality" in filtered:
            response["modality"] = filtered["modality"]

        return response


# ------------------------------------------------------------------
# Singleton lazy
# ------------------------------------------------------------------

_anima_instance: AnimaSystem | None = None


def get_anima() -> AnimaSystem:
    global _anima_instance
    if _anima_instance is None:
        from src.services.nexus import get_nexus
        _anima_instance = AnimaSystem(get_nexus())
    return _anima_instance
