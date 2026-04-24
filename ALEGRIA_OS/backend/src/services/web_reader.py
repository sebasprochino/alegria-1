import httpx
import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

logger = logging.getLogger("ALEGRIA_WEB_READER")

class WebReader:
    """
    Servicio para leer y extraer contenido de URLs.
    Permite a Anima 'visitar' páginas web.
    """
    
    def __init__(self):
        self.timeout = 15.0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def read_url(self, url: str) -> Dict[str, Any]:
        """
        Lee una URL y extrae el texto principal.
        """
        try:
            logger.info(f"🌐 [WEB_READER] Leyendo URL: {url}")
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Eliminar elementos innecesarios
                for script_or_style in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    script_or_style.decompose()
                
                # Extraer título
                title = soup.title.string if soup.title else "Sin título"
                
                # Extraer texto principal (heurística simple)
                # Priorizar article, main, o divs con mucho texto
                content = ""
                main_content = soup.find('article') or soup.find('main')
                
                if main_content:
                    content = main_content.get_text(separator='\n', strip=True)
                else:
                    # Fallback: todos los párrafos
                    paragraphs = soup.find_all('p')
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                
                # Limitar tamaño para el contexto del LLM
                max_chars = 5000
                if len(content) > max_chars:
                    content = content[:max_chars] + "... [Contenido truncado]"
                
                return {
                    "status": "ok",
                    "url": url,
                    "title": title.strip() if title else "Sin título",
                    "content": content.strip(),
                    "length": len(content)
                }
                
        except Exception as e:
            logger.error(f"❌ [WEB_READER] Error leyendo {url}: {e}")
            return {
                "status": "error",
                "url": url,
                "error": str(e)
            }

service = WebReader()
