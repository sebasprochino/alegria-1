"""
Domain Layer: Memory Port Contracts

This module defines the abstract interfaces (ports) that the domain layer
requires from memory providers. Following Port & Adapter (Hexagonal) architecture,
this establishes the contract WITHOUT knowing about implementation details.

Design Principles Applied:
- Dependency Inversion Principle (DIP): High-level policy depends on abstractions
- Interface Segregation Principle (ISP): Minimal, focused interfaces
- Single Responsibility Principle (SRP): Each class has one reason to change
"""

from abc import ABC, abstractmethod
from typing import Protocol, Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class LimitType(str, Enum):
    """
    Enumeration of limit types for Memoria del "No".
    
    Using str Enum for JSON serialization compatibility and
    explicit typing in domain logic.
    """
    WORD = "word"
    PHRASE = "phrase"
    TONE = "tone"
    TOPIC = "topic"
    FORMAT = "format"


@dataclass(frozen=True)
class Limit:
    """
    Immutable representation of a user-defined limit.
    
    Frozen=True provides:
    - Thread-safety without locks
    - Hashability for set operations
    - Cache-ability (can be used as dict key)
    """
    type: LimitType
    value: str
    context: str  # Human-readable explanation
    examples: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def matches(self, text: str) -> bool:
        """
        Checks if text violates this limit.
        
        Implementation uses case-insensitive matching for robustness.
        For production, consider:
        - Regex patterns for phrase limits
        - Fuzzy matching for typo tolerance
        - Sentiment analysis for tone limits
        """
        text_lower = text.lower()
        value_lower = self.value.lower()
        
        if self.type == LimitType.WORD:
            # Word boundary matching to avoid false positives
            # "revolucionario" shouldn't match "evolucionario"
            import re
            pattern = r'\b' + re.escape(value_lower) + r'\b'
            return bool(re.search(pattern, text_lower))
        
        elif self.type == LimitType.PHRASE:
            return value_lower in text_lower
        
        elif self.type == LimitType.TONE:
            # Tone detection requires NLP - placeholder for now
            # Production: integrate sentiment analysis model
            return False
        
        return False


