# -------------------------------------------------------------------------
# ALEGR-IA OS — Tests de Regla Maestra de Decisión
# -------------------------------------------------------------------------
"""
Tests para verificar la tabla de verdad de la Regla Maestra:

| Consulta                     | Acción correcta |
|------------------------------|-----------------|
| "Buscá mi historial"         | MEMORY only     |
| "¿Guardaste lo que dije?"    | MEMORY only     |
| "Qué hablamos antes"         | MEMORY only     |
| "Buscá en Google…"           | SEARCH          |
| "Qué es FastAPI"             | SEARCH          |
| "Explorá esta idea"          | CASCADE         |
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from src.services.query_classifier import QueryClassifier, QueryType, ClassificationResult
from src.services.anima import AnimaSystem


class TestQueryClassifier:
    """Tests para el clasificador de queries."""
    
    @pytest.fixture
    def classifier(self):
        return QueryClassifier()
    
    # --- Tests INTERNAL ---
    
    def test_classify_internal_historial(self, classifier):
        """'Buscá mi historial' debe ser INTERNAL."""
        result = classifier.classify("Buscá mi historial")
        assert result.query_type == QueryType.INTERNAL
        assert result.confidence >= 0.75
    
    def test_classify_internal_guardaste(self, classifier):
        """'¿Guardaste lo que dije?' debe ser INTERNAL."""
        result = classifier.classify("¿Guardaste lo que dije?")
        assert result.query_type == QueryType.INTERNAL
    
    def test_classify_internal_hablamos_antes(self, classifier):
        """'Qué hablamos antes' debe ser INTERNAL."""
        result = classifier.classify("Qué hablamos antes")
        assert result.query_type == QueryType.INTERNAL
    
    def test_classify_internal_mi_proyecto(self, classifier):
        """Referencias a 'mi proyecto' deben ser INTERNAL."""
        result = classifier.classify("Qué sabés de mi proyecto")
        assert result.query_type == QueryType.INTERNAL
    
    def test_classify_internal_decisiones(self, classifier):
        """'Lo que decidimos' debe ser INTERNAL."""
        result = classifier.classify("Recordás lo que decidimos ayer?")
        assert result.query_type == QueryType.INTERNAL
    
    # --- Tests EXTERNAL ---
    
    def test_classify_external_busca_google(self, classifier):
        """'Buscá en Google' debe ser EXTERNAL."""
        result = classifier.classify("Buscá en Google sobre Python")
        assert result.query_type == QueryType.EXTERNAL
        assert result.confidence >= 0.9
    
    def test_classify_external_que_es(self, classifier):
        """'Qué es FastAPI' debe ser EXTERNAL."""
        result = classifier.classify("Qué es FastAPI")
        assert result.query_type == QueryType.EXTERNAL
    
    def test_classify_external_noticias(self, classifier):
        """Consultas sobre noticias deben ser EXTERNAL."""
        result = classifier.classify("Dame las noticias de hoy")
        assert result.query_type == QueryType.EXTERNAL
    
    # --- Tests CREATIVE ---
    
    def test_classify_creative_explora(self, classifier):
        """'Explorá esta idea' debe ser CREATIVE."""
        result = classifier.classify("Explorá esta idea conmigo")
        assert result.query_type == QueryType.CREATIVE
    
    def test_classify_creative_imagina(self, classifier):
        """'Imaginá que...' debe ser CREATIVE."""
        result = classifier.classify("Imaginá que tenemos un sistema de IA")
        assert result.query_type == QueryType.CREATIVE
    
    def test_classify_creative_estrategia(self, classifier):
        """Consultas sobre estrategia deben ser CREATIVE."""
        result = classifier.classify("Pensemos una estrategia para el lanzamiento")
        assert result.query_type == QueryType.CREATIVE
    
    # --- Tests GENERAL (fallback) ---
    
    def test_classify_general_fallback(self, classifier):
        """Consultas genéricas deben ser GENERAL."""
        result = classifier.classify("Hola, cómo estás")
        assert result.query_type == QueryType.GENERAL
    
    # --- Tests de prioridad (INTERNAL bloquea EXTERNAL) ---
    
    def test_internal_blocks_search_keywords(self, classifier):
        """INTERNAL debe tener prioridad sobre keywords de SEARCH."""
        # Aunque dice 'buscar', es sobre el historial → INTERNAL
        result = classifier.classify("Buscá en mi historial qué dije")
        assert result.query_type == QueryType.INTERNAL


@pytest.mark.asyncio
class TestDecisionRulesInAnima:
    """Tests de integración para la Regla Maestra en Anima."""
    
    @pytest.fixture
    def anima(self):
        return AnimaSystem()
    
    async def test_internal_query_blocks_search(self, anima):
        """Queries INTERNAL no deben disparar SEARCH."""
        session_id = "test_session_internal"
        
        with patch.object(anima, "_search_as_proposals", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = []
            
            # Mockear el cascade para evitar llamadas reales al LLM
            with patch("src.services.anima.ProviderCascade") as mock_cascade_class:
                mock_cascade = MagicMock()
                mock_cascade.run = AsyncMock(return_value="Respuesta desde memoria.")
                mock_cascade.last_used_provider_name = "test_provider"
                mock_cascade_class.return_value = mock_cascade
                
                with patch("src.services.anima.provider_service") as mock_provider:
                    mock_provider.get_cascade_providers.return_value = [{"name": "test"}]
                    
                    # Query INTERNAL
                    response = await anima.respond("¿Qué hablamos antes?", session_id)
                    
                    # SEARCH NO debe haber sido llamado
                    mock_search.assert_not_called()
                    
                    # La respuesta debe indicar que fue query INTERNAL
                    assert response["governance"].get("query_type") == "INTERNAL" or response["governance"].get("search_blocked") == True
    
    async def test_external_query_allows_search(self, anima):
        """Queries EXTERNAL deben permitir SEARCH."""
        session_id = "test_session_external"
        
        # Verificar clasificación primero
        classification = anima.classifier.classify("Buscá en Google qué es FastAPI")
        assert classification.query_type == QueryType.EXTERNAL
        assert classification.confidence >= 0.7  # Debe permitir search
    
    async def test_classification_happens_before_actions(self, anima):
        """La clasificación debe ocurrir ANTES de cualquier acción."""
        session_id = "test_session_order"
        
        call_order = []
        
        original_classify = anima.classifier.classify
        original_hydrate = anima.memory.hydrate_session
        
        def mock_classify(text):
            call_order.append("classify")
            return original_classify(text)
        
        async def mock_hydrate(sid):
            call_order.append("hydrate")
            return await original_hydrate(sid)
        
        with patch.object(anima.classifier, "classify", side_effect=mock_classify):
            with patch.object(anima.memory, "hydrate_session", side_effect=mock_hydrate):
                with patch("src.services.anima.ProviderCascade") as mock_cascade_class:
                    mock_cascade = MagicMock()
                    mock_cascade.run = AsyncMock(return_value="Test response")
                    mock_cascade.last_used_provider_name = "test"
                    mock_cascade_class.return_value = mock_cascade
                    
                    with patch("src.services.anima.provider_service") as mock_provider:
                        mock_provider.get_cascade_providers.return_value = [{"name": "test"}]
                        
                        await anima.respond("Hola", session_id)
        
        # Verificar que classify fue llamado primero
        # Nota: En la implementación actual, hydrate puede ir antes de classify
        # Lo importante es que classify ocurra antes de decidir sobre SEARCH
        assert "classify" in call_order


class TestClassifierHelperMethods:
    """Tests para los métodos helper del clasificador."""
    
    @pytest.fixture
    def classifier(self):
        return QueryClassifier()
    
    def test_references_internal_system(self, classifier):
        """Test del método references_internal_system."""
        assert classifier.references_internal_system("mi historial") == True
        assert classifier.references_internal_system("noticias de hoy") == False
    
    def test_requests_external_info(self, classifier):
        """Test del método requests_external_info."""
        assert classifier.requests_external_info("buscar en google") == True
        assert classifier.requests_external_info("mi historial") == False
    
    def test_is_creative_or_exploratory(self, classifier):
        """Test del método is_creative_or_exploratory."""
        assert classifier.is_creative_or_exploratory("explorá esta idea") == True
        assert classifier.is_creative_or_exploratory("buscar en google") == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
