# -------------------------------------------------------------------------
# ALEGR-IA OS — src/utils/sanitizer.py
#
# PRINCIPIO: La IA no debe recibir ruido estructural ni logs sin procesar.
# -------------------------------------------------------------------------

import re
import logging

logger = logging.getLogger("ALEGRIA_SANITIZER")

def sanitize_llm_input(text: str, max_log_length: int = 1000) -> str:
    """
    Sanea el input antes de enviarlo al LLM Adapter.
    
    1. Trunca Tracebacks de Python excesivos.
    2. Normaliza espacios en blanco y saltos de línea.
    3. Asegura que el contenido sea un string válido.
    """
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
        
    # Truncar logs pesados / Tracebacks
    if "Traceback (most recent call last):" in text or "Stack trace:" in text:
        logger.info("🛡️ [SANITIZER] Detectado log/traceback pesado. Truncando para estabilidad.")
        # Intentamos mantener el encabezado y el error final, pero recortamos el medio si es muy largo
        if len(text) > max_log_length:
            parts = text.split("\n")
            if len(parts) > 20:
                text = "\n".join(parts[:10]) + "\n\n[... CONTENIDO TRUNCADO POR SEGURIDAD ...]\n\n" + "\n".join(parts[-10:])
            else:
                text = text[:max_log_length] + " [TRUNCATED]"

    # Eliminar espacios excesivos al inicio/final
    text = text.strip()
    
    return text

def sanitize_json_output(raw_text: str) -> str:
    """
    Limpia bloques de markdown ```json ... ``` para obtener solo el objeto.
    """
    cleaned = raw_text.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[-1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[-1].split("```")[0].strip()
    return cleaned
