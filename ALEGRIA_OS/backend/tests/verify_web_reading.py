import asyncio
import sys
import os

# Añadir el directorio backend al path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from src.services.anima import service as anima

async def test_web_reading():
    print("🚀 Probando lectura automática de noticias...")
    
    # Simular una petición de noticias de un sitio específico
    user_input = "Dame un resumen de las noticias de sport.es"
    session_id = "test_session_web_reading"
    
    print(f"Mensaje: {user_input}")
    
    # Ejecutar respond
    response = await anima.respond(user_input, session_id)
    
    print(f"\nRespuesta de Anima:\n{response['content']}")
    print(f"\nProveedor usado: {response['provider']}")
    print(f"Búsqueda realizada: {response['search_performed']}")
    print(f"Propuestas usadas: {response['proposals_used']}")
    
    # Verificar si hay contenido de lectura web en los logs o si la respuesta parece detallada
    if response['search_performed'] and response['proposals_used'] > 5:
        print("\n✅ ÉXITO: Se detectó búsqueda y múltiples propuestas (probablemente incluyendo lectura web).")
    else:
        print("\n⚠️ ADVERTENCIA: Los resultados podrían ser solo snippets de búsqueda.")

if __name__ == "__main__":
    asyncio.run(test_web_reading())
