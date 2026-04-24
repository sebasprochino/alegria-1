import feedparser
import httpx
import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("ALEGRIA_NEWS_SERVICE")

class NewsService:
    """
    Agregador de noticias y clima en tiempo real para ALEGR-IA.
    """
    
    # RSS de Google News Argentina (o global)
    RSS_FEEDS = {
        "general": "https://news.google.com/rss?hl=es-419&gl=AR&ceid=AR:es-419",
        "tecnologia": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=es-419&gl=AR&ceid=AR:es-419",
        "deportes": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=es-419&gl=AR&ceid=AR:es-419",
        "dinero": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=es-419&gl=AR&ceid=AR:es-419"
    }

    def __init__(self):
        self.cached_news = {}
        self.last_update = None

    async def get_dashboard_data(self, category: str = "general") -> Dict[str, Any]:
        """
        Retorna el conjunto de datos para el dashboard (Noticias + Clima).
        """
        try:
            # Ejecutamos en paralelo para máxima eficiencia
            news_task = self.fetch_news(category)
            weather_task = self.fetch_weather("-27.4691", "-58.8306") # Corrientes, AR
            
            news, weather = await asyncio.gather(news_task, weather_task)
            
            return {
                "status": "ok",
                "news": news,
                "weather": weather,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error obteniendo dashboard data: {e}")
            return {"status": "error", "message": str(e)}

    async def fetch_news(self, category: str) -> List[Dict[str, Any]]:
        url = self.RSS_FEEDS.get(category, self.RSS_FEEDS["general"])
        try:
            # feedparser no es async, usamos run_in_executor
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, lambda: feedparser.parse(url))
            
            processed = []
            for entry in feed.entries[:15]:
                # Limpiar el título (Google News suele poner la fuente al final: "Título - Fuente")
                title_parts = entry.title.rsplit(' - ', 1)
                title = title_parts[0]
                source = title_parts[1] if len(title_parts) > 1 else "Noticias"
                
                processed.append({
                    "id": entry.id,
                    "title": title,
                    "link": entry.link,
                    "source": source,
                    "time": entry.published,
                    "summary": entry.get("summary", ""),
                    # Imagen: Google News RSS no trae imagen directa de forma fácil, 
                    # usaremos un placeholder de calidad o intentaremos extraerla si es posible.
                    "image": self._get_placeholder_for_source(source)
                })
            return processed
        except Exception as e:
            logger.error(f"Error fetching news RSS: {e}")
            return []

    async def fetch_weather(self, lat: str, lon: str) -> Dict[str, Any]:
        """
        Obtiene clima real usando Open-Meteo (Gratis, sin API Key).
        """
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    current = data.get("current_weather", {})
                    daily = data.get("daily", {})
                    
                    return {
                        "temp": current.get("temperature"),
                        "condition": self._map_weather_code(current.get("weathercode")),
                        "wind": current.get("windspeed"),
                        "city": "Corrientes",
                        "forecast": [
                            {
                                "day": "Hoy",
                                "max": daily.get("temperature_2m_max", [0])[0],
                                "min": daily.get("temperature_2m_min", [0])[0],
                                "code": daily.get("weathercode", [0])[0]
                            },
                            {
                                "day": "Mañana",
                                "max": daily.get("temperature_2m_max", [0, 0])[1],
                                "min": daily.get("temperature_2m_min", [0, 0])[1],
                                "code": daily.get("weathercode", [0, 0])[1]
                            }
                        ]
                    }
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
        return {"temp": "--", "condition": "Despejado", "city": "Corrientes"}

    def _map_weather_code(self, code: int) -> str:
        # Simplificación de códigos WMO
        mapping = {
            0: "Despejado", 1: "Mayormente Despejado", 2: "Parcialmente Nublado", 3: "Nublado",
            45: "Niebla", 51: "Llovizna", 61: "Lluvia Ligera", 63: "Lluvia", 80: "Chubascos",
            95: "Tormenta"
        }
        return mapping.get(code, "Despejado")

    def _get_placeholder_for_source(self, source: str) -> str:
        # Generar una imagen de Unsplash basada en la fuente o categoría para que no se vea vacío
        import random
        topics = ["news", "business", "technology", "city", "world", "abstract"]
        topic = random.choice(topics)
        return f"https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop"

# Singleton
service = NewsService()
