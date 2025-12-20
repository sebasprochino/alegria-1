import os
import subprocess
from pathlib import Path

# ==========================================
# SCHEMA (EL PLANO)
# ==========================================
PRISMA_SCHEMA = """generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
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

def cirugia_final():
    print("🚑 INICIANDO TRANSFUSIÓN DE BASE DE DATOS...")
    
    # 1. Rutas Absolutas (Para no perdernos)
    base_path = Path.cwd()
    prisma_dir = base_path / "backend" / "prisma"
    prisma_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Asegurar el Schema
    schema_path = prisma_dir / "schema.prisma"
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write(PRISMA_SCHEMA)
    print("✅ Plano (Schema) asegurado.")

    # 3. Detectar comando Prisma
    if os.name == 'nt':
        prisma_cmd = str(base_path / "backend/venv/Scripts/prisma")
    else:
        prisma_cmd = str(base_path / "backend/venv/bin/prisma")

    # 4. PREPARAR EL ENTORNO (LA SOLUCIÓN AL ERROR)
    # Aquí creamos un entorno virtual temporal que SÍ tiene la variable
    # Usamos ruta absoluta para la DB para evitar errores de "dónde estoy"
    db_file_path = prisma_dir / "dev.db"
    # Convertimos a formato URI de archivo (file:C:/ruta/dev.db)
    # En Windows, las barras invertidas pueden dar problemas en URIs, usamos forward slash
    db_url = f"file:{db_file_path.as_posix()}"
    
    env_vars = os.environ.copy()
    env_vars["DATABASE_URL"] = db_url
    
    print(f"💉 Inyectando URL de DB: {db_url}")

    # 5. Generar Cliente
    print("⚡ Generando Cliente...")
    try:
        subprocess.run(
            [prisma_cmd, "generate", "--schema", str(schema_path)], 
            check=True,
            env=env_vars # <--- AQUÍ ESTÁ LA MAGIA
        )
    except Exception as e:
        print(f"❌ Error Generate: {e}")
        return

    # 6. DB Push (Crear tablas)
    print("💾 Creando Tablas (DB Push)...")
    try:
        subprocess.run(
            [prisma_cmd, "db", "push", "--schema", str(schema_path)], 
            check=True,
            env=env_vars # <--- AQUÍ TAMBIÉN
        )
        print("✅ Base de datos creada exitosamente.")
    except Exception as e:
        print(f"❌ Error DB Push: {e}")
        return
        
    # 7. Guardar esta config en el .env para el futuro
    env_file = base_path / "backend" / ".env"
    # Leemos contenido actual
    content = ""
    if env_file.exists():
        with open(env_file, "r") as f: content = f.read()
    
    # Si no tiene la URL correcta, la agregamos/reemplazamos
    if "DATABASE_URL" not in content:
        with open(env_file, "a") as f:
            f.write(f'\nDATABASE_URL="{db_url}"')
        print("📝 Archivo .env actualizado con la ruta absoluta.")

    print("\n✨ PACIENTE ESTABILIZADO ✨")
    print("---------------------------------------")
    print("Ya puedes ejecutar: .\\backend\\venv\\Scripts\\python.exe iniciar_alegria.py")

if __name__ == "__main__":
    cirugia_final()