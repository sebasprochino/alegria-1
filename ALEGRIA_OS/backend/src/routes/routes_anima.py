# -------------------------------------------------------------------------
# ALEGR-IA OS — src/routes/anima.py
#
# v2.1 — Agrega endpoint POST /generate para uso interno de módulos
#         estratégicos (Content Machine). Centraliza el copywriting en el
#         backend soberano, evitando llamadas directas al LLM desde el frontend.
#
# Endpoints:
#   POST /chat      → Kernel evalúa la intención       → doubt/rejected/authorized
#   POST /execute   → Kernel valida el mandato          → ejecuta vía handler
#   POST /proactive → Genera saludo proactivo (Detective)
#   POST /generate  → [NEW] Generación estratégica directa (Content Machine)
#
# NUNCA se filtra fuera del Kernel.
# -------------------------------------------------------------------------

import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from src.core.kernel import kernel
from src.services.nexus import get_nexus
from src.services.anima import get_anima
from src.os.creative.director import CreativeDirector
from src.core.handlers.registry import handler_exists, get_handler

router = APIRouter(tags=["anima"])
logger = logging.getLogger("ALEGRIA_ROUTES_ANIMA")

director = CreativeDirector()


# ─── Request Models ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    content: str
    provider: str = "ollama"


class ExecuteRequest(BaseModel):
    intention_id: str
    intent: str
    option_id: str


class GenerateRequest(BaseModel):
    """
    Body para generación estratégica directa (Content Machine).
    Bypasses la conversación y el pipeline de intención —
    llama al LLM con system prompt y user prompt construidos por el módulo.
    """
    strategy: str                      # "standard" | "nexus" | "radar"
    format: str                        # "instagram" | "linkedin" | "twitter" | "newsletter"
    topic: str                         # Tema libre del operador
    mode: str = "generate"             # "generate" | "ideas"
    brand_voice: Optional[str] = None  # Voz de marca activa (desde brand.json)
    brand_mood: Optional[str] = None   # Mood de marca activa


# ─── Prompts internos (Content Machine) ──────────────────────────────────────

_STRATEGY_SYSTEM: dict[str, str] = {
    "standard": (
        "Eres un experto en copywriting y estrategia de contenido digital. "
        "Operás bajo la voz de marca: INNOVADORA, ACCESIBLE, INSPIRADORA. "
        "Tono: Energético y confiable. "
        "Sin frases genéricas. Con autoridad y calidad auténtica. "
        "Español rioplatense (tuteo informal). Sin perorata — directo al valor."
    ),
    "nexus": (
        "Eres un analista de contenido especializado en hechos profundos y conexiones no obvias. "
        "Antes de escribir, identificás: (1) el dato inesperado detrás del tema, "
        "(2) la conexión sistémica que pocos ven, (3) la implicación futura. "
        "Integrás estos elementos como narrativa, nunca como lección académica. "
        "Tono: intelectual pero nunca pedante. Español rioplatense."
    ),
    "radar": (
        "Eres un especialista en tendencias virales y cultura digital. "
        "Conectás cualquier tema con lo que está traccionando ahora: "
        "formatos emergentes, conversaciones masivas, micro-tendencias en comunidades nicho. "
        "El contenido se siente urgente, relevante, de hoy. "
        "Español rioplatense, sin filtros corporativos."
    ),
}

