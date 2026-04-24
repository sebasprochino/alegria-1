"""
ALEGR-IA OS — Analizador de Dataset de Scoring
===============================================
Corre cuando tenés datos reales acumulados en sandbox_runs.jsonl

Detecta:
  1. Falsos HIGH  (score >= 85 pero hay failed_tests)
  2. Falsos LOW   (score < 60 pero sin failed_tests críticos)
  3. Señales inútiles (señales que no correlacionan con nivel real)
  4. Patrones por archivo (qué módulos fallan más)
  5. Distribución real vs distribución ideal

Uso:
  cd backend
  python scripts/analyze_dataset.py
  python scripts/analyze_dataset.py --min-runs 10   # valida mínimo antes de correr
"""

import sys
import os
import json
import argparse
from collections import defaultdict, Counter

# ── UTF-8 en Windows ──────────────────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../logs/sandbox_runs.jsonl")
)

# ── Thresholds (deben coincidir con classify_score en sandbox_runner.py) ──────
HIGH_THRESHOLD   = 85
MEDIUM_THRESHOLD = 60


# ── Carga ─────────────────────────────────────────────────────────────────────

def load_runs(path: str) -> list[dict]:
    if not os.path.exists(path):
        print(f"\n  [ERROR] No existe el archivo: {path}")
        print("  Corré primero algunos patches reales o el script de dataset sintético.\n")
        sys.exit(1)

    runs = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                runs.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  [WARN] Línea {i} inválida, ignorada: {e}")
    return runs


# ── Clasificadores ────────────────────────────────────────────────────────────

def is_false_high(run: dict) -> bool:
    """
    Falso HIGH: score alto pero hay tests que fallaron.
    Esto es el escenario más peligroso.
    """
    return run.get("score", 0) >= HIGH_THRESHOLD and bool(run.get("failed_tests"))


def is_false_low(run: dict) -> bool:
    """
    Falso LOW: score bajo pero sin ningún fallo crítico.
    Indica sobre-penalización (sistema demasiado conservador).
    """
    score = run.get("score", 100)
    failed = run.get("failed_tests", [])
    critical = run.get("critical_fail", False)
    return score < MEDIUM_THRESHOLD and not failed and not critical


def has_borderline_score(run: dict) -> bool:
    """
    Score en zona de borde: 58-62 (puede ir a MEDIUM o LOW con pequeño cambio de pesos).
    """
    return 58 <= run.get("score", 0) <= 62


# ── Análisis ──────────────────────────────────────────────────────────────────

