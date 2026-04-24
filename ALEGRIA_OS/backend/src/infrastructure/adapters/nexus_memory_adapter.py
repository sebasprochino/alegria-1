from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json
from src.domain.ports.memory import (
    MemoryPort, 
    FoundationalMemory, 
    Limit, 
    LimitType, 
    MemoryUnavailableError
)

logger = logging.getLogger(__name__)

class NexusMemoryAdapter(MemoryPort):
    """
    Adapts NexusSystem to MemoryPort interface.
    Implements caching, error handling, and graceful degradation.
    """
    
    def __init__(self, nexus_system):
        self._nexus = nexus_system
        self._cache: Optional[FoundationalMemory] = None
        self._cache_version: Optional[str] = None
    
    async def get_foundational_memory(self) -> Optional[FoundationalMemory]:
        """
        Retrieves memory with caching and fallback strategy.
        """
        try:
            # Version check first
            current_version = await self._nexus.service.get_memory_version()
            
            if self._cache and self._cache_version == current_version:
                logger.debug("Memory cache HIT (version=%s)", current_version)
                return self._cache
            
            logger.debug("Memory cache MISS, fetching from Nexus")
            raw_data = await self._nexus.service.get_context()
            
            # Transform raw Nexus data -> FoundationalMemory
            memory = self._transform_nexus_data(raw_data, current_version)
            
            # Update cache
            self._cache = memory
            self._cache_version = current_version
            
            return memory
            
        except Exception as e:
            logger.error("Failed to fetch foundational memory: %s", e)
            
            # Graceful degradation: return stale cache if available
            if self._cache:
                logger.warning("Returning STALE memory cache due to error")
                return self._cache
            
            # No cache available -> raise
            raise MemoryUnavailableError(
                "Memory backend unreachable and no cache available",
                cause=e
            )

    async def update_foundational_memory(self, updates: Dict[str, Any]) -> FoundationalMemory:
        """Updates memory and invalidates cache."""
        success = await self._nexus.service.save_memory(updates)
        if not success:
            raise MemoryUnavailableError("Failed to save memory updates to Nexus")
        
        # Invalidate cache
        self._cache = None
        self._cache_version = None
        
        # Fetch fresh data
        return await self.get_foundational_memory()

    async def add_limit(self, limit: Limit) -> FoundationalMemory:
        """Adds a new limit (placeholder for now, needs Nexus support)."""
        # For now, we update the whole memory structure
        # In a real scenario, Nexus would have a specific method for this
        current = await self.get_foundational_memory()
        new_limits = list(current.limits) + [limit]
        
        # We simulate saving back to Nexus
        # This would need a more robust implementation in NexusSystem
        logger.warning("add_limit is partially implemented via full memory update")
        return await self.update_foundational_memory({"limits": [l.to_dict() for l in new_limits]})

    async def remove_limit(self, limit_value: str) -> FoundationalMemory:
        """Removes a limit (placeholder for now)."""
        current = await self.get_foundational_memory()
        new_limits = [l for l in current.limits if l.value != limit_value]
        return await self.update_foundational_memory({"limits": [l.to_dict() for l in new_limits]})

    async def get_memory_version(self) -> str:
        """Returns current version string."""
        return await self._nexus.service.get_memory_version()

    def _transform_nexus_data(self, raw_data: Dict[str, Any], version: str) -> FoundationalMemory:
        """
        Transforms Nexus raw structure -> FoundationalMemory domain object.
        """
        # Extract limits from raw_data
        raw_limits = raw_data.get("limits", {})
        limits = []
        
        # Map prohibited words to WORD limits
        for word in raw_limits.get("prohibited_words", []):
            limits.append(Limit(
                type=LimitType.WORD,
                value=word,
                context="Palabra prohibida por el léxico base",
                created_at=datetime.utcnow()
            ))
            
        # Map rechazos to TOPIC limits (or similar)
        for rechazo in raw_limits.get("rechazos", []):
            limits.append(Limit(
                type=LimitType.TOPIC,
                value=rechazo,
                context="Rechazo explícito del creador",
                created_at=datetime.utcnow()
            ))

        return FoundationalMemory(
            vision=raw_data.get("vision", ""),
            creator_preferences=raw_data.get("preferences", {}),
            personality_traits=raw_data.get("personality", {}),
            limits=limits,
            created_at=datetime.fromisoformat(raw_data.get("created_at", datetime.utcnow().isoformat())),
            version=version
        )
