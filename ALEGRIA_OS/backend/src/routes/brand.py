# backend/src/routes/brand.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from src.services.brand_service import service as brand_service

router = APIRouter(tags=["brand"])

class UpdateBrandRequest(BaseModel):
    brand_id: str
    updates: Dict[str, Any]

@router.get("/active")
async def get_active_brand():
    """Obtiene la marca operativa actual."""
    return brand_service.get_active_brand()

@router.get("/all")
async def get_all_brands():
    """Lista todas las marcas registradas en el Studio."""
    return brand_service.get_all()

@router.post("/update")
async def update_brand(req: UpdateBrandRequest):
    """Actualiza la identidad de una marca específica."""
    success = brand_service.update_brand(req.brand_id, req.updates)
    if not success:
        raise HTTPException(status_code=404, detail=f"Marca {req.brand_id} no encontrada.")
    return {"status": "ok", "message": "Identidad de marca actualizada."}

@router.post("/set-active")
async def set_active(brand_id: str):
    """Cambia la marca activa del sistema."""
    data = brand_service.get_all()
    if brand_id in data["brands"]:
        data["active_brand"] = brand_id
        brand_service.save_all(data)
        return {"status": "ok", "active": brand_id}
    raise HTTPException(status_code=404, detail="Marca no existe.")

class ScanUrlRequest(BaseModel):
    url: str

@router.post("/scan-url")
async def scan_url(req: ScanUrlRequest):
    """Escaneo Operativo Autónomo: Web -> Identidad."""
    from src.services.web_navigator import service as nav_service
    from src.services.provider_registry import provider_registry
    from src.perception.veoscope.veoscope_entity import create_veoscope
    import json
    import time
    
    # 1. Scrape the URL
    scrape_data = await nav_service.scrape_with_screenshot(req.url)
    if "error" in scrape_data and not scrape_data.get("text"):
        raise HTTPException(status_code=400, detail=f"No se pudo extraer el enlace: {scrape_data['error']}")
    
    text_content = scrape_data["text"]
    screenshot_b64 = scrape_data["screenshot"]
    
    # 2. Extract Narrative Identity (Text)
    system_text_extract = "Eres ALEGR-IA. Extrae del texto la identidad. Devuelve SOLO JSON válido: {\"name\": \"Nombre\", \"category\": \"persona/brand/idea\", \"voice\": \"tono de voz\", \"mood\": \"mood\"}"
    extracted_text_raw = await provider_registry.chat(
        messages=[{"role": "system", "content": system_text_extract}, {"role": "user", "content": f"URL: {req.url}\n\nTEXTO:\n{text_content[:4000]}"}],
        system=system_text_extract
    )
    
    text_identity = {"name": "Identidad Extraída", "category": "brand", "voice": "", "mood": ""}
    try:
        json_str = extracted_text_raw.replace("```json", "").replace("```", "").strip()
        text_identity = json.loads(json_str)
    except:
        pass # fallback to defaults

    # 3. Extract Visual Identity (VeoScope)
    visual_analysis = {}
    if screenshot_b64:
        try:
            veo = create_veoscope()
            veo_result = await veo.process(query="Extrae ADN de marca visual", context={"image": screenshot_b64})
            if veo_result.get("status") == "ok":
                res_content = veo_result.get("content", {})
                if isinstance(res_content, str):
                    try:
                        v_json = res_content.replace("```json", "").replace("```", "").strip()
                        visual_analysis = json.loads(v_json)
                    except:
                        pass
                else:
                    visual_analysis = res_content
        except Exception as e:
            print(f"Error VeoScope en escaneo URL: {e}")

    # 4. Synthesize Brand Profile
    import random
    brand_id = f"gen_{int(time.time())}_{random.randint(100,999)}"
    
    palette = visual_analysis.get("adn_visual", {}).get("colores", ["#2B2B2B", "#F5F5F7"])
    
    # Save Initial Brand Skeleton
    new_brand = {
        "id": brand_id,
        "name": text_identity.get("name", req.url[:30]),
        "category": text_identity.get("category", "brand"),
        "voice": text_identity.get("voice", "Profesional"),
        "mood": text_identity.get("mood", "Claro"),
        "context": f"Origen: {req.url}\n\nResumen Texto Extraído:\n{text_content[:500]}...",
        "palette": palette,
        "gallery": [],
        "links": [req.url],
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    data = brand_service.get_all()
    data["brands"][brand_id] = new_brand
    data["active_brand"] = brand_id
    brand_service.save_all(data)

    # 5. Add the screenshot into the gallery using the real service
    if screenshot_b64:
        brand_service.add_to_gallery(brand_id, screenshot_b64, visual_analysis)
    
    # Return updated brand
    updated_brand = brand_service.get_all()["brands"][brand_id]
    return {"status": "ok", "brand": updated_brand}

class AddAssetRequest(BaseModel):
    brand_id: str
    image_data: str # base64

@router.post("/add-asset")
async def add_asset(req: AddAssetRequest):
    """Sube un activo directamente y genera su ADN (Prompt)."""
    from src.perception.veoscope.veoscope_entity import create_veoscope
    import json
    
    # 1. Analizar imagen para extraer ADN (Prompt para generador de video)
    visual_analysis = {}
    dna_prompt = ""
    try:
        veo = create_veoscope()
        # Pedimos específicamente un PROMPT para replicar la imagen en video
        query = "Analiza esta imagen y genera un PROMPT DETALLADO para replicar esta escena/sujeto exactamente en un generador de video (como Kling, Runway o Sora). Describe sujeto, iluminación, estilo y mood."
        veo_result = await veo.process(query=query, context={"image": req.image_data})
        
        if veo_result.get("status") == "ok":
            res_content = veo_result.get("content", {})
            if isinstance(res_content, str):
                dna_prompt = res_content
            else:
                dna_prompt = res_content.get("description") or res_content.get("adn_visual", {}).get("expresion") or str(res_content)
            
            visual_analysis = {"description": dna_prompt}
    except Exception as e:
        print(f"Error VeoScope en add_asset: {e}")
        dna_prompt = "Error analizando imagen."

    # 2. Guardar en Galería
    entry = brand_service.add_to_gallery(req.brand_id, req.image_data, visual_analysis)
    if entry:
        entry["dna_prompt"] = dna_prompt
        # Guardamos el dna_prompt permanentemente en el registro
        data = brand_service.get_all()
        for idx, item in enumerate(data["brands"][req.brand_id]["gallery"]):
            if item["url"] == entry["url"]:
                data["brands"][req.brand_id]["gallery"][idx]["dna_prompt"] = dna_prompt
                break
        brand_service.save_all(data)
        return {"status": "ok", "asset": entry}
    
    raise HTTPException(status_code=500, detail="Error al guardar el activo.")
