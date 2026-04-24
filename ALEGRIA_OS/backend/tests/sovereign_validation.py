"""
ALEGR-IA OS — Sovereign Validation Test
========================================
Validación de consistencia legal del sistema.

Fases:
  FASE 1 → 20 requests (sanity check)
  FASE 2 → 50 requests (baseline real)

Ejes de validación:
  1. Signature Success Rate (crypto_utils)
  2. Pipeline Integrity (AuditEmitter + RuleEngine)
  3. Orphans (escrituras parciales)
  4. Collisions (firmas duplicadas)

Regla dura: 100% o no es soberano.
"""

import sys
import os
import time
import json
import asyncio
import hashlib
import statistics
from typing import Dict, Any, List
from collections import Counter

# Setup path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.crypto_utils import (
    generate_sovereign_signature,
    verify_signature,
    get_content_hash,
)


# ─── Test Data Generator ─────────────────────────────────────────────────────

def generate_test_intents(n: int) -> List[Dict[str, Any]]:
    """Genera N intenciones de test con variación realista."""
    templates = [
        "buscar información sobre {topic}",
        "crear un script para {topic}",
        "analizar imagen de {topic}",
        "escribir contenido sobre {topic}",
        "investigar tendencias en {topic}",
        "ejecutar pipeline de {topic}",
        "generar reporte de {topic}",
        "optimizar rendimiento de {topic}",
        "configurar módulo de {topic}",
        "diagnosticar error en {topic}",
    ]
    topics = [
        "inteligencia artificial", "blockchain", "diseño UX",
        "marketing digital", "ciberseguridad", "cloud computing",
        "machine learning", "fintech", "edtech", "healthtech",
        "data science", "devops", "microservicios", "API REST",
        "frontend react", "backend python", "bases de datos",
        "testing automatizado", "CI/CD pipelines", "arquitectura",
    ]
    actions = [
        "execute_direct", "research_first", "dev_execute",
        "force_render", "retry_strict",
    ]
    operators = ["OPERATOR_01", "OPERATOR_02", "OPERATOR_ADMIN"]

    intents = []
    for i in range(n):
        template = templates[i % len(templates)]
        topic = topics[i % len(topics)]
        content = template.format(topic=topic)
        intents.append({
            "id": f"intent_{i:04d}_{int(time.time()*1000) % 100000}",
            "content": content,
            "action": actions[i % len(actions)],
            "operator": operators[i % len(operators)],
            "index": i,
        })
    return intents


# ─── MÓDULO 1: Validación Criptográfica ──────────────────────────────────────

def test_crypto_signatures(intents: List[Dict]) -> Dict[str, Any]:
    """Valida generación y verificación de firmas soberanas."""
    results = {
        "total": len(intents),
        "generated": 0,
        "verified": 0,
        "failed_gen": [],
        "failed_verify": [],
        "signatures": [],
        "latencies_ms": [],
    }

    for intent in intents:
        c_hash = get_content_hash(intent["content"])

        # Generación
        t0 = time.perf_counter()
        try:
            sig = generate_sovereign_signature(
                intention_id=intent["id"],
                operator_id=intent["operator"],
                action=intent["action"],
                content_hash=c_hash,
            )
            results["generated"] += 1
            results["signatures"].append(sig)
        except Exception as e:
            results["failed_gen"].append({"intent": intent["id"], "error": str(e)})
            continue

        gen_ms = (time.perf_counter() - t0) * 1000

        # Verificación
        t1 = time.perf_counter()
        try:
            valid = verify_signature(
                intention_id=intent["id"],
                operator_id=intent["operator"],
                action=intent["action"],
                content_hash=c_hash,
                signature=sig,
            )
            if valid:
                results["verified"] += 1
            else:
                results["failed_verify"].append({
                    "intent": intent["id"],
                    "sig": sig,
                    "reason": "recalc_mismatch",
                })
        except Exception as e:
            results["failed_verify"].append({"intent": intent["id"], "error": str(e)})

        verify_ms = (time.perf_counter() - t1) * 1000
        results["latencies_ms"].append(gen_ms + verify_ms)

    return results


