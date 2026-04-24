
import sys
import os
from pathlib import Path

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mocking the environment for imports to work if needed, 
# but we are running from backend/ so it should be fine if we set PYTHONPATH or append to sys.path

try:
    from src.services.provider_registry import ProviderRegistry
    from src.services.anima import AnimaChordata
    from src.services.llm_adapters import get_adapter
except ImportError as e:
    print(f"Import Error: {e}")
    # Try adjusting path if running from root
    sys.path.append(os.getcwd())
    from src.services.provider_registry import ProviderRegistry
    from src.services.anima import AnimaChordata
    from src.services.llm_adapters import get_adapter

def test_configuration():
    print("--- Testing Provider Registry ---")
    registry = ProviderRegistry()
    print(f"Providers loaded: {list(registry.providers.keys())}")
    print(f"Active Provider: {registry.active_provider}")
    
    active = registry.get_active()
    print(f"Get Active Result: {active}")

    if not active:
        print("❌ No active provider found in registry.")
        return

    print("\n--- Testing Anima Integration ---")
    anima = AnimaChordata()
    anima.set_provider_registry(registry)
    
    print("Refreshing adapter...")
    anima._refresh_adapter()
    
    if anima.current_adapter:
        print(f"Adapter loaded: {type(anima.current_adapter)}")
        print(f"Adapter config: {anima.current_adapter.__dict__}")
    else:
        print("❌ Anima failed to load adapter.")
        
        # Debug why
        adapter_class = get_adapter(active['name'])
        print(f"Adapter Class for {active['name']}: {adapter_class}")
        if adapter_class:
            try:
                print("Attempting manual instantiation...")
                inst = adapter_class(
                    api_key=active["api_key"],
                    model=active["model"],
                    endpoint=active.get("endpoint")
                )
                print("Manual instantiation successful.")
            except Exception as e:
                print(f"Manual instantiation failed: {e}")

if __name__ == "__main__":
    test_configuration()
