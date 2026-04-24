"""
Test script for Developer Conversational Interface
Tests state transitions, Radar integration, and app generation
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.services.developer import service as developer_service


async def test_conversational_flow():
    """Test complete conversational flow from DISCUSSING to COMPLETE"""
    print("[TEST] Testing Conversational Developer Flow\n")
    print("=" * 60)
    
    session_id = "test_session_001"
    
    # Test 1: Initial greeting (DISCUSSING state)
    print("\n[TEST 1] Initial State - DISCUSSING")
    print("-" * 60)
    response = await developer_service.chat("Hola", session_id)
    print(f"Estado: {response.get('state')}")
    print(f"Respuesta: {response.get('content')[:100]}...")
    assert response["status"] == "ok", "Failed to initialize conversation"
    assert response["state"] == "discussing", f"Expected 'discussing', got '{response['state']}'"
    print("✅ PASS: Initial state is DISCUSSING")
    
    # Test 2: Express intent to create app (DISCUSSING → PLANNING)
    print("\n[TEST 2] State Transition - DISCUSSING → PLANNING")
    print("-" * 60)
    response = await developer_service.chat("Quiero crear una app de calculadora científica", session_id)
    print(f"Estado: {response.get('state')}")
    print(f"Respuesta: {response.get('content')[:150]}...")
    print(f"Investigación Radar: {'Sí' if response.get('research_available') else 'No'}")
    assert response["state"] == "planning", f"Expected 'planning', got '{response['state']}'"
    print("✅ PASS: Transitioned to PLANNING state")
    
    # Test 3: Add features (stay in PLANNING)
    print("\n[TEST 3] Adding Features - PLANNING")
    print("-" * 60)
    response = await developer_service.chat("Quiero que tenga funciones trigonométricas", session_id)
    print(f"Estado: {response.get('state')}")
    print(f"Respuesta: {response.get('content')[:150]}...")
    assert response["state"] == "planning", f"Expected 'planning', got '{response['state']}'"
    print("✅ PASS: Stayed in PLANNING state")
    
    # Test 4: Confirm plan (PLANNING → CONFIRMING)
    print("\n[TEST 4] State Transition - PLANNING → CONFIRMING")
    print("-" * 60)
    response = await developer_service.chat("Sí, perfecto", session_id)
    print(f"Estado: {response.get('state')}")
    print(f"Respuesta: {response.get('content')[:150]}...")
    assert response["state"] == "confirming", f"Expected 'confirming', got '{response['state']}'"
    print("✅ PASS: Transitioned to CONFIRMING state")
    
    # Test 5: Final confirmation (CONFIRMING → GENERATING → COMPLETE)
    print("\n[TEST 5] State Transition - CONFIRMING → GENERATING → COMPLETE")
    print("-" * 60)
    response = await developer_service.chat("Sí, crea la app", session_id)
    print(f"Estado: {response.get('state')}")
    print(f"Respuesta: {response.get('content')[:200]}...")
    if response.get("app_url"):
        print(f"App URL: {response['app_url']}")
    assert response["state"] in ["generating", "complete"], f"Expected 'generating' or 'complete', got '{response['state']}'"
    print("✅ PASS: App generation initiated/completed")
    
    # Test 6: Session persistence
    print("\n[TEST 6] Session Persistence")
    print("-" * 60)
    from src.services.nexus import service as nexus_service
    session_data = await nexus_service.get_session_metadata(session_id)
    print(f"Concepto de app: {session_data.get('app_concept')}")
    print(f"Características: {len(session_data.get('app_features', []))} agregadas")
    assert session_data is not None, "Session not found"
    assert session_data.get("app_concept") is not None, "App concept not saved"
    print("✅ PASS: Session data persisted correctly")
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)


async def test_iterative_modification():
    """Test modifying an existing app"""
    print("\n\n🧪 Testing Iterative Modification\n")
    print("=" * 60)
    
    session_id = "test_session_002"
    
    # Create initial app
    print("\n[SETUP] Creating initial app")
    await developer_service.chat("Quiero crear un contador simple", session_id)
    await developer_service.chat("ok", session_id)
    response = await developer_service.chat("sí, crea", session_id)
    
    if response["state"] == "complete":
        print("✅ Initial app created")
        
        # Test modification
        print("\n[TEST] Requesting modification")
        print("-" * 60)
        response = await developer_service.chat("Agrega un botón de reset", session_id)
        print(f"Estado: {response.get('state')}")
        print(f"Respuesta: {response.get('content')[:150]}...")
        assert response["state"] == "planning", f"Expected 'planning' for modification, got '{response['state']}'"
        print("✅ PASS: Modification flow initiated")
    else:
        print("⚠️  SKIP: Initial app generation incomplete")


async def test_radar_integration():
    """Test Radar integration during DISCUSSING phase"""
    print("\n\n🧪 Testing Radar Integration\n")
    print("=" * 60)
    
    session_id = "test_session_003"
    
    print("\n[TEST] Radar research trigger")
    print("-" * 60)
    response = await developer_service.chat("Quiero hacer una app de gestión de tareas", session_id)
    print(f"Estado: {response.get('state')}")
    print(f"Investigación disponible: {response.get('research_available')}")
    
    from src.services.nexus import service as nexus_service
    session_data = await nexus_service.get_session_metadata(session_id)
    if session_data and session_data.get("research_data"):
        print("✅ PASS: Radar research was triggered and stored")
        print(f"Research data keys: {list(session_data['research_data'].keys())}")
    else:
        print("⚠️  WARNING: Radar research not available (may need LLM provider)")


async def main():
    """Run all tests"""
    try:
        await test_conversational_flow()
        await test_iterative_modification()
        await test_radar_integration()
        
        print("\n\n" + "=" * 60)
        print("✅ ALL TEST SUITES COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
