import requests
import json
import time

url = "http://127.0.0.1:8000/developer/create"

print("📡 Enviando planos de RADAR al Developer...")

payload = {
    "module_name": "radar",
    "description": """
    Módulo de Investigación (Radar) para ALEGRIA OS.
    Misión: Buscar información externa veraz y devolver resúmenes limpios.
    
    Requisitos Técnicos:
    1. Usar 'duckduckgo-search' para búsquedas anónimas y rápidas.
    2. Si falla la librería, manejar la excepción suavemente (return "No signal").
    3. Método principal: scan(query: str, max_results: int = 3).
    4. No romper nunca el flujo si no hay internet.
    """,
    "tech_tags": "python, duckduckgo-search"
}

try:
    start = time.time()
    response = requests.post(url, json=payload)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            print(f"\n✅ ¡RADAR CONSTRUIDO en {elapsed:.2f}s!")
            print(f"📁 Ubicación: {data['path']}")
            print("👁️ Ahora ALEGRIA puede ver el mundo.")
        else:
            print(f"\n❌ El Developer reportó error: {data.get('error')}")
    else:
        print(f"\n❌ Error de Servidor: {response.text}")

except Exception as e:
    print(f"\n❌ Error de conexión: {e}")