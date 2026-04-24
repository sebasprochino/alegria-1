# src/services/news_sensor.py

import httpx
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import asyncio

CLARIN_FEEDS = {
    "lo_ultimo": "https://www.clarin.com/rss/lo-ultimo/",
    "politica": "https://www.clarin.com/rss/politica/",
    "mundo": "https://www.clarin.com/rss/mundo/",
    "sociedad": "https://www.clarin.com/rss/sociedad/",
    "policiales": "https://www.clarin.com/rss/policiales/",
    "ciudades": "https://www.clarin.com/rss/ciudades/",
    "opinion": "https://www.clarin.com/rss/opinion/",
    "cartas": "https://www.clarin.com/rss/cartas_al_pais/",
    "cultura": "https://www.clarin.com/rss/cultura/",
    "rural": "https://www.clarin.com/rss/rural/",
    "economia": "https://www.clarin.com/rss/economia/",
    "tecnologia": "https://www.clarin.com/rss/tecnologia/",
    "internacional": "https://www.clarin.com/rss/internacional/",
    "revista_nie": "https://www.clarin.com/rss/revista-enie/",
    "viva": "https://www.clarin.com/rss/viva/",
    "br": "https://www.clarin.com/rss/br/",
    "futbol": "https://www.clarin.com/rss/deportes/",
    "deportes": "https://www.clarin.com/rss/deportes/",
    "tv": "https://www.clarin.com/rss/espectaculos/tv/",
    "cine": "https://www.clarin.com/rss/espectaculos/cine/",
    "musica": "https://www.clarin.com/rss/espectaculos/musica/",
    "teatro": "https://www.clarin.com/rss/espectaculos/teatro/",
    "espectaculos": "https://www.clarin.com/rss/espectaculos/",
    "autos": "https://www.clarin.com/rss/autos/",
    "buena_vida": "https://www.clarin.com/rss/buena-vida/",
    "viajes": "https://www.clarin.com/rss/viajes/",
    "arq": "https://www.clarin.com/rss/arq/",
}

class NewsSensor:
    """
    Sensor especializado en fuentes de noticias confiables (Sovereign Sources).
    """

    async def fetch_feed(self, category: str = "lo_ultimo", limit: int = 5) -> List[Dict[str, Any]]:
        url = CLARIN_FEEDS.get(category, CLARIN_FEEDS["lo_ultimo"])
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
            root = ET.fromstring(response.content)
            items = []
            
            for item in root.findall(".//item")[:limit]:
                title = item.find("title").text if item.find("title") is not None else "Sin título"
                link = item.find("link").text if item.find("link") is not None else ""
                description = item.find("description").text if item.find("description") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                
                # Limpiar descripción (Clarín suele meter HTML)
                import re
                description = re.sub(r'<[^>]*>', '', description).strip()
                
                items.append({
                    "title": title,
                    "link": link,
                    "summary": description,
                    "date": pub_date,
                    "source": "Clarín"
                })
                
            return items
        except Exception as e:
            print(f"Error fetching RSS: {e}")
            return []

    async def search_news(self, query: str, category: str = "lo_ultimo") -> str:
        """
        Busca y formatea noticias de Clarín como un reporte de sensor.
        """
        items = await self.fetch_feed(category)
        if not items:
            return f"❌ [NEWS] No se pudo conectar con el sensor Clarín ({category})."

        # Filtrar si hay query
        if query and query.lower() != "lo ultimo" and query.lower() != "lo último":
            filtered = [
                i for i in items 
                if query.lower() in i['title'].lower() or query.lower() in i['summary'].lower()
            ]
            if filtered:
                items = filtered

        report = f"📰 [NEWS] Sonda Clarín: {category.upper()}\n"
        report += f"Filtro: {query if query else 'Ninguno'}\n\n"
        
        for i in items[:5]:
            report += f"• **{i['title']}**\n  ↳ {i['summary'][:150]}...\n  🔗 {i['link']}\n\n"
            
        return report

service = NewsSensor()
