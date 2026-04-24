# -------------------------------------------------------------------------
# ALEGR-IA OS — src/core/modality_router.py
#
# PRINCIPIO: El sistema reconoce la naturaleza del input antes de procesarlo.
# No alucina texto sobre datos visuales. No usa texto puro para analizar imágenes.
#
# Modalidades soportadas:
#   text   → modelo de texto (default del provider activo)
#   vision → modelo de visión (Groq Llama Vision / Gemini Vision)
#   audio  → reservado para expansión futura
#
# Markers reconocidos:
#   [Análisis Visual Requerido]
#   [Análisis VEO Requerido]
#   [Análisis Visual...]        (forma parcial, compat. con VEOscope)
#   Presencia de metadatos de imagen en el payload
#
# Author: Sebastián Fernández
# -------------------------------------------------------------------------

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger("ALEGRIA_MODALITY_ROUTER")

# ─── Marcadores que fuerzan modalidad visión ──────────────────────────────────
_VISION_MARKERS: list[str] = [
    r"\[Análisis Visual Requerido\]",
    r"\[Análisis VEO Requerido",  # forma parcial para VEO
    r"\[Análisis Visual",         # forma parcial (compat. VEOscope)
    r"\[visual_analysis\]",       # marker programático interno
    r"\[image_input\]",
]

_VISION_PATTERN = re.compile("|".join(_VISION_MARKERS), re.IGNORECASE)

# ─── Modelo de visión preferido por proveedor ─────────────────────────────────
# Se selecciona el primer modelo disponible en la config del proveedor activo.
_VISION_MODEL_PREFERENCES: dict[str, list[str]] = {
    "groq": [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.2-90b-vision-preview",
        "llama-3.2-11b-vision-preview",
    ],
    "gemini": [
        "gemini-2.5-flash",
        "gemini-3.1-flash-lite-preview",
        "gemini-2.1-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
    ],
}


class ModalityRouter:
    """
    Detecta la modalidad del input y resuelve el modelo a usar.

    RESPONSABILIDADES:
    - Inspeccionar texto en busca de marcadores visuales.
    - Inspeccionar metadatos de payload para presencia de archivos de imagen.
    - Devolver un dict con modality + model_override listo para usar.
    - Registrar en log para auditoría.

    NO llama al LLM. NO modifica el mensaje. Solo clasifica y recomienda.
    """

    def detect(
        self,
        message: str,
        file_metadata: Optional[Dict[str, Any]] = None,
        provider_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Clasifica el input y devuelve la modalidad con el modelo recomendado.

        Args:
            message: Texto del input del operador.
            file_metadata: Metadatos de archivo adjunto (si existe).
                           Esperado: {"type": "image/png", "name": "...", ...}
            provider_config: Config del proveedor activo (para resolver modelo compatible).
                             Esperado: {"provider_type": "groq", "models": [...], ...}

        Returns:
            {
                "modality": "text" | "vision" | "audio",
                "model_override": str | None,  # None = usar el modelo activo
                "provider_type": str | None,
                "reason": str
            }
        """
        modality = self._detect_modality(message, file_metadata)

        if modality == "vision":
            model_override, provider_type = self._resolve_vision_model(provider_config)
            logger.info(
                f"🔭 [MODALITY] Vision detectada → modelo={model_override} | "
                f"provider={provider_type}"
            )
            return {
                "modality": "vision",
                "model_override": model_override,
                "provider_type": provider_type,
                "reason": self._get_trigger_reason(message, file_metadata),
            }

        logger.debug(f"📝 [MODALITY] Texto estándar detectado.")
        return {
            "modality": "text",
            "model_override": None,
            "provider_type": None,
            "reason": "input_text_only",
        }

    # ─── Internals ────────────────────────────────────────────────────────────

    def _detect_modality(
        self,
        message: str,
        file_metadata: Optional[Dict[str, Any]],
    ) -> str:
        # 1. Marcador textual explícito
        if _VISION_PATTERN.search(message):
            return "vision"

        # 2. Archivo adjunto de tipo imagen
        if file_metadata:
            mime = file_metadata.get("type", "").lower()
            if mime.startswith("image/") or mime in ("application/pdf",):
                return "vision"
            name = file_metadata.get("name", "").lower()
            if any(name.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")):
                return "vision"

        return "text"

    def _resolve_vision_model(
        self,
        provider_config: Optional[Dict[str, Any]],
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Selecciona el mejor modelo de visión disponible en la config activa.
        Fallback: groq llama-3.2-90b si no hay config.
        """
        if not provider_config:
            return "llama-3.2-90b-vision-preview", "groq"

        ptype = provider_config.get("provider_type", "groq").lower()
        available_models: list[str] = provider_config.get("models", [])
        preferences = _VISION_MODEL_PREFERENCES.get(ptype, [])

        for preferred in preferences:
            if preferred in available_models:
                return preferred, ptype

        # Si el proveedor activo no tiene visión, intentamos groq como fallback
        logger.warning(
            f"⚠️ [MODALITY] Proveedor '{ptype}' sin modelo de visión disponible. "
            f"Fallback a groq llama-3.2-90b-vision-preview."
        )
        return "llama-3.2-90b-vision-preview", "groq"

    def _get_trigger_reason(
        self,
        message: str,
        file_metadata: Optional[Dict[str, Any]],
    ) -> str:
        if _VISION_PATTERN.search(message):
            match = _VISION_PATTERN.search(message)
            return f"marker:{match.group(0)[:30]}"
        if file_metadata:
            return f"file:{file_metadata.get('type', 'unknown')}"
        return "unknown"


# ─── Singleton ────────────────────────────────────────────────────────────────
modality_router = ModalityRouter()
