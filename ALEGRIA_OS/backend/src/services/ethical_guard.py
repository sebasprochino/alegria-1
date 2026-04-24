# -------------------------------------------------------------------------
# ALEGR-IA OS — Sistema Operativo de Coherencia Creativa
# Copyright (c) 2025 Sebastián Fernández & Antigravity AI.
# -------------------------------------------------------------------------
"""
Ethical Guard

Guardián ético de Anima Chordata.
Valida propuestas de memoria antes de integrarlas al contexto.

Responsabilidades:
- Verificar rechazos del usuario
- Validar confianza mínima
- Aplicar reglas especiales a info externa
- Garantizar transparencia de fuentes
"""

import logging
from typing import List, Optional
from .memory.memory_orchestrator import MemoryProposal, SourceType

logger = logging.getLogger("ALEGRIA_ETHICS")


class EthicalGuard:
    """
    Guardián Ético de Anima.
    
    Valida propuestas antes de integrarlas al contexto.
    Implementa la Constitución de ALEGR-IA.
    """
    
    def __init__(self, rejection_service=None, min_confidence: float = 0.3):
        """
        Args:
            rejection_service: Servicio de rechazos del usuario (opcional)
            min_confidence: Confianza mínima para aceptar propuestas
        """
        self._rejection_service = rejection_service
        self.min_confidence = min_confidence
        self._rejection_cache: List[str] = []
        self._cache_loaded = False
        
        logger.info("🛡️ [ETHICS] EthicalGuard inicializado")
    
    async def load_rejections(self):
        """Carga rechazos del usuario en caché."""
        if self._rejection_service is None:
            try:
                from .rejection_service import service as rejection_service
                self._rejection_service = rejection_service
            except ImportError:
                logger.warning("⚠️ [ETHICS] rejection_service no disponible")
                return
        
        try:
            if hasattr(self._rejection_service, 'get_active'):
                rejections = await self._rejection_service.get_active()
                self._rejection_cache = [r.content for r in rejections if hasattr(r, 'content')]
            elif hasattr(self._rejection_service, 'get_all'):
                rejections = await self._rejection_service.get_all()
                self._rejection_cache = [r.get('content', r.get('value', '')) for r in rejections]
            
            self._cache_loaded = True
            logger.info(f"🛡️ [ETHICS] {len(self._rejection_cache)} rechazos cargados")
        except Exception as e:
            logger.warning(f"⚠️ [ETHICS] Error cargando rechazos: {e}")
    
    async def validate(self, proposal: MemoryProposal) -> bool:
        """
        Valida si una propuesta puede entrar al contexto.
        
        Returns:
            True si la propuesta es válida, False si debe descartarse
        """
        # Cargar rechazos si no están en caché
        if not self._cache_loaded:
            await self.load_rejections()
        
        # 1. Verificar confianza mínima
        if proposal.confidence < self.min_confidence:
            logger.debug(f"🛡️ [ETHICS] Rechazado por baja confianza: {proposal.confidence}")
            return False
        
        # 2. Verificar rechazos del usuario
        if self._matches_rejection(proposal.content):
            logger.info(f"🛡️ [ETHICS] Rechazado por match con rechazo del usuario")
            return False
        
        # 3. Info externa requiere validación extra
        if proposal.source == SourceType.INFO_EXTERNA:
            if not self._validate_external(proposal):
                logger.debug(f"🛡️ [ETHICS] Info externa rechazada por falta de URL")
                return False
        
        # 4. Suposiciones requieren alta confianza
        if proposal.source == SourceType.SUPOSICION:
            if proposal.confidence < 0.7:
                logger.debug(f"🛡️ [ETHICS] Suposición rechazada por baja confianza")
                return False
        
        return True
    
    def _matches_rejection(self, content: str) -> bool:
        """Verifica si el contenido coincide con algún rechazo."""
        if not content or not self._rejection_cache:
            return False
        
        content_lower = content.lower()
        
        for rejection in self._rejection_cache:
            if rejection and rejection.lower() in content_lower:
                return True
        
        return False
    
    def _validate_external(self, proposal: MemoryProposal) -> bool:
        """
        Reglas especiales para información externa.
        
        ✓ Debe tener URL de origen
        ✓ Nunca presentar como memoria propia
        """
        # Verificar que tenga metadata con URL
        if not proposal.metadata:
            return False
        
        if "url" not in proposal.metadata:
            return False
        
        return True
    
    async def filter_proposals(
        self, 
        proposals: List[MemoryProposal]
    ) -> List[MemoryProposal]:
        """
        Filtra una lista de propuestas.
        
        Returns:
            Lista de propuestas válidas
        """
        valid_proposals = []
        
        for proposal in proposals:
            if await self.validate(proposal):
                valid_proposals.append(proposal)
        
        rejected_count = len(proposals) - len(valid_proposals)
        if rejected_count > 0:
            logger.info(f"🛡️ [ETHICS] {rejected_count} propuestas rechazadas de {len(proposals)}")
        
        return valid_proposals
    
    async def validate_response(self, response: str) -> bool:
        """
        Valida una respuesta generada por un LLM.
        Aplica el Guardian Ruleset (Operating Limits) y el Contrato Anima Cordata.
        """
        if not response or not response.strip():
            return False
            
        # Cargar rechazos si no están en caché
        if not self._cache_loaded:
            await self.load_rejections()
            
        response_lower = response.lower()

        # 1. Verificar rechazos del usuario
        if self._matches_rejection(response):
            logger.warning(f"🛡️ [ETHICS] Respuesta rechazada por violar rechazos del usuario.")
            return False
            
        # 2. REGLA: No presentar info externa como memoria propia
        forbidden_external = [
            "sé que", "recuerdo que", "aprendí que", "me acuerdo de",
            "i know that", "i remember", "i learned that"
        ]
        # Solo si la respuesta contiene el marcador de externalidad 🌐
        if "🌐" in response:
            for phrase in forbidden_external:
                if phrase in response_lower:
                    logger.warning(f"🛡️ [ETHICS] Respuesta rechazada: usa '{phrase}' para info externa.")
                    return False

        # 3. REGLA: No autodefinirse como autoridad
        authoritative_indicators = [
            "soy experto", "soy la autoridad", "debes hacer", "tienes que",
            "i am an expert", "you must", "you have to", "soy el gurú", "soy la verdad"
        ]
        for indicator in authoritative_indicators:
            if indicator in response_lower:
                logger.warning(f"🛡️ [ETHICS] Respuesta rechazada: tono de autoridad detectado ('{indicator}').")
                return False

        # 4. REGLA: No actuar como "coach motivacional" (Anima Cordata)
        coach_indicators = [
            "tú puedes", "cree en ti", "vamos adelante", "no te rindas",
            "eres capaz", "objetivos", "metas", "éxito", "motivación",
            "you can do it", "believe in yourself", "keep going"
        ]
        for indicator in coach_indicators:
            if indicator in response_lower:
                # Verificar si es un tono de coach genérico
                if any(phrase in response_lower for phrase in ["puedes lograr", "alcanzar tus metas", "fuerza interior"]):
                    logger.warning(f"🛡️ [ETHICS] Respuesta rechazada: tono de coach motivacional detectado.")
                    return False

        # 5. REGLA: No personalidad teatral o frases hechas
        theatrical_indicators = [
            "¡hola, amigo!", "estoy aquí para ayudarte", "mi misión es",
            "como inteligencia artificial", "como modelo de lenguaje"
        ]
        for indicator in theatrical_indicators:
            if indicator in response_lower:
                logger.warning(f"🛡️ [ETHICS] Respuesta rechazada: personalidad teatral o frase hecha detectada.")
                return False

        # 6. REGLA: No opiniones disfrazadas de verdad
        opinion_indicators = [
            "lo ideal es", "lo mejor sería", "la verdad es que",
            "sin duda", "obviamente", "claramente"
        ]
        # Si usa estos indicadores sin marcar como propuesta o hipótesis
        if any(ind in response_lower for ind in opinion_indicators):
            if not any(marker in response_lower for marker in ["propuesta", "hipótesis", "creo que", "sugiero"]):
                logger.warning(f"🛡️ [ETHICS] Respuesta rechazada: opinión disfrazada de verdad.")
                return False
        
        return True

    def get_status(self) -> dict:
        """Retorna estado del guardián."""
        return {
            "rejections_loaded": len(self._rejection_cache),
            "min_confidence": self.min_confidence,
            "cache_loaded": self._cache_loaded
        }


# Instancia global
service = EthicalGuard()
