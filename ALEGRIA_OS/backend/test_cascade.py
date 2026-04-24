import asyncio
from src.services.provider_registry import service

async def test():
    try:
        response = await service.chat([{'role': 'user', 'content': 'hola'}], system="You are a test assistant")
        print("RESPONSE:", response)
    except Exception as e:
        print("ERROR:", e)

if __name__ == '__main__':
    asyncio.run(test())
