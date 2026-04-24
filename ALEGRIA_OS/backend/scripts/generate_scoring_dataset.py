"""
ALEGR-IA OS — Dataset Generator para Calibración de Scoring
=============================================================
Genera 15 runs sintéticos cubriendo los 5 escenarios requeridos:

  TIPO 1 — patch correcto             → HIGH esperado
  TIPO 2 — patch rompe endpoint       → LOW o MEDIUM
  TIPO 3 — patch rompe identidad      → LOW
  TIPO 4 — técnico OK, semántica FAIL → MEDIUM/LOW
  TIPO 5 — patch inútil (no crítico)  → MEDIUM

Uso:
  cd backend
  python scripts/generate_scoring_dataset.py

Genera:   backend/logs/sandbox_runs.jsonl
"""

import sys
import os
import json
import datetime

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.sandbox_runner import compute_confidence_score

LOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../logs/sandbox_runs.jsonl")
)

# ── Casos de test sintéticos ──────────────────────────────────────────────────
# Formato: (label, tipo, tests[], semantic[])
# tests/semantic son listas de dicts como los que devuelve sandbox_runner.

SCENARIOS = [

    # ─── TIPO 1: Patch correcto ───────────────────────────────────────────────
    ("T1-A: Todo OK", "correct_patch", [
        {"test": "Health Check",              "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",       "status": 200, "success": True},
        {"test": "Developer Agent Endpoint",  "status": 200, "success": True},
    ], [
        {"test": "developer_structure",      "status": "ok", "success": True},
        {"test": "developer_content_length", "status": "ok", "success": True},
        {"test": "developer_identity",       "status": "ok", "success": True},
    ]),

    ("T1-B: Todo OK (variante)", "correct_patch", [
        {"test": "Health Check",              "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",       "status": 200, "success": True},
        {"test": "Developer Agent Endpoint",  "status": 200, "success": True},
    ], [
        {"test": "developer_structure",      "status": "ok", "success": True},
        {"test": "developer_content_length", "status": "ok", "success": True},
        {"test": "developer_identity",       "status": "ok", "success": True},
    ]),

    # ─── TIPO 2: Patch rompe endpoint ────────────────────────────────────────
    ("T2-A: Endpoint caído (Health Check falla)", "endpoint_broken", [
        {"test": "Health Check",              "error": "Connection refused", "success": False},
        {"test": "Anima Chat Endpoint",       "error": "Connection refused", "success": False},
        {"test": "Developer Agent Endpoint",  "error": "Connection refused", "success": False},
    ], [
        {"test": "developer_semantic_critical", "error": "Connection refused", "success": False, "critical": True},
    ]),

    ("T2-B: Solo Developer Endpoint caído", "endpoint_broken", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        {"test": "Developer Agent Endpoint", "error": "HTTPError 500", "status": 500, "success": False},
    ], [
        {"test": "developer_semantic_critical", "error": "HTTP Error 500", "success": False, "critical": True},
    ]),

    ("T2-C: Developer endpoint → 404", "endpoint_broken", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        {"test": "Developer Agent Endpoint", "error": "HTTPError 404", "status": 404, "success": False},
    ], [
        {"test": "developer_semantic_critical", "error": "HTTP Error 404", "success": False, "critical": True},
    ]),

    # ─── TIPO 3: Patch rompe identidad ────────────────────────────────────────
    ("T3-A: LLM devuelve error disfrazado", "identity_broken", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        {"test": "Developer Agent Endpoint", "status": 200, "success": True},
    ], [
        {"test": "developer_structure",      "status": "ok", "success": True},
        {"test": "developer_content_length", "status": "ok", "success": True},
        {"test": "developer_identity",
         "error": "La respuesta delata un error interno del LLM o del pipeline",
         "success": False, "critical": True},
    ]),

    ("T3-B: LLM semantic safety falla (respuesta contiene 'falló')", "identity_broken", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        {"test": "Developer Agent Endpoint", "status": 200, "success": True},
    ], [
        {"test": "developer_structure",       "status": "ok", "success": True},
        {"test": "developer_content_length",  "status": "ok", "success": True},
        {"test": "developer_semantic_safety",
         "error": "La respuesta indica un error interno del LLM o pipeline",
         "success": False},
    ]),

    ("T3-C: Identity + structure ambos fallan", "identity_broken", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        {"test": "Developer Agent Endpoint", "status": 200, "success": True},
    ], [
        {"test": "developer_structure",
         "error": "Falta el campo 'response' en la respuesta", "success": False},
        {"test": "developer_content_length",  "status": "ok", "success": True},
        {"test": "developer_identity",
         "error": "La respuesta delata un error interno del LLM o del pipeline",
         "success": False, "critical": True},
    ]),

    # ─── TIPO 4: Técnico OK, semántica FAIL ────────────────────────────────────
    ("T4-A: Técnico OK / Respuesta vacía", "semantic_only_fail", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        {"test": "Developer Agent Endpoint", "status": 200, "success": True},
    ], [
        {"test": "developer_structure",      "status": "ok", "success": True},
        {"test": "developer_content_length",
         "error": "La respuesta es demasiado corta o vacía", "success": False},
        {"test": "developer_identity",       "status": "ok", "success": True},
    ]),

    ("T4-B: Técnico OK / Sin campo response", "semantic_only_fail", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        {"test": "Developer Agent Endpoint", "status": 200, "success": True},
    ], [
        {"test": "developer_structure",
         "error": "Falta el campo 'response' en la respuesta", "success": False},
        {"test": "developer_content_length", "status": "ok", "success": True},
        {"test": "developer_identity",       "status": "ok", "success": True},
    ]),

    ("T4-C: Técnico OK / Respuesta vacía + sin structure", "semantic_only_fail", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        {"test": "Developer Agent Endpoint", "status": 200, "success": True},
    ], [
        {"test": "developer_structure",
         "error": "Falta el campo 'response' en la respuesta", "success": False},
        {"test": "developer_content_length",
         "error": "La respuesta es demasiado corta o vacía", "success": False},
        {"test": "developer_identity",       "status": "ok", "success": True},
    ]),

    # ─── TIPO 5: Patch inútil (no cambia nada crítico) ────────────────────────
    ("T5-A: Patch cosmético (comentario)", "inert_patch", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        {"test": "Developer Agent Endpoint", "status": 200, "success": True},
    ], [
        {"test": "developer_structure",      "status": "ok", "success": True},
        {"test": "developer_content_length", "status": "ok", "success": True},
        {"test": "developer_identity",       "status": "ok", "success": True},
    ]),

    ("T5-B: Patch solo logs — falla coverage", "inert_patch", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "status": 200, "success": True},
        # Solo 2 tests técnicos → LOW_TEST_COVERAGE heurística
    ], [
        {"test": "developer_structure",      "status": "ok", "success": True},
        {"test": "developer_content_length", "status": "ok", "success": True},
        {"test": "developer_identity",       "status": "ok", "success": True},
    ]),

    ("T5-C: Patch endpoint no crítico falla", "inert_patch", [
        {"test": "Health Check",             "status": 200, "success": True},
        {"test": "Anima Chat Endpoint",      "error": "Timeout", "success": False},
        {"test": "Developer Agent Endpoint", "status": 200, "success": True},
    ], [
        {"test": "developer_structure",      "status": "ok", "success": True},
        {"test": "developer_content_length", "status": "ok", "success": True},
        {"test": "developer_identity",       "status": "ok", "success": True},
    ]),

]


