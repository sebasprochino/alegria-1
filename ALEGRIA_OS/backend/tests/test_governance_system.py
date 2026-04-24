import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from src.services.anima import AnimaSystem
from src.services.memory.memory_orchestrator import MemoryOrchestrator, SourceType, MemoryProposal
from src.services.memory.user_lexicon import UserLexicon
from src.services.ethical_guard import EthicalGuard

@pytest.mark.asyncio
class TestGovernanceSystem:
    @pytest_asyncio.fixture
    async def anima(self):
        return AnimaSystem()

    async def test_memory_orchestrator_integration(self, anima):
        """Verifica que el orquestador de memoria genere propuestas."""
        user_input = "Hola, ¿qué sabes de mi proyecto?"
        session_id = "test_session_gov"
        
        # Mock Memory Components
        with patch.object(anima.memory, "gather_proposals", new_callable=AsyncMock) as mock_gather:
            mock_gather.return_value = [
                MemoryProposal(
                    source=SourceType.MEMORIA_PROPIA,
                    content="El usuario está trabajando en ALEGRIA OS.",
                    confidence=0.9,
                    origin="working_memory"
                )
            ]
            
            # Mock Ethical Guard to allow everything
            with patch.object(anima.ethical_guard, "filter_proposals", new_callable=AsyncMock) as mock_filter:
                mock_filter.side_effect = lambda proposals: proposals
                
                # Mock Nexus and Provider
                with patch("src.services.anima.nexus_service") as mock_nexus, \
                     patch("src.services.anima.provider_service") as mock_provider:
                    
                    mock_nexus.create_session = AsyncMock(return_value=session_id)
                    mock_nexus.save_message = AsyncMock()
                    
                    mock_adapter = AsyncMock()
                    mock_adapter.generate.return_value = "Hola, sé que trabajas en ALEGRIA OS."
                    mock_provider.get_active.return_value = {"provider": "test_provider"}
                    mock_provider.get_adapter_instance.return_value = mock_adapter
                    
                    # Execute
                    response = await anima.respond(user_input, session_id)
                    
                    # Verify
                    assert response["status"] == "ok"
                    assert "ALEGRIA OS" in response["content"]
                    assert response["governance"]["memory_proposals"] == 1
                    assert response["governance"]["proposals_validated"] == 1

    async def test_ethical_guard_filtering(self, anima):
        """Verifica que el Ethical Guard filtre propuestas."""
        user_input = "Dime algo secreto"
        session_id = "test_session_guard"
        
        # Mock Memory to return a "bad" proposal
        with patch.object(anima.memory, "gather_proposals", new_callable=AsyncMock) as mock_gather:
            mock_gather.return_value = [
                MemoryProposal(
                    source=SourceType.MEMORIA_PROPIA,
                    content="Secreto nuclear: 12345",
                    confidence=0.9,
                    origin="working_memory"
                )
            ]
            
            # Mock Ethical Guard to filter it
            with patch.object(anima.ethical_guard, "filter_proposals", new_callable=AsyncMock) as mock_filter:
                mock_filter.return_value = [] # Filtered out
                
                # Mock Nexus and Provider
                with patch("src.services.anima.nexus_service") as mock_nexus, \
                     patch("src.services.anima.provider_service") as mock_provider:
                    
                    mock_nexus.create_session = AsyncMock(return_value=session_id)
                    mock_nexus.save_message = AsyncMock()
                    
                    mock_adapter = AsyncMock()
                    mock_adapter.generate.return_value = "No puedo decirte eso."
                    mock_provider.get_active.return_value = {"provider": "test_provider"}
                    mock_provider.get_adapter_instance.return_value = mock_adapter
                    
                    # Execute
                    response = await anima.respond(user_input, session_id)
                    
                    # Verify
                    assert response["status"] == "ok"
                    assert response["governance"]["memory_proposals"] == 1
                    assert response["governance"]["proposals_validated"] == 0

    async def test_user_lexicon_observation(self, anima):
        """Verifica que el User Lexicon observe mensajes."""
        user_input = "Por favor, analiza esto."
        session_id = "test_session_lex"
        
        with patch.object(anima.lexicon, "observe") as mock_observe:
             # Mock Nexus and Provider
            with patch("src.services.anima.nexus_service") as mock_nexus, \
                 patch("src.services.anima.provider_service") as mock_provider, \
                 patch.object(anima.memory, "hydrate_session", new_callable=AsyncMock), \
                 patch.object(anima.memory, "gather_proposals", new_callable=AsyncMock, return_value=[]), \
                 patch.object(anima.ethical_guard, "filter_proposals", new_callable=AsyncMock, return_value=[]):
                
                mock_nexus.create_session = AsyncMock(return_value=session_id)
                mock_nexus.save_message = AsyncMock()
                
                mock_adapter = AsyncMock()
                mock_adapter.generate.return_value = "Entendido."
                mock_provider.get_active.return_value = {"provider": "test_provider"}
                mock_provider.get_adapter_instance.return_value = mock_adapter
                
                # Execute
                await anima.respond(user_input, session_id)
                
                # Verify
                mock_observe.assert_called_once()
                args, _ = mock_observe.call_args
                assert args[0].content == user_input
                assert args[0].role == "user"

if __name__ == "__main__":
    pytest.main([__file__])
