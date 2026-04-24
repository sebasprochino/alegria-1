
import sys
import os
import time

# Añadir el path para importar el runner
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from services.sandbox_runner import run_sandbox

def test_real_scenarios():
    file_to_patch = "backend/src/routes/motion.py"
    
    with open(file_to_patch, "r", encoding="utf-8") as f:
        original_content = f.read()

    print("--- CASO 1: PATCH CORRECTO ---")
    # Añadimos un comentario
    correct_content = original_content + "\n# Comentario de prueba correcto\n"
    res1 = run_sandbox(file_to_patch, correct_content)
    print(f"Status: {res1['status']}")
    if 'error' in res1: print(f"Error: {res1['error']}")
    print(f"Confidence: {res1.get('confidence')}")
    print(f"Signals: {res1.get('confidence', {}).get('signals')}")
    
    print("\n--- CASO 2: ERROR MENOR (Syntax Error) ---")
    # Error de sintaxis: falta un paréntesis
    error_content = original_content.replace("router = APIRouter()", "router = APIRouter(")
    res2 = run_sandbox(file_to_patch, error_content)
    print(f"Status: {res2['status']}")
    print(f"Confidence: {res2.get('confidence')}")
    
    print("\n--- CASO 3: ROMPE ENDPOINT (Runtime Error) ---")
    # Rompe el import o la lógica de una ruta
    broken_content = original_content.replace("from src.services.motion_service import motion_service", "motion_service = None")
    res3 = run_sandbox(file_to_patch, broken_content)
    print(f"Status: {res3['status']}")
    print(f"Confidence: {res3.get('confidence')}")

if __name__ == "__main__":
    test_real_scenarios()
