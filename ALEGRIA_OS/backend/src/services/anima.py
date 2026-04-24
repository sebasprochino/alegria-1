"""
ALEGR-IA OS — src/services/anima.py
===================================
 PRINCIPIO: Anima NO decide. Anima NO filtra. Anima CONSTRUYE.
 
 ARQUITECTURA DE RESILIENCIA (N1/N3):
   - N1 (Runtime Crítico): Generación LLM. Nunca debe fallar por servicios auxiliares.
   - N2 (Enriquecimiento): Clasificación y contexto. Robustez con fallbacks.
   - N3 (Persistencia/Auditoría): DB, Logs, Métricas. Siempre no bloqueante y fail-silent.
 
 Responsabilidades únicas:

  1. Recibir clasificación de NEXUS.
  2. Solicitar al AnimaBuilder el contexto ACSP.
  3. Ejecutar la llamada al LLM (Generación).
  4. Formatear para el Kernel (Audit).
"""

import logging
import json
from typing import Dict, Any, Optional
from src.services.anima_builder import get_anima_builder

logger = logging.getLogger("ALEGRIA_ANIMA")

class AnimaSystem:
    """
    Anima — El Constructor de Ejecución.
    Transforma la intención clasificada en instrucciones técnicas (ACSP).
    """

    def __init__(self, nexus):
        self.nexus = nexus
        self.builder = get_anima_builder()

    async def generate_raw(
        self, 
        message: str, 
        file_metadata: Optional[Dict[str, Any]] = None,
        forced_classification: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Paso 1: NEXUS clasifica.
        Paso 2: ANIMA construye.
        Paso 3: LLM genera.
        """
        import traceback
        import os
        logger.info(f"📍 [ANIMA TRACE] Executing generate_raw from {os.path.abspath(__file__)}")
        logger.debug(f"📍 [ANIMA STACK]\n{''.join(traceback.format_stack())}")
        
        from src.services.provider_registry import service as provider_registry
        from src.services.audit_emitter import audit_emitter
        import time
        import uuid
        
        intention_id = str(uuid.uuid4())[:8]

        # --- PASO 1: Clasificación Soberana (NEXUS) ---
        classification = forced_classification or self.nexus.classify_request(message)
        logger.info(f"⚖️ [ANIMA] Pedido clasificado como: {classification['type']}")

        # AUDIT: RECIBIDO
        await audit_emitter.emit({
            "intention_id": intention_id,
            "stage": "received",
            "timestamp": time.time(),
            "agent": classification["type"].upper(),
            "data": {"message": message[:100] + "..." if len(message) > 100 else message}
        })

        # --- PASO 2: Construcción de Contexto (ANIMA BUILDER) ---
        # El builder nos da el System Prompt y el esquema esperado
        context = self.builder.build_acsp_context(classification, message)
        
        # --- PASO 3: Preparación de Modalidad ---
        modality = "vision" if classification["type"] == "visual" else "text"
        messages = [{"role": "user", "content": message}]
        
        # Inyectar imagen si es necesario
        if modality == "vision" and file_metadata and file_metadata.get("data"):
            messages[0]["content"] = [
                {"type": "text", "text": message},
                {"type": "image_url", "image_url": {"url": file_metadata["data"]}}
            ]

        # --- PASO 4: Generación Soberana (LLM) ---
        try:
            # AUDIT: PROVIDER (INICIO)
            t_start_llm = time.time()
            await audit_emitter.emit({
                "intention_id": intention_id,
                "stage": "provider",
                "timestamp": t_start_llm,
                "agent": classification["type"].upper(),
                "data": {"agent_template": context["agent"], "modality": modality}
            })

            # Consolidamos el System Prompt del Builder
            full_system = f"{context['system_prompt']}\n\n{context['user_payload']}"
            
            raw_text = await provider_registry.chat(
                messages=messages,
                system=full_system,
                modality=modality
            )
            
            t_end_llm = time.time()
            duration_llm = t_end_llm - t_start_llm
            logger.info(f"🔵 [ANIMA] Generación completada vía {context['agent']} ({duration_llm:.2f}s).")
            
            # ─────────────────────────────
            # PARSEO DEL ESQUEMA HÍBRIDO
            # ─────────────────────────────
            import json
            try:
                # Extraer JSON en caso de que el LLM agregue backticks (```json ... ```)
                clean_text = raw_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()
                
                parsed_data = json.loads(clean_text)
                if "is_ambiguous" not in parsed_data:
                    raise ValueError("Schema no cumple el contrato híbrido")
            except Exception as e:
                logger.warning(f"⚠️ [ANIMA] Fallo parseo de contrato híbrido: {e}. Forzando ambigüedad de seguridad.")
                parsed_data = {
                    "is_ambiguous": True,
                    "clarification_question": "El sistema arrojó una respuesta no estructurada. ¿Querés intentar de nuevo?",
                    "options": [
                        {"id": "opt_retry", "text": "Reintentar mandato"},
                        {"id": "opt_cancel", "text": "Cancelar ejecución"}
                    ],
                    "technical_payload": None
                }
            
            # Inyectar el payload parseado en raw_text (opcional, o pasarlo como campo nuevo)
            # Pasamos raw_text original al antigravity, pero el JSON estructurado a la respuesta final.
            
            # ─────────────────────────────
            # ANTIGRAVITY CHECK
            # ─────────────────────────────
            from src.services.developer import developer_antigravity
            
            dev_check = developer_antigravity.review(
                response=raw_text,
                context={"request_type": classification["type"]}
            )

            await audit_emitter.emit({
                "intention_id": intention_id,
                "stage": "antigravity",
                "timestamp": time.time(),
                "agent": "DEVELOPER",
                "data": dev_check
            })

            if dev_check["risk"]:
                raw_text = (
                    raw_text +
                    "\n\n---\n⚠️ Developer Advisory:\n" +
                    "\n".join(f"- {i}" for i in dev_check["issues"])
                )
            
            # --- PASO 5: Filtrado y Auditoría Semántica (RuleEngine) ---
            from src.core.rule_engine import service as rule_engine
            
            t_start_guard = time.time()
            # El RuleEngine analiza si la salida es segura, coherente y soberana
            filtered = await rule_engine.filter_output(
                {
                    "raw": raw_text,
                    "source": "llm",
                    "intention_id": intention_id
                },
                mode="execution"
            )
            t_end_guard = time.time()
            
            status = filtered.get("status", "Authorized")
            alert_level = filtered.get("analysis", {}).get("alert_level", "none")

            # AUDIT: GUARD (SEGURIDAD)
            await audit_emitter.emit({
                "intention_id": intention_id,
                "stage": "guard",
                "timestamp": t_end_guard,
                "agent": "KERNEL",
                "data": {
                    "alert_level": alert_level,
                    "duration": t_end_guard - t_start_guard,
                    "score": filtered.get("analysis", {}).get("confidence", 1.0)
                }
            })

            # AUDIT: RESPONSE (EXITO)
            await audit_emitter.emit({
                "intention_id": intention_id,
                "stage": "response",
                "timestamp": time.time(),
                "agent": classification["type"].upper(),
                "data": {
                    "length": len(raw_text) if raw_text else 0, 
                    "status": status,
                    "duration": time.time() - t_start_llm
                }
            })
            
            # Si el Kernel duda o rechaza, devolvemos el objeto bloqueado para intervención humana
            # REGLA DE ORO: No modificamos el raw, pero lo encapsulamos según el status.
            return {
                "status": status,
                "raw": raw_text,
                "content": filtered.get("content", parsed_data.get("clarification_question", "")),
                
                # Campos del contrato híbrido:
                "is_ambiguous": parsed_data.get("is_ambiguous", True),
                "clarification_question": parsed_data.get("clarification_question"),
                "options": parsed_data.get("options", []),
                "technical_payload": parsed_data.get("technical_payload"),
                
                "blocked_response": raw_text if status != "Authorized" else None,
                "alert_level": alert_level,
                "analysis": filtered.get("analysis"),
                "agent": context["agent"],
                "agent_name": context["agent"].upper(),
                "intention_id": intention_id,
                "modality": modality,
                "message_ref": message
            }

        except Exception as e:
            t_error = time.time()
            logger.error(f"❌ [ANIMA] Error en generación: {e}")
            
            # AUDIT: ERROR
            await audit_emitter.emit({
                "intention_id": intention_id,
                "stage": "error",
                "timestamp": t_error,
                "agent": classification["type"].upper(),
                "data": {"error": str(e), "duration": t_error - t_start_llm}
            })

            logger.error(f"[ANIMA FALLBACK] {e}")

            return {
                "status": "ok",
                "raw": "FALLBACK_RESPONSE",
                "content": "Sistema activo. No hay conexión con modelos externos.",
                "response": "Sistema activo. No hay conexión con modelos externos.",
                "provider": "fallback",
                "source": "fallback",
                "message_ref": message,
                "intention_id": intention_id
            }


    def format_response(self, filtered: Dict[str, Any]) -> Dict[str, Any]:
        """
        Empaqueta el resultado final auditado por el KERNEL para la UI.
        """
        status = filtered.get("status", "Authorized")
        content = filtered.get("content", "")
        raw = filtered.get("raw", "")
        
        response = {
            "status": status,
            "response": content,
            "raw_attempt": raw,
            "mode": filtered.get("mode", "conversation"),
            "meta": filtered.get("meta", {}),
            "audit": filtered.get("audit", {}), # Inyectado por el Kernel
            
            # Pasamos los campos híbridos al frontend
            "is_ambiguous": filtered.get("is_ambiguous", False),
            "clarification_question": filtered.get("clarification_question"),
            "options": filtered.get("options", []),
            "technical_payload": filtered.get("technical_payload")
        }
        
        if "trace" in filtered:
            response["trace"] = filtered["trace"]
            
        return response

# Singleton
_anima_instance: AnimaSystem | None = None

def get_anima() -> AnimaSystem:
    global _anima_instance
    if _anima_instance is None:
        from src.services.nexus import get_nexus
        _anima_instance = AnimaSystem(get_nexus())
    return _anima_instance
