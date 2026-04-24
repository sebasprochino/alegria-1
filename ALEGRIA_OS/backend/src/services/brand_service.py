# backend/src/services/brand_service.py
import json
import os
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger("ALEGRIA_BRAND_SERVICE")

class BrandService:
    def __init__(self):
        self.data_path = os.path.join("data", "brand.json")
        self._ensure_data()

    def _ensure_data(self):
        if not os.path.exists("data"):
            os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.data_path):
            default = {
                "active_brand": "AlegrIA",
                "brands": {
                    "AlegrIA": {
                        "name": "AlegrIA",
                        "id": "AlegrIA",
                        "category": "brand",
                        "voice": "Innovadora, accesible, inspiradora",
                        "mood": "Energético y confiable",
                        "palette": ["#7c3aed", "#3b82f6", "#00f6ff"],
                        "gallery": [],
                        "links": [],
                        "updated_at": "2026-04-17T00:00:00Z"
                    }
                }
            }
            self.save_all(default)
            logger.info("📦 [BRAND] Archivo de marca inicializado.")

    def _clean_data(self, data: Any) -> Any:
        """Limpia recursivamente los datos para asegurar que sean serializables (Fix BUG-01)."""
        if isinstance(data, dict):
            return {str(k): self._clean_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_data(i) for i in data]
        elif isinstance(data, (str, int, float, bool, type(None))):
            return data
        else:
            try:
                return str(data)
            except:
                return "[Unserializable]"

    def get_all(self) -> Dict[str, Any]:
        try:
            if not os.path.exists(self.data_path):
                self._ensure_data()
                
            with open(self.data_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    raise ValueError("Archivo vacío")
                data = json.loads(content)
                return self._clean_data(data)
        except Exception as e:
            logger.error(f"❌ [BRAND] Error leyendo brand.json (BUG-01 Fix): {e}")
            return {"active_brand": "AlegrIA", "brands": {}}

    def save_all(self, data: Dict[str, Any]):
        try:
            clean_data = self._clean_data(data)
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(clean_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ [BRAND] Error guardando brand.json: {e}")

    def get_active_brand(self) -> Dict[str, Any]:
        data = self.get_all()
        brand_id = data.get("active_brand", "AlegrIA")
        return data["brands"].get(brand_id, list(data["brands"].values())[0])

    def update_brand(self, brand_id: str, updates: Dict[str, Any]):
        data = self.get_all()
        if brand_id in data["brands"]:
            # Normalización de campos para coincidir con el blueprint
            if "analysis" in updates:
                analysis = updates["analysis"]
                adn = analysis.get("adn_visual", {})
                narrative = analysis.get("contexto_narrativo", {})
                category = analysis.get("category") or updates.get("category")
                
                if category:
                    data["brands"][brand_id]["category"] = category

                # Normalización inteligente de identidad base
                if category == "persona":
                    data["brands"][brand_id]["voice"] = narrative.get("arquetipo") or narrative.get("voz") or data["brands"][brand_id]["voice"]
                    data["brands"][brand_id]["mood"] = adn.get("expresion") or adn.get("estilo") or data["brands"][brand_id]["mood"]
                else:
                    data["brands"][brand_id]["voice"] = narrative.get("voz") or narrative.get("emocion") or data["brands"][brand_id]["voice"]
                    data["brands"][brand_id]["mood"] = adn.get("estilo") or adn.get("iluminacion") or data["brands"][brand_id]["mood"]
                
                if adn.get("colores"):
                    data["brands"][brand_id]["palette"] = adn.get("colores")
            else:
                data["brands"][brand_id].update(updates)
            
            data["brands"][brand_id]["updated_at"] = datetime.now().isoformat()
            
            self.save_all(data)
            logger.info(f"✅ [BRAND] Marca '{brand_id}' actualizada.")
            return True
        return False

    def add_to_gallery(self, brand_id: str, image_data: str, analysis: Dict[str, Any]):
        """
        Ancla una imagen analizada a la galería de la marca con sus metadatos clínicos.
        Si la identidad no existe, la crea automáticamente.
        """
        data = self.get_all()
        
        # 0. Auto-Inicialización si no existe
        if brand_id not in data["brands"]:
            logger.info(f"✨ [BRAND] Creando nueva identidad: '{brand_id}' via VEO Scanner.")
            
            # Extraer metadatos básicos del análisis si están disponibles
            adn = analysis.get("adn_visual", {})
            narrative = analysis.get("contexto_narrativo", {})
            category = analysis.get("category", "brand")
            
            new_brand = {
                "id": brand_id,
                "name": analysis.get("name", brand_id),
                "category": category,
                "voice": narrative.get("voz") or narrative.get("arquetipo") or "Pendiente de definición",
                "mood": adn.get("estilo") or adn.get("expresion") or "Pendiente",
                "palette": adn.get("colores") if isinstance(adn.get("colores"), list) else ["#cbd5e1"],
                "gallery": [],
                "links": [],
                "updated_at": datetime.now().isoformat()
            }
            data["brands"][brand_id] = new_brand

        # 1. Persistencia física en la ruta especificada
        import base64
        import time

        # Usamos la ruta oficial de storage/uploads
        storage_base = os.path.join(os.getcwd(), "storage", "uploads")
        gallery_path = os.path.join(storage_base, "brand_gallery")
        os.makedirs(gallery_path, exist_ok=True)

        filename = f"veo_{int(time.time())}.jpg"
        file_path = os.path.join(gallery_path, filename)
        
        try:
            if "base64," in image_data:
                header, encoded = image_data.split(",", 1)
                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(encoded))
            elif image_data.startswith("http"):
                filename = None 
            else:
                import shutil
                if os.path.exists(image_data):
                    shutil.copy(image_data, file_path)
                else:
                    logger.error(f"Archivo no encontrado para galería: {image_data}")
                    return None
            
            # 2. Registro en JSON
            final_url = image_data if not filename else f"/api/storage/file/brand_gallery/{filename}"
            
            entry = {
                "id": str(int(time.time())),
                "url": final_url,
                "analysis": analysis,
                "created_at": datetime.now().isoformat()
            }
            
            gallery = data["brands"][brand_id].get("gallery", [])
            gallery.insert(0, entry)
            data["brands"][brand_id]["gallery"] = gallery[:20] 
            
            self.save_all(data)
            logger.info(f"📸 [BRAND] Nueva captura clínica guardada en '{brand_id}'.")
            return entry
        except Exception as e:
            logger.error(f"Error guardando imagen en galería: {e}")
            return None

# Singleton
service = BrandService()
