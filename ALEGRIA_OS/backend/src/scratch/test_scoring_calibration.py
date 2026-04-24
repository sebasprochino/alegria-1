
import sys
import os

# Añadir el path para importar el runner
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from services.sandbox_runner import compute_confidence_score, classify_score

def run_calibration_test():
    print("CALIBRACION DE SCORING - CASOS DE PRUEBA\n")

    # Caso 1: Patch correcto
    # 3 tests técnicos OK, 3 tests semánticos OK
    c1_tests = [{"test": "T1", "success": True}, {"test": "T2", "success": True}, {"test": "T3", "success": True}]
    c1_sem = [{"test": "S1", "success": True}, {"test": "S2", "success": True}, {"test": "S3", "success": True}]
    res1 = compute_confidence_score(c1_tests, c1_sem)
    print(f"Caso 1 (Correcto): Score={res1['score']} | Level={res1['level']} | Signals={res1['signals']}")

    # Caso 2: Patch con error menor
    # 2 tests técnicos OK, 1 FAIL. Semántica OK.
    c2_tests = [{"test": "T1", "success": True}, {"test": "T2", "success": True}, {"test": "T3", "success": False}]
    c2_sem = [{"test": "S1", "success": True}, {"test": "S2", "success": True}, {"test": "S3", "success": True}]
    res2 = compute_confidence_score(c2_tests, c2_sem)
    print(f"Caso 2 (Error Menor): Score={res2['score']} | Level={res2['level']} | Signals={res2['signals']}")

    # Caso 3: Patch rompe endpoint
    # 3 tests técnicos FAIL. Semántica FAIL.
    c3_tests = [{"test": "T1", "success": False}, {"test": "T2", "success": False}, {"test": "T3", "success": False}]
    c3_sem = [{"test": "S1", "success": False}]
    res3 = compute_confidence_score(c3_tests, c3_sem)
    print(f"Caso 3 (Rompe Endpoint): Score={res3['score']} | Level={res3['level']} | Signals={res3['signals']}")

    # Caso 4: Patch rompe semántica
    # Tests técnicos OK. 1 Semantic FAIL.
    c4_tests = [{"test": "T1", "success": True}, {"test": "T2", "success": True}, {"test": "T3", "success": True}]
    c4_sem = [{"test": "S1", "success": False}]
    res4 = compute_confidence_score(c4_tests, c4_sem)
    print(f"Caso 4 (Rompe Semántica): Score={res4['score']} | Level={res4['level']} | Signals={res4['signals']}")

    # Caso 5: Patch vacío / inútil
    # Cobertura baja, semántica FAIL.
    c5_tests = [{"test": "T1", "success": False}]
    c5_sem = [{"test": "S1", "success": False}]
    res5 = compute_confidence_score(c5_tests, c5_sem)
    print(f"Caso 5 (Vacío/Inútil): Score={res5['score']} | Level={res5['level']} | Signals={res5['signals']}")

if __name__ == "__main__":
    run_calibration_test()
