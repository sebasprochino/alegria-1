import sys
import os
import asyncio

# El directorio actual es backend
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

async def test_search():
    try:
        from src.services.search_module import service
        print(f"DEBUG: Primary provider: {service.primary_provider}")
        results = await service.search_async("test", max_results=1)
        print(f"DEBUG: Results found: {len(results)}")
        if results:
            print(f"DEBUG: First result: {results[0]['title']}")
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())
