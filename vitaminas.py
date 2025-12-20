import subprocess
import sys
import os

def inyectar_vitaminas():
    print("💊 INYECTANDO DEPENDENCIAS FALTANTES...")
    
    # 1. Detectar pip del entorno virtual
    if os.name == 'nt':
        pip_cmd = "backend\\venv\\Scripts\\pip.exe"
        prisma_cmd = "backend\\venv\\Scripts\\prisma.exe"
    else:
        pip_cmd = "backend/venv/bin/pip"
        prisma_cmd = "backend/venv/bin/prisma"

    # 2. Instalar Librerías de los Agentes
    libs = [
        "duckduckgo-search",  # Para Radar
        "google-genai",       # Para Anima (Modelo nuevo)
        "prisma"              # Para Nexus
    ]
    
    print(f"⬇️  Instalando: {', '.join(libs)}...")
    try:
        subprocess.run([pip_cmd, "install"] + libs, check=True)
        print("✅ Librerías instaladas.")
    except Exception as e:
        print(f"❌ Error instalando libs: {e}")

    # 3. Regenerar Cliente Prisma (Para Nexus)
    print("🔄 Regenerando memoria (Prisma Client)...")
    try:
        subprocess.run([prisma_cmd, "generate", "--schema=backend/prisma/schema.prisma"], check=True)
        subprocess.run([prisma_cmd, "db", "push", "--schema=backend/prisma/schema.prisma"], check=False)
        print("✅ Memoria Nexus sincronizada.")
    except Exception as e:
        print(f"⚠️ Advertencia Prisma: {e}")

    print("\n✨ SISTEMA CURADO ✨")
    print("---------------------------------------")
    print("1. Cierra la ventana negra del servidor (anima_guardian).")
    print("2. Vuelve a ejecutar: .\\backend\\venv\\Scripts\\python.exe anima_guardian.py")
    print("3. Recarga la página web (F5).")
    print("---------------------------------------")

if __name__ == "__main__":
    inyectar_vitaminas()