_FORMAT_USER: dict[str, str] = {
    "instagram": (
        'Crea un POST DE INSTAGRAM sobre: "{topic}"\n\n'
        "ESTRUCTURA OBLIGATORIA:\n"
        "- Línea 1: Hook visual/emocional (máx 10 palabras, sin clichés)\n"
        "- Párrafo desarrollo: 3-4 líneas con el corazón del mensaje\n"
        "- CTA específico y no genérico\n"
        "- Salto de línea\n"
        "- 15-20 hashtags estratégicos (mezcla niche + masivos)\n\n"
        "Emojis con precisión quirúrgica — solo en puntos clave.\n"
        "Máximo 2200 caracteres. Post completo listo para copiar."
    ),
    "linkedin": (
        'Crea un ARTÍCULO DE LINKEDIN sobre: "{topic}"\n\n'
        "ESTRUCTURA:\n"
        "- Titular (máx 10 palabras, genera curiosidad o urgencia)\n"
        "- Gancho de apertura: 2-3 líneas que rompan expectativas\n"
        "- Desarrollo: 4-6 párrafos cortos (máx 4 líneas c/u)\n"
        "- Dato o insight que solo alguien dentro del campo conocería\n"
        "- Cierre con perspectiva propia — no consejo genérico\n"
        "- CTA de conversación ('¿Qué pensás vos?')\n\n"
        "Entre 800 y 1200 palabras. Profesional pero con voz humana real."
    ),
    "twitter": (
        'Crea un HILO VIRAL PARA X (Twitter) sobre: "{topic}"\n\n'
        "REGLAS:\n"
        "- Entre 8 y 12 tweets\n"
        "- Tweet 1: Hook. Genera FOMO o curiosidad inmediata. Sin 'un hilo:'\n"
        "- Tweets 2-N: Cada uno autónomo pero avanza la narrativa\n"
        "- Último tweet: Conclusión que reencuadra todo + pedido de RT o pregunta\n"
        "- Cada tweet: máximo 270 caracteres\n"
        "- Numeración: 1/ 2/ 3/ al inicio de cada tweet\n\n"
        "Hilo completo, tweet por tweet, separados por línea en blanco."
    ),
    "newsletter": (
        'Crea una NEWSLETTER COMPLETA sobre: "{topic}"\n\n'
        "ESTRUCTURA:\n"
        "**ASUNTO:** (máx 50 chars, con emoji inicial)\n"
        "**PREVIEW TEXT:** (máx 90 chars)\n\n"
        "---\n\n"
        "**[SECCIÓN INTRODUCTORIA]**\n"
        "Apertura personal/contextual (2-3 párrafos)\n\n"
        "**[CUERPO PRINCIPAL]**\n"
        "Desarrollo sustancial con 3-4 secciones y subtítulos cortos\n\n"
        "**[DATO/RECURSO DE LA SEMANA]**\n"
        "Un insight accionable o recurso concreto\n\n"
        "**[CIERRE]**\n"
        "Despedida con personalidad + pregunta al lector\n\n"
        "---\n"
        "600-900 palabras. Tono: carta a un amigo muy inteligente."
    ),
}

