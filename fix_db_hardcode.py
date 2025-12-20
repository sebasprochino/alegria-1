import os
import subprocess
from pathlib import Path

# ==========================================
# SCHEMA CON RUTA FIJA (SIN VARIABLES DE ENTORNO)
# ==========================================
# Fíjate en la línea 'url': Ya no dice env(), dice file:./dev.db
PRISMA_SCHEMA_HARDCODED = """generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = "file:./dev.db"
}

model Project {
  id        String   @id @default(cuid())
  name      String
  brandKit  String
  createdAt DateTime @default(now())
  agents    Agent[]
  history   History[]
}

model Agent {
  id        String @id @default(cuid())
  projectId String
  role      String
  project   Project @relation(fields: [projectId], references: [id])
}

model History {
  id        String @id @default(cuid())
  projectId String
  type      String
  details   String
  createdAt DateTime @default(now())
  project   Project @relation(fields: [projectId], references: [id])
}

model CodingError {
  id         String   @id @default(cuid())
  moduleName String
  badCode    String
  errorMsg   String
  timestamp  DateTime @default(now())
}
"""

def forzar_db():
    print("🔨 FORZANDO CONFIGURACIÓN DE BASE DE DATOS (HARDCODE)...")
    
    # 1. Ubicar carpeta
    base_path = Path.cwd()
    prisma_dir = base_path / "backend" / "prisma"
    prisma_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Escribir Schema con ruta FIJA
    schema_path = prisma_dir / "schema.prisma"
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write(PRISMA_SCHEMA_HARDCODED)
    print("✅ Schema reescrito con ruta directa (file:./dev.db).")

    # 3. Detectar comando Prisma
    if os.name == 'nt':
        prisma_cmd = str(base_path / "backend/venv/Scripts/prisma")
    else:
        prisma_cmd = str(base_path / "backend/venv/bin/prisma")

    # 4. Ejecutar Comandos (Ahora no fallarán por falta de variables)
    print("⚡ Generando Cliente (Sin buscar variables)...")
    try:
        subprocess.run([prisma_cmd, "generate", "--schema", str(schema_path)], check=True)
        print("✅ Cliente generado.")
    except Exception as e:
        print(f"❌ Error Generate: {e}")
        return

    print("💾 Creando Tablas (DB Push)...")
    try:
        subprocess.run([prisma_cmd, "db", "push", "--schema", str(schema_path)], check=True)
        print("✅ Base de datos creada exitosamente.")
    except Exception as e:
        print(f"❌ Error DB Push: {e}")
        return

    print("\n✨ PROBLEMA RESUELTO ✨")
    print("---------------------------------------")
    print("El sistema ya tiene memoria.")
    print("Ejecuta: .\\backend\\venv\\Scripts\\python.exe iniciar_alegria.py")

if __name__ == "__main__":
    forzar_db()