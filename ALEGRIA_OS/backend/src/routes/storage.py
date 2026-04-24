from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import shutil
from pathlib import Path

router = APIRouter(tags=["storage"])

# Anchor to backend/ directory regardless of CWD
_BACKEND_DIR = Path(__file__).resolve().parents[2]  # src/routes/storage.py -> backend/
UPLOAD_DIR = _BACKEND_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validar extensión básica
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov"]:
        raise HTTPException(status_code=400, detail="Formato no soportado.")
    
    # Generar nombre único
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_name
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Retornar la ruta relativa o absoluta para que el OS la use
        return {
            "status": "ok",
            "filename": file.filename,
            "path": str(file_path),
            "url": f"/api/storage/file/{unique_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{filepath:path}")
async def get_file(filepath: str):
    from fastapi.responses import FileResponse
    # Resolver ruta absoluta evitando Directory Traversal
    safe_path = (UPLOAD_DIR / filepath).resolve()
    
    if not str(safe_path).startswith(str(UPLOAD_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Acceso denegado.")
        
    if not safe_path.exists() or not safe_path.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")
        
    return FileResponse(safe_path)
