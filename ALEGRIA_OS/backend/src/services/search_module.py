"""
ALEGRIA OS - Search Module
Integración con Google Custom Search API y DuckDuckGo como fallback.
"""
import os
import logging
import httpx
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
from dotenv import load_dotenv

# Cargar .env desde el directorio backend
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(os.path.dirname(_current_dir))
_env_path = os.path.join(_backend_dir, ".env")
load_dotenv(_env_path)

logger = logging.getLogger("ALEGRIA_SEARCH")


class GoogleSearchProvider:
    """
    Proveedor de búsqueda usando Google Custom Search API.
    Proporciona resultados de búsqueda en tiempo real desde Google.
    """
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.is_configured = bool(api_key and search_engine_id)
        
        if self.is_configured:
            logger.info("✅ [GOOGLE] Proveedor de Google Custom Search configurado.")
        else:
            logger.warning("⚠️ [GOOGLE] Credenciales de Google no configuradas.")
    
    async def search(self, query: str, max_results: int = 5, date_restrict: str = None) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda usando Google Custom Search API.
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados (máx. 10 por request)
            date_restrict: Restricción temporal (ej: 'd1' para las últimas 24h, 'w1' para la última semana)
            
        Returns:
            Lista de resultados con title, link, snippet
        """
        if not self.is_configured:
            logger.warning("⚠️ [GOOGLE] Proveedor no configurado, saltando...")
            return []
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(max_results, 10),  # Google limita a 10 por request
            }
            if date_restrict:
                params["dateRestrict"] = date_restrict
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "pagemap": item.get("pagemap", {}), # Inyectar metadata rica (scores, dates, etc)
                    "source": "google",
                })
            
            logger.info(f"🔍 [GOOGLE] Encontrados {len(results)} resultados para: {query}")
            return results
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ [GOOGLE] Error HTTP {e.response.status_code}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ [GOOGLE] Error inesperado: {e}")
            return []
    
    def search_sync(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Versión síncrona para compatibilidad."""
        if not self.is_configured:
            return []
        
        try:
            import httpx
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(max_results, 10),
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "source": "google",
                })
            
            logger.info(f"🔍 [GOOGLE] Encontrados {len(results)} resultados para: {query}")
            return results
            
        except Exception as e:
            logger.error(f"❌ [GOOGLE] Error: {e}")
            return []


class DuckDuckGoProvider:
    """
    Proveedor de búsqueda usando DuckDuckGo.
    Sirve como fallback cuando Google no está disponible.
    """
    
    def __init__(self):
        logger.info("✅ [DUCKDUCKGO] Proveedor inicializado como fallback.")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda en DuckDuckGo.
        """
        try:
            # Instanciar localmente para evitar problemas de sesión en async
            with DDGS() as ddgs:
                raw_results = ddgs.text(query, max_results=max_results)
                results = []
                
                for item in raw_results:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("href", item.get("link", "")),
                        "snippet": item.get("body", item.get("snippet", "")),
                        "source": "duckduckgo",
                    })
                
                logger.info(f"🔍 [DUCKDUCKGO] Encontrados {len(results)} resultados para: {query}")
                return results
            
        except Exception as e:
            logger.error(f"❌ [DUCKDUCKGO] Error buscando '{query}': {e}")
            return []


class SearchService:
    """
    Servicio unificado de búsqueda.
    Prioriza Google Custom Search API y usa DuckDuckGo como fallback.
    """
    
    def __init__(self):
        # Cargar credenciales desde .env
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY", "")
        self.google_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
        
        # Inicializar proveedores
        self.google = GoogleSearchProvider(
            api_key=self.google_api_key,
            search_engine_id=self.google_engine_id
        )
        self.duckduckgo = DuckDuckGoProvider()
        
        # Determinar proveedor primario
        self.primary_provider = "google" if self.google.is_configured else "duckduckgo"
        logger.info(f"🎯 [SEARCH] Proveedor primario: {self.primary_provider.upper()}")
    
    async def search_async(self, query: str, max_results: int = 5, date_restrict: str = None) -> List[Dict[str, Any]]:
        """
        Búsqueda asíncrona con fallback automático.
        """
        logger.info(f"🔍 [SEARCH] Iniciando búsqueda: '{query}'")
        
        # Intentar con Google primero si está configurado
        if self.google.is_configured:
            results = await self.google.search(query, max_results, date_restrict)
            if results:
                return results
            logger.warning("⚠️ [SEARCH] Google falló, usando fallback...")
        
        # Fallback a DuckDuckGo (no soporta dateRestrict nativo del mismo modo aquí)
        return self.duckduckgo.search(query, max_results)
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Búsqueda síncrona (mantiene compatibilidad con código existente).
        """
        logger.info(f"🔍 [SEARCH] Iniciando búsqueda síncrona: '{query}'")
        
        # Intentar con Google primero
        if self.google.is_configured:
            results = self.google.search_sync(query, max_results)
            if results:
                return results
            logger.warning("⚠️ [SEARCH] Google falló, usando fallback...")
        
        # Fallback a DuckDuckGo
        return self.duckduckgo.search(query, max_results)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retorna el estado del servicio de búsqueda.
        """
        return {
            "primary_provider": self.primary_provider,
            "google_configured": self.google.is_configured,
            "duckduckgo_available": True,
        }


# Instancia global del servicio (Cargará las nuevas credenciales de Google al reiniciar/recargar)
service = SearchService()
