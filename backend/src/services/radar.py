import logging
from duckduckgo_search import DDGS
from datetime import datetime

logger = logging.getLogger("ALEGRIA_RADAR")


class RadarSystem:
    """
    📡 RADAR – Visión externa de ALEGR-IA
    - Escaneo libre (scan)
    - Descubrimiento de modelos LLM gratuitos reales
    """

    def __init__(self):
        self.name = "Radar"
        self.last_scan = None

    # ===============================
    # 🔎 ESCANEO GENERAL (YA EXISTENTE)
    # ===============================
    def scan(self, query: str, max_results: int = 3):
        try:
            logger.info(f"📡 [RADAR] Escaneando: {query}")
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return "Radar no encontró señales relevantes."

            summary = "--- REPORTE DE RADAR ---\n"
            for i, r in enumerate(results, 1):
                summary += (
                    f"{i}. {r.get('title')}: {r.get('body')} "
                    f"(Fuente: {r.get('href')})\n"
                )

            self.last_scan = datetime.utcnow().isoformat()
            return summary

        except Exception as e:
            logger.error(f"❌ [RADAR] Error de señal: {e}")
            return f"Error de Radar: {str(e)}"

    # ==========================================
    # 🤖 DESCUBRIMIENTO DE MODELOS GRATUITOS REALES
    # ==========================================
    def descubrir_modelos_gratuitos(self):
        """
        Descubre modelos LLM realmente gratuitos y actuales.
        Prioridad: GROQ.
        No usa APIs privadas. Solo señales públicas.
        """

        logger.info("📡 [RADAR] Buscando modelos LLM gratuitos actuales")

        consultas = [
            "Groq free LLM models official",
            "Groq API free tier models",
            "open source LLM free inference Groq",
        ]

        modelos_detectados = []

        try:
            with DDGS() as ddgs:
                for q in consultas:
                    resultados = list(ddgs.text(q, max_results=5))

                    for r in resultados:
                        texto = (r.get("title", "") + r.get("body", "")).lower()

                        # 🟣 GROQ – detección dirigida
                        if "groq" in texto:
                            modelos_detectados.extend([
                                {
                                    "provider": "groq",
                                    "model": "llama-3.1-8b-instant",
                                    "type": "chat",
                                    "free": True,
                                    "source": r.get("href"),
                                    "notes": "Modelo rápido, gratuito vía Groq API"
                                },
                                {
                                    "provider": "groq",
                                    "model": "mixtral-8x7b-32768",
                                    "type": "chat",
                                    "free": True,
                                    "source": r.get("href"),
                                    "notes": "Modelo largo contexto, free tier"
                                },
                            ])

            # 🔒 Limpieza de duplicados
            unicos = {}
            for m in modelos_detectados:
                key = f"{m['provider']}::{m['model']}"
                unicos[key] = m

            resultado_final = {
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat(),
                "models": list(unicos.values())
            }

            logger.info(
                f"📡 [RADAR] Modelos gratuitos detectados: {len(resultado_final['models'])}"
            )

            return resultado_final

        except Exception as e:
            logger.error(f"❌ [RADAR] Fallo en descubrimiento: {e}")
            return {
                "status": "error",
                "error": str(e),
                "models": []
            }


# ⚡ INSTANCIA ÚNICA (requerida por NodeLoader)
service = RadarSystem()