def analyze(runs: list[dict]) -> None:
    n = len(runs)
    sep = "=" * 65

    print(f"\n{sep}")
    print(f"  ALEGR-IA SCORING DATASET ANALYSIS — {n} runs")
    print(f"{sep}\n")

    # ── 1. Distribución global ─────────────────────────────────────────────────
    level_counts = Counter(r.get("level", "?") for r in runs)
    print("  [1] DISTRIBUCIÓN GLOBAL")
    print(f"  {'Nivel':<10} {'Barra':<25} {'Count':>6}  {'%':>6}")
    print("  " + "-" * 55)
    for level in ["HIGH", "MEDIUM", "LOW"]:
        count = level_counts.get(level, 0)
        pct   = count / n * 100
        bar   = "#" * count
        flag  = ""
        # Alertas de distribución
        if level == "HIGH"   and pct > 60: flag = " << SOBREREPRESENTADO"
        if level == "MEDIUM" and pct > 65: flag = " << SISTEMA TIBIO"
        if level == "LOW"    and pct > 70: flag = " << SOBRE-PENALIZA"
        print(f"  {level:<10} {bar:<25} {count:>6}  {pct:>5.1f}%{flag}")

    # Ideal target
    print("\n  Distribución ideal: HIGH 20-40% | MEDIUM 30-50% | LOW 20-40%")

    # ── 2. Falsos HIGH (crítico) ───────────────────────────────────────────────
    false_highs = [r for r in runs if is_false_high(r)]
    print(f"\n{sep}")
    print(f"  [2] FALSOS HIGH — {len(false_highs)} encontrados", end="")
    if false_highs:
        print("  *** ACCION REQUERIDA ***")
    else:
        print("  (ninguno)")
    print(f"  {'-'*55}")
    for r in false_highs:
        patch = r.get("patch", "?")[-50:]
        score = r.get("score")
        fails = ", ".join(r.get("failed_tests", []))
        sigs  = " | ".join(r.get("signals", []))
        print(f"  PATCH:  {patch}")
        print(f"  Score:  {score}  Level: {r.get('level')}")
        print(f"  Fallos: {fails}")
        print(f"  Sigs:   {sigs}")
        print()
    if false_highs:
        print("  >> AJUSTE SUGERIDO: bajar HIGH_THRESHOLD o subir penalización")
        print("     de los tests que fallan en estos casos.\n")

    # ── 3. Falsos LOW ──────────────────────────────────────────────────────────
    false_lows = [r for r in runs if is_false_low(r)]
    print(f"\n{sep}")
    print(f"  [3] FALSOS LOW — {len(false_lows)} encontrados", end="")
    if false_lows:
        print("  (posible sobre-penalización)")
    else:
        print("  (ninguno)")
    print(f"  {'-'*55}")
    for r in false_lows:
        patch = r.get("patch", "?")[-50:]
        score = r.get("score")
        sigs  = " | ".join(r.get("signals", []))
        print(f"  PATCH:  {patch}  Score: {score}")
        print(f"  Sigs:   {sigs}\n")
    if false_lows:
        print("  >> AJUSTE SUGERIDO: revisar si LOW_TEST_COVERAGE o")
        print("     NO_SEMANTIC_VALIDATION penalizan demasiado en este contexto.\n")

    # ── 4. Zona borderline ─────────────────────────────────────────────────────
    borderlines = [r for r in runs if has_borderline_score(r)]
    print(f"\n{sep}")
    print(f"  [4] ZONA BORDERLINE (score 58-62) — {len(borderlines)} runs")
    print(f"  {'-'*55}")
    if borderlines:
        print("  Estos runs pueden cambiar de nivel con ajustes menores de pesos.\n")
        for r in borderlines:
            patch = r.get("patch", "?")[-50:]
            score = r.get("score")
            level = r.get("level")
            fails = ", ".join(r.get("failed_tests", [])) or "—"
            print(f"  score={score} level={level}  fails=[{fails}]")
            print(f"  patch: {patch}\n")
    else:
        print("  (ninguno — zona limpia)\n")

    # ── 5. Señales más frecuentes ──────────────────────────────────────────────
    print(f"\n{sep}")
    print("  [5] SEÑALES MAS FRECUENTES")
    print(f"  {'-'*55}")
    signal_counter: Counter = Counter()
    for r in runs:
        for sig in r.get("signals", []):
            # Normalizar: quitar el detalle numérico de penalty=XX
            base_sig = sig.split(" (penalty")[0]
            signal_counter[base_sig] += 1

    for sig, count in signal_counter.most_common(12):
        pct = count / n * 100
        useless_flag = ""
        # Una señal que aparece en TODOS los runs probablemente no discrimina
        if pct > 80:
            useless_flag = " << posiblemente inutil (demasiado frecuente)"
        print(f"  {count:>4} / {n}  ({pct:>5.1f}%)  {sig}{useless_flag}")

    # ── 6. Patrones por módulo ─────────────────────────────────────────────────
    print(f"\n{sep}")
    print("  [6] PATRONES POR MODULO (archivos que fallan mas)")
    print(f"  {'-'*55}")
    module_failures: dict = defaultdict(lambda: {"total": 0, "failed": 0})
    for r in runs:
        patch_path = r.get("patch", "unknown")
        module = patch_path.split("/")[0] if "/" in patch_path else patch_path
        module_failures[module]["total"] += 1
        if r.get("failed_tests"):
            module_failures[module]["failed"] += 1

    for module, stats in sorted(module_failures.items(),
                                 key=lambda x: x[1]["failed"] / max(x[1]["total"], 1),
                                 reverse=True):
        fail_rate = stats["failed"] / stats["total"] * 100
        bar = "#" * stats["failed"]
        print(f"  {module:<35}  fail_rate={fail_rate:.0f}%  [{bar}]")

    # ── 7. Score stats ─────────────────────────────────────────────────────────
    print(f"\n{sep}")
    print("  [7] ESTADISTICAS DE SCORE")
    print(f"  {'-'*55}")
    scores = [r.get("score", 0) for r in runs]
    if scores:
        avg   = sum(scores) / len(scores)
        mn    = min(scores)
        mx    = max(scores)
        p25   = sorted(scores)[len(scores)//4]
        p75   = sorted(scores)[len(scores)*3//4]
        p50   = sorted(scores)[len(scores)//2]
        print(f"  Min:  {mn}")
        print(f"  P25:  {p25}")
        print(f"  P50:  {p50}  (mediana)")
        print(f"  P75:  {p75}")
        print(f"  Max:  {mx}")
        print(f"  Avg:  {avg:.1f}")

        # Alerta: si mediana está muy alta, el sistema es optimista
        if p50 >= 80:
            print("\n  >> ALERTA: mediana >= 80 — el sistema tiende a ser optimista.")
            print("     Revisar si los tests semanticos estan realmente corriendo.\n")
        elif p50 <= 40:
            print("\n  >> ALERTA: mediana <= 40 — el sistema puede estar sobre-penalizando.\n")

    # ── Resumen ejecutivo ──────────────────────────────────────────────────────
    print(f"\n{sep}")
    print("  RESUMEN EJECUTIVO")
    print(f"  {'-'*55}")
    issues = []
    if false_highs:
        issues.append(f"  !! {len(false_highs)} FALSOS HIGH detectados — ACCION CRITICA REQUERIDA")
    if false_lows:
        issues.append(f"  !  {len(false_lows)} FALSOS LOW detectados — revisar penalizaciones")
    if borderlines:
        issues.append(f"  ~  {len(borderlines)} runs en zona borderline — sensibles a re-calibracion")

    if not issues:
        print("  OK sistema parece bien calibrado con los datos actuales.")
        print("  Continua acumulando runs reales antes del proximo ajuste.")
    else:
        for issue in issues:
            print(issue)

    print(f"\n  Total runs analizados: {n}")
    print(f"  Archivo: {LOG_PATH}")
    print(f"\n{sep}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analiza sandbox_runs.jsonl")
    parser.add_argument(
        "--min-runs", type=int, default=0,
        help="Mínimo de runs requeridos para correr el análisis (default: 0)"
    )
    args = parser.parse_args()

    runs = load_runs(LOG_PATH)

    if args.min_runs and len(runs) < args.min_runs:
        print(f"\n  [INFO] Solo hay {len(runs)} runs. Esperando {args.min_runs} antes de analizar.")
        print("  Seguí corriendo patches reales.\n")
        sys.exit(0)

    # Separar sintéticos de reales para análisis diferenciado
    real_runs      = [r for r in runs if not r.get("patch", "").startswith("synthetic/")]
    synthetic_runs = [r for r in runs if r.get("patch", "").startswith("synthetic/")]

    if real_runs:
        print(f"\n  [{len(real_runs)} runs REALES + {len(synthetic_runs)} sintéticos]")
        print("  Analizando solo runs reales para el diagnóstico de producción...")
        analyze(real_runs)
    else:
        print(f"\n  [AVISO] Solo hay {len(synthetic_runs)} runs sintéticos.")
        print("  El análisis sobre datos sintéticos es útil para validar el modelo,")
        print("  pero el ajuste de pesos requiere runs reales.\n")
        analyze(runs)


if __name__ == "__main__":
    main()