_IDEAS_USER: dict[str, str] = {
    "standard": (
        "Sugiere 4 IDEAS DE CONTENIDO para marca personal o negocio digital. "
        "Temas con tracción real, no genéricos. "
        "Respondé SOLO con un JSON array de strings:\n"
        '["idea 1", "idea 2", "idea 3", "idea 4"]'
    ),
    "nexus": (
        "Sugiere 4 TEMAS PROFUNDOS con ángulos no obvios para contenido de alto valor. "
        "Cada idea implica una conexión sistémica o dato inesperado. "
        "Respondé SOLO con un JSON array de strings:\n"
        '["idea 1", "idea 2", "idea 3", "idea 4"]'
    ),
    "radar": (
        "Sugiere 4 TEMAS VIRALES para contenido en redes, conectados con tendencias reales de 2025. "
        "Respondé SOLO con un JSON array de strings:\n"
        '["idea 1", "idea 2", "idea 3", "idea 4"]'
    ),
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

from src.os.perception.intent_detector import detect_mode, get_explicit_action
from src.core.rule_engine import service as rule_engine


def filter_valid_paths(paths: list) -> list:
    valid = []
    for p in paths:
        if handler_exists(p.get("id")):
            valid.append(p)
    return valid


# ─── Endpoints ────────────────────────────────────────────────────────────────

def detect_direct_command(text: str) -> Optional[str]:
    """Valida si el input es un mandato determinista implacable de visión."""
    t = text.lower()
    if "análisis veo" in t or "analisis veo" in t:
        return "visual.veoscope"
    if "análisis visual" in t or "analisis visual" in t:
        return "visual.analyze"
    if '"type": "vision_request"' in t or "'type': 'vision_request'" in t:
        return "visual.veoscope"
    return None


@router.post("/chat")
async def chat(req: ChatRequest):
    """
    Despachador Inteligente con Modality Router integrado e Inyección Directa.
    """
    logger.info(f"⚔️ [ROUTE /chat] Entrada: '{req.content[:60]}'")

    # 1. Bypass Soberano de Comandos Directos Visuales
    cmd = detect_direct_command(req.content)
    if cmd:
        logger.info(f"🔴 [ROUTE /chat] Ejecución Directa Visual detectada: {cmd}")
        return await execute(ExecuteRequest(
            intention_id="direct_cmd",
            intent=req.content,
            option_id=cmd
        ))

    mode = detect_mode(req.content)
    anima = get_anima()

    try:
        if mode == "execution":
            action_id = get_explicit_action(req.content)
            if action_id and handler_exists(action_id):
                logger.info(f"🔴 [ROUTE /chat] Ejecución Directa Standard: {action_id}")
                return await execute(ExecuteRequest(
                    intention_id="direct_cmd",
                    intent=req.content,
                    option_id=action_id
                ))
            return {
                "status": "blocked",
                "mode": "execution",
                "response": "Para ejecutar una opción propuesta, usa el panel de selección superior."
            }

        if mode == "conversation":
            logger.info("🟢 [ROUTE /chat] Modo: Conversación")
            raw_result = await anima.generate_raw(req.content)
            filtered = await rule_engine.filter_output(raw_result, mode="conversation")
            response = anima.format_response(filtered)
            response["mode"] = "conversation"
            return response

        if mode == "intention":
            logger.info("🟡 [ROUTE /chat] Modo: Intención")
            nexus = get_nexus()
            from src.services.memory.user_lexicon import Message as LexicalMessage
            nexus.memory.register_observation(content=req.content, source="user")
            nexus.lexicon.observe(LexicalMessage(role="user", content=req.content))

            decision = await kernel.process_intent(req.content)

            if "paths" in decision:
                decision["paths"] = filter_valid_paths(decision["paths"])
                if not decision["paths"] and decision["status"] != "blocked":
                    return {
                        "status": "Doubt",
                        "mode": "intention",
                        "response": "He detectado una intención operativa, pero no tengo herramientas habilitadas para esta solicitud.",
                        "intention_id": decision.get("intention_id"),
                        "paths": []
                    }

            decision["mode"] = "intention"
            return decision

        return {"status": "error", "message": "Modo de percepción no reconocido."}

    except Exception as e:
        logger.error(f"❌ [ROUTE /chat] Error crítico: {e}")
        return {
            "status": "error",
            "message": f"Error interno en el Nexo de percepción: {str(e)}",
            "mode": "error"
        }


@router.post("/execute")
async def execute(req: ExecuteRequest):
    """
    Ejecución autorizada por el Kernel Soberano con auditoría CDM.
    """
    logger.info(f"⚔️ [ROUTE /execute] Mandato recibido: {req.intention_id} | {req.option_id}")

    operational_trace = []
    try:
        payload = kernel.authorize_path(req.intention_id, req.option_id)
        operational_trace.append({
            "step": "KERNEL_GATE",
            "ok": True,
            "intention_id": req.intention_id,
            "path_id": req.option_id,
            "audit": kernel.get_audit_trail()
        })
    except Exception as e:
        logger.error(f"⚠️ [ROUTE /execute] Kernel Block: {e}")
        return {
            "status": "error",
            "message": str(e),
            "trace": [{"step": "KERNEL_GATE", "ok": False, "reason": str(e)}]
        }

    try:
        handler_info = get_handler(req.option_id)
        if not handler_info:
            raise ValueError(f"No existe un handler registrado para '{req.option_id}'")

        handler_path = handler_info["handler"]
        module_name, func_name = handler_path.rsplit(".", 1)

        import importlib
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)

        nexus = get_nexus()
        from src.services.memory.user_lexicon import Message as LexicalMessage
        nexus.memory.register_observation(
            content=f"OPERADOR AUTORIZÓ: {req.option_id} para '{req.intent}'",
            source="user"
        )
        nexus.lexicon.observe(LexicalMessage(role="user", content=f"Autorizado: {req.option_id}"))

        result = await func(req.intent)

        if isinstance(result, dict) and "trace" in result:
            operational_trace.extend(result["trace"])
            output_content = result["output"]
            execution_status = result["status"]
        else:
            output_content = result.get("response") if isinstance(result, dict) else str(result)
            execution_status = "success"
            kernel.update_session_context(req.option_id, output_content)
            operational_trace.append({
                "step": "OS_HANDLER_EXEC",
                "data": f"Ejecutor '{req.option_id}' completado."
            })

        variant = {
            "content": output_content,
            "aesthetic_meta": {"tone": "tech_sovereign", "clarity": "high"}
        }
        cdm_verdict = director.evaluate_variant(variant)
        operational_trace.append({
            "step": "CDM_GATE",
            "status": cdm_verdict["status"],
            "score": cdm_verdict.get("score"),
            "reasoning": cdm_verdict.get("reasoning", [])
        })

        final_status = (
            "success"
            if execution_status == "success" and cdm_verdict["status"] != "rejected"
            else "stopped"
        )
        operational_trace.append({
            "step": "STATUS_FINAL",
            "status": final_status,
            "integrity_hash": kernel.get_audit_trail()
        })

        anima = get_anima()
        raw_dict = {
            "type": result.get("type", "llm") if isinstance(result, dict) else "llm",
            "raw": output_content,
            "source": "os_execution_registry",
            "message_ref": req.intent,
            "integrity_hash": kernel.get_audit_trail()
        }

        filtered = await rule_engine.filter_output(raw_dict, mode="execution")

        if filtered.get("type") == "tool":
            logger.info("🛡️ [ROUTE /execute] Bypass soberano: entrega sin narrativa LLM.")
            filtered["status"] = "Authorized"

        filtered["trace"] = operational_trace
        return anima.format_response(filtered)

    except Exception as e:
        logger.error(f"❌ [ROUTE /execute] Fallo en ejecución del OS: {e}")
        return {
            "status": "error",
            "message": f"Fallo en ejecución: {str(e)}",
            "trace": operational_trace + [{"step": "OS_CRITICAL", "data": str(e)}]
        }


