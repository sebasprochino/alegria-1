import os
import shutil
import subprocess
import tempfile
import time
import logging
import urllib.request
import json
import datetime

logger = logging.getLogger("ALEGRIA_SANDBOX_RUNNER")

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

def run_tests(base_url: str):
    """
    Ejecuta assertions reales sobre los endpoints críticos del sandbox.
    """
    results = []

    def test(name, url, method="GET", data=None):
        try:
            req = urllib.request.Request(url, method=method)
            if data:
                req.add_header('Content-Type', 'application/json')
                json_data = json.dumps(data).encode('utf-8')
                res = urllib.request.urlopen(req, data=json_data, timeout=5)
            else:
                res = urllib.request.urlopen(req, timeout=5)
            
            results.append({
                "test": name,
                "status": res.getcode(),
                "success": 200 <= res.getcode() < 300
            })
        except urllib.error.HTTPError as e:
            results.append({
                "test": name,
                "status": e.code,
                "error": str(e),
                "success": False
            })
        except Exception as e:
            results.append({
                "test": name,
                "error": str(e),
                "success": False
            })

    # 🧪 TESTS CLAVE
    test("Health Check", f"{base_url}/status")
    
    # Anima Chat (Validación de existencia de ruta)
    test("Anima Chat Endpoint", f"{base_url}/anima/chat", method="POST", data={"message": "ping"})
    
    # Developer Agent (Validación de existencia de ruta)
    test("Developer Agent Endpoint", f"{base_url}/api/developer/agent-chat", method="POST", data={"messages": [{"role": "user", "content": "ping"}]})

    return results

# Tests que, si fallan, son CRÍTICOS para el sistema (peso diferencial)
_CRITICAL_SEMANTIC_TESTS = {"developer_identity", "developer_semantic_critical"}

def run_semantic_tests(base_url: str):
    """
    Ejecuta assertions semánticas para validar que el sistema no solo levante,
    sino que se comporte correctamente y mantenga su identidad.

    Cada sub-test es independiente: un fallo en uno NO impide la evaluación
    de los siguientes. Esto evita que fallos encubiertos inflen el score.
    """
    results = []

    def post(url, payload):
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        return urllib.request.urlopen(req, timeout=10)

    # ── Paso 1: Intentar obtener respuesta del Developer Agent ──────────────
    raw_data = None
    call_error = None
    try:
        res = post(
            f"{base_url}/api/developer/agent-chat",
            {
                "messages": [{"role": "user", "content": "hola"}],
                "mode": "chat"
            }
        )
        raw_data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        call_error = str(e)

    # ── Sub-test A: Conectividad al endpoint ────────────────────────────────
    if call_error:
        results.append({
            "test": "developer_semantic_critical",
            "error": call_error,
            "success": False,
            "critical": True
        })
        # Sin respuesta, los siguientes sub-tests no tienen sentido
        return results

    # ── Sub-test B: Estructura de la respuesta ──────────────────────────────
    if "response" not in raw_data:
        results.append({
            "test": "developer_structure",
            "error": "Falta el campo 'response' en la respuesta",
            "success": False,
            "critical": False
        })
    else:
        results.append({
            "test": "developer_structure",
            "status": "ok",
            "success": True,
            "critical": False
        })

    # ── Sub-test C: Longitud mínima de contenido ────────────────────────────
    response_text = raw_data.get("response", "").lower()
    if len(response_text) < 10:
        results.append({
            "test": "developer_content_length",
            "error": "La respuesta es demasiado corta o vacía",
            "success": False,
            "critical": False
        })
    else:
        results.append({
            "test": "developer_content_length",
            "status": "ok",
            "success": True,
            "critical": False
        })

    # ── Sub-test D: Identidad semántica (CRÍTICO) ───────────────────────────
    # El agente NO debe devolver mensajes de error disfrazados como respuesta.
    if "error" in response_text or "falló" in response_text or "exception" in response_text:
        results.append({
            "test": "developer_identity",
            "error": "La respuesta delata un error interno del LLM o del pipeline",
            "success": False,
            "critical": True
        })
    elif len(response_text) >= 10:
        results.append({
            "test": "developer_identity",
            "status": "ok",
            "success": True,
            "critical": True
        })

    return results

def classify_score(score):
    if score >= 85:
        return "HIGH"
    elif score >= 60:
        return "MEDIUM"
    else:
        return "LOW"

# Pesos diferenciales por categoría de test semántico
_SEMANTIC_WEIGHTS = {
    "developer_semantic_critical": 35,  # Endpoint inaccesible — crítico
    "developer_identity": 35,           # Respuesta incoherente / error encubierto
    "developer_structure": 20,          # Falta campo 'response'
    "developer_content_length": 20,     # Respuesta vacía
    "developer_semantic_safety": 25,    # Error LLM detectado (nivel medio-alto)
}
_DEFAULT_SEMANTIC_PENALTY = 20

