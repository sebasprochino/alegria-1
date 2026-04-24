# -------------------------------------------------------------------------
# ALEGR-IA OS — Sistema Operativo de Coherencia Creativa
# Copyright (c) 2025 Sebastián Fernández & Antigravity AI.
# -------------------------------------------------------------------------
"""
User Lexical Model (ULM)

Modela CÓMO se expresa el Director, no qué sabe.
Permite que Anima devuelva ideas usando la estructura lingüística del usuario.

Principios:
- Aprende patrones, NO contenido
- No inventa estilo
- No imita voces externas
- No reescribe hechos
"""

import json
import os
import re
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime
from collections import Counter

logger = logging.getLogger("ALEGRIA_LEXICON")


@dataclass
class LexicalPatterns:
    """Patrones lingüísticos del Director."""
    dominant_verbs: List[str] = field(default_factory=list)
    connectors: List[str] = field(default_factory=list)
    avg_sentence_length: float = 15.0
    emphasis_patterns: List[str] = field(default_factory=list)
    semantic_keywords: List[str] = field(default_factory=list)
    detected_tone: str = "sereno"
    total_observations: int = 0
    last_updated: str = ""
    consent_granted: bool = False  # Regla: Aprender requiere consentimiento
    
    # Frecuencias acumuladas
    verb_frequencies: Dict[str, int] = field(default_factory=dict)
    connector_frequencies: Dict[str, int] = field(default_factory=dict)
    keyword_frequencies: Dict[str, int] = field(default_factory=dict)

    # Nuevos campos requeridos
    preferred_terms: List[str] = field(default_factory=list)
    common_structures: List[str] = field(default_factory=list)
    technical_level: str = "medio" # bajo | medio | alto
    forbidden_tone: List[str] = field(default_factory=list)


@dataclass
class Message:
    """Mensaje para observación léxica."""
    role: str  # "user" o "anima"
    content: str


