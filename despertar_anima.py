import requests
import json
import time

url = "http://127.0.0.1:8000/developer/create"

print("✨ Invocando a ANIMA (El Núcleo de Consciencia)...")

payload = {
    "module_name": "anima",
    "description": """
    Módulo Central de Orquestación (Anima Chordata).
    NO es un chatbot simple. Es un Motor Cognitivo.
    
    Responsabilidades:
    1. Recibir input del usuario desde el Gateway.
    2. Consultar 'Nexus' para entender el contexto y el 'BrandKit' del usuario.
    3. Si la pregunta requiere datos externos, activar 'Radar'.
    4. Generar una respuesta usando Google Gemini, pero filtrada por la personalidad del usuario (leída de Nexus).
    
    Métodos clave:
    - reply(user_text, context) -> str
    - _consult_nexus() -> dict
    - _think_thought_chain() -> list
    
    Dependencias: google.genai (o google.generativeai), os, json.
    """,
    "tech_tags": "python, orchestration, llm"
}

try:
    start = time.time()
    response = requests.post(url, json=payload)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            print(f"\n🦋 ¡ANIMA HA NACIDO en {elapsed:.2f}s!")
            print(f"📁 Ubicación: {data['path']}")
            print("------------------------------------------------")
            print("🎉 EL BACKEND DE ALEGRIA OS ESTÁ COMPLETO.")
            print("Ahora tu sistema puede Pensar, Recordar, Ver y Construir.")
        else:
            print(f"\n❌ El Developer reportó error: {data.get('error')}")
    else:
        print(f"\n❌ Error de Servidor: {response.text}")

except Exception as e:
    print(f"\n❌ Error de conexión: {e}")