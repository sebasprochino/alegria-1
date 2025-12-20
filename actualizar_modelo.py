import os
from pathlib import Path

def upgrade_model():
    print("🚀 Actualizando núcleo a modelo: gemini-2.5-flash-preview-09-2025...")
    
    dev_path = Path("backend/src/services/developer.py")
    
    if not dev_path.exists():
        print(f"❌ No encuentro el archivo en: {dev_path}")
        return

    # Leer el código actual
    with open(dev_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Reemplazo directo sin preguntar
    new_content = content.replace("gemini-1.5-pro", "gemini-2.5-flash-preview-09-2025")
    
    # Guardar cambios
    with open(dev_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ Developer actualizado.")
    print("---------------------------------------------")
    print("1. Cierra la ventana negra del servidor (anima_guardian).")
    print("2. Vuelve a ejecutar: .\\backend\\venv\\Scripts\\python.exe anima_guardian.py")
    print("3. Prueba de nuevo: despertar_nexus.py")

if __name__ == "__main__":
    upgrade_model()