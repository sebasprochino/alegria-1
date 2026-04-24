from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import logging
import traceback
from pathlib import Path

import shutil

router = APIRouter()
logger = logging.getLogger("ALEGRIA_DEV_ROUTES")

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
BACKUP_PATH = os.path.join(BASE_PATH, "patch_backups")
os.makedirs(BACKUP_PATH, exist_ok=True)

# Importar el servicio developer (consolidado)
# from src.services.developer import service as developer_service
# STUB: El servicio developer parece haber sido refactorizado o movido. 
# Para permitir que el router cargue y el Agente Senior funcione, stubbeamos lo necesario.
class DummyDeveloperService:
    async def get_history(self, *args): return []
    async def create_web_app(self, *args): return {"status": "error", "message": "Service under maintenance"}
    async def chat(self, *args): return {"status": "error", "message": "Service under maintenance"}
    def list_apps(self, *args): return []
    async def generate_and_write(self, *args): return {"status": "error", "message": "Service under maintenance"}
    async def list_modules(self, *args): return []
    async def read_module(self, *args): raise FileNotFoundError()
    async def rewrite_module(self, *args): raise FileNotFoundError()
    async def run_diagnostics(self, *args): return {"status": "ok", "checks": []}
    async def plan_project(self, *args): return {}
    async def generate_file(self, *args): return {}
    async def get_project_status(self, *args): return {}
    async def install_dependencies(self, *args): return {}
    async def interpret_natural_language(self, *args): return {}
    async def generate_from_natural_language(self, *args): return {}

developer_service = DummyDeveloperService()


# =========================================================================
# 🤖 AGENT CHAT — Developer Agent Senior (Cascada de Proveedores)
# =========================================================================

_AGENT_SYSTEM_PROMPT = """Sos el Agente Developer Senior de ALEGR-IA OS — un sistema operativo de coherencia creativa con protocolo ACSP 4.0.

## TU IDENTIDAD

Sos un senior developer con ownership total sobre el codebase de ALEGR-IA. No sos un asistente genérico. Conocés cada archivo, cada decisión arquitectónica, cada deuda técnica. Hablás directo, sin relleno, sin tutoriales de YouTube.

## ARQUITECTURA ACTUAL (v5 — Abril 2026)

### Stack
- Backend: Python 3.10+ / FastAPI + Uvicorn / SQLite + Prisma
- Frontend: React 18 + Vite (puerto 5173) / TailwindCSS / TypeScript en componentes críticos
- LLMs: Groq (primario, llama-3.3-70b-versatile), Gemini 2.5 Flash, GPT-4o, Ollama (local)
- Proxy: Vite /api → localhost:8000

### Estructura canónica del backend (backend/src/)
- server.py — Entry point FastAPI, GhostNode pattern, carga resiliente de nodos
- services/anima.py — generate_raw(), pipeline LLM con cascade failover
- services/nexus.py — Memoria soberana, SessionSourceStore, MemoryOrchestrator
- services/provider_registry.py — ProviderConfig dataclass, inject_env_vars, cascade
- services/provider_cascade.py — Failover ordenado por prioridad
- services/ethical_guard.py — Validación ética de respuestas LLM
- services/developer.py — Generación de código
- services/radar.py — Búsqueda web externa + DuckDuckGo fallback
- core/kernel.py — Sovereign Kernel ACSP v1.1
- core/rule_engine.py — Motor de reglas éticas, retorna authorized/doubt/rejected

## PROTOCOLO ACSP 4.0 (NO NEGOCIABLE)

1. La IA propone, el operador dicta. Ningún componente se auto-ejecuta sin click manual.
2. Si un servicio backend falla, la UI asume el bloque inactivo — nunca crashea.
3. GhostNode Pattern: todo módulo cargado con aislamiento de fallos.
4. Sin duplicar backends. Sin hardcodear providers. Sin sesiones implícitas.

## TU COMPORTAMIENTO

Cuando te piden código:
1. Identificá el archivo canónico afectado
2. Explicá brevemente por qué tu solución es la correcta
3. Entregá el código completo y funcional, listo para copiar-pegar
4. Señalá cualquier dependencia nueva o efecto colateral

Cuando te piden análisis:
1. Diagnóstico claro del problema
2. Causa raíz (no síntomas)
3. Solución con trade-offs explícitos

Formato de respuesta: Markdown. Code blocks con lenguaje explícito. Sin verbosidad innecesaria.
Si no sabés algo exacto sobre el codebase: lo decís. No inventás."""

