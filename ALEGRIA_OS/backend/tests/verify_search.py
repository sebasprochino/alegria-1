import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from src.services.search_module import service as search_service
from src.services.anima import service as anima_service

async def test_search():
    print("🚀 Starting Search Verification...")
    
    # 1. Test Search Service directly
    print("🔍 Testing SearchService...")
    results = search_service.search("python programming language")
    print(f"✅ Results found: {len(results)}")
    if results:
        print(f"  - Top result: {results[0].get('title')}")
    
    # 2. Test Anima Context Building (Search Trigger)
    print("\n🧠 Testing Anima Context (Trigger)...")
    context = await anima_service._build_context("Quiero buscar información sobre python", "test_session")
    
    print(f"✅ Search Performed: {context.get('search_performed')}")
    assert context.get('search_performed') == True
    assert "INFORMACIÓN DE BÚSQUEDA EN TIEMPO REAL" in context['system']
    
    # 3. Test Anima Context Building (No Trigger)
    print("\n🧠 Testing Anima Context (No Trigger)...")
    context_no = await anima_service._build_context("Hola, ¿cómo estás?", "test_session")
    
    print(f"✅ Search Performed: {context_no.get('search_performed')}")
    assert context_no.get('search_performed') == False
    assert "INFORMACIÓN DE BÚSQUEDA EN TIEMPO REAL" not in context_no['system']
    
    print("🎉 Verification Successful!")

if __name__ == "__main__":
    asyncio.run(test_search())
