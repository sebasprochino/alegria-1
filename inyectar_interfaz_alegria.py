import os
import shutil

BASE_PATH = r"G:\ALEGRIA_OS\ALEGRIA_OS"
ORIGEN = os.path.join(BASE_PATH, "src", "AlegrIAAnimaV4.tsx")
DESTINO_DIR = os.path.join(BASE_PATH, "frontend", "src", "anima")
DESTINO = os.path.join(DESTINO_DIR, "AnimaUI.jsx")

print("🌱 Iniciando inyección de Anima UI...")

if not os.path.exists(ORIGEN):
    print("❌ No se encontró AlegrIAAnimaV4.tsx en src/")
    exit(1)

os.makedirs(DESTINO_DIR, exist_ok=True)

if os.path.exists(DESTINO):
    print("⚠️ AnimaUI.jsx ya existe. No se sobrescribe.")
else:
    shutil.copy2(ORIGEN, DESTINO)
    print("✅ AnimaUI.jsx inyectado en frontend/src/anima/")

print("🧠 Anima sigue intacta en su origen.")
print("🌿 Inyección completada con dignidad.")
