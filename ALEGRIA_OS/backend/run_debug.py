import asyncio
import logging
from src.services.anima import get_anima

# Configurar logging básico
logging.basicConfig(level=logging.INFO)

async def run_debug():
    print("--- INICIANDO DEBUG ---")
    anima = get_anima()
    session_id = "debug_session_1"
    
    user_input = "quién es el presidente de argentina hoy"
    print(f"Enviando input: '{user_input}'")
    
    try:
        response = await anima.respond(user_input, session_id=session_id)
        print("\n--- RESPUESTA ---")
        print(f"Status: {response.get('status')}")
        print(f"Content: {response.get('content')}")
        print(f"Meta: {response.get('meta')}")
    except Exception as e:
        print(f"\n--- EXCEPCIÓN NO CAPTURADA ---")
        print(e)

if __name__ == "__main__":
    asyncio.run(run_debug())