# ─── MÓDULO 2: Detección de Colisiones ───────────────────────────────────────

def test_collisions(signatures: List[str]) -> Dict[str, Any]:
    """Detecta firmas duplicadas (BUG CRÍTICO si hay colisiones)."""
    counter = Counter(signatures)
    duplicates = {sig: count for sig, count in counter.items() if count > 1}
    return {
        "total_signatures": len(signatures),
        "unique_signatures": len(counter),
        "collisions": len(duplicates),
        "collision_details": duplicates,
    }


# ─── MÓDULO 3: Pipeline Integrity ────────────────────────────────────────────

async def test_pipeline_integrity(intents: List[Dict]) -> Dict[str, Any]:
    """Valida que el pipeline RuleEngine procesa sin pérdida de eventos."""
    from src.core.rule_engine import RuleEngine
    from src.services.audit_emitter import AuditEmitter

    # Fresh instances para test aislado
    emitter = AuditEmitter()
    captured_events = []

    # Suscriptor de captura
    queue = await emitter.subscribe()

    async def drain_queue():
        while True:
            try:
                ev = queue.get_nowait()
                captured_events.append(ev)
            except asyncio.QueueEmpty:
                break

    results = {
        "total": len(intents),
        "emitted": 0,
        "captured": 0,
        "rule_engine_processed": 0,
        "rule_engine_errors": [],
        "latencies_ms": [],
        "guard_durations_ms": [],
    }

    # Mock rule engine con dependencias mínimas
    rule_engine = RuleEngine()

    # Mock ethical_guard y rejection_service para test aislado
    class MockEthicalGuard:
        async def validate_response(self, text):
            return True

    class MockRejectionService:
        async def get_user_rejections(self):
            return []

    class MockClassifier:
        def classify(self, text):
            return "informational"

    rule_engine.ethical_guard = MockEthicalGuard()
    rule_engine.rejection_service = MockRejectionService()
    rule_engine.classifier = MockClassifier()
    rule_engine._initialized = True

    for intent in intents:
        t0 = time.perf_counter()

        # Emit audit event
        try:
            await emitter.emit({
                "intention_id": intent["id"],
                "stage": "validation_test",
                "timestamp": time.time(),
                "agent": "SOVEREIGN_VALIDATOR",
                "data": {"action": intent["action"], "content": intent["content"][:50]},
            })
            results["emitted"] += 1
        except Exception as e:
            results["rule_engine_errors"].append({
                "intent": intent["id"],
                "phase": "emit",
                "error": str(e),
            })

        # Process through RuleEngine
        t_guard = time.perf_counter()
        try:
            re_result = await rule_engine.process_intent(intent["content"])
            if re_result.get("status") in ("authorized", "doubt"):
                results["rule_engine_processed"] += 1
            else:
                results["rule_engine_errors"].append({
                    "intent": intent["id"],
                    "phase": "process",
                    "status": re_result.get("status"),
                    "reason": re_result.get("reason", "unknown"),
                })
        except Exception as e:
            results["rule_engine_errors"].append({
                "intent": intent["id"],
                "phase": "process",
                "error": str(e),
            })

        guard_ms = (time.perf_counter() - t_guard) * 1000
        results["guard_durations_ms"].append(guard_ms)

        total_ms = (time.perf_counter() - t0) * 1000
        results["latencies_ms"].append(total_ms)

    # Drain captured events
    await asyncio.sleep(0.05)
    await drain_queue()
    results["captured"] = len(captured_events)

    emitter.unsubscribe(queue)
    return results


# ─── MÓDULO 4: Detección de Huérfanos ────────────────────────────────────────

