from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging

from src.services.motion_service import motion_service

router = APIRouter()
logger = logging.getLogger("ALEGRIA_OS_MOTION_ROUTE")

class MotionRequest(BaseModel):
    prompt: str
    aspect_ratio: Optional[str] = "16:9"
    duration: Optional[int] = 5
    model: Optional[str] = "wan2.1"
    provider: Optional[str] = "siliconflow"

@router.post("/generate")
async def generate_video(request: MotionRequest):
    """
    Solicita la generación de un video.
    """
    try:
        result = await motion_service.generate_video(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio,
            duration=request.duration,
            model=request.model,
            provider=request.provider
        )
        return result
    except Exception as e:
        logger.error(f"Error en /generate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """
    Consulta el estado de un video en proceso.
    """
    status = motion_service.get_job_status(job_id)
    if status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return status
