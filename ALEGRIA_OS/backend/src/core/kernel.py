"""
ALEGRIA OS - Sovereign Kernel Layer
Wraps the Alegria SDK (ACSP v1.1) to provide strict governance
over the creative system.

Constitution (SDK) + Government (Kernel) + Economy (OS Creative Pipeline)
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pydantic import ValidationError
from src.alegria_sdk import AlegriаSDK, AdapterConfig, GroqAdapter, AdapterCascade
from src.core.handlers import registry

logger = logging.getLogger("ALEGRIA_KERNEL")

class SovereignKernel:
    """
    La Capa Kernel gobierna SI se puede ejecutar.
    Utiliza el SDK oficial para validar la intención y asegurar la soberanía.
    """

    def __init__(self):
        # Configuración del motor de gobernanza
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            logger.warning("⚠️ [KERNEL] No GROQ_API_KEY found. Governance node might be degraded.")
        
        self.sdk = AlegriаSDK.from_groq(api_key=api_key)
        # Caché de payloads para mantener integridad entre /chat y /execute
        self._payload_cache: Dict[str, Any] = {}
        # Memoria de la última intención ejecutada con éxito (Context Anchoring)
        self._last_session_context: Dict[str, Any] = {}
        logger.info("✅ [KERNEL] Nucleo soberano inicializado (ACSP v1.1)")

    def update_session_context(self, action: str, data: Any):
        """Actualiza el ancla de contexto con el resultado de la última ejecución."""
        self._last_session_context = {
            "action": action,
            "data": data,
            "integrity": self.get_audit_trail()
        }
        logger.info(f"💾 [KERNEL] Contexto actualizado: '{action}'")

    def get_session_context(self) -> Dict[str, Any]:
        """Retorna el ancla de contexto actual."""
        return self._last_session_context

    async def process_intent(self, objective: str, constraints: List[str] = None) -> Dict[str, Any]:
        """
        Paso 1: Procesa la intención del operador.
        Enriquece el objetivo con el contexto anclado de la sesión.
        """
        # Enriquecimiento de contexto (Fix #3)
        if self._last_session_context:
            action = self._last_session_context.get("action")
            data = str(self._last_session_context.get("data"))[:1000] # Capamos para no saturar
            objective = f"[CONTEXTO: última acción '{action}' retornó: {data}]\n\n{objective}"
            logger.info("🔗 [KERNEL] Objetivo enriquecido con contexto previo.")

        try:
            payload = await self.sdk.process(
                objective=objective,
                constraints=constraints or [],
                timestamp=True
            )
            
            # Guardamos el payload en cache para el siguiente paso (select)
            self._payload_cache[payload.intention.id] = payload

            # Retornamos una estructura compatible con el frontend de ALEGRIA OS
            # Los paths son estrategias de interpretación (UUIDs), no comandos directos.
            paths = []
            for p in payload.state.paths:
                is_valid, reason = self.validate_path(p)
                if is_valid:
                    paths.append({
                        "id": p.id,
                        "type": getattr(p, "type", "strategy"),
                        "strategy": p.strategy,
                        "rationale": p.rationale,
                        "tone": p.tone,
                        "risk": "bajo" # Podría extraerse semánticamente
                    })
                else:
                    logger.warning(f"⚠️ [KERNEL] Ignorando path estructuralmente inválido ({reason}): {p.id}")

            return {
                "status": payload.state.status if paths else "blocked",
                "intention_id": payload.intention.id,
                "paths": paths,
                "blocked": payload.state.status == "blocked" or not paths,
                "reason": getattr(payload.state, "block_reason", None) or ("No viable execution paths" if not paths else None),
            }
        except ValidationError as ve:
            # Capturamos errores de validación de Pydantic (ej. texto muy corto)
            logger.warning(f"⚖️ [KERNEL] Intención bloqueada por validación: {ve.errors()[0]['msg']}")
            return {
                "status": "blocked",
                "blocked": True,
                "reason": "La intención es demasiado breve o ambigua para ser procesada soberanamente. (Mínimo 5 caracteres)."
            }
        except Exception as e:
            logger.error(f"❌ [KERNEL] Error procesando intención: {e}")
            return {"status": "error", "message": str(e)}

    def authorize_path(self, intention_id: str, path_id: str) -> Any:
        """
        Paso 2: Validación humana explícita (SELECT).
        Transiciona la intención a estado 'ready' en el SDK.
        """
        # Eliminada la validación de handler directo porque path_id es un UUID de estrategia
        # y no una función del registro.

        # Bypass Soberano para comandos directos (Fix #2)
        if intention_id == "direct_cmd":
            logger.info(f"⚖️ [KERNEL] Autorizando comando directo: {path_id}")
            return None # O un mock object si el SDK lo requiere
            
        payload = self._payload_cache.get(intention_id)
        if not payload:
            logger.error(f"❌ [KERNEL] Payload no encontrado para ID: {intention_id}")
            raise ValueError("Sesión soberana expirada o inválida.")

        try:
            authorized_payload = self.sdk.select(payload, path_id)
            logger.info(f"⚖️ [KERNEL] Intención autorizada por operador: {path_id}")
            return authorized_payload
        except Exception as e:
            logger.error(f"❌ [KERNEL] Fallo en autorización soberana: {e}")
            raise

    async def execute_constitutionally(self, payload: Any) -> Dict[str, Any]:
        """
        Paso 3: Ejecución controlada por el Kernel.
        Asegura que la salida respeta el contrato ACSP.
        """
        try:
            # El SDK ejecuta el path seleccionado usando su motor interno
            result = await self.sdk.execute(payload)
            # Limpiamos cache
            if payload.intention.id in self._payload_cache:
                del self._payload_cache[payload.intention.id]
                
            return result
        except Exception as e:
            logger.error(f"❌ [KERNEL] Violación de protocolo en ejecución: {e}")
            return {"status": "violation", "error": str(e)}

    def validate_path(self, path: Any) -> Tuple[bool, str]:
        """
        Validación estructural de una estrategia propuesta.
        Asegura que el path sea una declaración de intenciones y no una ejecución encubierta.
        """
        path_type = getattr(path, "type", None)
        if path_type != "strategy":
            return False, f"invalid_path_type ({path_type})"
            
        if not getattr(path, "strategy", None):
            return False, "missing_strategy"
            
        return True, "ok"

    def validate_step(self, step: Dict[str, Any], state: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Validación soberana de un paso propuesto por el Planner.
        Asegura que la acción sea ejecutable y autorizada.
        """
        step_type = step.get("type")
        if step_type != "proposed_action" and step_type != "action":
            return True, "ok" # Respuestas directas no requieren validación de registro
            
        action = step.get("action")
        if not registry.handler_exists(action) and action != "OS_Final_Answer":
            logger.warning(f"❌ [KERNEL] Rechazo de acción no registrada: {action}")
            return False, f"La acción '{action}' no es una herramienta registrada en el OS."
            
        # Aquí se podrían añadir reglas de gobernanza adicionales por estado
        logger.info(f"⚖️ [KERNEL] Acción '{action}' validada estructuralmente.")
        return True, "ok"

    def audit_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Auditoría Pura (Arquitectura Operativa Definitiva).
        
        Evalúa el output sin modificarlo, sin bloqueos y sin deducciones internas.
        Registra cumplimiento de contrato ACSP.
        """
        audit_report = {
            "valid_json": False,
            "acsp_compliant": False,
            "structure_score": 0.0,
            "issues": []
        }

        # 1. Validación de JSON
        try:
            data = json.loads(raw_output)
            audit_report["valid_json"] = True
            audit_report["structure_score"] += 0.5
        except Exception:
            # Si no es JSON, podría ser texto libre (válido para diálogo)
            audit_report["issues"].append("free_text_output")
            return audit_report

        # 2. Validación ACSP (Acciones)
        # Un ACSP válido contiene al menos una acción técnica
        if isinstance(data, dict):
            if "action" in data or "steps" in data:
                audit_report["acsp_compliant"] = True
                audit_report["structure_score"] += 0.5
            else:
                audit_report["issues"].append("missing_acsp_keys")
        else:
            audit_report["issues"].append("not_a_dictionary")

        logger.info(f"🧾 [KERNEL] Auditoría completada. Score: {audit_report['structure_score']}")
        return audit_report

    def get_audit_trail(self) -> str:
        """Retorna la cadena de hashes de integridad del SDK."""
        return self.sdk.get_audit()

# Singleton instance
kernel = SovereignKernel()
