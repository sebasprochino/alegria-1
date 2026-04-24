from pydantic import BaseModel
from typing import Dict, Any, Optional

class ActionContract(BaseModel):
    action: str
    args: Dict[str, Any]
    confidence: float
    thought: Optional[str] = None
