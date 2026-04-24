import pytest
import pytest_asyncio
import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock
from src.services.rejection_service import RejectionService
from src.services.anima import AnimaSystem

@pytest.mark.asyncio
class TestRejectionSystem:
    @pytest_asyncio.fixture
    async def service(self):
        return RejectionService()

    @pytest_asyncio.fixture
    async def anima(self):
        return AnimaSystem()

    async def test_add_and_get_rejections(self, service):
        """Verifica que se puedan agregar y recuperar rechazos."""
        user_id = "test_user_1"
        
        # Mock DB
        with patch("src.services.rejection_service.db_service") as mock_db:
            mock_db.connected = True
            mock_db.db.userpreferences.find_unique = AsyncMock(return_value=None)
            mock_db.db.userpreferences.create = AsyncMock(return_value=None)
            mock_db.db.userpreferences.update = AsyncMock(return_value=None)

            # Agregar rechazo
            rejection = await service.add_rejection(
                user_id=user_id,
                rejection_type="topic",
                description="Política partidaria",
                severity="strict"
            )

            assert rejection["type"] == "topic"
            assert rejection["description"] == "Política partidaria"
            assert rejection["severity"] == "strict"
            assert "id" in rejection

    async def test_build_rejection_prompt(self, service):
        """Verifica que el prompt de rechazos se construya correctamente."""
        user_id = "test_user_2"
        rejections = [
            {
                "id": "1",
                "type": "topic",
                "description": "Fútbol",
                "severity": "strict",
                "active": True
            },
            {
                "id": "2",
                "type": "behavior",
                "description": "Sarcasmo",
                "severity": "moderate",
                "active": True
            }
        ]

        with patch.object(service, "get_user_rejections", return_value=rejections):
            prompt = await service.build_rejection_prompt(user_id)
            
            assert "RECHAZOS EXPLÍCITOS DEL USUARIO" in prompt
            assert "🚫 RECHAZOS ESTRICTOS" in prompt
            assert "Fútbol" in prompt
            assert "⚠️  RECHAZOS MODERADOS" in prompt
            assert "Sarcasmo" in prompt

    async def test_anima_integration(self, anima):
        """Verifica que Anima incluya los rechazos en su system prompt."""
        user_input = "Hola Anima"
        session_id = "test_session"
        
        rejection_prompt = "🚫 RECHAZOS ESTRICTOS: No hablar de política."
        
        with patch("src.services.anima.rejection_service.build_rejection_prompt", return_value=rejection_prompt), \
             patch("src.services.anima.nexus_service") as mock_nexus, \
             patch("src.services.anima.search_service") as mock_search:
            
            mock_nexus.get_context = AsyncMock(return_value={"identity": "Anima"})
            mock_nexus.get_conversation_history = AsyncMock(return_value=[])
            mock_nexus.get_user_preferences = AsyncMock(return_value={})
            
            context = await anima._build_context(user_input, session_id)
            
            assert rejection_prompt in context["system"]
            assert "Anima" in context["system"]

if __name__ == "__main__":
    pytest.main([__file__])
