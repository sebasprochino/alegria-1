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
import json
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.core.kernel import kernel
from src.services.nexus import get_nexus
from src.services.anima import get_anima
from src.services.radar import get_radar
from src.os.creative.director import CreativeDirector
from src.core.handlers.registry import handler_exists, get_handler

# ─── NUEVO: Ejecutor de Pipelines (VeoScope) ────────────────────────────────
from src.os.pipeline.vision_executor import run_vision_pipeline

router = APIRouter(tags=["anima"])
logger = logging.getLogger("ALEGRIA_ROUTES_ANIMA")

director = CreativeDirector()


@router.get("/audit/stream")
async def audit_stream():
    """
    Endpoint SSE (Server-Sent Events) para auditoría en tiempo real.
    Permite que la UI visualice el flujo cognitivo de ANIMA (BUG-05).
    """
    from src.services.audit_emitter import audit_emitter

    async def event_generator():
        queue = await audit_emitter.subscribe()
        try:
            while True:
                # Esperar evento de la cola con timeout para mantener la conexión viva
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive comment
                    yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            # Cliente desconectado
            audit_emitter.unsubscribe(queue)
        except Exception as e:
            logger.error(f"❌ [SSE] Error en generador: {e}")
            audit_emitter.unsubscribe(queue)

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no" # Importante para Nginx/Proxies
        }
    )

@router.get("/audit/history/{intention_id}")
async def get_audit_history(intention_id: str):
    """
    Recupera el historial de eventos persistidos para una intención.
    Permite el Replay del Timeline.
    """
    nexus = get_nexus()
    if not nexus or not nexus.memory:
        return {"status": "error", "message": "Nexus Memory no disponible."}
    
    events = await nexus.memory.get_events(intention_id)
    return {
        "intention_id": intention_id,
        "events": events
    }

@router.post("/audit/error")
async def report_frontend_error(req: Dict[str, Any]):
    """
    Recibe reportes de fallos de la UI y los emite al AuditEmitter
    para visibilidad en el Timeline.
    """
    from src.services.audit_emitter import audit_emitter
    import time

    error_data = {
        "intention_id": "ui-crash",
        "stage": "error",
        "timestamp": time.time(),
        "agent": "FRONTEND",
        "data": {
            "message": req.get("message"),
            "stack": req.get("stack"),
            "componentStack": req.get("componentStack"),
            "context": req.get("context"),
            "status": "CRITICAL_CRASH"
        }
    }
    
    await audit_emitter.emit(error_data)
    logger.error(f"💥 [UI ERROR] {req.get('message')}")
    
    return {"status": "received"}



# ─── Request Models ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    content: str
    provider: str = "ollama"
    file_metadata: Optional[dict] = None


class ExecuteRequest(BaseModel):
    intent: str
    option_id: str
    intention_id: Optional[str] = None


class GenerateRequest(BaseModel):
    """
    Body para generación estratégica directa (Content Machine / Production Studio).
    """
    strategy: str                      # "standard" | "nexus" | "radar"
    format: str                        # "instagram" | "video" | "movie" | etc.
    topic: str                         # Tema libre del operador
    mode: str = "generate"             # "generate" | "ideas"
    brand_id: Optional[str] = None     # Identificativo de la marca/persona en Brand Studio
    brand_voice: Optional[str] = None     # Fallback de voz

