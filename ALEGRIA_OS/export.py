import os
import zipfile
import datetime

source_dir = "."
desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
timestamp = datetime.datetime.now().strftime("%Y%md_%H%M")
zip_filename = os.path.join(desktop_dir, f"ALEGRIA_OS_Export_{timestamp}.zip")

# Carpetas/archivos a ignorar enCUALQUIER nivel
EXCLUDES = {
    "node_modules", 
    "venv", 
    "env",
    "__pycache__", 
    ".git", 
    "dist", 
    "build", 
    "temp",
    ".next",
    ".vscode",
    ".idea"
}
EXCLUDE_EXTS = {".zip", ".log", ".pyc"}

# El SDK root a veces está duplicado, vamos a filtrarlo si encontramos el root
ROOT_SDK = "alegria_sdk"

print("==========================================")
print(" Empezando empaquetado seguro de ALEGRIA OS...")
print("==========================================")

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(source_dir):
        # Filtrar directorios in situ
        dirs[:] = [d for d in dirs if d not in EXCLUDES]
        
        # Filtrar duplicate root SDK
        if root == "." and ROOT_SDK in dirs:
            dirs.remove(ROOT_SDK)

        for file in files:
            if any(file.endswith(ext) for ext in EXCLUDE_EXTS):
                continue
                
            abs_path = os.path.join(root, file)
            # Evitar empaquetar archivos dentro del temp/Desktop por las dudas
            rel_path = os.path.relpath(abs_path, source_dir)
            zipf.write(abs_path, arcname=rel_path)

print("\n✅ ¡Exportación Exitosa!")
print(f"📦 Archivo guardado comprimido y sin basura en tu Escritorio: \n{zip_filename}")
print("==========================================")