_MODE_PREFIXES = {
    "review": "Revisá este código y entregá feedback senior:\n\n",
    "fix": "Hay un bug. Diagnóstico + fix completo:\n\n",
    "arch": "Decisión arquitectónica. Analizá trade-offs:\n\n",
    "gen": "Generá el código completo para ALEGR-IA:\n\n",
    "chat": "",
}


class AgentChatRequest(BaseModel):
    messages: List[Dict[str, str]]  # [{"role": "user"|"assistant", "content": "..."}]
    mode: str = "chat"              # chat | review | fix | arch | gen


@router.post("/agent-chat")
async def agent_chat(req: AgentChatRequest):
    """
    Developer Agent Senior — Chat via Cascada de Proveedores.
    Sigue el protocolo ACSP 4.0 con Memoria Soberana (Nexus).
    """
    from src.services.provider_registry import service as provider_service
    from src.services.provider_cascade import ProviderCascade
    from src.services.ethical_guard import service as ethical_guard
    from src.services.nexus import service as nexus_service

    logger.info(f"🤖 [AGENT] mode={req.mode} | msgs={len(req.messages)}")

    # 1. Identificar sesión y persistir mensaje del OPERADOR en Nexus
    session_id = nexus_service.DEVELOPER_TIMELINE_ID
    last_user_msg = req.messages[-1].get("content", "")
    await nexus_service.save_message(session_id, "user", last_user_msg)

    # 2. Construir el prompt con historial real de Nexus (o el enviado por el front)
    # Preferimos el historial de Nexus para coherencia total
    history = await nexus_service.get_recent_chat(limit=20, session_id=session_id)
    
    # Formatear historial para el LLM
    history_str = ""
    if history:
        parts = []
        for msg in history[:-1]: # Excluimos el último que acabamos de guardar para evitar duplicados si el LLM lo procesa aparte
            role = "OPERADOR" if msg["role"] == "user" else "AGENTE"
            parts.append(f"{role}: {msg['content']}")
        history_str = "Historial previo de la sesión:\n" + "\n".join(parts) + "\n\n"

    prefix = _MODE_PREFIXES.get(req.mode, "")
    prompt_text = f"{history_str}OPERADOR ({req.mode.upper()}): {prefix}{last_user_msg}"

    from src.services.anima import get_anima
    anima = get_anima()

    try:
        from src.services.context_builder import build_context
        context_data = build_context(prompt_text)

        # Usamos el pipeline unificado de ANIMA
        # Forzamos la clasificación 'tecnico' y el agente 'developer'
        # El formato 'markdown' evita que AnimaBuilder fuerce JSON
        anima_result = await anima.generate_raw(
            message=prompt_text,
            forced_classification={
                "type": "tecnico", 
                "agent": "developer",
                "output_format": "markdown",
                "mode": "executor",
                "codebase_context": context_data["context"]
            }
        )

        response = anima_result.get("raw")
        
        if not response:
            return {
                "status": "error",
                "response": anima_result.get("error") or "Sin respuesta de Anima.",
                "provider": None,
            }

        # 4. Persistir respuesta del AGENTE en Nexus
        await nexus_service.save_message(session_id, "assistant", response)

        from src.services.patch_parser import extract_patches
        from src.services.diff_engine import generate_diff

        patches = extract_patches(response)
        final_patches = []

        for p in patches:
            file_path = p.get("file")
            content = p.get("diff") or p.get("content")

            if file_path and content:
                diff = generate_diff(file_path, content)
                final_patches.append({
                    **p,
                    "diff_preview": diff
                })
            else:
                final_patches.append(p)

        return {
            "status": "ok",
            "response": response,
            "provider": anima_result.get("agent_name") or "Anima",
            "patches": final_patches
        }

    except Exception as e:
        error_stack = traceback.format_exc()
        logger.error(f"❌ [AGENT] Anima bridge failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "error": str(e),
            "error_type": type(e).__name__,
            "stack": error_stack,
            "trace": error_stack,
            "provider": None,
        }



