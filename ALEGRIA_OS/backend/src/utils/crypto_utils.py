import hashlib
import json
import time
from typing import Dict, Any

def generate_sovereign_signature(intention_id: str, operator_id: str, action: str, content_hash: str) -> str:
    """
    Genera un hash único (Acta de Decisión) que vincula una intención, 
    un operador y una acción específica. 
    Representa la trazabilidad legal del sistema ALEGR-IA.
    """
    # Salt soberano (podría venir de una variable de entorno)
    SOVEREIGN_SALT = "ALEGRIA_OS_SOVEREIGN_V1_ACTA"
    
    payload = {
        "intention_id": intention_id,
        "operator": operator_id,
        "action": action,
        "content_hash": content_hash,
        "salt": SOVEREIGN_SALT
    }
    
    # Serialización estable
    payload_str = json.dumps(payload, sort_keys=True)
    
    # Firma (Hash SHA-256)
    signature = hashlib.sha256(payload_str.encode()).hexdigest()
    
    return f"SIG_{signature[:16].upper()}"

def verify_signature(intention_id: str, operator_id: str, action: str, content_hash: str, signature: str) -> bool:
    """
    Verifica si una firma (Acta) es válida recalculando el hash con los mismos parámetros.
    """
    expected = generate_sovereign_signature(intention_id, operator_id, action, content_hash)
    return expected == signature

def get_content_hash(content: str) -> str:
    """Retorna un hash corto del contenido para validación rápida."""
    if not content: return "null"
    return hashlib.md5(content.encode()).hexdigest()[:8]