# ── Correr y persistir ────────────────────────────────────────────────────────

def run():
    # Forzar UTF-8 en stdout para evitar UnicodeEncodeError en Windows (cp1252)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    print(f"\n{'='*65}")
    print(f"  ALEGR-IA SCORING DATASET GENERATOR — {len(SCENARIOS)} escenarios")
    print(f"{'='*65}\n")
    print(f"{'ESCENARIO':<45} {'SCORE':>6} {'NIVEL':<8} {'SEÑALES'}")
    print("-" * 65)

    results_by_type = {}

    for label, scenario_type, tests, semantic in SCENARIOS:
        confidence = compute_confidence_score(tests, semantic)
        score  = confidence["score"]
        level  = confidence["level"]
        signals = confidence["signals"]

        # Recopilar por tipo para resumen final
        results_by_type.setdefault(scenario_type, []).append(level)

        # Construir log entry
        failed_tests = (
            [t["test"] for t in tests    if not t.get("success")] +
            [s["test"] for s in semantic if not s.get("success")]
        )
        log_entry = {
            "timestamp":    datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
            "patch":        f"synthetic/{label.replace(' ', '_').replace(':', '')}",
            "scenario_type": scenario_type,
            "score":        score,
            "level":        level,
            "critical_fail": confidence.get("critical_fail", False),
            "failed_tests": failed_tests,
            "signals":      signals,
        }

        # Persistir
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # Imprimir fila
        signal_short = ", ".join(signals) if signals else "—"
        print(f"  {label:<43} {score:>5}  {level:<8} {signal_short[:35]}")

    # ── Resumen por tipo ───────────────────────────────────────────────────────
    print(f"\n{'='*65}")
    print("  RESUMEN POR TIPO DE ESCENARIO")
    print(f"{'='*65}")
    for stype, levels in results_by_type.items():
        dist = {l: levels.count(l) for l in set(levels)}
        print(f"  {stype:<30} -> {dist}")

    # ── Distribución global ────────────────────────────────────────────────────
    all_levels = [l for levels in results_by_type.values() for l in levels]
    total = len(all_levels)
    print(f"\n  Distribución global ({total} runs):")
    for level in ["HIGH", "MEDIUM", "LOW"]:
        count = all_levels.count(level)
        pct   = count / total * 100
        bar   = "█" * count
        print(f"    {level:<8} {bar:<20} {count:>2} / {total}  ({pct:.0f}%)")

    print(f"\n  ✅ Dataset guardado en: {LOG_PATH}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    run()
