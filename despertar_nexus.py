import requests
import json

# URL del servidor vivo
url = "http://127.0.0.1:8000/developer/create"

# La orden para Anima Developer
payload = {
    "module_name": "nexus",
    "description": """
    Módulo central de memoria y contexto para ALEGRIA OS.
    Responsabilidades:
    1. Gestionar el estado global del sistema (Health, Active Project).
    2. Leer y escribir en la base de datos (Prisma) para guardar proyectos y preferencias.
    3. Mantener el 'BrandKit' del usuario activo.
    4. Debe tener métodos: get_context(project_id), save_memory(data), load_memory().
    Reglas: Usar Singleton pattern.
    """,
    "tech_tags": "python, prisma, singleton"
}

print(f"🧠 Enviando orden telepática a Anima Developer...")

try:
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("\n✅ ¡ÉXITO! El Developer respondió:")
        print(json.dumps(response.json(), indent=2))
        print("\n✨ Nexus ha sido creado. El servidor se recargará automáticamente en unos segundos.")
    else:
        print(f"\n❌ Error {response.status_code}: {response.text}")

except Exception as e:
    print(f"\n❌ Error de conexión: {e}")
    print("Asegúrate de que la ventana del servidor (anima_guardian) siga abierta.")