def test_orphans(
    crypto_results: Dict, pipeline_results: Dict, intents: List[Dict]
) -> Dict[str, Any]:
    """
    Detecta inconsistencias reales (no cosméticas).

    Arquitectura persist-first:
      - orphan_signatures: firma generada pero no verificable → CRÍTICO
      - orphan_pipeline: intent no procesado por RuleEngine → CRÍTICO
      - sse_drops: eventos no capturados por suscriptor SSE → NO CRÍTICO (by design)
    """
    processed_count = pipeline_results["rule_engine_processed"]
    emitted_count = pipeline_results["emitted"]
    captured_count = pipeline_results["captured"]

    orphan_signatures = crypto_results["generated"] - crypto_results["verified"]
    orphan_pipeline = len(intents) - processed_count
    sse_drops = emitted_count - captured_count

    # Solo fallos CRÍTICOS cuentan como huérfanos reales
    total_critical = orphan_signatures + orphan_pipeline

    return {
        "orphan_signatures": orphan_signatures,
        "orphan_pipeline": orphan_pipeline,
        "total_orphans": total_critical,
        "sse_drops": sse_drops,  # non-critical, informational
        "detail": {
            "sigs_generated": crypto_results["generated"],
            "sigs_verified": crypto_results["verified"],
            "events_emitted": emitted_count,
            "events_captured": captured_count,
            "pipeline_input": len(intents),
            "pipeline_processed": processed_count,
        },
    }


# ─── REPORTE ─────────────────────────────────────────────────────────────────

