
import sys
import os
import importlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DEBUG_LOADER")

# Add backend to sys.path
sys.path.append(os.getcwd())

class GhostNode:
    """Nodo fantasma para manejar fallos gracefully."""
    def __init__(self, name: str, error: str):
        self.name = name
        self.error = error
        self.is_ghost = True

class NodeLoader:
    """Cargador dinámico de nodos del sistema."""
    def __init__(self):
        self.nodes = {}

    def load(self, module_name: str, internal_name: str):
        try:
            module = importlib.import_module(f"src.services.{module_name}")
            importlib.reload(module)
            self.nodes[internal_name] = module
            logger.info(f"✅ [NODE UP] {internal_name.upper()} conectado.")
        except Exception as e:
            logger.error(f"❌ [NODE DOWN] Fallo {internal_name}: {e}")
            self.nodes[internal_name] = GhostNode(internal_name, str(e))

def test_loading():
    print("--- Testing Server Node Loading ---")
    system = NodeLoader()
    
    # Load nodes as server.py does
    nodes_to_load = [
        ("developer", "developer"),
        ("dependency_manager", "dependencies"),
        ("world_gateway", "gateway"),
        ("nexus", "nexus"),
        ("radar", "radar"),
        ("provider_registry", "providers"),
        ("anima", "anima")
    ]

    for module, name in nodes_to_load:
        system.load(module, name)

    print("\n--- Checking Node Status ---")
    for name, node in system.nodes.items():
        is_ghost = getattr(node, "is_ghost", False)
        status = "👻 GHOST" if is_ghost else "✅ ACTIVE"
        error = getattr(node, "error", "None") if is_ghost else "None"
        print(f"{name}: {status} (Error: {error})")

    # Check connection logic
    print("\n--- Checking Connections ---")
    anima = system.nodes.get("anima")
    providers = system.nodes.get("providers")
    
    if not getattr(anima, "is_ghost", False) and not getattr(providers, "is_ghost", False):
        print("Attempting to connect Anima -> Providers...")
        try:
            anima.service.set_provider_registry(providers.service)
            print("✅ Connection successful.")
            
            # Test refresh
            print("Testing _refresh_adapter...")
            anima.service._refresh_adapter()
            if anima.service.current_adapter:
                 print(f"✅ Adapter loaded: {type(anima.service.current_adapter)}")
            else:
                 print("❌ Adapter NOT loaded after refresh.")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    else:
        print("❌ Cannot connect: One or both nodes are ghosts.")

if __name__ == "__main__":
    test_loading()
