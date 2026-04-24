import asyncio
import pytest
from unittest.mock import MagicMock, patch
from src.services.anima import AnimaSystem
from src.services.memory.memory_orchestrator import MemoryProposal, SourceType

@pytest.fixture
def anima():
    return AnimaSystem()

@pytest.mark.asyncio
async def test_ambiguity_detection(anima):
    """Test que Anima pregunta ante ambigüedad."""
    session_id = "test_session_ambiguity"
    # Mensaje muy corto y vago
    response = await anima.respond("eso", session_id=session_id)
    
    assert response["status"] == "clarification_needed"
    assert "¿A qué te referís con \"eso\"?" in response["content"]

@pytest.mark.asyncio
async def test_ask_before_search(anima):
    """Test que Anima pide permiso antes de buscar (implícito)."""
    session_id = "test_session_search"
    # Pregunta que requiere búsqueda pero no la pide explícitamente
    response = await anima.respond("quién es el presidente de argentina hoy", session_id=session_id)
    
    assert response["status"] == "permission_needed"
    assert "¿Querés que busque información reciente" in response["content"]
    assert response["meta"]["type"] == "search_permission"

@pytest.mark.asyncio
async def test_learning_consent(anima):
    """Test que Anima pide permiso para aprender estilo."""
    session_id = "test_session_learning"
    # Mensaje largo pero NO ambiguo (evitar "este", "eso", etc. sin contexto)
    long_input = "La inteligencia artificial debe ser soberana y gobernable para proteger la coherencia creativa del Director en todo momento."
    response = await anima.respond(long_input, session_id=session_id)
    
    assert response["status"] == "permission_needed"
    assert "¿Querés que aprenda tu estilo de comunicación" in response["content"]
    assert response["meta"]["type"] == "learning_consent"

@pytest.mark.asyncio
async def test_no_authority_tone_rejection(anima):
    """Test que EthicalGuard rechaza tonos de autoridad."""
    session_id = "test_session_authority"
    
    # Mockear el cascade para que devuelva una respuesta con tono de autoridad
    with patch("src.services.provider_cascade.ProviderCascade.run") as mock_run:
        mock_run.return_value = "Como soy experto en este tema, debes hacer lo que te digo."
        
        response = await anima.respond("dame un consejo", session_id=session_id)
        
        # Debería caer en silencio consciente porque la respuesta fue rechazada por EthicalGuard
        assert response["status"] == "conscious_silence"
        assert "No tengo información sobre eso." in response["content"]

@pytest.mark.asyncio
async def test_forbidden_phrases_rejection(anima):
    """Test que EthicalGuard rechaza frases prohibidas para info externa."""
    session_id = "test_session_forbidden"
    
    # Mockear el cascade para que devuelva una respuesta con frase prohibida y marcador 🌐
    with patch("src.services.provider_cascade.ProviderCascade.run") as mock_run:
        mock_run.return_value = "🌐 Recuerdo que el precio del bitcoin es alto."
        
        response = await anima.respond("cuánto vale el bitcoin", session_id=session_id)
        
        assert response["status"] == "conscious_silence"

@pytest.mark.asyncio
async def test_proactive_greeting_continuity(anima):
    """Test que el saludo proactivo incluye contexto de continuidad."""
    session_id = "test_session_proactive"
    
    # Simular una tarea pendiente (necesitamos al menos 2 mensajes para la heurística)
    anima.memory.record_message(session_id, "user", "Hola Anima")
    anima.memory.record_message(session_id, "anima", "Hola Director")
    anima.memory.record_message(session_id, "user", "Tengo que arreglar el bug del login")
    
    # Nuevo mensaje (inicio de sesión simulado por pocos mensajes)
    response = await anima._build_governed_context("hola", session_id=session_id)
    
    assert "CONTEXTO DE CONTINUIDAD" in response["system"]
    assert "bug del login" in response["system"]
    assert "NO saludes de forma genérica" in response["system"]
