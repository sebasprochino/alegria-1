import json
import logging
import re
from typing import Dict, Any, List, Optional
from src.services.provider_registry import service as provider_registry
from src.core.handlers.registry import list_handlers

logger = logging.getLogger("ALEGRIA_PLANNER")

PLANNER_SYSTEM_PROMPT = """
Eres el OS Planner (ALEGR-IA OS), un agente soberano de razonamiento.
Tu objetivo es cumplir el mandato del operador usando las herramientas disponibles.

### 🧬 FILOSOFÍA DE CONTROL (PROMPT LIMITATION)
Este prompt NO te guía, te LIMITA. Tienes terminantemente prohibido actuar fuera de los márgenes definidos. No eres un asistente creativo; eres un motor de ejecución técnica.

### 📜 Frase Base
El usuario define. Ánima interpreta. Léxico optimiza. Nexus recuerda. Radar obtiene. El sistema ejecuta.

### ⚔️ CONTRATO DE ACCIÓN (MANDATORIO)
1. Tu respuesta debe ser ÚNICAMENTE un objeto JSON válido.
2. Está PROHIBIDO cualquier texto antes o después del JSON.
3. Está PROHIBIDO saludar, explicar pasos o confirmar que estás buscando información.
4. Si necesitas pensar, usa el campo "thought" dentro del JSON.

### 🛠️ REALIDAD OPERATIVA (Registry)
1. Solo existen las herramientas listadas en 'HERRAMIENTAS DISPONIBLES'.
2. Si una herramienta no está en la lista, el sistema NO puede ejecutarla. 
3. NUNCA inventes parámetros o nombres de acciones fuera del Registro.
4. Está PROHIBIDO simular la salida de una herramienta o inventar observaciones.

### REGLAS DE ORO
1. Usa el ciclo ReAct: Pensamiento -> Acción -> Observación.
2. Si tienes la respuesta final, usa la acción 'OS_Final_Answer'.

### HERRAMIENTAS DISPONIBLES
{tools}

### FORMATO DE SALIDA (ÚNICO PERMITIDO)
{{
  "thought": "tu razonamiento estratégico",
  "action": "Nombre_De_La_Acción",
  "args": {{ ... parámetros de la acción ... }}
}}
"""

def detect_fake_execution(raw: str) -> bool:
    """
    Detecta si el LLM está simulando una ejecución (Markdown blocks o marcadores de observación).
    """
    # Patrones comunes de simulación
    pats = [
        r"```[\s\S]*?```",
        r"Observation:",
        r"Observación:",
        r"Result:",
        r"\[insertar",
        r"\[resultado",
        r"\[v[íi]deo\]",
        r"buscando información en",
        r"buscando en radar"
    ]
    for pat in pats:
        if re.search(pat, raw, re.IGNORECASE):
            return True
    return False

def normalize_step(data: Dict[str, Any], raw: str = "") -> Dict[str, Any]:
    """
    Estandariza la propuesta del LLM. 
    Cambia 'type: action' por 'type: proposed_action' para ACSP v1.1.
    """
    if detect_fake_execution(raw):
        logger.warning(f"⚠️ [PLANNER] Simulación detectada en crudo: {raw[:100]}...")
        return {
            "type": "error",
            "thought": "Detección de simulación de ejecución (Fake Execution). Bloqueo soberano.",
            "reason": "simulation_detected"
        }

    action = data.get("action")
    thought = data.get("thought", "")
    args = data.get("args") or data.get("action_input") or {}
    
    if action:
        return {
            "type": "proposed_action",
            "thought": thought,
            "action": action,
            "args": args
        }
    
    return {
        "type": "respond",
        "thought": thought,
        "response": data.get("response", "No se detectó acción ni propuesta.")
    }

async def plan_step(messages: List[Dict[str, str]], profile_context: str) -> Dict[str, Any]:
    """
    Llama al LLM para generar el siguiente paso del plan.
    """
    handlers = list_handlers()
    tools_desc = "\n".join([f"- {k}: {v}" for k, v in handlers.items()])
    tools_desc += "\n- OS_Final_Answer: Entrega el resultado final al operador."
    
    system_prompt = PLANNER_SYSTEM_PROMPT.format(
        tools=tools_desc,
        profile_context=profile_context
    )
    
    raw_response = await provider_registry.chat(
        messages=messages,
        system=system_prompt
    )
    
    # Limpieza de JSON
    match = re.search(r'\{.*\}', raw_response, re.DOTALL)
    json_str = match.group(0) if match else raw_response
    
    try:
        data = json.loads(json_str)
        return normalize_step(data, raw_response)
    except json.JSONDecodeError:
        logger.warning(f"⚠️ [PLANNER] Error parseando JSON: {raw_response}")
        return {
            "type": "error",
            "thought": "Error de formato en la respuesta del modelo.",
            "raw": raw_response
        }