class UserLexicon:
    """
    Modelo Léxico del Director.
    
    Aprende patrones lingüísticos del usuario para que Anima
    pueda expresarse de forma coherente con su estilo.
    """
    
    # Conectores comunes en español
    KNOWN_CONNECTORS = [
        "pero", "sin embargo", "aunque", "además", "también",
        "por eso", "entonces", "así que", "porque", "ya que",
        "es decir", "o sea", "por ejemplo", "de hecho", "en realidad",
        "básicamente", "principalmente", "obviamente", "claramente"
    ]
    
    # Patrones de énfasis
    EMPHASIS_PATTERNS = [
        r"\*\*[^*]+\*\*",  # **texto**
        r"__[^_]+__",      # __texto__
        r"MAYÚSCULAS",     # Palabras en mayúsculas
        r"!!+",            # Múltiples signos
        r"\?{2,}",         # Múltiples interrogaciones
    ]
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            # Path robusto hacia backend/storage
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Subir desde src/services/memory hasta backend/
            base_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            storage_path = os.path.join(base_dir, "storage", "user_lexicon.json")
        
        self.storage_path = storage_path
        self.patterns = self._load_or_create()
        logger.info(f"[LEXICON] Inicializado en {self.storage_path} con {self.patterns.total_observations} observaciones")
    
    def _load_or_create(self) -> LexicalPatterns:
        """Carga patrones existentes o crea nuevos."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return LexicalPatterns(**data)
            except Exception as e:
                logger.warning(f"⚠️ [LEXICON] Error cargando: {e}")
        
        return LexicalPatterns()
    
    def _persist(self):
        """Guarda patrones a disco."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self.patterns), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ [LEXICON] Error guardando: {e}")
    
    def grant_consent(self):
        """Otorga consentimiento para aprender patrones."""
        self.patterns.consent_granted = True
        self._persist()
        logger.info("📝 [LEXICON] Consentimiento otorgado por el usuario")

    def observe(self, message: Message):
        """
        Aprende patrones del Director.
        Solo procesa mensajes del usuario si hay consentimiento.
        """
        if not self.patterns.consent_granted:
            return
            
        if message.role != "user":
            return
        
        content = message.content
        if not content or len(content) < 10:
            return
        
        # Extraer y acumular patrones
        self._update_verbs(content)
        self._update_connectors(content)
        self._update_sentence_length(content)
        self._update_emphasis(content)
        self._update_keywords(content)
        self._detect_tone(content)
        
        self.patterns.total_observations += 1
        self.patterns.last_updated = datetime.utcnow().isoformat()
        
        # Actualizar campos de alto nivel
        self.patterns.preferred_terms = self.patterns.semantic_keywords[:10]
        self.patterns.common_structures = self.patterns.connectors[:5] + self.patterns.emphasis_patterns[:3]

        # Persistir cada 5 observaciones
        if self.patterns.total_observations % 5 == 0:
            self._persist()
            logger.info(f"📝 [LEXICON] Guardado ({self.patterns.total_observations} observaciones)")
    
    def _update_verbs(self, content: str):
        """Extrae y actualiza verbos dominantes."""
        # Heurística simple: palabras que terminan en -ar, -er, -ir, -ando, -iendo
        words = content.lower().split()
        verb_patterns = [
            r'\w+ar\b', r'\w+er\b', r'\w+ir\b',
            r'\w+ando\b', r'\w+iendo\b',
            r'\w+ado\b', r'\w+ido\b'
        ]
        
        for word in words:
            for pattern in verb_patterns:
                if re.match(pattern, word) and len(word) > 3:
                    self.patterns.verb_frequencies[word] = \
                        self.patterns.verb_frequencies.get(word, 0) + 1
        
        # Top 10 verbos
        sorted_verbs = sorted(
            self.patterns.verb_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        self.patterns.dominant_verbs = [v[0] for v in sorted_verbs[:10]]
    
    def _update_connectors(self, content: str):
        """Detecta conectores usados frecuentemente."""
        content_lower = content.lower()
        
        for connector in self.KNOWN_CONNECTORS:
            if connector in content_lower:
                self.patterns.connector_frequencies[connector] = \
                    self.patterns.connector_frequencies.get(connector, 0) + 1
        
        # Top 5 conectores
        sorted_connectors = sorted(
            self.patterns.connector_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        self.patterns.connectors = [c[0] for c in sorted_connectors[:5]]
    
    def _update_sentence_length(self, content: str):
        """Calcula longitud promedio de frases."""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            current_avg = sum(lengths) / len(lengths)
            
            # Promedio móvil
            n = self.patterns.total_observations + 1
            old_avg = self.patterns.avg_sentence_length
            self.patterns.avg_sentence_length = (old_avg * (n-1) + current_avg) / n
    
    def _update_emphasis(self, content: str):
        """Detecta patrones de énfasis."""
        for pattern in self.EMPHASIS_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    if match not in self.patterns.emphasis_patterns:
                        self.patterns.emphasis_patterns.append(match)
        
        # Limitar a 20 patrones
        self.patterns.emphasis_patterns = self.patterns.emphasis_patterns[-20:]
    
    def _update_keywords(self, content: str):
        """Extrae palabras con carga semántica."""
        # Palabras largas (>6 chars) que no son stopwords comunes
        stopwords = {
            "porque", "también", "cuando", "donde", "como", "para",
            "sobre", "entre", "desde", "hasta", "durante", "mediante"
        }
        
        words = content.lower().split()
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 6 and clean_word not in stopwords:
                self.patterns.keyword_frequencies[clean_word] = \
                    self.patterns.keyword_frequencies.get(clean_word, 0) + 1
        
        # Top 15 keywords
        sorted_keywords = sorted(
            self.patterns.keyword_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        self.patterns.semantic_keywords = [k[0] for k in sorted_keywords[:15]]
    
    def _detect_tone(self, content: str):
        """Detecta tono general del mensaje."""
        content_lower = content.lower()
        
        # Indicadores de tono
        formal_indicators = ["usted", "podría", "sería", "agradecer"]
        informal_indicators = ["dale", "onda", "piola", "tranqui", "jaja"]
        intense_indicators = ["!", "urgente", "crítico", "importante"]
        calm_indicators = ["tranquilo", "sereno", "calma", "relax"]
        
        formal_score = sum(1 for i in formal_indicators if i in content_lower)
        informal_score = sum(1 for i in informal_indicators if i in content_lower)
        intense_score = sum(1 for i in intense_indicators if i in content_lower)
        calm_score = sum(1 for i in calm_indicators if i in content_lower)
        
        if calm_score > 0 or (intense_score == 0 and formal_score == 0):
            self.patterns.detected_tone = "sereno"
        elif intense_score > calm_score:
            self.patterns.detected_tone = "intenso"
        elif formal_score > informal_score:
            self.patterns.detected_tone = "formal"
        else:
            self.patterns.detected_tone = "casual"

        # Detectar nivel técnico
        tech_terms = [
            "api", "endpoint", "json", "python", "react", "backend", "frontend",
            "deploy", "server", "database", "interface", "module", "class",
            "function", "variable", "const", "await", "async"
        ]
        tech_score = sum(1 for t in tech_terms if t in content_lower)
        
        if tech_score > 3:
            self.patterns.technical_level = "alto"
        elif tech_score > 0:
            self.patterns.technical_level = "medio"
        else:
            self.patterns.technical_level = "bajo"
    
    def rephrase(self, text: str) -> str:
        """
        Expresa el texto usando el léxico del Director.
        
        NOTA: Esta es una implementación básica.
        En producción, usaría el LLM para reformular.
        """
        # Por ahora, retornamos el texto sin cambios
        # La transformación real se hará via prompt al LLM
        return text
    
    def get_style_prompt(self, light: bool = True) -> str:
        """
        Genera instrucciones de alineación estructural para el LLM.
        En modo 'light' (por defecto), se enfoca en la dirección conceptual, 
        no en la mímica lingüística.
        """
        if self.patterns.total_observations < 3:
            return ""

        parts = [
            "\nDIRECCIÓN CONCEPTUAL DEL DIRECTOR (Contexto de Alineación):",
            f"- Foco de Intensidad: {self.patterns.detected_tone}",
            f"- Densidad de Pensamiento: {'Estructurada' if self.patterns.avg_sentence_length > 15 else 'Ágil'}",
        ]

        # Inyección sutil de keywords como 'conceptos ancla'
        if self.patterns.semantic_keywords:
            anchors = ", ".join(self.patterns.semantic_keywords[:3])
            parts.append(f"- Conceptos Ancla: {anchors}")

        # Guía de nivel técnico
        parts.append(f"- Nivel de Abstracción Técnica: {self.patterns.technical_level}")

        if not light:
            if self.patterns.dominant_verbs:
                parts.append(f"- Ejes de Acción: {', '.join(self.patterns.dominant_verbs[:3])}")
        
        parts.append("\nINSTRUCCIÓN: Mantén tu propia voz como Anima, pero alinea tu dirección de pensamiento con esta estructura. Prioriza la claridad y la coherencia sistémica.")

        return "\n".join(parts)
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas del modelo léxico."""
        return {
            "total_observations": self.patterns.total_observations,
            "last_updated": self.patterns.last_updated,
            "detected_tone": self.patterns.detected_tone,
            "avg_sentence_length": round(self.patterns.avg_sentence_length, 1),
            "top_verbs": self.patterns.dominant_verbs[:5],
            "top_connectors": self.patterns.connectors[:3],
            "top_keywords": self.patterns.semantic_keywords[:5]
        }


# Instancia global del servicio
service = UserLexicon()

def get_lexicon():
    """Provider para el Sistema de Memoria Léxica."""
    return service
