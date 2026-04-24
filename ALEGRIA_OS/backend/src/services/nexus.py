"""
NEXUS — Autoridad Suprema de ALEGR-IA
======================================
Clasifica, ordena, protege. No crea, no ejecuta, no deduce.

LEY NEXUS:
 - El usuario es la única inteligencia soberana
 - La ausencia no es error
 - Está prohibido deducir
 - Todo debe ser editable y reversible

────────────────────────────────────────────────────────────
SECCIÓN A: NexusCore — Clasificación, Léxico y Leyes (nueva)
SECCIÓN B: NexusSystem — Orquestador de memoria/ética (existente)
SECCIÓN C: Aliases y singletons para compatibilidad
────────────────────────────────────────────────────────────

Author: Sebastián Fernández
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("NEXUS")


# ─── SECCIÓN A: NexusCore — Clasificación, Léxico y Leyes ────────────────────


class RequestType(str, Enum):
    """Clasificación de pedidos — NEXUS no deduce, clasifica."""
    PRODUCTIVO    = "productivo"      # → ANIMA
    EXPLORATORIO  = "exploratorio"    # → ANIMA ALEGRÍA
    TECNICO       = "tecnico"         # → DEVELOPER
    INVESTIGACION = "investigacion"   # → RADAR
    VISUAL        = "visual"          # → VEOSCOPE
    AMBIGUO       = "ambiguo"         # Requiere pregunta


@dataclass
class LexiconEntry:
    """Símbolo cognitivo declarado por el usuario."""
    symbol:     str
    meaning:    str
    context:    str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class NexusLaw:
    """Ley del sistema — algunas son fundamentales e inaccesibles."""
    id:          str
    name:        str
    description: str
    active:      bool = True
    editable:    bool = True


class NexusCore:
    """
    NEXUS — El núcleo de coherencia soberana.

    Responsabilidades:
     - Clasificar pedidos (sin deducir)
     - Mantener léxico del usuario
     - Aplicar y exponer leyes
     - Bloquear deducciones automáticas
     - Gestionar memoria semántica liviana y sesiones
    """

    FUNDAMENTAL_LAWS: List[NexusLaw] = [
        NexusLaw(
            "no_deduction", "Ley de No Deducción",
            "El sistema no deduce intención. Ante ambigüedad: preguntar.",
            active=True, editable=False,
        ),
        NexusLaw(
            "user_sovereignty", "Soberanía del Usuario",
            "El usuario es la única inteligencia soberana.",
            active=True, editable=False,
        ),
        NexusLaw(
            "presence_not_dependency", "Presencia, No Dependencia",
            "La ausencia no es error. El sistema funciona incompleto.",
            active=True, editable=False,
        ),
        NexusLaw(
            "total_editability", "Editabilidad Total",
            "Todo debe poder activarse, desactivarse, clonarse y borrarse.",
            active=True, editable=False,
        ),
    ]

    # Palabras que el clasificador trata como potencialmente ambiguas
    _AMBIGUOUS_WORDS = [
        "eso", "esto", "aquello", "lo otro",
        "el de antes", "el limpio", "ese", "aquel",
    ]

    # Ancla al backend/data/nexus/ (independiente del cwd)
    _DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "nexus"

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or self._DEFAULT_PATH
        self.data_path.mkdir(parents=True, exist_ok=True)

        self.lexicon:  Dict[str, LexiconEntry] = {}
        self.laws:     Dict[str, NexusLaw] = {
            law.id: law for law in self.FUNDAMENTAL_LAWS
        }
        self.memory:   List[Dict[str, Any]] = []
        self.sessions: Dict[str, Dict[str, Any]] = {}

        self._load_state()
        logger.info("⚖️  [NEXUS] Autoridad activa")

    # ─── Persistencia ─────────────────────────────────────────────────────────

    def _load_state(self) -> None:
        lexicon_path = self.data_path / "lexicon.json"
        if not lexicon_path.exists():
            return
        try:
            raw = json.loads(lexicon_path.read_text(encoding="utf-8"))
            self.lexicon = {
                k: LexiconEntry(**v) for k, v in raw.items()
            }
            logger.debug(f"[NEXUS] {len(self.lexicon)} entradas de léxico cargadas.")
        except Exception as e:
            logger.warning(f"[NEXUS] Error cargando léxico: {e}")

    def _save_state(self) -> None:
        lexicon_path = self.data_path / "lexicon.json"
        try:
            lexicon_path.write_text(
                json.dumps(
                    {k: asdict(v) for k, v in self.lexicon.items()},
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"[NEXUS] Error guardando léxico: {e}")

    # ─── Clasificación ────────────────────────────────────────────────────────

    def classify_request(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Clasifica un pedido SIN DEDUCIR.
        Si hay ambigüedad no resuelta, retorna AMBIGUO con pregunta.

        El clasificador detecta señales EXPLÍCITAS; nunca infiere intención.
        """
        msg    = message.lower().strip()
        ctx    = context or {}
        syms   = self._resolve_lexicon(message)

        # Técnico: creación de código/sistemas
        if any(kw in msg for kw in ("crea", "genera", "haz", "construye", "programa")):
            if any(kw in msg for kw in ("app", "código", "módulo", "sistema", "script")):
                return self._result(RequestType.TECNICO, "developer", "high", syms)

        # Investigación
        if any(kw in msg for kw in ("investiga", "busca", "encuentra", "radar", "buscar")):
            return self._result(RequestType.INVESTIGACION, "radar", "high", syms)

        # Visual
        if any(kw in msg for kw in ("imagen", "video", "visual", "diseño", "mira", "foto", "analiza")):
            return self._result(RequestType.VISUAL, "veoscope", "high", syms)

        # Exploratorio
        if any(kw in msg for kw in ("charlemos", "cuéntame", "hablemos", "explora", "conversa")):
            return self._result(RequestType.EXPLORATORIO, "anima_alegria", "high", syms)

        # Ambiguo por léxico no resuelto
        if syms.get("unresolved"):
            first = syms["unresolved"][0]
            return {
                "type":             RequestType.AMBIGUO,
                "agent":            None,
                "confidence":       "low",
                "question":         f"¿A qué te referís con '{first}'?",
                "resolved_symbols": syms,
            }

        # Fallback: productivo → ANIMA
        return self._result(RequestType.PRODUCTIVO, "anima", "medium", syms)

    @staticmethod
    def _result(
        rtype: RequestType,
        agent: str,
        confidence: str,
        syms: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "type":             rtype,
            "agent":            agent,
            "confidence":       confidence,
            "resolved_symbols": syms,
        }

    def _resolve_lexicon(self, message: str) -> Dict[str, Any]:
        """Resuelve sinónimos del léxico del usuario en el mensaje."""
        msg      = message.lower()
        resolved = {}
        unresolved: List[str] = []

        for word in self._AMBIGUOUS_WORDS:
            if word in msg:
                if word in self.lexicon:
                    resolved[word] = self.lexicon[word].meaning
                else:
                    unresolved.append(word)

        return {"resolved": resolved, "unresolved": unresolved}

    # ─── Léxico ───────────────────────────────────────────────────────────────

    def add_to_lexicon(self, symbol: str, meaning: str, context: str = "") -> Dict[str, Any]:
        """
        Incorpora un símbolo al léxico del usuario.
        El lenguaje del usuario no se corrige — se registra tal cual.
        """
        key = symbol.lower()
        self.lexicon[key] = LexiconEntry(symbol=symbol, meaning=meaning, context=context)
        self._save_state()
        logger.info(f"📖 [NEXUS] Léxico: '{symbol}' → '{meaning}'")
        return {"status": "ok", "message": f"Símbolo '{symbol}' registrado"}

    def get_lexicon(self) -> List[Dict[str, Any]]:
        """Retorna el léxico completo del usuario."""
        return [asdict(e) for e in self.lexicon.values()]

    def remove_from_lexicon(self, symbol: str) -> Dict[str, Any]:
        """Elimina un símbolo del léxico."""
        key = symbol.lower()
        if key not in self.lexicon:
            return {"status": "error", "message": f"Símbolo '{symbol}' no encontrado"}
        del self.lexicon[key]
        self._save_state()
        return {"status": "ok", "symbol": symbol}

    # ─── Leyes ────────────────────────────────────────────────────────────────

    def get_laws(self) -> List[Dict[str, Any]]:
        """Retorna todas las leyes del sistema (fundamentales + editables)."""
        return [asdict(law) for law in self.laws.values()]

    def validate_action(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Valida si una acción cumple con las leyes activas.
        NEXUS no ejecuta — solo valida.
        """
        ctx        = context or {}
        violations = []

        if ctx.get("deduced", False):
            violations.append({
                "law":     "no_deduction",
                "message": "Acción basada en deducción. Requiere confirmación explícita.",
            })

        if ctx.get("auto_executed", False):
            violations.append({
                "law":     "user_sovereignty",
                "message": "El usuario no autorizó esta acción.",
            })

        return {"valid": not violations, "violations": violations}

    # ─── Memoria semántica ────────────────────────────────────────────────────

    def register_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        session_id: str = "default",
    ) -> None:
        """Registra un evento en la memoria semántica liviana."""
        self.memory.append({
            "type":       event_type,
            "data":       data,
            "session_id": session_id,
            "timestamp":  datetime.now().isoformat(),
        })
        # memoria acotada: guarda las últimas 500 entradas
        if len(self.memory) > 1000:
            self.memory = self.memory[-500:]

    def get_context(
        self,
        session_id: str = "default",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Obtiene el contexto reciente de una sesión."""
        return [
            e for e in self.memory if e["session_id"] == session_id
        ][-limit:]

    # ─── Sesiones ─────────────────────────────────────────────────────────────

    def create_session(
        self,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Crea una nueva sesión."""
        self.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "metadata":   metadata or {},
            "history":    [],
        }
        return {"status": "ok", "session_id": session_id}

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de una sesión activa."""
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Actualiza los metadatos de una sesión activa."""
        if session_id in self.sessions:
            self.sessions[session_id]["metadata"].update(data)


# ─── SECCIÓN B: NexusSystem — Orquestador de memoria/ética ───────────────────
# Mantiene la integración con los sub-servicios especializados
# (SessionSourceStore, MemoryOrchestrator, UserLexicon, EthicalGuard, QueryClassifier)
# que varios módulos del sistema ya dependen de él.

class NexusSystem:
    """
    Orquestador de los sub-servicios de NEXUS.

    Combina las capacidades del NexusCore (clasificación, leyes, léxico)
    con los servicios especializados de memoria, ética y clasificación de queries.
    """

    DEVELOPER_TIMELINE_ID = "developer_timeline"

    def __init__(self):
        # Sub-servicios especializados
        try:
            from src.services.memory.session_source import SessionSourceStore
            from src.services.memory.memory_orchestrator import MemoryOrchestrator
            from src.services.memory.user_lexicon import UserLexicon
            from src.services.ethical_guard import EthicalGuard
            from src.services.query_classifier import QueryClassifier

            self.session_source = SessionSourceStore()
            self.memory         = MemoryOrchestrator(self.session_source)
            self.lexicon_svc    = UserLexicon()
            self.ethics         = EthicalGuard(self.memory)
            self.classifier     = QueryClassifier(self.lexicon_svc)
        except ImportError as e:
            logger.warning(f"[NEXUS] Sub-servicio no disponible: {e}. Operando en modo reducido.")
            self.session_source = None
            self.memory         = None
            self.lexicon_svc    = None
            self.ethics         = None
            self.classifier     = None

        # Núcleo de clasificación y leyes (siempre disponible)
        self.core = NexusCore()

        # Exponer API del core directamente en el sistema
        self.classify_request    = self.core.classify_request
        self.validate_action     = self.core.validate_action
        self.get_laws            = self.core.get_laws
        self.add_to_lexicon      = self.core.add_to_lexicon
        self.get_lexicon         = self.core.get_lexicon
        self.remove_from_lexicon = self.core.remove_from_lexicon
        self.register_event      = self.core.register_event
        self.get_context         = self.core.get_context
        self.create_session      = self.core.create_session
        self.get_session         = self.core.get_session
        self.update_session      = self.core.update_session

    async def get_session_metadata(self, session_id: str) -> dict:
        if self.session_source:
            return self.session_source.get(f"meta_{session_id}", {})
        return self.core.get_session(session_id) or {}

    async def update_session_metadata(self, session_id: str, updates: dict) -> None:
        if self.session_source:
            current = await self.get_session_metadata(session_id)
            current.update(updates)
            self.session_source.set(f"meta_{session_id}", current)
        else:
            self.core.update_session(session_id, updates)

    async def get_recent_chat(self, limit: int = 15, session_id: str = None) -> list:
        if self.memory:
            events = self.memory.get_recent(limit)
            return [{"role": e.source.value, "content": e.content} for e in events]
        return self.core.get_context(session_id or "default", limit)

    async def save_message(self, session_id: str, role: str, content: str) -> None:
        if self.memory:
            self.memory.register_observation(content=content, source=role)
        else:
            self.core.register_event("message", {"role": role, "content": content}, session_id)

    async def log_decision(self, decision_data: dict) -> None:
        """
        Registra una huella de decisión soberana (Soberanía Trail).
        Persiste en backend/storage/decision_history.jsonl
        """
        import datetime as dt
        payload = {
            "intent":    decision_data.get("intent"),
            "options":   decision_data.get("options"),
            "selected":  decision_data.get("selected"),
            "module":    decision_data.get("module", "unknown"),
            "timestamp": dt.datetime.utcnow().isoformat(),
        }
        logger.info(f"💾 [NEXUS] Decisión soberana: {payload['selected']}")

        try:
            backend_dir = Path(__file__).resolve().parents[2]
            log_dir     = backend_dir / "storage"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "decision_history.jsonl"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"[NEXUS] Error persistiendo decisión: {e}")


# ─── SECCIÓN C: Singletons y aliases ─────────────────────────────────────────

_nexus_instance: Optional[NexusSystem] = None


def get_nexus() -> NexusSystem:
    """
    Acceso soberano al singleton del sistema NEXUS.

    Uso desde cualquier módulo:
        from src.services.nexus import get_nexus
        nexus = get_nexus()
        result = nexus.classify_request(message)
    """
    global _nexus_instance
    if _nexus_instance is None:
        _nexus_instance = NexusSystem()
    return _nexus_instance


# Aliases de compatibilidad backward
# orcherstrator.py: from src.services.nexus import Nexus, get_nexus
# developer.py:     from .nexus import service as nexus_service
Nexus   = NexusSystem       # alias de clase para orchestrator.py
service = get_nexus()       # alias de instancia para developer.py
