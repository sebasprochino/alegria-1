# -------------------------------------------------------------------------
# ALEGR-IA OS — Tests for World Gateway + Dependency Manager
# Copyright (c) 2025 Sebastián Fernández & Antigravity AI.
# -------------------------------------------------------------------------

import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import sys


class TestDependencyManager:
    """Tests para DependencyManager - instalación automática de paquetes."""

    @pytest.fixture
    def dep_manager(self):
        """Crea instancia fresca de DependencyManager."""
        from src.services.dependency_manager import DependencyManager
        return DependencyManager()

    def test_install_success(self, dep_manager):
        """Verifica instalación exitosa de un paquete."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Mock open para no escribir realmente
            with patch("builtins.open", MagicMock()):
                result = dep_manager.install("requests")
            
            assert result["status"] == "success"
            assert result["pkg"] == "requests"
            # Verificar que se llamó pip install
            calls = mock_run.call_args_list
            assert any("install" in str(call) for call in calls)

    def test_install_failure(self, dep_manager):
        """Verifica manejo de error en instalación."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("pip failed")
            
            result = dep_manager.install("fake_package")
            
            assert result["status"] == "error"
            assert "pip failed" in result["error"]

    def test_execute_install_tool(self, dep_manager):
        """Verifica que execute() despacha correctamente a install()."""
        with patch.object(dep_manager, "install") as mock_install:
            mock_install.return_value = {"status": "success", "pkg": "pandas"}
            
            result = dep_manager.execute("install_tool", {"query": "pandas"})
            
            mock_install.assert_called_once_with("pandas")
            assert result["status"] == "success"

    def test_execute_unknown_action(self, dep_manager):
        """Verifica que acciones desconocidas retornan error."""
        result = dep_manager.execute("unknown_action", {})
        
        assert "error" in result
        assert "Unknown action" in result["error"]


class TestUniversalAdapter:
    """Tests para UniversalAdapter - carga dinámica de módulos."""

    @pytest.fixture
    def adapter(self):
        """Crea instancia fresca de UniversalAdapter."""
        from src.services.world_gateway import UniversalAdapter
        return UniversalAdapter("json")  # Módulo siempre disponible

    def test_connect_existing_module(self, adapter):
        """Verifica conexión exitosa con módulo existente."""
        result = adapter.connect()
        
        assert result is True
        assert adapter.status == "connected"
        assert adapter.module is not None

    def test_connect_nonexistent_module(self):
        """Verifica fallo con módulo inexistente."""
        from src.services.world_gateway import UniversalAdapter
        adapter = UniversalAdapter("this_module_does_not_exist_12345")
        
        result = adapter.connect()
        
        assert result is False
        assert adapter.status == "disconnected"

    def test_execute_sync_function(self, adapter):
        """Verifica ejecución de función síncrona."""
        adapter.connect()
        
        # json.dumps es síncrono
        result = adapter.execute("dumps", obj={"test": 123})
        
        assert result == '{"test": 123}'


@pytest.mark.asyncio
class TestWorldGateway:
    """Tests para WorldGateway - orquestador de capacidades."""

    @pytest_asyncio.fixture
    async def gateway(self):
        """Crea instancia fresca de WorldGateway."""
        from src.services.world_gateway import WorldGateway
        return WorldGateway()

    async def test_ensure_capability_already_loaded(self, gateway):
        """Verifica que módulos cargados se reutilizan."""
        # Cargar json primero
        result1 = await gateway.ensure_capability("json")
        result2 = await gateway.ensure_capability("json")
        
        assert result1 is True
        assert result2 is True
        assert len(gateway.adapters) == 1  # Solo una entrada

    async def test_ensure_capability_new_module(self, gateway):
        """Verifica carga de nuevo módulo disponible."""
        result = await gateway.ensure_capability("os")
        
        assert result is True
        assert "os" in gateway.adapters
        assert gateway.adapters["os"].status == "connected"

    async def test_ensure_capability_missing_no_dep_manager(self, gateway):
        """Verifica comportamiento sin DependencyManager configurado."""
        result = await gateway.ensure_capability("fake_module_xyz")
        
        assert result is False  # No puede instalar sin dep_manager

    async def test_ensure_capability_auto_install(self, gateway):
        """Verifica auto-instalación cuando dep_manager está disponible."""
        # Mock del DependencyManager
        mock_dep = MagicMock()
        mock_dep.service = MagicMock()
        mock_dep.service.execute.return_value = {"status": "success"}
        gateway.set_dependency_manager(mock_dep)
        
        # Primera vez: módulo no existe, intentará instalar
        with patch("src.services.world_gateway.UniversalAdapter.connect") as mock_connect:
            # Primero falla, luego tiene éxito (simula instalación)
            mock_connect.side_effect = [False, True]
            
            result = await gateway.ensure_capability("new_package")
        
        # Debe haber intentado instalar
        mock_dep.service.execute.assert_called_once_with(
            "install_tool", 
            {"query": "new_package"}
        )

    async def test_use_executes_function(self, gateway):
        """Verifica que use() ejecuta funciones correctamente."""
        result = await gateway.use("json", "dumps", obj={"key": "value"})
        
        assert result == '{"key": "value"}'

    async def test_use_missing_capability(self, gateway):
        """Verifica error cuando la capacidad no está disponible."""
        result = await gateway.use("fake_module_abc", "some_function")
        
        assert "error" in result
        assert "Capability missing" in result["error"]


@pytest.mark.asyncio
class TestIntegration:
    """Tests de integración entre WorldGateway y DependencyManager."""

    async def test_gateway_with_real_dep_manager(self):
        """Test de integración con DependencyManager real (sin instalar)."""
        from src.services.world_gateway import WorldGateway
        from src.services.dependency_manager import DependencyManager
        
        gateway = WorldGateway()
        dep_mgr = DependencyManager()
        
        # Simular el nodo como lo hace NodeLoader
        mock_node = MagicMock()
        mock_node.service = dep_mgr
        
        gateway.set_dependency_manager(mock_node)
        
        # Verificar que módulos del sistema funcionan
        result = await gateway.use("os", "getcwd")
        assert isinstance(result, str)
        
        # Verificar json
        result = await gateway.use("json", "loads", s='{"a": 1}')
        assert result == {"a": 1}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
