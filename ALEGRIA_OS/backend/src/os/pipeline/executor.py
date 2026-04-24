import json
import logging
import asyncio
from typing import Dict, Any, List

from src.os.pipeline.planner import plan_step
from src.core.handlers.registry import get_handler, handler_exists
from src.os.creative.profile.profile import get_default_profile, prune_profile
from src.os.creative.profile.updater import update_profile

logger = logging.getLogger("ALEGRIA_EXECUTOR")

async def run_pipeline(user_input: str, max_iterations: int = 5):
    """
    Motor de ejecución del OS. Orquesta el ciclo Plan -> Exec -> Observe.
    Solo ejecuta acciones validadas por el Handler Registry.
    """
    trace = []
    profile = get_default_profile()
    
    trace.append({"step": "profile_init", "data": "Perfil creativo cargado."})
    
    # Recuperar memoria reciente para contexto (Fix: Evita pérdida de contexto en mandatos encadenados)
    from src.services.nexus import get_nexus
    nexus = get_nexus()
    recent_memory = nexus.memory.get_recent(limit=6)
    
    messages = []
    for entry in recent_memory:
        role = "user" if entry.source == "user" else "assistant"
        messages.append({"role": role, "content": entry.content})
        
    # Añadimos la intención actual si no está ya (el último mensaje de memoria suele ser este)
    if not messages or messages[-1]["content"] != user_input:
        messages.append({"role": "user", "content": f"Intención operativa: {user_input}"})
    else:
        # Enriquecemos el último mensaje para que el Planner sepa que es el objetivo actual
        messages[-1]["content"] = f"Intención operativa: {messages[-1]['content']}"
    
    state = {"improve_count": 0, "goal": user_input, "profile": profile}
    final_output = None
    
    try:
        for i in range(max_iterations):
            trace.append({"step": "PLANNER_THOUGHT", "data": f"Ciclo {i+1}: Generando plan soberano..."})
            
            # 1. PLAN: Delegamos la generación del paso al Planner
            profile_context = f"Estilo: {profile.get('style')} | Prefs: {profile.get('preferences')}"
            step = await plan_step(messages, profile_context)
            
            # 🛡️ MANDATORY ACTION GATE (Fix: Bloqueo de simulaciones textuales)
            # Si estamos en el primer ciclo de una ejecución soberana, EXIGIMOS una acción.
            if i == 0 and step["type"] == "respond":
                logger.warning("🛡️ [EXECUTOR] Bloqueo de simulación: Se requiere acción técnica.")
                trace.append({
                    "step": "SIMULATION_BLOCK", 
                    "data": "El Planner intentó responder con texto en lugar de ejecutar una herramienta."
                })
                # Inyectamos el error y forzamos reintento (una sola vez para evitar bucles)
                messages.append({
                    "role": "user", 
                    "content": "ERROR: No se permite respuesta textual. DEBES ejecutar una herramienta del Registry (Action Contract). Si ya tienes la respuesta final, usa 'OS_Final_Answer'."
                })
                continue

            if step["type"] == "error":
                trace.append({"step": "PLANNER_ERROR", "data": step.get("thought", "Error desconocido")})
                break
                
            # 2. VALIDATE: Contrato de Acción (Proposal vs Authorization)
            from src.core.kernel import kernel
            is_authorized, reason = kernel.validate_step(step, state)
            
            trace.append({
                "step": "PLANNER_PROPOSAL",
                "thought": step["thought"],
                "action": step.get("action", "Respond"),
                "authorized": is_authorized
            })
            
            if not is_authorized:
                logger.warning(f"❌ [EXECUTOR] Bloqueo de seguridad: {reason}")
                trace.append({"step": "PLANNER_SECURITY_BLOCK", "data": reason})
                messages.append({"role": "user", "content": f"ERROR DE SEGURIDAD: {reason}"})
                continue

            # 3. EVALUAR: Si es respuesta final, terminamos
            if step["type"] == "respond" or step.get("action") == "OS_Final_Answer":
                final_output = step.get("response") or step.get("args", {}).get("answer") or str(step.get("args"))
                trace.append({"step": "PLANNER_COMPLETION", "data": "Objetivo alcanzado."})
                break
                
            # 3. EXECUTE: Ejecución vía Registry
            action_id = step["action"]
            args = step["args"]
            
            if handler_exists(action_id):
                trace.append({"step": "PLANNER_ACTION_EXEC", "data": f"Ejecutando: {action_id}"})
                
                try:
                    # Recuperar handler dinámicamente
                    h_info = get_handler(action_id)
                    module_name, func_name = h_info["handler"].rsplit(".", 1)
                    
                    import importlib
                    module = importlib.import_module(module_name)
                    handler_func = getattr(module, func_name)
                    
                    # Ejecutar (los handlers esperan un string JSON por ahora por compatibilidad)
                    input_str = json.dumps(args) if isinstance(args, (dict, list)) else str(args)
                    observation = await handler_func(input_str)
                    
                    # ⚔️ REGLA SOBERANA: Si el mandato fue una herramienta de sensor (Radar, etc), terminamos YA.
                    # Evita que el LLM añada narrativa o placeholders en la siguiente iteración.
                    TERMINAL_ACTIONS = ["radar.search", "dev.execute", "research_first", "news.clarin", "system.navigate"]
                    if action_id in TERMINAL_ACTIONS:
                        logger.info(f"🎯 [EXECUTOR] Acción Terminal '{action_id}' detectada. Bloqueando narrativa LLM.")
                        trace.append({"step": "PLANNER_OBSERVATION", "data": "Resultado final capturado del sensor."})
                        return {
                            "status": "success",
                            "output": observation,
                            "type": "tool",
                            "trace": trace,
                            "final_profile": state["profile"]
                        }

                    trace.append({"step": "PLANNER_OBSERVATION", "data": f"Resultado de {action_id} capturado."})
                    messages.append({"role": "assistant", "content": json.dumps(step)})
                    messages.append({"role": "user", "content": f"Observación de {action_id}: {observation}"})
                    
                except Exception as e:
                    logger.error(f"❌ [EXECUTOR] Error ejecutando {action_id}: {e}")
                    observation = f"Error de ejecución: {str(e)}"
                    messages.append({"role": "user", "content": observation})
            else:
                # BLOQUEO DE SEGURIDAD: No se ejecuta nada que no esté en el Registry
                error_msg = f"Acción '{action_id}' no está registrada o habilitada."
                trace.append({"step": "PLANNER_SECURITY_BLOCK", "data": error_msg})
                messages.append({"role": "user", "content": f"Error: {error_msg}"})
    except Exception as e:
        logger.error(f"❌ [EXECUTOR] Pipeline crash: {e}")
        return {
            "status": "error",
            "output": f"Error crítico en el motor de ejecución: {str(e)}",
            "trace": trace + [{"step": "EXECUTOR_CRASH", "data": str(e)}],
            "final_profile": state["profile"]
        }
            
    final_status = "success" if final_output else "stopped"
    return {
        "status": final_status,
        "output": final_output or "Límite de iteraciones alcanzado sin respuesta final.",
        "type": "llm", # Por defecto es orquestación del LLM
        "trace": trace,
        "final_profile": state["profile"]
    }
