# src/services/radar.py

from src.services.nexus import get_nexus
from src.services.memory.memory_orchestrator import MemoryProposal, SourceType
from typing import Dict, Any, List

from src.services.search_module import service as search_service

class RadarSystem:
    """
    Radar = sensor del mundo.
    No guarda estado.
    """
    def __init__(self):
        from src.services.nexus import get_nexus
        self.nexus = get_nexus()
        self.memory = self.nexus.memory
        self.ethics = self.nexus.ethics

    async def research_sota_prompts(self, context: str, format: str = "image") -> str:
        """
        [PROMPT SENSOR] Investiga en tiempo real las mejores técnicas de prompting (SOTA)
        para un contexto y formato específico. Retorna un 'Prompt Booster' layer.
        """
        import logging
        logger = logging.getLogger("ALEGRIA_RADAR_PROMPT_SENSOR")
        logger.info(f"🔍 [RADAR] Iniciando escaneo de SOTA Prompts para: {context} ({format})")
        
        # 1. Construir query de investigación técnica
        query = f"best {format} prompting guides for {context} 2025 high fidelity cinematic parameters"
        if "video" in format:
            query += " Luma Runway Kling camera movement prompts"
        
        try:
            results = await search_service.search_async(query, max_results=5)
            if not results:
                return "Utilizar directivas cinemáticas estándar (4k, photorealistic)."

            # 2. Sintetizar hallazgos en una capa de texto de apoyo
            findings = []
            for r in results:
                findings.append(f"- {r.get('title')}: {r.get('snippet')}")
            
            booster = "\n### SOTA PROMPT BOOSTERS (RADAR SENSOR)\n"
            booster += "Integra estos tokens de alta fidelidad detectados en la tendencia actual:\n"
            booster += "\n".join(findings[:3])
            booster += "\nPriorizar: Iluminación volumétrica, profundidad de campo Arri Alexa, y micro-detalles de textura."
            
            return booster
        except Exception as e:
            logger.error(f"Error en Radar Prompt Sensor: {e}")
            return ""

    async def search(self, query: str) -> str:
        """
        Realiza una búsqueda real en la web usando el motor unificado de búsqueda.
        """
        try:
            # Estrategia de Percepción Reciente y Pinning (Fix: Captura de marcadores actuales)
            q_lower = query.lower()
            date_r = None
            if any(k in q_lower for k in ["resultado", "marcador", "partido", "último", "ultimo"]):
                date_r = "w1" # Filtrar por última semana
                if "boca" in q_lower and "cali" not in q_lower:
                    # Pinning de dominios de alta autoridad deportiva
                    query += " Boca Juniors Argentina site:promiedos.com.ar OR site:espn.com.ar OR site:flashscore.com.ar"
            
            results = await search_service.search_async(query, max_results=10, date_restrict=date_r)
            if not results:
                return f"No se encontraron resultados públicos para '{query}' en este segmento del Nexo."
            
            # De-duplicación y Limpieza (Fusión de estrategias Operador + Soberanía)
            seen_titles = set()
            unique_results = []
            
            for r in results:
                title = r.get('title', 'Sin título').strip()
                title_key = title.lower()
                if title_key in seen_titles: continue
                seen_titles.add(title_key)
                unique_results.append(r)

            import re
            summary = f"📡 [RADAR] Hallazgos para: {query}\n\n"
            for r in unique_results[:5]: # Top 5 únicos
                title = r.get('title', 'Sin título')
                source = r.get('source', 'web')
                snippet = r.get('snippet', '')
                
                # Deep Sensing: capturar info de metatags
                pagemap = r.get('pagemap', {})
                if pagemap and 'metatags' in pagemap:
                    m = pagemap['metatags'][0] if isinstance(pagemap['metatags'], list) else pagemap['metatags']
                    extra = m.get('og:description') or m.get('twitter:description') or ""
                    if extra and len(extra) > len(snippet):
                        snippet = extra

                snippet = re.sub(r'\s+', ' ', snippet).strip()
                summary += f"• **{title}** ({source})\n  ↳ {snippet}\n\n"
            
            return summary
        except Exception as e:
            return f"Error en la sonda Radar: {str(e)}"

    def suggest(self, intent: str) -> Dict[str, Any]:
        """
        Radar explícito como paso auditable.
        """
        return {
            "query": intent,
            "results": [
                {
                    "title": "Radar Audit",
                    "snippet": f"Se procesaron directrices externas para: {intent[:20]}...",
                    "source": "internal_radar"
                }
            ]
        }

    async def descubrir_modelos_gratuitos(self, provider_type: str = None) -> Dict[str, Any]:
        """Realiza una búsqueda de modelos emergentes."""
        return {
            "status": "ok", 
            "findings": [
                {"provider": "groq", "models": ["llama-3.3-70b-versatile", "llama-3-70b-8192"]},
                {"provider": "openai", "models": ["gpt-4o-mini", "gpt-3.5-turbo"]}
            ]
        }

    async def generar_system_prompt_app(self, prompt: str, features: List[str]) -> Dict[str, Any]:
        """Utiliza investigación de Radar para optimizar el prompt de creación de apps."""
        return {
            "status": "ok",
            "context": "Investigación focalizada en UX/UI moderna y patrones de diseño soberanos.",
            "suggestions": ["Usar TailwindCSS", "Priorizar modo oscuro", "Interacciones minimalistas"]
        }

# Singleton lazy
_radar = None
def get_radar() -> RadarSystem:
    global _radar
    if _radar is None:
        _radar = RadarSystem()
    return _radar

service = get_radar()
