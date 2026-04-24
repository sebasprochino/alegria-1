# backend/src/os/pipeline/detective.py
import logging
import json
from datetime import datetime
from src.services.memory.user_lexicon import get_lexicon
from src.services.provider_registry import service as provider_registry

logger = logging.getLogger("ALEGRIA_DETECTIVE")

PROMPT_DETECTIVE = """
Eres el 'Detective Contextual' de ALEGR-IA OS. Tu misión es convertir el historial en ESTRATEGIAS PREDICTIVAS.

Sigue este flujo (Blueprint de Memoria Contextual):
1. AUDITORÍA DE CONVERSACIONES: Analiza chats anteriores de forma autónoma.
2. EXTRACCIÓN DE PATRONES: Identifica dudas recurrentes (ej: sobre implementación de IA, optimización, bloqueos).
3. RESOLUCIÓN ANTICIPADA: Genera soluciones proactivas ANTES de que el usuario haga la siguiente pregunta.

Responde ÚNICAMENTE en JSON plano:
{
  "auditoria": "resumen ejecutivo de lo hablado",
  "patrones_identificados": ["patrón 1", "patrón 2"],
  "estrategias_predictivas": [
    {
      "solucion": "explicación clara de la solución anticipada", 
      "accion_sugerida": "comando o acción concreta", 
      "justificacion": "basado en el patrón X"
    }
  ]
}
"""

class DetectivePipeline:
    def __init__(self):
        # Referencia diferida a Nexus para acceder a memoria y léxico
        self._nexus = None

    @property
    def nexus(self):
        if self._nexus is None:
            from src.services.nexus import get_nexus
            self._nexus = get_nexus()
        return self._nexus

    @property
    def memory(self):
        return self.nexus.memory

    @property
    def lexicon(self):
        return self.nexus.lexicon

    async def run_audit(self):
        logger.info("🕵️ [DETECTIVE] Iniciando auditoría autónoma de conversaciones...")
        
        try:
            # 1. Obtener historial sustancial (últimos 30 mensajes para detectar patrones reales)
            recent = self.memory.get_recent(limit=30)
            history_text = "\n".join([f"{m.role if hasattr(m, 'role') else m.source}: {m.content}" for m in recent])
            
            if len(recent) < 5:
                return {
                    "status": "insufficient_data", 
                    "message": "Espera a tener más interacción para generar estrategias predictivas sólidas."
                }

            # 2. Análisis profundo con LLM Soberano (Prioridad Groq Llama 3.3 70b o Llama 4 Scout)
            res_raw = await provider_registry.chat(
                messages=[{"role": "user", "content": f"{PROMPT_DETECTIVE}\n\nHISTORIAL:\n{history_text}"}],
                temperature=0.2
            )
            
            # 3. Limpieza y parseo
            cleaned = res_raw.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[-1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[-1].split("```")[0].strip()
            
            analysis = json.loads(cleaned)
            analysis["timestamp"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "type": "insight", # 👈 Marcado como insight para la UI
                "category": "context_enrichment",
                "output": analysis
            }
            
        except Exception as e:
            logger.error(f"❌ [DETECTIVE] Error fatal en pipeline predictivo: {e}")
            return {
                "status": "error",
                "message": f"El detective contextual falló: {str(e)}"
            }

    async def get_proactive_hint(self):
        """Genera un saludo proactivo basado en el último análisis y el contexto de marca activo."""
        try:
            from src.services.brand_service import service as brand_service
            active_brand = brand_service.get_active_brand()
            brand_name = active_brand.get('name', 'AlegrIA')
            
            res = await self.run_audit()
            if res["status"] == "success":
                insight = res["output"]
                # Normalización de claves (plural vs singular)
                strategies = insight.get("estrategias_predictivas") or insight.get("estrategia_predictiva") or []
                
                if strategies and isinstance(strategies, list) and len(strategies) > 0:
                    top = strategies[0]
                    # Normalización de campos de la estrategia
                    sugerencia = top.get("solucion") or top.get("sugerencia") or top.get("accion_sugerida") or "seguir optimizando"
                    patron = (insight.get('patrones_identificados') or ["el análisis de marca"])[0]
                    
                    return {
                        "text": f"Hola Sebastián, estuve auditando el avance de '{brand_name}'. Basado en {patron}, mi sugerencia para hoy es: {sugerencia}",
                        "insight": insight
                    }
            
            # Fallback seguro
            return {
                "text": f"Hola Sebastián. El BrandKit de '{brand_name}' está listo para ser expandido. ¿En qué dirección vamos hoy?",
                "insight": {"auditoria": "Sistema listo para ejecución.", "patrones_identificados": ["Inicio de sesión"], "estrategias_predictivas": []}
            }
        except Exception as e:
            logger.error(f"❌ [DETECTIVE] Error crítico en get_proactive_hint: {e}")
            return {
                "text": "Hola Sebastián. Sistema ALEGR-IA OS operativo. ¿Iniciamos una nueva fase de producción?",
                "insight": {"error": str(e)}
            }

# Singleton instance
service = DetectivePipeline()
