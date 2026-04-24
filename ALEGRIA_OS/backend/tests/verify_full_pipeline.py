import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add backend to path
sys.path.append(os.getcwd())

# Mock services BEFORE importing anima
sys.modules['src.services.nexus'] = MagicMock()
sys.modules['src.services.provider_registry'] = MagicMock()
sys.modules['src.services.search_module'] = MagicMock()

from src.services.anima import AnimaSystem

async def test_pipeline():
    print("Starting Full Pipeline Verification (Mocked)...")
    
    # Setup Mocks
    nexus_mock = sys.modules['src.services.nexus'].service
    nexus_mock.get_context = AsyncMock(return_value={"identity": "Test Anima"})
    nexus_mock.get_conversation_history = AsyncMock(return_value=[
        {"role": "user", "content": "Hi"},
        {"role": "anima", "content": "Hello"}
    ])
    nexus_mock.get_user_preferences = AsyncMock(return_value={
        "tone": "formal",
        "length": "short",
        "topics": "tech"
    })
    
    search_mock = sys.modules['src.services.search_module'].service
    search_mock.search = MagicMock(return_value=[
        {"title": "Python", "body": "Python is a language", "href": "http://python.org"}
    ])
    
    # Initialize Anima
    anima = AnimaSystem()
    
    # Test 1: Context Building with History + Preferences + Search
    print("\nTesting Context Building...")
    context = await anima._build_context("buscar python", "session_id")
    
    # Verify System Prompt Content
    system_prompt = context['system']
    print(f"System Prompt:\n{system_prompt[:200]}...")
    
    assert "Test Anima" in system_prompt
    assert "Historial de conversación reciente" in system_prompt
    assert "Usuario: Hi" in system_prompt
    assert "Preferencias del usuario" in system_prompt
    assert "Tono: formal" in system_prompt
    assert "INFORMACIÓN DE BÚSQUEDA EN TIEMPO REAL" in system_prompt
    assert "Python is a language" in system_prompt
    
    print("All context elements present.")
    print("Verification Successful!")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
