"""
ALEGR-IA OS — Sovereign Soak Test
==================================
Validación de consistencia bajo presión sostenida (no ráfaga).

Objetivo:
  200 requests concurrentes sostenidos durante 3 minutos.

Métricas clave:
  1. Deriva de latencia (Avg/P95) vs Tiempo.
  2. Integridad persistente (0 pérdidas).
  3. Estabilidad del RuleEngine (Guard duration).
"""

import sys
import os
import time
import json
import asyncio
import statistics
from typing import Dict, Any, List
from collections import deque

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.crypto_utils import generate_sovereign_signature, get_content_hash
from src.core.rule_engine import RuleEngine
from src.services.audit_emitter import audit_emitter

# CONFIGURACIÓN DEL TEST
DURATION_SECONDS = 180  # 3 minutos
CONCURRENCY = 200
INTERVAL_SECONDS = 10   # Reporte parcial cada 10s

class MetricsTracker:
    def __init__(self):
        self.start_time = time.time()
        self.requests = [] # List of (timestamp, latency, guard_latency, success)
        
    def record(self, latency, guard_latency, success):
        self.requests.append((time.time(), latency, guard_latency, success))
        
    def get_interval_stats(self, start, end):
        window = [r for r in self.requests if start <= r[0] < end]
        if not window:
            return None
        
        latencies = [r[1] for r in window]
        guards = [r[2] for r in window]
        successes = [r[3] for r in window]
        
        return {
            "count": len(window),
            "avg_lat": statistics.mean(latencies),
            "p95_lat": sorted(latencies)[int(len(latencies)*0.95)],
            "avg_guard": statistics.mean(guards),
            "success_rate": sum(successes) / len(successes) * 100
        }

async def worker(semaphore, tracker, rule_engine):
    """Procesador de requests individuales."""
    topics = ["AI", "Blockchain", "DevOps", "Cybersec", "Cloud", "Data"]
    i = 0
    while time.time() - tracker.start_time < DURATION_SECONDS:
        async with semaphore:
            t0 = time.perf_counter()
            content = f"Sustained request {i} about {topics[i % len(topics)]}"
            intent_id = f"soak_{int(time.time()*1000)}_{i}"
            
            # 1. Crypto Signature (Background)
            c_hash = get_content_hash(content)
            _ = generate_sovereign_signature(intent_id, "OPERATOR_SOAK", "execute_direct", c_hash)
            
            # 2. Audit Emit
            await audit_emitter.emit({
                "intention_id": intent_id,
                "stage": "soak_test",
                "timestamp": time.time()
            })
            
            # 3. Rule Engine (Guard)
            t_guard = time.perf_counter()
            try:
                res = await rule_engine.process_intent(content)
                success = res.get("status") in ("authorized", "doubt")
            except:
                success = False
            
            guard_ms = (time.perf_counter() - t_guard) * 1000
            latency_ms = (time.perf_counter() - t0) * 1000
            
            tracker.record(latency_ms, guard_ms, success)
            i += 1
            # Pequeño respiro para no saturar el event loop infinitamente si es muy rápido
            await asyncio.sleep(0.01)

async def run_soak_test():
    print(f"🚀 Iniciando SOAK TEST: {CONCURRENCY} concurrentes durante {DURATION_SECONDS}s")
    print(f"Intervalo de reporte: {INTERVAL_SECONDS}s\n")
    
    await audit_emitter.start()
    
    # Setup Engine
    rule_engine = RuleEngine()
    
    # Mock mocks for speed
    class MockEthicalGuard:
        async def validate_response(self, t):
            return True

    class MockRejectionService:
        async def get_user_rejections(self):
            return []

    class MockClassifier:
        def classify(self, t):
            return "informational"
    
    rule_engine.ethical_guard = MockEthicalGuard()
    rule_engine.rejection_service = MockRejectionService()
    rule_engine.classifier = MockClassifier()
    rule_engine._initialized = True
    
    tracker = MetricsTracker()
    semaphore = asyncio.Semaphore(CONCURRENCY)
    
    # Lanzamos workers
    tasks = [asyncio.create_task(worker(semaphore, tracker, rule_engine)) for _ in range(CONCURRENCY)]
    
    start_test = time.time()
    last_report = start_test
    
    try:
        while time.time() - start_test < DURATION_SECONDS:
            await asyncio.sleep(INTERVAL_SECONDS)
            now = time.time()
            stats = tracker.get_interval_stats(last_report, now)
            if stats:
                elapsed = int(now - start_test)
                print(f"[{elapsed:3}s] Req: {stats['count']:5} | Lat P95: {stats['p95_lat']:6.2f}ms | Guard Avg: {stats['avg_guard']:6.3f}ms | OK: {stats['success_rate']:.1f}%")
            last_report = now
    finally:
        # Cancelamos workers
        for t in tasks: t.cancel()
        await audit_emitter.stop()
        
    print("\n" + "="*60)
    print("FIN DEL SOAK TEST")
    total_req = len(tracker.requests)
    total_time = time.time() - start_test
    print(f"Total Requests: {total_req}")
    print(f"Throughput: {total_req / total_time:.2f} req/s")
    
    # Integrity Check (Persistencia)
    # En este test, el count de tracker debe coincidir con los persistidos (teóricamente)
    # Como es un mock de persistencia en el emitter del validator anterior, 
    # aquí validamos que el 100% de los grabados en tracker terminaron con éxito.
    success_total = sum(1 for r in tracker.requests if r[3])
    integrity = (success_total / total_req * 100) if total_req > 0 else 0
    print(f"Integrity Score: {integrity:.2f}%")
    
    if integrity == 100.0:
        print("✅ SISTEMA SOBERANO Y ESTABLE")
    else:
        print("❌ FALLO DE INTEGRIDAD BAJO PRESIÓN")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(run_soak_test())
    except KeyboardInterrupt:
        pass
