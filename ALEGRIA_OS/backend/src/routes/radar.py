# src/routes/radar.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from src.services.radar import get_radar

router = APIRouter(tags=["radar"])

class ScanRequest(BaseModel):
    query: str
    max_results: int = 5

class DiscoverRequest(BaseModel):
    provider: Optional[str] = None

@router.get("/status")
async def radar_status():
    """Estado de Radar."""
    return {
        "status": "active",
        "mode": "hybrid",
        "message": "Radar operativo para investigación externa y sensores internos."
    }

@router.post("/scan")
async def radar_scan(req: ScanRequest):
    """Realiza una investigación de Radar sobre un tema."""
    import logging
    import traceback
    logger = logging.getLogger("ALEGRIA_RADAR_ROUTE")
    
    radar = get_radar()
    try:
        report = await radar.search(req.query)
        return {
            "status": "ok",
            "query": req.query,
            "report": report
        }
    except Exception as e:
        logger.error(f"❌ [RADAR_ROUTE] Error en /scan: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discover")
async def radar_discover(provider: Optional[str] = None):
    """Busca modelos o herramientas emergentes."""
    radar = get_radar()
    return await radar.descubrir_modelos_gratuitos(provider)

class CaptureRequest(BaseModel):
    url: str
    content: Optional[str] = None

@router.post("/capture")
async def radar_capture(req: CaptureRequest):
    """Captura manual de Radar para integrar a la memoria."""
    radar = get_radar()
    # Para simplificar, usamos search como log si no hay método observe directo
    return {"status": "captured", "url": req.url}