@dataclass(frozen=True)
class FoundationalMemory:
    """
    Immutable snapshot of foundational memory.
    
    This is a VALUE OBJECT in DDD terminology - identified by its
    values, not by identity. Two FoundationalMemory instances with
    same values are considered equal.
    
    Design Decision: Frozen dataclass vs Pydantic BaseModel
    - Frozen dataclass: Zero runtime overhead, stdlib, hashable
    - Pydantic: Validation, serialization, but adds dependency
    
    Chose frozen dataclass for domain layer purity. Adapters
    can use Pydantic for I/O validation.
    """
    vision: str
    creator_preferences: Dict[str, Any]
    personality_traits: Dict[str, Any]
    limits: List[Limit]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0.0"  # Semantic versioning for cache invalidation
    
    def to_prompt_context(self, max_tokens: int = 1500) -> str:
        """
        Serializes memory to LLM-optimized prompt context.
        
        Token Budget Strategy:
        1. Limits (Priority 1) - Non-negotiable, always included
        2. Vision (Priority 2) - Core identity, truncated if needed
        3. Personality (Priority 3) - Nice-to-have, omitted if budget tight
        
        Token Estimation:
        Using rough heuristic: 1 token ≈ 4 characters (OpenAI tokenizer average)
        For production: use tiktoken library for accurate counting
        
        Args:
            max_tokens: Maximum tokens to allocate for memory context
            
        Returns:
            Formatted string ready for LLM system prompt
        """
        sections = []
        estimated_tokens = 0
        
        # Helper: Estimate tokens from text
        def estimate_tokens(text: str) -> int:
            return len(text) // 4
        
        # Helper: Add section if budget allows
        def try_add_section(title: str, content: str, priority: int) -> bool:
            nonlocal estimated_tokens
            section = f"{title}:\n{content}\n"
            tokens = estimate_tokens(section)
            
            if estimated_tokens + tokens <= max_tokens:
                sections.append(section)
                estimated_tokens += tokens
                return True
            return False
        
        # Priority 1: LIMITS (always included, critical for safety)
        if self.limits:
            limits_text = self._format_limits()
            try_add_section("LÍMITES ABSOLUTOS", limits_text, priority=1)
        
        # Priority 2: VISION (truncate if needed)
        if self.vision:
            vision_text = self.vision
            remaining_budget = max_tokens - estimated_tokens
            
            if estimate_tokens(vision_text) > remaining_budget:
                # Truncate intelligently at sentence boundary
                sentences = vision_text.split('. ')
                truncated = []
                for sentence in sentences:
                    if estimate_tokens('. '.join(truncated + [sentence])) < remaining_budget - 50:
                        truncated.append(sentence)
                    else:
                        break
                vision_text = '. '.join(truncated) + '...'
            
            try_add_section("VISIÓN", vision_text, priority=2)
        
        # Priority 3: PERSONALITY (optional)
        if self.personality_traits and estimated_tokens < max_tokens * 0.8:
            personality_text = self._format_personality()
            try_add_section("PERSONALIDAD", personality_text, priority=3)
        
        return "\n".join(sections)
    
    def _format_limits(self) -> str:
        """Formats limits in compact, scannable format."""
        if not self.limits:
            return "Sin límites definidos"
        
        formatted = []
        for limit in self.limits:
            examples_str = f" (ej: {', '.join(limit.examples[:2])})" if limit.examples else ""
            formatted.append(f"  • [{limit.type.value}] {limit.value}: {limit.context}{examples_str}")
        
        return "\n".join(formatted)
    
    def _format_personality(self) -> str:
        """Formats personality traits in compact format."""
        if not self.personality_traits:
            return "Sin traits definidos"
        
        return ", ".join(f"{k}={v}" for k, v in self.personality_traits.items())
    
    def check_violations(self, text: str) -> List[Limit]:
        """
        Checks text against all limits and returns violations.
        
        This implements "Memoria del No" validation logic.
        Returns empty list if no violations found.
        
        Performance: O(n*m) where n=len(limits), m=len(text)
        For large text: consider preprocessing (tokenization, indexing)
        """
        violations = []
        for limit in self.limits:
            if limit.matches(text):
                violations.append(limit)
        return violations
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes to dictionary for storage/transmission.
        
        Note: frozen dataclass doesn't have asdict() by default
        because it would return mutable dict. We explicitly construct
        immutable-friendly representation.
        """
        return {
            "vision": self.vision,
            "creator_preferences": self.creator_preferences,
            "personality_traits": self.personality_traits,
            "limits": [
                {
                    "type": limit.type.value,
                    "value": limit.value,
                    "context": limit.context,
                    "examples": limit.examples,
                    "created_at": limit.created_at.isoformat()
                }
                for limit in self.limits
            ],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "version": self.version
        }


class MemoryPort(Protocol):
    """
    Port (interface) for memory provider implementations.
    
    Using Protocol (PEP 544) instead of ABC for structural subtyping:
    - No explicit inheritance required
    - Duck typing with type safety
    - More Pythonic than Java-style interfaces
    
    Design Decision: Sync vs Async
    All methods are async to support:
    - Database I/O operations
    - Network calls (distributed memory)
    - Concurrent access patterns
    
    Even if current implementation is sync (SQLite), async interface
    future-proofs for Redis, PostgreSQL, etc.
    """
    
    async def get_foundational_memory(self) -> Optional[FoundationalMemory]:
        """
        Retrieves current foundational memory snapshot.
        
        Returns:
            FoundationalMemory if configured, None if not initialized
            
        Raises:
            MemoryUnavailableError: If backend is down but operation critical
            
        Implementation Notes:
        - MUST implement caching at adapter level
        - SHOULD use version-based cache invalidation
        - MAY return stale cache if backend unavailable (graceful degradation)
        """
        ...
    
    async def update_foundational_memory(
        self, 
        updates: Dict[str, Any]
    ) -> FoundationalMemory:
        """
        Updates specific fields of foundational memory.
        
        Implements partial update semantics (PATCH not PUT):
        - Only provided fields are updated
        - Unspecified fields remain unchanged
        - Returns updated snapshot
        
        Args:
            updates: Dictionary with fields to update
                    Valid keys: vision, creator_preferences, personality_traits
                    
        Returns:
            Updated FoundationalMemory snapshot
            
        Raises:
            ValueError: If updates contain invalid fields
            MemoryUnavailableError: If operation fails
        """
        ...
    
    async def add_limit(self, limit: Limit) -> FoundationalMemory:
        """
        Adds a new limit to foundational memory.
        
        Implements append-only semantics for auditability.
        To modify existing limit: add new version with updated context.
        
        Args:
            limit: Limit instance to add
            
        Returns:
            Updated FoundationalMemory snapshot
        """
        ...
    
    async def remove_limit(self, limit_value: str) -> FoundationalMemory:
        """
        Removes limit by its value.
        
        Args:
            limit_value: The value string of the limit to remove
            
        Returns:
            Updated FoundationalMemory snapshot
            
        Raises:
            ValueError: If limit not found
        """
        ...
    
    async def get_memory_version(self) -> str:
        """
        Returns current version string for cache invalidation.
        
        Implementation strategies:
        - Incremental counter (v1, v2, v3...)
        - Timestamp (2024-01-01T12:00:00Z)
        - Content hash (SHA256 of serialized memory)
        
        Returns:
            Version string (must be comparable/sortable)
        """
        ...


class MemoryUnavailableError(Exception):
    """
    Raised when memory backend is unreachable.
    
    This is a DOMAIN exception, not infrastructure.
    Domain logic can catch this to implement fallback strategies.
    """
    
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause  # Original exception for debugging


class MemoryValidationError(Exception):
    """
    Raised when memory data fails validation.
    
    Examples:
    - Invalid limit type
    - Missing required fields
    - Malformed data structure
    """
    pass


# Type aliases for clarity
MemorySnapshot = FoundationalMemory
LimitList = List[Limit]