@router.post("/proactive")
async def get_proactive_greeting():
    """Genera saludo proactivo basado en el Detective Contextual."""
    from src.os.pipeline.detective import service as detective
    hint = await detective.get_proactive_hint()
    if hint:
        anima = get_anima()
        return anima.format_response({
            "status": "Authorized",
            "content": hint["text"],
            "raw": hint["text"],
            "type": "llm",
            "insight": hint["insight"]
        })
    return {"status": "none"}


@router.post("/generate")
async def generate_content(req: GenerateRequest):
    """
    [NEW v2.1] Generación estratégica directa — Content Machine.

    Bypasses el pipeline conversacional/intención. No pasa por el Kernel de
    propuesta porque el operador ya tomó la decisión de estrategia y formato.

    El output sí pasa por format_response() para logging y empaquetado estándar.

    Modes:
        generate → genera el contenido completo según estrategia + formato + tema
        ideas    → retorna 4 ideas de contenido como JSON array
    """
    logger.info(
        f"✍️  [ROUTE /generate] strategy={req.strategy} | "
        f"format={req.format} | mode={req.mode} | "
        f"topic='{req.topic[:50]}'"
    )

    try:
        from src.services.provider_registry import service as provider_registry

        # ── Construir system prompt con brand voice opcional ──────────────────
        base_system = _STRATEGY_SYSTEM.get(req.strategy, _STRATEGY_SYSTEM["standard"])

        if req.brand_voice or req.brand_mood:
            brand_addendum = "\n\n### VOZ DE MARCA ACTIVA\n"
            if req.brand_voice:
                brand_addendum += f"- Voz: {req.brand_voice}\n"
            if req.brand_mood:
                brand_addendum += f"- Mood: {req.brand_mood}\n"
            base_system += brand_addendum

        # ── Construir user prompt ─────────────────────────────────────────────
        if req.mode == "ideas":
            user_msg = _IDEAS_USER.get(req.strategy, _IDEAS_USER["standard"])
        else:
            template = _FORMAT_USER.get(req.format, _FORMAT_USER["instagram"])
            user_msg = template.format(topic=req.topic)

        # ── Llamar al provider activo (sin historial conversacional) ─────────
        raw_text = await provider_registry.chat(
            messages=[{"role": "user", "content": user_msg}],
            system=base_system,
        )

        logger.info(
            f"✅ [ROUTE /generate] Generación completada | "
            f"chars={len(raw_text)} | strategy={req.strategy} | format={req.format}"
        )

        return {
            "status": "Authorized",
            "response": raw_text,
            "raw_attempt": raw_text,
            "strategy": req.strategy,
            "format": req.format,
            "mode": req.mode,
            "meta": {
                "raw": raw_text,
                "strategy": req.strategy,
                "format": req.format,
                "topic": req.topic,
                "sovereignty": "ALEGR-IA OS — Autoría humana preservada",
            },
        }

    except Exception as e:
        logger.error(f"❌ [ROUTE /generate] Error: {e}")
        return {
            "status": "error",
            "response": "",
            "message": f"Error en generación: {str(e)}",
            "strategy": req.strategy,
            "format": req.format,
        }