def compute_confidence_score(tests, semantic):
    """
    Calcula un puntaje de confianza (0-100) basado en los resultados de las validaciones.

    Lógica de calibración:
    - Fallos técnicos: -30 c/u (infraestructura)
    - Fallos semánticos: peso diferencial según criticidad del test
    - Caps escalonados por severidad:
        · identity / LLM-error → cap 49 (LOW forzado — sistema que responde mal)
        · endpoint caído       → cap 59 (MEDIUM máximo — comportamiento desconocido)
    """
    score = 100
    signals = []

    # 🔧 Penalización técnica — peso fijo (fallos de infraestructura)
    tech_fails = [t for t in tests if not t.get("success")]
    if tech_fails:
        penalty = len(tech_fails) * 30
        score -= penalty
        for f in tech_fails:
            signals.append(f"TECH_FAIL: {f['test']}")

    # 🧠 Penalización semántica — peso diferencial por criticidad
    semantic_fails = [s for s in semantic if not s.get("success")]
    for f in semantic_fails:
        test_name = f.get("test", "")
        penalty = _SEMANTIC_WEIGHTS.get(test_name, _DEFAULT_SEMANTIC_PENALTY)
        score -= penalty
        signals.append(f"SEM_FAIL: {test_name} (penalty={penalty})")

    # 🚨 Caps escalonados por severidad semántica
    #
    # Tier 1 — LOW forzado (sistema no confiable):
    #   developer_identity falla   → el agente responde mal (peor que no responder)
    #   developer_semantic_safety  → el LLM delata error interno en su respuesta
    #
    # Tier 2 — MEDIUM máximo (sistema inaccesible, no sabemos cómo responde):
    #   developer_semantic_critical → endpoint caído

    failed_test_names = {f.get("test", "") for f in semantic_fails}

    identity_compromised = bool(
        failed_test_names & {"developer_identity", "developer_semantic_safety"}
    )
    endpoint_down = "developer_semantic_critical" in failed_test_names
    critical_fail = identity_compromised or endpoint_down

    if identity_compromised:
        score = min(score, 49)   # LOW directo — sistema que responde mal
        signals.append("IDENTITY_COMPROMISED_CAP_49")
    elif endpoint_down:
        score = min(score, 59)   # MEDIUM máximo — no podemos evaluar comportamiento
        signals.append("ENDPOINT_DOWN_CAP_59")

    # ⚠️ Heurísticas de Cobertura
    if len(tests) < 3:
        score -= 10
        signals.append("LOW_TEST_COVERAGE")

    if not semantic:
        score -= 15
        signals.append("NO_SEMANTIC_VALIDATION")

    # Clamping final
    score = max(0, min(score, 100))

    return {
        "score": score,
        "level": classify_score(score),
        "signals": signals,
        "critical_fail": critical_fail
    }

_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../logs/sandbox_runs.jsonl"))

def _persist_run_log(file_path: str, result: dict):
    """
    Guarda cada run de sandbox como una línea JSON (JSONL) para análisis de patrones.
    Formato por línea:
      { patch, score, level, failed_tests, critical_fail, timestamp }
    """
    try:
        confidence = result.get("confidence", {})
        failed_tests = (
            [t["test"] for t in result.get("tests", []) if not t.get("success")] +
            [s["test"] for s in result.get("semantic", []) if not s.get("success")]
        )
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "patch": file_path,
            "score": confidence.get("score"),
            "level": confidence.get("level"),
            "critical_fail": confidence.get("critical_fail", False),
            "failed_tests": failed_tests,
            "signals": confidence.get("signals", []),
        }
        os.makedirs(os.path.dirname(_LOG_PATH), exist_ok=True)
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        logger.info(f"📝 Run log guardado: score={log_entry['score']} level={log_entry['level']}")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo guardar run log: {e}")

def run_sandbox(file_path: str, new_content: str):
    """
    Levanta una instancia efímera del sistema en un puerto alternativo
    para validar la integridad del parche en runtime.
    """
    sandbox_dir = None
    proc = None
    try:
        # 📁 Crear sandbox temporal
        sandbox_dir = tempfile.mkdtemp(prefix="alegria_sandbox_")
        logger.info(f"📂 Creando sandbox en: {sandbox_dir}")

        # Copiar proyecto entero (ignorar venv y data pesada si es posible)
        # Por ahora copia simple para asegurar integridad
        shutil.copytree(BASE_PATH, sandbox_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns('venv', '.git', '__pycache__', 'patch_backups', 'patch_sandbox'))

        target_file = os.path.join(sandbox_dir, file_path)

        if not os.path.exists(target_file):
            return {"status": "error", "error": f"Archivo no encontrado en sandbox: {file_path}"}

        # Aplicar patch en el entorno aislado
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        # 🚀 Levantar servidor en puerto alternativo (8010)
        # Usamos python -m uvicorn para máxima compatibilidad en Windows
        env = os.environ.copy()
        # Aseguramos que el PYTHONPATH incluya el sandbox_dir para los imports de src
        env["PYTHONPATH"] = sandbox_dir
        
        proc = subprocess.Popen(
            ["python", "-m", "uvicorn", "src.server:app", "--host", "127.0.0.1", "--port", "8010"],
            cwd=sandbox_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Esperar a que el servidor intente levantar
        time.sleep(5)

        # 🧪 Ejecutar batería de tests técnicos
        base_url = "http://127.0.0.1:8010"
        tests = run_tests(base_url)
        
        # 🧪 Ejecutar validación semántica
        semantic = run_semantic_tests(base_url)

        # 📊 Calcular Score de Confianza
        confidence = compute_confidence_score(tests, semantic)

        # Determinar éxito global
        all_passed = all(t.get("success") for t in tests) and all(t.get("success") for t in semantic)

        result = {
            "status": "ok" if all_passed else "failed",
            "message": "Validación completa finalizada." if all_passed else "La validación falló (técnica o semántica).",
            "tests": tests,
            "semantic": semantic,
            "confidence": confidence,
            "sandbox_path": sandbox_dir
        }

        # 💾 Persistir log de run para análisis de patrones
        _persist_run_log(file_path, result)

        return result

    except Exception as e:
        logger.error(f"❌ Error en sandbox runner: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        # 🧹 Limpieza: matar proceso
        if proc:
            try:
                # Intentamos leer un poco del stderr si falló
                if not proc.poll():
                    proc.terminate()
                    proc.wait(timeout=2)
            except:
                proc.kill()
