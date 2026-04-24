import os
import logging
import asyncio
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ALEGRIA_OS_MOTION")

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")

# Mapeo de modelos para Replicate
REPLICATE_MODELS = {
    "wan2.1": "lucataco/wan2.1-t2v-14b:7492c64906f02279761922765893f18e95c10488f55e5b326d9c6e5e8e9d36a3",
    "ltx-video": "lightricks/ltx-video:760533355601556024922765893f18e95c10488f55e5b326d9c6e5e8e9d36a3"
}

# Mapeo de modelos para SiliconFlow (Gratis/OpenAI Compatible)
SILICONFLOW_MODELS = {
    "wan2.1": "Pro/Alibaba/Wan2.1-T2V-14B",
    "cogvideo-5b": "THUDM/CogVideoX-5B"
}

class MotionService:
    """
    Servicio Soberano de Generación de Video.
    Soporta múltiples proveedores: Replicate (Pago) y SiliconFlow (Gratis Tier).
    """
    
    def __init__(self):
        self.active_jobs = {}
        logger.info("🎬 [MOTION] Motor de Movimiento inicializado")

    async def generate_video(self, prompt: str, aspect_ratio: str = "16:9", duration: int = 5, model: str = "wan2.1", provider: str = "siliconflow"):
        """
        Solicita la generación según el proveedor elegido.
        """
        job_id = f"job_{os.urandom(4).hex()}"
        
        if provider == "siliconflow":
            if not SILICONFLOW_API_KEY:
                return {"status": "doubt", "message": "Falta SILICONFLOW_API_KEY en .env. Regístrate en siliconflow.cn para obtener créditos gratuitos."}
            return await self._generate_siliconflow(job_id, prompt, aspect_ratio, model)
        
        elif provider == "replicate":
            if not REPLICATE_API_TOKEN:
                return {"status": "doubt", "message": "Falta REPLICATE_API_TOKEN en .env."}
            return await self._generate_replicate(job_id, prompt, aspect_ratio, model)
            
        return {"status": "error", "message": "Proveedor no soportado"}

    async def _generate_siliconflow(self, job_id: str, prompt: str, aspect_ratio: str, model: str):
        """
        Generación vía SiliconFlow (Async via Polling si lo soportan, o sync si es rápido).
        Nota: SiliconFlow suele ser síncrono para video corto o asíncrono vía batches.
        """
        model_name = SILICONFLOW_MODELS.get(model, SILICONFLOW_MODELS["wan2.1"])
        url = "https://api.siliconflow.cn/v1/video/generations"
        
        headers = {
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio
        }

        self.active_jobs[job_id] = {"status": "processing", "progress": 10, "prompt": prompt, "provider": "siliconflow"}

        async def _run_task():
            async with httpx.AsyncClient(timeout=300) as client:
                try:
                    response = await client.post(url, json=payload, headers=headers)
                    data = response.json()
                    
                    if "images" in data or "video" in data or "url" in data:
                        # Estructura típica de SiliconFlow
                        video_url = data.get("video") or data.get("url") or (data.get("images")[0] if "images" in data else None)
                        self.active_jobs[job_id].update({"status": "completed", "progress": 100, "result": video_url})
                    else:
                        error_msg = data.get("error", {}).get("message", "Error desconocido en SiliconFlow")
                        self.active_jobs[job_id].update({"status": "error", "error": error_msg})
                except Exception as e:
                    self.active_jobs[job_id].update({"status": "error", "error": str(e)})

        asyncio.create_task(_run_task())
        return {"job_id": job_id, "status": "queued"}

    async def _generate_replicate(self, job_id: str, prompt: str, aspect_ratio: str, model: str):
        """
        Generación vía Replicate.
        """
        version = REPLICATE_MODELS.get(model, REPLICATE_MODELS["wan2.1"]).split(":")[-1]
        url = "https://api.replicate.com/v1/predictions"
        
        headers = {
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "version": version,
            "input": {"prompt": prompt, "aspect_ratio": aspect_ratio}
        }

        self.active_jobs[job_id] = {"status": "processing", "progress": 5, "prompt": prompt, "provider": "replicate"}

        async def _poll_task():
            async with httpx.AsyncClient() as client:
                try:
                    resp = await client.post(url, json=payload, headers=headers)
                    pred = resp.json()
                    rep_id = pred["id"]
                    
                    while True:
                        await asyncio.sleep(4)
                        status_resp = await client.get(f"{url}/{rep_id}", headers=headers)
                        status_data = status_resp.json()
                        
                        curr_status = status_data["status"]
                        if curr_status == "succeeded":
                            res = status_data["output"]
                            url_res = res[0] if isinstance(res, list) else res
                            self.active_jobs[job_id].update({"status": "completed", "progress": 100, "result": url_res})
                            break
                        elif curr_status == "failed":
                            self.active_jobs[job_id].update({"status": "error", "error": status_data.get("error")})
                            break
                        else:
                            self.active_jobs[job_id]["progress"] = min(self.active_jobs[job_id].get("progress", 0) + 10, 95)
                except Exception as e:
                    self.active_jobs[job_id].update({"status": "error", "error": str(e)})

        asyncio.create_task(_poll_task())
        return {"job_id": job_id, "status": "queued"}

    def get_job_status(self, job_id: str):
        return self.active_jobs.get(job_id, {"status": "not_found"})

motion_service = MotionService()