class OverrideRequest(BaseModel):
    """
    Mandato de intervención humana para sobrepasar bloqueos del Kernel.
    """
    action: str                        # "force_render" | "retry_strict"
    content: str                       # El prompt original o el raw bloqueado
    intention_id: Optional[str] = None
    brand_mood: Optional[str] = None      # Fallback de mood
    lyrics: Optional[str] = None          # Letra de canción (para formato music_video)
    references: Optional[List[Dict[str, Any]]] = None  # Lista de [{type: "image"|"video", data: "base64"}]
    optimization: str = "master"       # "master" | "luma" | "runway" | "kling"
    # New: Camera Controls
    camera_rotate: Optional[float] = 0
    camera_vertical: Optional[float] = 0
    camera_zoom: Optional[float] = 1.0


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
        "- CTA de conversación (\'¿Qué pensás vos?\')\n\n"
        "Entre 800 y 1200 palabras. Profesional pero con voz humana real."
    ),
    "twitter": (
        'Crea un HILO VIRAL PARA X (Twitter) sobre: "{topic}"\n\n'
        "REGLAS:\n"
        "- Entre 8 y 12 tweets\n"
        "- Tweet 1: Hook. Genera FOMO o curiosidad inmediata. Sin \'un hilo:\'\n"
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
    "video": (
        'Crea el guion técnico de un VIDEO ESTRATÉGICO para: "{topic}"\n\n'
        "ESTRUCTURA DE PRODUCCIÓN (OBLIGATORIA):\n"
        "1. NARRATIVA: Descripción general del concepto.\n"
        "2. STORYBOARD MODULAR: Crea exactamente 3-5 bloques con el formato:\n"
        "   [SCENE X] Título o tiempo\n"
        "   [ACTION]: Qué sucede en pantalla.\n"
        "   [PROMPT]: Prompt específico para IA de imagen/video.\n\n"
        "3. PROMPTS DE VALOR:\n"
        "- [MASTER]: Prompt universal de alta fidelidad\n"
        "- [OPTIMIZADO]: Prompt adaptado para {optimization_target}\n\n"
        "Reglas: Enfoque en movimiento de cámara, iluminación y consistencia."
    ),
    "movie": (
        'Desarrolla el TREATMENT CINEMATOGRÁFICO para: "{topic}"\n\n'
        "SECCIONES:\n"
        "- LOGLINE: Una frase potente\n"
        "- SINOPSIS: Narrativa emocional clara\n"
        "- BEAT SHEET: 5 puntos clave de la historia\n"
        "- VISUAL DIRECTIVE: Estética, colorimetría y ritmo\n"
        "- PROMPTS DE SECUENCIA: 3 prompts técnicos para los momentos clave de la película."
    ),
    "interview": (
        'Crea el guion de una ENTREVISTA PROFUNDA sobre: "{topic}"\n\n'
        "PERSONAJES:\n"
        "- Entrevistador: Curioso, punzante pero respetuoso\n"
        "- Entrevistado: Responde basándose en el ADN de identidad activo\n\n"
        "FORMATO:\n"
        "- 4-6 preguntas estratégicas\n"
        "- Respuestas con voz y mood específicos de la marca/persona."
    ),
    "tutorial": (
        'Diseña un TUTORIAL ESTRATÉGICO sobre: "{topic}"\n\n'
        "PASOS:\n"
        "- Requisitos previos\n"
        "- Ejecución paso a paso (con directivas visuales para video)\n"
        "- Pro-tips exclusivos\n\n"
        "PROMPTS DE APOYO: 3 prompts para generar B-roll o overlays técnicos."
    ),
    "music_video": (
        'Crea el TRATAMIENTO VISUAL para un VIDEO MUSICAL sobre: "{topic}"\n\n'
        "LETRA DISPONIBLE:\n"
        "{lyrics}\n\n"
        "REQUERIMIENTOS DE PRODUCCIÓN (OBLIGATORIOS):\n"
        "1. NARRATIVA VISUAL: Sentimiento y estética general.\n"
        "2. STORYBOARD POR ESTROFAS:\n"
        "   Divide la letra en 5-8 escenas cinematográficas usando el formato:\n"
        "   [SCENE X] Título\n"
        "   [ACTION]: Descripción visual poética vinculada a la letra.\n"
        "   [PROMPT]: Prompt técnico para generación visual.\n\n"
        "3. PROMPTS MAESTROS:\n"
        "- [MASTER]: Un prompt cinemático unificado.\n"
        "- [{optimization_target}]: Prompt optimizado técnicamente."
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

from src.os.orchestrator import get_os

os_engine = get_os()

@router.post("/chat")
async def chat(req: ChatRequest):
    """
    Ruta de Chat Unificada (Arquitectura Operativa Definitiva).
    Delega el flujo soberano al motor del OS:
    NEXUS (Clasifica) -> ANIMA (Construye) -> LLM (Genera) -> KERNEL (Audita).
    """
    try:
        # Ejecutamos el flujo centralizado
        response = await os_engine.process(
            user_input=req.content,
            file_metadata=req.file_metadata
        )
        return response

    except Exception as e:
        import traceback
        error_stack = traceback.format_exc()
        logger.error(f"❌ [ROUTE /chat] Error crítico en flujo soberano: {e}")
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__,
            "stack": error_stack,
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

        # ── 1. Resolver Identidad de Marca si se provee ID ────────────────────
        brand_voice = req.brand_voice
        brand_mood = req.brand_mood
        
        if req.brand_id:
            from src.services.brand_service import service as brand_service
            brands_data = brand_service.get_all()
            if req.brand_id in brands_data.get("brands", {}):
                brand = brands_data["brands"][req.brand_id]
                brand_voice = brand.get("voice", brand_voice)
                brand_mood = brand.get("mood", brand_mood)
                
                # --- NEW: Face-Locking Logic ---
                if brand.get("category") == "persona":
                    gallery = brand.get("gallery", [])
                    if gallery:
                        # Buscamos la primera imagen (la más reciente o principal) como referencia facial
                        face_ref = gallery[0].get("url")
                        if face_ref:
                            if not req.references: req.references = []
                            # Inyectamos como referencia visual prioritaria
                            req.references.insert(0, {"type": "image", "data": face_ref, "is_face": True})
                            logger.info(f"👤 [GENERATE] Face-Lock activado: Usando referencia de {req.brand_id}")
                
                logger.info(f"🎭 [GENERATE] Identidad inyectada: {req.brand_id} ({brand.get('category')})")

        # ── 2. Resolver Contexto Visual si hay referencias ───────────────────
        visual_blueprint = ""
        if req.references and len(req.references) > 0:
            logger.info(f"👁️ [GENERATE] Analizando {len(req.references)} referencias visuales para Blueprint...")
            from src.perception.veoscope.veoscope_entity import create_veoscope
            veoscope = create_veoscope()
            
            # Construir contexto para análisis de producción
            v_context = {
                "images": [r["data"] for r in req.references if r["type"] == "image"],
                "video": next((r["data"] for r in req.references if r["type"] == "video"), None)
            }
            
            blueprint_prompt = "Analiza estas referencias para crear un BLUEPRINT DE PRODUCCIÓN consistente. "
            blueprint_prompt += "Extrae: Iluminación, Texturas, Rasgos clave y Estética dominante."
            
            try:
                # Usamos un modo específico interno de veoscope (lo crearemos en el siguiente paso)
                v_res = await veoscope.process(blueprint_prompt, context=v_context)
                visual_blueprint = f"\n\n### BLUEPRINT VISUAL (CONSISTENCIA)\n{v_res.get('content', '')}"
            except Exception as ve:
                logger.warning(f"⚠️ [GENERATE] Error en análisis visual: {ve}")

        # ── 3. Construir system prompt ────────────────────────────────────────
        base_system = _STRATEGY_SYSTEM.get(req.strategy, _STRATEGY_SYSTEM["standard"])

        if brand_voice or brand_mood:
            brand_addendum = "\n\n### VOZ DE IDENTIDAD ACTIVA\n"
            if brand_voice:
                brand_addendum += f"- Voz/Arquetipo: {brand_voice}\n"
            if brand_mood:
                brand_addendum += f"- Mood/Estilo: {brand_mood}\n"
            base_system += brand_addendum
            
        # ── 2.1 Resolver Radar SOTA Boost (Si aplica) ─────────────────────────
        if req.strategy == "radar":
            try:
                radar_service = get_radar()
                sota_booster = await radar_service.research_sota_prompts(req.topic, req.format)
                base_system += f"\n{sota_booster}"
            except Exception as re:
                logger.warning(f"⚠️ [GENERATE] Radar SOTA Sensor falló: {re}")

        # ── 2.2 Resolver Cámara Soberana ──────────────────────────────────────
        if req.camera_rotate is not None:
            from src.utils.camera_translator import translate_camera_params
            cam_directive = translate_camera_params(req.camera_rotate, req.camera_vertical or 0, req.camera_zoom or 1.0)
            base_system += f"\n\n### SOVEREIGN CAMERA DIRECTIVE\n- Angle/Shot: {cam_directive}\n"

        if visual_blueprint:
            base_system += visual_blueprint

        # ── 4. Construir user prompt ──────────────────────────────────────────
        if req.mode == "ideas":
            user_msg = _IDEAS_USER.get(req.strategy, _IDEAS_USER["standard"])
        else:
            template = _FORMAT_USER.get(req.format, _FORMAT_USER["instagram"])
            # Inyección dinámica de variables según el template
            formatting_kwargs = {
                "topic": req.topic,
                "optimization_target": req.optimization,
                "lyrics": req.lyrics or "No proporcionada por el operador."
            }
            user_msg = template.format(**formatting_kwargs)

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
            "mode": req.mode or "generate",
            "meta": {
                "raw": raw_text,
                "strategy": req.strategy,
                "format": req.format,
                "topic": req.topic,
                "sovereignty": "ALEGR-IA OS — Autoría humana preservada",
            },
        }

    except Exception as e:
        logger.error(f"❌ [GENERATE] Error en motor central: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/save-to-brand")
async def save_to_brand(req: Dict[str, Any]):
    """
    Persiste un prompt o script generado en la galería del Brand Studio.
    """
    try:
        from src.services.brand_service import service as brand_service
        brand_id = req.get("brand_id", "AlegrIA")
        content = req.get("content", "")
        image_url = req.get("image_url")
        
        # Preparar análisis ficticio para el registro en galería
        analysis = {
            "name": f"Producción: {req.get('topic', 'Sin título')}",
            "adn_visual": { "estilo": "Generado vía Production Studio" },
            "contexto_narrativo": { "descripcion": content[:200] + "..." },
            "technical_prompt": content
        }
        
        # Si no hay imagen, usamos un placeholder visual
        img_to_save = image_url or "https://placehold.co/600x400/162129/FFFFFF?text=Production+Asset"
        
        res = brand_service.add_to_gallery(brand_id, img_to_save, analysis)
        if res:
            return {"status": "ok", "message": "Guardado en Brand Studio"}
        raise Exception("Error al guardar en galería")
    except Exception as e:
        logger.error(f"❌ Error en save_to_brand: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/generate-image")
async def generate_image_route(req: Dict[str, Any]):
    """
    Genera un visual previo para una escena/prompt técnico.
    """
    try:
        from src.services.provider_registry import provider_registry
        prompt = req.get("prompt", "")
        if not prompt:
            return {"status": "error", "message": "No hay prompt para visualizar"}

        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        # Estrategia 1: OpenAI (DALL-E 3)
        if openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                logger.info(f"🎨 [VISUALIZER] Intentando DALL-E 3 para: {prompt[:50]}...")
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"Cinematic production still, high fidelity, 8k, realistic: {prompt}",
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                return {"status": "ok", "image_url": response.data[0].url}
            except Exception as oe:
                err_msg = str(oe)
                if "billing_hard_limit_reached" in err_msg:
                    logger.warning("⚠️ OpenAI Billing Limit alcanzado. Intentando fallback...")
                else:
                    logger.error(f"❌ Error en DALL-E: {oe}")
        
        # Estrategia 2: Fallback Gemini (Imagen 3)
        if gemini_key:
            try:
                from src.services.llm_adapters.gemini_adapter import GeminiAdapter
                adapter = GeminiAdapter(api_key=gemini_key)
                
                logger.info(f"🎨 [VISUALIZER] Fallback a Imagen 3 para: {prompt[:50]}...")
                img_data = await adapter.generate_image(prompt)
                return {"status": "ok", "image_url": img_data}
            except Exception as ge:
                logger.error(f"❌ Error en Gemini Imagen (Fallback): {ge}")

        return {"status": "error", "message": "No hay proveedores de imagen disponibles o con saldo suficiente."}
        
    except Exception as e:
        logger.error(f"❌ Error crítico en generate_image: {e}")
        return {"status": "error", "message": str(e)}
@router.post("/override")
async def execute_override(req: OverrideRequest):
    """
    Punto de intervención humana (Override).
    Permite al operador ejecutar acciones explícitas sobre respuestas bloqueadas.
    """
    from src.services.audit_emitter import audit_emitter
    from src.utils.crypto_utils import generate_sovereign_signature, get_content_hash
    import time

    # Generación de la Firma Soberana (Trazabilidad Legal)
    c_hash = get_content_hash(req.content or "")
    signature = generate_sovereign_signature(
        intention_id=req.intention_id or "root",
        operator_id="OPERATOR_01", # TODO: Implementar gestión de perfiles de operador
        action=req.action,
        content_hash=c_hash
    )

    # AUDIT: OVERRIDE con FIRMA
    await audit_emitter.emit({
        "intention_id": req.intention_id or "human-override",
        "stage": "override",
        "timestamp": time.time(),
        "agent": "OPERATOR",
        "data": {
            "action": req.action,
            "signature": signature,
            "status": "LEGALLY_SIGNED"
        }
    })

    if req.action == "force_render":
        # El operador asume la responsabilidad y libera el contenido original
        return {
            "status": "Authorized",
            "content": req.content,
            "mode": "override_release",
            "agent_name": "OPERATOR"
        }

    if req.action == "retry_strict":
        # Reintento con instrucción de seguridad reforzada
        from src.services.anima import get_anima
        anima = get_anima()
        
        strict_prompt = f"POR FAVOR, SÉ EXTREMADAMENTE CONCISO Y TÉCNICO. EVITA RELLENO EMOCIONAL O AUTO-REFERENCIAS.\n\nMandato: {req.content}"
        
        result = await anima.generate_raw(
            message=strict_prompt
        )
        
        return result

    return {"status": "error", "message": "Acción de override no reconocida."}
