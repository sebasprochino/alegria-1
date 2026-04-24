import asyncio
import json
import time
from typing import Dict, Any, List

from src.services.memory.memory_orchestrator import MemoryOrchestrator

memory = MemoryOrchestrator(session_source="system")


class AuditEmitter:
    def __init__(self):
        self.subscribers: List[asyncio.Queue] = []

        # Cola interna (NO pierde eventos)
        self.queue: asyncio.Queue = asyncio.Queue()

        # Config batching
        self.batch_size = 25
        self.flush_interval = 0.1  # segundos

        self._worker_task = None
        self._running = False

    # ─────────────────────────────
    # PUBLIC API
    # ─────────────────────────────
    async def emit(self, event: Dict[str, Any]):
        # 1. Persistencia → SIEMPRE
        await self.queue.put(event)

        # 2. Streaming → best effort
        for q in self.subscribers:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass  # permitido perder UI

    async def subscribe(self):
        q = asyncio.Queue(maxsize=100)  # UI puede dropear
        self.subscribers.append(q)
        return q

    def unsubscribe(self, queue):
        """Remueve un suscriptor para evitar leaks y crashes en SSE."""
        try:
            self.subscribers = [q for q in self.subscribers if q != queue]
        except Exception:
            pass

    # ─────────────────────────────
    # WORKER
    # ─────────────────────────────
    async def start(self):
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        self._running = False
        if self._worker_task:
            await self._worker_task

    async def _worker(self):
        batch: List[Dict[str, Any]] = []
        last_flush = time.time()

        while self._running:
            try:
                timeout = self.flush_interval
                event = await asyncio.wait_for(self.queue.get(), timeout)

                batch.append(event)

                if len(batch) >= self.batch_size:
                    await self._flush(batch)
                    batch.clear()
                    last_flush = time.time()

            except asyncio.TimeoutError:
                # flush por tiempo
                if batch:
                    await self._flush(batch)
                    batch.clear()
                    last_flush = time.time()

    async def _flush(self, batch: List[Dict[str, Any]]):
        try:
            await memory.store_events_batch(batch)
        except Exception as e:
            # GhostNode: no rompe sistema
            print(f"[AuditEmitter] flush error: {e}")


audit_emitter = AuditEmitter()