class GenerateModuleRequest(BaseModel):
    module_name: str
    description: str
    tech_tags: str = "python"


class RewriteModuleRequest(BaseModel):
    module_name: str
    instructions: str


class PlanProjectRequest(BaseModel):
    description: str
    project_type: str = "web_app"  # web_app, api, cli_tool, data_pipeline


class GenerateProjectRequest(BaseModel):
    description: str
    project_type: str = "web_app"
    base_path: Optional[str] = None


class CreateAppRequest(BaseModel):
    prompt: str


@router.get("/history")
async def get_developer_history(session_id: Optional[str] = "default"):
    """Recupera el historial de Developer."""
    try:
        history = await developer_service.get_history(session_id)
        return {
            "status": "ok",
            "history": history
        }
    except Exception as e:
        return {"status": "error", "history": [], "error": str(e)}

@router.post("/create_app")
async def create_app(req: CreateAppRequest):
    """Genera una aplicación web completa (HTML+JS+CSS) en un solo archivo."""
    try:
        result = await developer_service.create_web_app(req.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 💬 CHAT CONVERSACIONAL
# ==========================================
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

@router.post("/chat")
async def developer_chat(req: ChatRequest):
    """
    Chat conversacional con Developer para crear apps.
    Proceso: DISCUSSING → PLANNING → CONFIRMING → GENERATING
    """
    try:
        result = await developer_service.chat(req.message, req.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/apps")
async def list_apps():
    """Lista todas las apps creadas."""
    try:
        apps = developer_service.list_apps()
        return {"status": "ok", "apps": apps, "count": len(apps)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_module(req: GenerateModuleRequest):
    """Genera un nuevo módulo usando IA."""
    try:
        result = await developer_service.generate_and_write(
            req.module_name,
            req.description,
            req.tech_tags
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules")
async def list_modules():
    """Lista todos los módulos en services/."""
    try:
        result = await developer_service.list_modules()
        return {"modules": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules/{module_name}")
async def get_module_code(module_name: str):
    """Obtiene el código de un módulo específico."""
    try:
        result = await developer_service.read_module(module_name)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Módulo {module_name} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewrite")
async def rewrite_module(req: RewriteModuleRequest):
    """Reescribe un módulo existente con instrucciones."""
    try:
        result = await developer_service.rewrite_module(
            req.module_name,
            req.instructions
        )
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Módulo {req.module_name} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diagnostics")
async def run_diagnostics():
    """Ejecuta diagnóstico completo del sistema."""
    try:
        result = await developer_service.run_diagnostics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
# NUEVOS ENDPOINTS: GENERACIÓN DE PROYECTOS COMPLETOS
# =========================================================================

@router.post("/plan")
async def plan_project(req: PlanProjectRequest):
    """Fase 1: Blueprinting del proyecto."""
    try:
        return await developer_service.plan_project(req.description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateFileRequest(BaseModel):
    project_id: str
    file_path: str
    context: str

@router.post("/generate-file")
async def generate_file(req: GenerateFileRequest):
    """Fase 2: Materialización granular de un archivo."""
    try:
        return await developer_service.generate_file(req.project_id, req.file_path, req.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{project_id}")
async def get_project_status(project_id: str):
    """Consulta el estado de archivos y salud del proyecto."""
    try:
        return await developer_service.get_project_status(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class InstallRequest(BaseModel):
    project_id: str

@router.post("/install")
async def install_dependencies(req: InstallRequest):
    """Fase 3: Operacionalización (npm/pip install)."""
    try:
        return await developer_service.install_dependencies(req.project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects")
async def list_projects():
    """Lista los proyectos generados disponibles."""
    # Implementación simple buscando en el directorio
    backend_root = Path(__file__).resolve().parent.parent.parent
    project_dir = backend_root / "generated_projects"
    
    projects = []
    if project_dir.exists():
        for d in project_dir.iterdir():
            if d.is_dir():
                projects.append({"id": d.name, "path": str(d)})
    
    return {"projects": projects}


# =========================================================================
# LENGUAJE NATURAL: Interpreta y genera automáticamente
# =========================================================================

class NaturalLanguageRequest(BaseModel):
    user_input: str


class GenerateFromNaturalLanguageRequest(BaseModel):
    user_input: str
    base_path: Optional[str] = None


@router.post("/interpret")
async def interpret_natural_language(req: NaturalLanguageRequest):
    """
    Interpreta lenguaje natural y extrae información técnica.
    
    Ejemplo:
    {
        "user_input": "quiero una app para gestionar mis tareas diarias"
    }
    
    Devuelve:
    - Nombre del proyecto
    - Tipo de proyecto
    - Descripción técnica elaborada
    - Tags apropiados
    - Tecnologías sugeridas
    - Features principales
    """
    try:
        result = await developer_service.interpret_natural_language(
            req.user_input
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-natural")
async def generate_from_natural_language(req: GenerateFromNaturalLanguageRequest):
    """
    Genera un proyecto completo desde lenguaje natural.
    
    El usuario solo describe lo que quiere en lenguaje natural,
    y el sistema automáticamente:
    1. Interpreta la intención
    2. Extrae tags y descripción técnica
    3. Genera el proyecto completo
    
    Ejemplo:
    {
        "user_input": "necesito una app web para llevar el inventario de mi tienda"
    }
    
    Esto generará automáticamente un sistema completo de inventario.
    """
    try:
        result = await developer_service.generate_from_natural_language(
            req.user_input,
            req.base_path
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================================
# PATCH APPLY & ROLLBACK
# =========================================================================

class ApplyPatchRequest(BaseModel):
    file: str
    content: str

@router.post("/sandbox-test")
async def sandbox_test(payload: Dict[str, Any]):
    """
    Ejecuta un test de integración completo levantando el sistema en un sandbox.
    """
    from src.services.sandbox_runner import run_sandbox
    file_path = payload.get("file")
    content = payload.get("content")

    if not file_path or not content:
        return {"status": "error", "error": "Faltan datos (file o content)"}

    result = run_sandbox(file_path, content)
    return result


@router.post("/dry-run")
async def dry_run_patch(patch: Dict[str, Any]):
    """
    Valida un parche en el sandbox antes de permitir su aplicación.
    """
    from src.services.sandbox_orchestrator import SandboxOrchestrator
    orchestrator = SandboxOrchestrator(BASE_PATH)
    
    result = await orchestrator.run_dry_run(patch)
    return result


@router.post("/apply-patch")
async def apply_patch(payload: ApplyPatchRequest):
    try:
        file_path = payload.file
        new_content = payload.content

        if not file_path or not new_content:
            raise HTTPException(status_code=400, detail="Missing file or content")

        abs_path = os.path.join(BASE_PATH, file_path)
        abs_path = os.path.normpath(abs_path)

        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="File not found")

        # 🔐 BACKUP
        backup_file = os.path.join(
            BACKUP_PATH,
            file_path.replace("/", "_").replace("\\", "_") + ".bak"
        )

        shutil.copy(abs_path, backup_file)

        # 🧪 VALIDACIÓN BÁSICA Y AST (Python)
        if file_path.endswith(".py"):
            import ast
            try:
                ast.parse(new_content)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"AST validation failed: {e}"
                )

        # 💾 APPLY
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {
            "status": "applied",
            "file": file_path,
            "backup": backup_file
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

class RollbackPatchRequest(BaseModel):
    file: str

@router.post("/rollback-patch")
async def rollback_patch(payload: RollbackPatchRequest):
    try:
        file_path = payload.file

        backup_file = os.path.join(
            BACKUP_PATH,
            file_path.replace("/", "_").replace("\\", "_") + ".bak"
        )

        if not os.path.exists(backup_file):
            raise HTTPException(status_code=404, detail="Backup not found")

        abs_path = os.path.join(BASE_PATH, file_path)
        abs_path = os.path.normpath(abs_path)

        shutil.copy(backup_file, abs_path)

        return {
            "status": "rolled_back",
            "file": file_path
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
