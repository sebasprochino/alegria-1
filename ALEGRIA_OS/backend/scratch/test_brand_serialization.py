
import sys
import os
import json

# Agregar el path del backend para importar los módulos
sys.path.append(os.path.join(os.getcwd(), "backend"))

from src.services.brand_service import service as brand_service

def test_serialization():
    print("Testing BrandService.get_all() serialization...")
    try:
        data = brand_service.get_all()
        print("Data loaded successfully.")
        
        # Intentar serializar como lo haría FastAPI
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        print("Serialization successful.")
        # print(json_str[:500])
    except Exception as e:
        print(f"Serialization FAILED: {e}")

if __name__ == "__main__":
    test_serialization()
