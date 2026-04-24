# src/services/memory/memory_orchestrator.py

from typing import List
from dataclasses import dataclass, field
from enum import Enum
import time


class SourceType(str, Enum):
    USER = "user"
    SYSTEM = "system"
    EXTERNAL = "external"
    INFO_EXTERNA = "info_externa"    # Nueva categoría para EthicalGuard
    SUPOSICION = "suposicion"        # Nueva categoría para razonamiento
    ANIMA = "anima"
    RADAR = "radar"
    DEVELOPER = "developer"
    ASSISTANT = "assistant"


@dataclass
class MemoryEvent:
    timestamp: float
    content: str
    source: SourceType


@dataclass
class MemoryProposal:
    """
    Propuesta de memoria (contrato público).
    No guarda estado.
    """
    content: str
    source: SourceType = SourceType.SYSTEM
    importance: float = 0.5
    confidence: float = 1.0          # ⭐ Agregado para EthicalGuard
    metadata: dict = field(default_factory=dict) # ⭐ Agregado para fuentes externas (URL, etc)


class WorkingMemory:
    """
    Ventana de memoria viva.
    """
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.events: List[MemoryEvent] = []

    def add(self, event: MemoryEvent):
        self.events.append(event)
        if len(self.events) > self.window_size:
            self.events.pop(0)


class MemoryOrchestrator:
    """
    MEMORIA ÚNICA
    -------------
    Vive sobre una sesión infinita.
    No se reinicia.
    No se duplica.
    """
    def __init__(self, session_source):
        self.session_source = session_source
        self.working_memory = WorkingMemory(window_size=50)
        
        # Integración con la DB Soberana (SQLite)
        from src.infrastructure.database import get_db
        self.db = get_db()

        print("[MEMORY] MemoryOrchestrator inicializado con Persistencia")

    def register_observation(self, content: str, source: str):
        try:
            source_type = SourceType(source)
        except ValueError:
            source_type = SourceType.EXTERNAL  # Fallback seguro para fuentes no registradas
            
        event = MemoryEvent(
            timestamp=time.time(),
            content=content,
            source=source_type
        )
        self.working_memory.add(event)

    def accept_proposal(self, proposal: MemoryProposal):
        """
        Acepta una propuesta y la convierte en evento real.
        """
        event = MemoryEvent(
            timestamp=time.time(),
            content=proposal.content,
            source=proposal.source
        )
        self.working_memory.add(event)

    async def store_event(self, event: dict):
        """
        Persiste un evento de auditoría en la base de datos histórica.
        """
        import json
        try:
            await self.db.insert("audit_log", {
                "intention_id": event.get("intention_id"),
                "stage": event.get("stage"),
                "timestamp": event.get("timestamp"),
                "agent": event.get("agent"),
                "data": json.dumps(event.get("data", {}))
            })
        except Exception as e:
            # GhostNode: la falla en persistencia nunca debe bloquear el sistema
            print(f"⚠️ [MEMORY] Error persistiendo evento de auditoría: {e}")

    async def store_events_batch(self, events: list):
        import json
        rows = [
            {
                "intention_id": e.get("intention_id"),
                "stage": e.get("stage"),
                "timestamp": e.get("timestamp"),
                "agent": e.get("agent"),
                "data": json.dumps(e.get("data", {}))
            }
            for e in events
        ]

        try:
            await self.db.insert_many("audit_log", rows)
        except Exception as e:
            # GhostNode: la falla en persistencia nunca debe bloquear el sistema
            print(f"⚠️ [MEMORY] Error persistiendo batch de auditoría: {e}")


    async def get_events(self, intention_id: str) -> List[dict]:
        """
        Recupera el historial de eventos para una intención específica.
        """
        import json
        rows = await self.db.query(
            "SELECT * FROM audit_log WHERE intention_id = ? ORDER BY timestamp ASC",
            (intention_id,)
        )
        
        # Des-serializar el campo data
        for row in rows:
            if isinstance(row["data"], str):
                try:
                    row["data"] = json.loads(row["data"])
                except:
                    pass
        
        return rows

    def get_recent(self, limit: int = None) -> List[MemoryEvent]:
        events = list(self.working_memory.events)
        if limit:
            return events[-limit:]
        return events
