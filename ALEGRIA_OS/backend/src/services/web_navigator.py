import logging
import asyncio
import sys
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

logger = logging.getLogger("ALEGRIA_WEB_NAVIGATOR")

class WebNavigatorService:
    def __init__(self):
        # Redundant fix for Windows subprocesses
        if sys.platform == 'win32':
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            except Exception as e:
                logger.debug(f"Aviso loop policy: {e}")

    async def scrape_url(self, url: str) -> str:
        if not url.startswith("http"):
            url = "https://" + url

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Ocultar que es un bot
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                )
                page = await context.new_page()
                
                logger.info(f"Navegando a la URL: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                # Esperamos a que la red se estabilice un poco, ideal para sitios SPA
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)
                except:
                    pass # ignoramos si no llega a networkidle

                html_content = await page.content()
                await browser.close()
                
                return self._clean_html(html_content, url)

        except Exception as e:
            logger.error(f"Error extrayendo URL {url}: {e}")
            return f"Error accediendo a la web: {str(e)}"

    async def scrape_with_screenshot(self, url: str) -> dict:
        if not url.startswith("http"):
            url = "https://" + url

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 800}
                )
                page = await context.new_page()
                
                logger.info(f"Navegando y escaneando visualmente: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)
                except:
                    pass
                
                html_content = await page.content()
                
                import base64
                screenshot_bytes = await page.screenshot(type="jpeg", quality=60)
                b64_screenshot = f"data:image/jpeg;base64,{base64.b64encode(screenshot_bytes).decode('utf-8')}"
                
                await browser.close()
                text_content = self._clean_html(html_content, url)
                
                return {
                    "text": text_content,
                    "screenshot": b64_screenshot
                }

        except Exception as e:
            logger.error(f"Error escaneando visualmente URL {url}: {e}")
            return {"error": str(e), "text": "", "screenshot": None}

    def _clean_html(self, html: str, url: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        
        # Eliminar elementos ruidosos
        for element in soup(["script", "style", "noscript", "meta", "link", "header", "footer", "nav", "svg", "button", "iframe"]):
            element.decompose()
            
        text = soup.get_text(separator="\n", strip=True)
        
        # Reducir multiples lineas en blanco a un maximo de 2
        import re
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Limitar la longitud por si es excesivamente largo (ej max 15000 chars)
        if len(text) > 15000:
            text = text[:15000] + "\n...[Contenido Truncado por Longitud Máxima]..."
            
        return f"=== CONTENIDO DE: {url} ===\n\n{text}"

service = WebNavigatorService()