def compute_latency_stats(latencies: List[float]) -> Dict[str, float]:
    if not latencies:
        return {"avg": 0, "p50": 0, "p95": 0, "p99": 0, "max": 0}
    s = sorted(latencies)
    n = len(s)
    return {
        "avg": round(statistics.mean(s), 3),
        "p50": round(s[n // 2], 3),
        "p95": round(s[int(n * 0.95)], 3),
        "p99": round(s[int(n * 0.99)], 3),
        "max": round(s[-1], 3),
    }


def print_report(phase: int, n: int, crypto: Dict, collisions: Dict,
                 pipeline: Dict, orphans: Dict):
    sig_rate = (crypto["verified"] / crypto["total"] * 100) if crypto["total"] else 0
    pipe_rate = (pipeline["rule_engine_processed"] / pipeline["total"] * 100) if pipeline["total"] else 0

    crypto_lat = compute_latency_stats(crypto["latencies_ms"])
    pipe_lat = compute_latency_stats(pipeline["latencies_ms"])
    guard_lat = compute_latency_stats(pipeline["guard_durations_ms"])

    sep = "=" * 65
    print(f"\n{sep}")
    print(f"  ALEGR-IA OS — SOVEREIGN VALIDATION REPORT")
    print(f"  FASE {phase} → {n} requests")
    print(f"  Timestamp: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}")
    print(sep)

    # ── Resultados Primarios ──
    print(f"\n  ┌─────────────────────────────────────────────────┐")
    print(f"  │  Signature Success Rate:  {sig_rate:6.1f}%  ({crypto['verified']}/{crypto['total']})")
    print(f"  │  Pipeline Integrity:      {pipe_rate:6.1f}%  ({pipeline['rule_engine_processed']}/{pipeline['total']})")
    print(f"  │  Orphans:                 {orphans['total_orphans']}")
    print(f"  │  Collisions:              {collisions['collisions']}")
    print(f"  └─────────────────────────────────────────────────┘")

    # ── Verdict ──
    all_pass = (
        sig_rate == 100.0
        and pipe_rate == 100.0
        and orphans["total_orphans"] == 0
        and collisions["collisions"] == 0
    )
    verdict = "✅ SOBERANO" if all_pass else "❌ FALLO — NO ES SOBERANO"
    print(f"\n  VEREDICTO: {verdict}")

    # ── Alertas ──
    alerts = []
    if sig_rate < 100:
        alerts.append(f"  ⚠️  Firma: {crypto['failed_verify']}")
    if pipe_rate < 100:
        alerts.append(f"  ⚠️  Pipeline: {pipeline['rule_engine_errors'][:3]}")
    if orphans["total_orphans"] > 0:
        alerts.append(f"  ⚠️  Huérfanos: {json.dumps(orphans['detail'])}")
    if collisions["collisions"] > 0:
        alerts.append(f"  🔴  COLISIONES: {json.dumps(collisions['collision_details'])}")

    if alerts:
        print(f"\n  ── ALERTAS ──")
        for a in alerts:
            print(a)

    # ── Latencia ──
    print(f"\n  ── LATENCIA (ms) ──")
    print(f"  Crypto:    avg={crypto_lat['avg']}  p50={crypto_lat['p50']}  p95={crypto_lat['p95']}  max={crypto_lat['max']}")
    print(f"  Pipeline:  avg={pipe_lat['avg']}  p50={pipe_lat['p50']}  p95={pipe_lat['p95']}  max={pipe_lat['max']}")
    print(f"  Guard:     avg={guard_lat['avg']}  p50={guard_lat['p50']}  p95={guard_lat['p95']}  max={guard_lat['max']}")

    # ── Señales de Alerta (aunque pase) ──
    if crypto_lat["p95"] > 2 * crypto_lat["avg"] and crypto_lat["avg"] > 0:
        print(f"\n  ⚠️  SEÑAL: latency P95 ({crypto_lat['p95']}) > 2x promedio ({crypto_lat['avg']}) → cuello de botella")
    if guard_lat["max"] > guard_lat["avg"] * 3 and guard_lat["avg"] > 0:
        print(f"  ⚠️  SEÑAL: guard duration creciendo → revisar RuleEngine")

    print(f"\n{sep}\n")
    return all_pass


# ─── MAIN ────────────────────────────────────────────────────────────────────

async def run_phase(phase: int, n: int) -> bool:
    print(f"\n🚀 Ejecutando FASE {phase} → {n} requests...")
    intents = generate_test_intents(n)

    # 1. Crypto
    print(f"  [1/4] Validación criptográfica...")
    crypto = test_crypto_signatures(intents)

    # 2. Collisions
    print(f"  [2/4] Detección de colisiones...")
    collisions = test_collisions(crypto["signatures"])

    # 3. Pipeline
    print(f"  [3/4] Integridad del pipeline...")
    pipeline = await test_pipeline_integrity(intents)

    # 4. Orphans
    print(f"  [4/4] Detección de huérfanos...")
    orphans = test_orphans(crypto, pipeline, intents)

    return print_report(phase, n, crypto, collisions, pipeline, orphans)


async def main():
    # FASE 1: 20 requests (sanity)
    phase1_pass = await run_phase(1, 20)

    if not phase1_pass:
        print("❌ FASE 1 FALLÓ — PARANDO.")
        sys.exit(1)

    print("✅ FASE 1 PASÓ → Ejecutando FASE 2...")

    # FASE 2: 50 requests (baseline real)
    phase2_pass = await run_phase(2, 50)

    if not phase2_pass:
        print("❌ FASE 2 FALLÓ.")
        sys.exit(1)

    print("✅ FASE 2 PASÓ → Ejecutando FASE 3...")

    # FASE 3: 100 requests (stress)
    phase3_pass = await run_phase(3, 100)

    if not phase3_pass:
        print("❌ FASE 3 FALLÓ.")
        sys.exit(1)

    print("✅ FASE 3 PASÓ → Ejecutando FASE 4...")

    # FASE 4: 200 requests (límite)
    phase4_pass = await run_phase(4, 200)

    if not phase4_pass:
        print("❌ FASE 4 FALLÓ.")
        sys.exit(1)

    print("🔥 4 FASES PASARON — Sistema soberano validado bajo carga.")


if __name__ == "__main__":
    asyncio.run(main())
