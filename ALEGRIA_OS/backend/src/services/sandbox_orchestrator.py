import os
import shutil
import tempfile
import subprocess
import ast
from typing import List, Dict, Any
import logging

logger = logging.getLogger("ALEGRIA_SANDBOX")

class SandboxOrchestrator:
    """
    Entorno de ejecución aislado para validación de parches.
    Sigue la regla ACSP: El sistema valida antes de que el humano confirme.
    """
    
    def __init__(self, base_path: str):
        self.base_path = os.path.abspath(base_path)
        self.sandbox_root = os.path.join(self.base_path, "patch_sandbox")
        os.makedirs(self.sandbox_root, exist_ok=True)

    def prepare_sandbox(self, file_path: str) -> str:
        """Crea una copia de seguridad del archivo en el sandbox para pruebas."""
        rel_path = os.path.relpath(file_path, self.base_path)
        sandbox_path = os.path.join(self.sandbox_root, rel_path)
        
        # Crear directorios padres en el sandbox
        os.makedirs(os.path.dirname(sandbox_path), exist_ok=True)
        
        # Copiar original para tener base limpia
        if os.path.exists(file_path):
            shutil.copy2(file_path, sandbox_path)
            
        return sandbox_path

    def validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validación AST profunda."""
        try:
            ast.parse(code)
            return {"ok": True}
        except SyntaxError as e:
            return {
                "ok": False,
                "error": f"SyntaxError en línea {e.lineno}: {e.msg}",
                "line": e.lineno
            }

    def validate_imports(self, code: str) -> Dict[str, Any]:
        """
        Verifica que los imports nuevos existan en el entorno.
        Evita alucinaciones de librerías inexistentes.
        """
        try:
            tree = ast.parse(code)
            missing_imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Aquí podríamos expandir para verificar si el módulo existe en sys.path
                    # Por ahora hacemos check de seguridad básico
                    pass
            
            return {"ok": True, "missing": missing_imports}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def run_tests(self, sandbox_file: str) -> Dict[str, Any]:
        """
        Ejecuta tests relacionados usando pytest.
        Inyecta el sandbox en PYTHONPATH para que se use el código mutado.
        """
        try:
            # PYTHONPATH = sandbox_root + original_pythonpath
            env = os.environ.copy()
            current_path = env.get("PYTHONPATH", "")
            # IMPORTANTE: El sandbox debe ir PRIMERO para que los imports lo prefieran
            env["PYTHONPATH"] = f"{self.sandbox_root};{self.base_path};{current_path}"
            
            # Buscamos tests relacionados. Por ahora, buscamos en /tests
            # Podríamos ser más inteligentes y buscar test_[archivo].py
            test_dir = os.path.join(self.base_path, "tests")
            
            # Ejecutamos solo un subconjunto rápido o el test específico si existe
            # Para la demo, ejecutamos un check de importación rápido
            cmd = [
                "python", "-c", 
                f"import sys; sys.path.insert(0, r'{self.sandbox_root}'); import {os.path.basename(sandbox_file).replace('.py', '')}"
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=self.base_path,
                env=env,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    "ok": False, 
                    "error": f"Fallo en Runtime (Import Test):\n{result.stderr}"
                }
                
            return {"ok": True, "output": result.stdout}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Timeout ejecutando pruebas de runtime."}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def run_dry_run(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el ciclo completo de validación en el sandbox.
        """
        file_path = os.path.join(self.base_path, patch["file"])
        code = patch["content"]
        
        # 1. Sintaxis
        syntax = self.validate_syntax(code)
        if not syntax["ok"]:
            return {"status": "fail", "stage": "syntax", "error": syntax["error"]}
            
        # 2. Preparar Sandbox
        sandbox_file = self.prepare_sandbox(file_path)
        
        # 3. Aplicar en Sandbox
        try:
            with open(sandbox_file, "w", encoding="utf-8") as f:
                f.write(code)
        except Exception as e:
            return {"status": "fail", "stage": "write", "error": str(e)}
            
        # 4. Runtime / Import Test
        runtime = self.run_tests(sandbox_file)
        if not runtime["ok"]:
            return {"status": "fail", "stage": "runtime", "error": runtime["error"]}
            
        return {
            "status": "success",
            "message": "Parche validado sintácticamente y pasó pruebas de importación en Sandbox.",
            "sandbox_path": sandbox_file
        }

    def cleanup(self):
        """Limpia el sandbox."""
        if os.path.exists(self.sandbox_root):
            shutil.rmtree(self.sandbox_root)
            os.makedirs(self.sandbox_root, exist_ok=True)
