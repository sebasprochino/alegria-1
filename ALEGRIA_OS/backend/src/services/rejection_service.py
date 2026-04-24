# -------------------------------------------------------------------------
# ALEGR-IA OS — Sistema Operativo de Coherencia Creativa
# Copyright (c) 2025 Sebastián Fernández & Antigravity AI.
# Todos los derechos reservados.
# -------------------------------------------------------------------------

import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from .database import service as db_service

logger = logging.getLogger("ALEGRIA_REJECTION")

REJECTION_TYPES = ["topic", "behavior", "style", "content", "language"]
SEVERITY_LEVELS = ["strict", "moderate", "soft"]

class RejectionService:
    def __init__(self):
        self.name = "RejectionService"
        self.version = "1.0.0"
        self.db = db_service

    async def get_user_rejections(self, user_id: str = "default") -> List[Dict[str, Any]]:
        try:
            if not self.db.connected:
                await self.db.connect()

            if not self.db.connected:
                return []

            try:
                prefs = await self.db.db.userpreferences.find_unique(
                    where={"userId": user_id}
                )
                custom_rejections = getattr(prefs, "customRejections", None) if prefs else None
                if not prefs or not custom_rejections:
                    return []
                rejections = json.loads(custom_rejections)
                return rejections if isinstance(rejections, list) else []
            except Exception as e:
                logger.warning(f"⚠️ [REJECTION] Fallo lectura DB: {e}")
                return []


        except Exception as e:
            logger.error(f"❌ [REJECTION] Error obteniendo rechazos: {e}")
            return []

    async def add_rejection(self, user_id="default", rejection_type="topic", description="", severity="moderate", active=True):
        try:
            if rejection_type not in REJECTION_TYPES:
                raise ValueError(f"Tipo inválido: {REJECTION_TYPES}")
            if severity not in SEVERITY_LEVELS:
                raise ValueError(f"Severidad inválida: {SEVERITY_LEVELS}")
            if not description or len(description.strip()) < 3:
                raise ValueError("Descripción corta")

            current_rejections = await self.get_user_rejections(user_id)
            new_rejection = {
                "id": str(uuid.uuid4()),
                "type": rejection_type,
                "description": description.strip(),
                "severity": severity,
                "active": active,
                "created_at": datetime.utcnow().isoformat()
            }
            current_rejections.append(new_rejection)
            await self._save_rejections(user_id, current_rejections)
            return new_rejection
        except Exception as e:
            logger.error(f"❌ [REJECTION] Error agregando: {e}")
            raise

    async def update_rejection(self, user_id="default", rejection_id="", updates=None):
        try:
            current_rejections = await self.get_user_rejections(user_id)
            updated = None
            for r in current_rejections:
                if r["id"] == rejection_id:
                    for k, v in (updates or {}).items():
                        if k in ["type", "description", "severity", "active"]:
                            r[k] = v
                    r["updated_at"] = datetime.utcnow().isoformat()
                    updated = r
                    break
            if updated:
                await self._save_rejections(user_id, current_rejections)
            return updated
        except Exception as e:
            logger.error(f"❌ [REJECTION] Error actualizando: {e}")
            raise

    async def delete_rejection(self, user_id="default", rejection_id=""):
        try:
            current_rejections = await self.get_user_rejections(user_id)
            initial = len(current_rejections)
            current_rejections = [r for r in current_rejections if r["id"] != rejection_id]
            if len(current_rejections) < initial:
                await self._save_rejections(user_id, current_rejections)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ [REJECTION] Error eliminando: {e}")
            raise

    async def build_rejection_prompt(self, user_id: str = "default") -> str:
        try:
            rejections = await self.get_user_rejections(user_id)
            active = [r for r in rejections if r.get("active", True)]
            if not active: return ""

            prompt = ["⚠️ RECHAZOS DEL USUARIO (PRIORIDAD MÁXIMA)\n"]
            for r in active:
                prompt.append(f"- [{r.get('severity', 'moderate').upper()}] {r.get('description', '')}")
            return "\n".join(prompt)
        except: return ""

    async def _save_rejections(self, user_id: str, rejections: List[Dict[str, Any]]):
        try:
            if not self.db.connected:
                await self.db.connect()
            
            if not self.db.connected:
                return

            rejections_json = json.dumps(rejections, ensure_ascii=False)
            try:
                existing = await self.db.db.userpreferences.find_unique(where={"userId": user_id})
                if existing:
                    await self.db.db.userpreferences.update(where={"userId": user_id}, data={"customRejections": rejections_json})
                else:
                    await self.db.db.userpreferences.create(data={"userId": user_id, "customRejections": rejections_json})
            except Exception as e:
                logger.warning(f"⚠️ [REJECTION] DB Fallback: {e}")

        except Exception as e:
            logger.error(f"❌ [REJECTION] Error fatal save: {e}")

service = RejectionService()
