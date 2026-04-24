"""
ALEGRIA_OS — src/os/orchestrator.py
===================================
El cerebro operativo del sistema. Controla el flujo soberana:
NEXUS → ANIMA → LLM → KERNEL.
"""

import logging
from typing import Dict, Any, Optional
from src.services.anima import get_anima
from src.services.nexus import get_nexus
from src.core.kernel import kernel
from src.services.brand_service import service as brand_service

logger = logging.getLogger("ALEGRIA_OS")

class AlegriaOS:
    """
    Motor de Ejecución Soberana.
    Implementa el flujo de la Arquitectura Operativa Definitiva.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlegriaOS, cls).__new__(cls)
            cls._instance.anima = get_anima()
            cls._instance.nexus = get_nexus()
        return cls._instance

    async def process(self, user_input: str, file_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        FLUJO GLOBAL DEFINITIVO:
        1. NEXUS  → Clasifica (sin deducir)
        2. ANIMA  → Construye el contexto (ACSP builder)
        3. LLM    → Genera el output crudo
        4. KERNEL → Audita (sin bloquear ni modificar)
        """
        logger.info(f"⚔️ [OS] Procesando: '{user_input[:50]}...'")

        # 1. CLASIFICACIÓN (NEXUS)
        # Se ejecuta dentro de anima.generate_raw o aquí para transparencia
        classification = self.nexus.classify_request(user_input)
        
        # 2 y 3. CONSTRUCCIÓN Y GENERACIÓN (ANIMA)
        # Ánima usa el AnimaBuilder internamente basado en la clasificación
        execution_result = await self.anima.generate_raw(
            message=user_input,
            file_metadata=file_metadata,
            forced_classification=classification
        )

        # 4. AUDITORÍA (KERNEL / RULE ENGINE)
        # El Kernel audita el output intacto. No modifica, no bloquea.
        from src.core.rule_engine import service as rule_engine
        from src.services.audit_emitter import audit_emitter
        import time

        t_start_guard = time.time()
        
        # El motor de reglas analiza coherencia, ética y "humo" (fluff)
        filtered = await rule_engine.filter_output(execution_result, mode="execution")
        
        t_end_guard = time.time()
        
        # Mapeo de status a alert_level para el Timeline
        # Authorized -> none, Doubt -> warning, Rejected -> critical
        status_map = {
            "Authorized": "authorized",
            "Doubt": "doubt",
            "Rejected": "rejected",
            "error": "rejected"
        }
        alert_level = status_map.get(filtered.get("status"), "authorized")

        # AUDIT: GUARD (SEGURIDAD)
        await audit_emitter.emit({
            "intention_id": execution_result.get("intention_id") or "os-proc",
            "stage": "guard",
            "timestamp": t_end_guard,
            "agent": "KERNEL",
            "data": {
                "alert_level": alert_level,
                "duration": t_end_guard - t_start_guard,
                "score": filtered.get("analysis", {}).get("confidence", 1.0)
            }
        })

        # 5. ENSAMBLAJE FINAL
        # Mantenemos el output intacto según la REGLA DE ORO
        content = self._extract_content(execution_result["raw"])
        
        # 6. PERSISTENCIA EN BRAND STUDIO (Soberanía Visual)
        # Si es un análisis visual y contiene datos estructurados, lo anclamos a la marca
        if execution_result.get("modality") == "vision":
            self._try_persist_to_brand(execution_result["raw"], file_metadata)

        final_response = self.anima.format_response({
            "status": filtered.get("status", "Authorized"),
            "content": content,
            "raw": execution_result["raw"],
            "meta": {
                "classification": classification,
                "modality": execution_result.get("modality"),
                "agent": execution_result.get("agent"),
                "analysis": filtered.get("analysis")
            },
            "audit": kernel.audit_output(execution_result["raw"])
        })

        logger.info(f"✅ [OS] Flujo completado. Status: {filtered.get('status')}")
        return final_response

    def _try_persist_to_brand(self, raw: str, file_metadata: Optional[Dict[str, Any]]):
        """Intenta identificar y persistir datos de marca en el Studio."""
        import json
        try:
            data = json.loads(raw)
            # Detectamos si es un análisis clínico (VEOSCOPE)
            # Buscamos campos clave: adn_visual, contexto_narrativo, etc.
            is_clinical = any(k in data for k in ["adn_visual", "contexto_narrativo", "analysis"])
            
            if is_clinical:
                active_brand = brand_service.get_active_brand()
                brand_id = active_brand.get("id", "AlegrIA")
                
                # Imagen: si viene en el metadata la usamos, si no, es difícil persistir sin la fuente
                image_source = None
                if file_metadata and file_metadata.get("data"):
                    image_source = file_metadata["data"]
                
                if image_source:
                    brand_service.add_to_gallery(
                        brand_id=brand_id,
                        image_data=image_source,
                        analysis=data.get("analysis") or data
                    )
                    logger.info(f"💾 [OS] Análisis visual auto-persistido en Brand Studio: {brand_id}")
        except Exception as e:
            logger.debug(f"[OS] No se pudo auto-persistir análisis: {e}")

    def _extract_content(self, raw: str) -> str:
        """
        Helper para extraer el campo 'response' o similar si el LLM devolvió JSON,
        o devolver el raw si es texto libre. No modifica el raw, solo extrae para la UI.
        """
        import json
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data.get("response") or data.get("analysis") or str(data)
        except:
            pass
        return raw

def get_os() -> AlegriaOS:
    return AlegriaOS()
