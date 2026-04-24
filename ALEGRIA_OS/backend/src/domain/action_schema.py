from pydantic import BaseModel
from typing import Dict, Any, Optional

class ActionContract(BaseModel):
    """
    Contrato de Acción (Action Contract)
    
    El LLM ya no 'responde', sino que 'propone acciones'.
    El sistema valida, filtra y ejecuta.
    """
    action: str
    args: Dict[str, Any]
    confidence: float
    reasoning: Optional[str] = None

    def is_executable(self, threshold: float = 0.8) -> bool:
        return self.confidence >= threshold
