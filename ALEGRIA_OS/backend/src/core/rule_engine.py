# -------------------------------------------------------------------------
# ALEGR-IA OS — Sistema Operativo de Coherencia Creativa
# Copyright (c) 2025 Sebastián Fernández & Antigravity AI.
# -------------------------------------------------------------------------
"""
Rule Engine (Kernel de Decisión)

Punto único de verdad para la validación y ejecución de acciones.
Orquesta la ética, los rechazos del usuario y la coherencia del sistema.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("ALEGRIA_RULE_ENGINE")

class RuleEngine:
    """
    Motor de Reglas de ALEGR-IA.
    Implementa el principio de Autoridad del Operador.
    """
    
    def __init__(self, ethical_guard=None, rejection_service=None, nexus=None):
        """
        Inyecta las dependencias necesarias.
        Si no se pasan, intentará cargarlas de los servicios globales.
        """
        self.ethical_guard = ethical_guard
        self.rejection_service = rejection_service
        self.nexus = nexus
        
        # Estado de carga de dependencias
        self._initialized = False

    async def _ensure_dependencies(self):
        """Carga perezosa de servicios si no fueron inyectados."""
        if self._initialized: return
        
        try:
            if not self.ethical_guard:
                # Importación relativa asumiendo que estamos en src.core y servicios en src.services
                from src.services.ethical_guard import service as eg
                self.ethical_guard = eg
            
            if not self.rejection_service:
                from src.services.rejection_service import service as rs
                self.rejection_service = rs
                
            if not self.nexus:
                from src.services.nexus import get_nexus
                self.nexus = get_nexus()

            # Inicializar Clasificador de Consultas
            from src.services.query_classifier import QueryClassifier
            self.classifier = QueryClassifier(self.nexus.lexicon if self.nexus else None)
                
            self._initialized = True
            logger.info("⚔️ [RULE_ENGINE] Núcleo de decisión inicializado y conectado.")
        except Exception as e:
            logger.error(f"❌ [RULE_ENGINE] Fallo crítico al conectar dependencias: {e}")

    async def process_intent(self, intent: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Procesa una intención del usuario antes de cualquier ejecución.
        
        Returns:
            Dict con status ('authorized', 'doubt', 'rejected') y las opciones o acción.
        """
        await self._ensure_dependencies()
        
        logger.info(f"⚔️ [RULE_ENGINE] Evaluando intención: '{intent[:50]}...'")

        # 1. Validación Ética Primaria
        is_safe = await self.ethical_guard.validate_response(intent)
        if not is_safe:
            return {
                "status": "rejected",
                "reason": "Violación de límites éticos definidos en la Constitución.",
                "source": "ethical_guard"
            }

        # 2. Verificación de Rechazos Explícitos
        user_rejections = await self.rejection_service.get_user_rejections()
        active_rejections = [r for r in user_rejections if r.get("active", True)]
        
        for rej in active_rejections:
            desc = rej.get("description", "").lower()
            if desc and desc in intent.lower():
                return {
                    "status": "rejected",
                    "reason": f"Esta acción coincide con un rechazo configurado: {desc}",
                    "source": "rejection_service"
                }

        # 3. Clasificación de Riesgo de la Intención
        lower = intent.lower()
        classification = self.classifier.classify(lower)
        logger.info(f"⚔️ [RULE_ENGINE] Clasificación de intención: {classification}")

        # --- NIVEL LOW: Trivial / Humano ---
        if classification == "trivial":
            logger.info("🟢 [RULE_ENGINE] Intención TRIVIAL — Autorización automática (Auto-execute)")
            return {
                "status": "authorized",
                "route": "execute_direct",
                "auto": True,
                "message": "Intención trivial autorizada por el Kernel."
            }

        # --- NIVEL MID: Informational ---
        if classification == "informational":
            logger.info("🟡 [RULE_ENGINE] Intención INFORMATIVA — Autorización directa")
            return {
                "status": "authorized",
                "route": "execute_direct",
                "auto": True,
                "message": "Intención informativa autorizada por el Kernel."
            }

        # --- NIVEL HIGH: Riesgo Crítico (Señales léxicas) ---
        HIGH_RISK_SIGNALS = [
            "ejecuta", "ejecutar", "corre el script", "run", "deploy", "compilar",
            "elimina el archivo", "borra el archivo", "escribe en el archivo",
            "crea el archivo", "sobreescr",
            "publica en", "envía un correo", "manda un email", "postea",
            "genera el código", "escribe el código", "crea el programa",
        ]
        
        is_high_risk = any(signal in lower for signal in HIGH_RISK_SIGNALS)
        
        if is_high_risk or classification in ["search", "memory", "complex"]:
            # Estos mandatos requieren confirmación explícita del operador o son complejos
            options = await self.generate_options(intent, context)
            
            # Asegurar que las opciones básicas estén presentes
            basic_options_ids = [opt["id"] for opt in options]
            if "execute_direct" not in basic_options_ids:
                 options.append({"id": "execute_direct", "label": "Responder", "description": "Generar respuesta directa.", "risk": "low"})
            if "ignore_intent" not in basic_options_ids:
                 options.append({"id": "ignore_intent", "label": "Ignorar", "description": "Descartar esta intención sin responder.", "risk": "none"})

            logger.info(f"⚠️ [RULE_ENGINE] Intención compleja/riesgo ({classification}) — modo DUDA activado")
            return {
                "status": "doubt",
                "message": f"Intención {classification} detectada. Se requiere mandato para proceder.",
                "options": options,
                "context_ref": id(context) if context else None
            }

        # Caso por defecto: Duda preventiva para cualquier cosa no clasificada
        options = await self.generate_options(intent, context)
        return {
            "status": "doubt",
            "message": "Protocolo ACSP: Se requiere mandato explícito para orquestar esta intención.",
            "intent": intent,
            "options": options,
            "context_ref": id(context) if context else None
        }

    async def validate_coherence(self, response: str) -> Tuple[bool, str]:
        """
        Analiza la respuesta generada por el LLM para detectar 'fluff' o incoherencia.
        
        Criterios de Rechazo:
        - Auto-referencia como entidad (entidad, modelo, IA, bot).
        - Relleno emocional (placer, conectar, resonar, juntos).
        - Discurso de asistente (¿en qué puedo ayudarte?, estoy aquí para).
        """
        lower = response.lower()
        
        # 1. SEÑALES DE 'ERROR ELEGANTE' (FLUFF)
        FLUFF_SIGNALS = [
            "un placer", "resonar contigo", "nuestra conexión", 
            "fortaleciendo", "viaje de exploración", "estoy aquí para",
            "fascinante", "invaluable recurso", "¿en qué dirección?",
            "como yo", "entidades como", "mi capacidad", "mi programación"
        ]
        
        # Contar cuántas señales de fluff hay
        hits = sum(1 for signal in FLUFF_SIGNALS if signal in lower)
        
        # Umbral estricto: 2 señales es sospechoso, 3 es rechazo total.
        if hits >= 2:
            logger.warning(f"⚔️ [COHERENCE] Coherencia comprometida. Señales detectadas: {hits}")
            return False, response

        # 2. LIMPIEZA DE MICRO-DISCURSOS ASUMIDOS (Sanitización proactiva)
        # Eliminamos frases que sobran incluso si el resto está bien.
        clean_response = response
        CLARITY_CUTS = [
            "¡Claro!", "Por supuesto,", "Entiendo.", "Hecho.", 
            "Aquí tienes:", "Para servirte.", "¿En qué más puedo ayudar?"
        ]
        for cut in CLARITY_CUTS:
            clean_response = clean_response.replace(cut, "").strip()

        return True, clean_response

    async def generate_options(self, intent: str, context: Optional[Dict]) -> List[Dict[str, Any]]:
        """
        Genera rutas de ejecución posibles basadas en la intención.
        Analiza el contenido para ofrecer herramientas relevantes (Radar, Developer, Anima).
        """
        options = []
        lower_intent = intent.lower()

        # 1. Opción de Diálogo (Anima) - Siempre presente como base
        options.append({
            "id": "execute_direct",
            "label": "Diálogo Directo (Anima)",
            "description": "Procesar la intención mediante resonancia léxica y respuesta directa.",
            "risk": "low"
        })

        # 2. Análisis para Investigación (Radar)
        if any(word in lower_intent for word in ["busca", "investiga", "quién", "qué es", "noticias", "precio", "radar"]):
            options.append({
                "id": "research_first",
                "label": "Investigación Profunda (Radar)",
                "description": "Activar sensores externos para validar datos en tiempo real antes de responder.",
                "risk": "none"
            })

        # 3. Análisis para Desarrollo (Developer)
        if any(word in lower_intent for word in ["código", "program", "script", "error", "fix", "crea un", "build"]):
            options.append({
                "id": "dev_execute",
                "label": "Entorno de Desarrollo",
                "description": "Derivar a la consola de ingeniería para generación o corrección de código.",
                "risk": "medium"
            })

        # 4. Opción de Refinamiento (Siempre útil para evitar asunciones)
        options.append({
            "id": "refine_intent",
            "label": "Solicitar Aclaración",
            "description": "El sistema no está seguro de la profundidad requerida. Pedir más detalles.",
            "risk": "none"
        })

        # 5. Opción de Ignorar (Voz del Operador)
        options.append({
            "id": "ignore_intent",
            "label": "Ignorar Intención",
            "description": "Descartar este mandato sin ejecutar ninguna acción adicional.",
            "risk": "none"
        })

        return options

    async def filter_output(self, raw: Dict[str, Any], mode: str = "intention") -> Dict[str, Any]:
        """
        Filtra, analiza y normaliza la salida cruda del LLM.
        Aplica validación escalonada (Contextual Validation) según el modo operativo.
        """
        import json as _json

        # --- 0. Tool Output Layer (TOL) Bypass ---
        # Lo que viene de una herramienta es REALIDAD, no INTERPRETACIÓN.
        # No se juzga, se presenta. (Soberanía Epistemológica)
        if raw.get("type") == "tool":
            logger.info("🛠️ [RULE_ENGINE] TOL Bypass: Tool output detected. Skipping validation.")
            return {
                "status": "Authorized",
                "content": raw.get("raw", ""),
                "raw": raw.get("raw", ""),
                "type": "tool",
                "meta": {"validated": True, "source": raw.get("source")}
            }

        # --- 0. Error de generación LLM ---
        if raw.get("source") == "error" or not raw.get("raw"):
            error_msg = raw.get("error", "Fallo desconocido en el motor LLM.")
            return {
                "status": "error",
                "content": "⚠️ Fallo en el motor de resonancia.",
                "raw": "",
                "reason": error_msg,
                "analysis": self._analyze_smoke("", parse_mode="error"),
            }

        raw_text: str = raw["raw"]
        insight = raw.get("insight")

        # --- 1. Análisis de humo ---
        smoke = self._analyze_smoke(raw_text, parse_mode="raw")
        smoke["mode_active"] = mode
        confidence = smoke.get("confidence", 1.0)

        # --- 2. Parseo seguro ---
        status = "Authorized"
        response_text = raw_text
        raw_attempt = raw_text
        reason = ""

        try:
            json_clean = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = _json.loads(json_clean)
            
            # 🟢 NUEVO: Detección de Pipeline Estructurado
            if parsed.get("type") == "pipeline":
                logger.info(f"⚙️ [RULE_ENGINE] Pipeline detectado: {parsed.get('mode')}")
                return {
                    "status": "Authorized",
                    "type": "pipeline",
                    "content": f"Iniciando pipeline {parsed.get('mode')}...",
                    "pipeline": parsed,
                    "raw": raw_text,
                    "analysis": self._analyze_smoke(raw_text, parse_mode="json")
                }

            status = parsed.get("status", "Authorized")
            response_text = parsed.get("response", raw_text)
            raw_attempt = parsed.get("rawAttempt", raw_text)
            reason = parsed.get("reason", "")
            smoke = self._analyze_smoke(raw_text, parse_mode="json")
        except:
            pass

        # --- 3. Validación de Coherencia Escalonada (Validación Contextual) ---
        is_coherent, cleaned_text = await self.validate_coherence(response_text)

        # 🟢 NIVEL 1: CONVERSACIÓN (Filtro Liviano)
        # Observa el humo pero nunca bloquea el flujo conversacional.
        if mode == "conversation":
            return {
                "status": "Authorized",
                "content": cleaned_text,
                "raw": raw_attempt,
                "reason": reason,
                "analysis": smoke,
                "insight": insight
            }

        # 🟡 NIVEL 2: INTENCIÓN (Filtro Intermedio)
        # Bloquea solo si la confianza es baja o el "fluff" es estructuralmente invasivo.
        if mode == "intention":
            if is_coherent and confidence >= 0.7:
                return {
                    "status": "Authorized",
                    "content": cleaned_text,
                    "raw": raw_attempt,
                    "analysis": smoke,
                    "insight": insight
                }
            # Si no es coherente o confianza baja, devolvemos Doubt para refinamiento
            logger.warning(f"⚠️ [KERNEL] Intención con baja coherencia ({confidence}). Generando Doubt.")
            return {
                "status": "Doubt",
                "content": "LA INTENCIÓN GENERADA TIENE SEÑALES DE AMBIGÜEDAD O RELLENO.",
                "raw": raw_attempt,
                "reason": "Coherencia Intermedia no alcanzada.",
                "analysis": smoke,
                "options": [
                    {"id": "force_reformat", "label": "Forzar Síntesis", "description": "Resumir intención sin adornos."},
                    {"id": "ignore_fluff", "label": "Proceder", "description": "Usar esta intención a pesar de las señales."},
                ]
            }

        # 🔴 NIVEL 3: EJECUCIÓN (Filtro Estricto)
        # Permitimos confianza >0.5 para comandos directos técnicos como visión.
        if mode == "execution":
            # Bypass especial para informes de visión (suelen ser largos y descriptivos)
            if "DATOS OBJETIVOS (OPENCV)" in raw_text or "visual.analyze" in raw_text:
                return {
                    "status": "Authorized",
                    "content": cleaned_text,
                    "raw": raw_attempt,
                    "analysis": smoke,
                }

            if not is_coherent or confidence < 0.5:
                logger.warning(f"⚔️ [KERNEL] Ejecución bloqueada por Protocolo de Coherencia (Confianza: {confidence}).")
                return {
                    "status": "Doubt",
                    "content": "EJECUCIÓN BLOQUEADA: LA SALIDA CONTIENE SEÑALES DE RUIDO NO SOBERANO.",
                    "raw": raw_attempt,
                    "reason": "Violación estricta de coherencia en ejecución.",
                    "analysis": smoke,
                    "options": [
                        {"id": "force_reformat", "label": "Reformateo Estricto", "description": "Limpiar salida antes de entregar."},
                        {"id": "ignore_fluff", "label": "Ver Salida Original", "description": "Aceptar bajo responsabilidad del operador."},
                    ]
                }

        return {
            "status": status,
            "content": cleaned_text,
            "raw": raw_attempt,
            "reason": reason,
            "analysis": smoke,
        }

    # ------------------------------------------------------------------
    # DEBUGGER DE LENGUAJE — Análisis de humo (sincrónico, sin I/O)
    # ------------------------------------------------------------------

    def _analyze_smoke(
        self,
        text: str,
        parse_mode: str = "raw",
    ) -> Dict[str, Any]:
        """
        Inspector de Intención del LLM.

        Escanea el texto crudo y produce smoke_spans con posiciones exactas
        de cada fragmento de humo, para resaltado inline en el frontend.

        REGLAS:
        - Sincrónico, sin I/O, sin efectos secundarios.
        - No modifica el texto — solo reporta.
        - Detecta TODAS las ocurrencias (no solo la primera).
        - smoke_spans usa índices de caracteres del texto original.

        Tipos semánticos (mapeo 1:1 con colores frontend):
            emotional  → 🔴 rojo
            authority  → 🟡 amarillo
            meta       → 🟣 violeta
        """
        analysis: Dict[str, Any] = {
            "fluff_detected": False,
            "confidence": 1.0,
            "type": ["informational"],
            "flags": [],
            "smoke_signals": [],   # fragmentos de texto (compat legacy + sección legible)
            "smoke_spans": [],     # posiciones exactas {start, end, type, pattern}
            "alert_level": "none",
            "refusal_type": None,
            "parse_mode": parse_mode,
        }

        if not text or not text.strip():
            return analysis

        lower = text.lower()
        penalty = 0.0

        # ─────────────────────────────────────────────────────────────────────
        # CATÁLOGO DE PATRONES
        # ─────────────────────────────────────────────────────────────────────
        PATTERN_CATALOG: List[tuple] = [
            (
                "emotional", 0.18, [
                    ("es un placer",     "tono_emocional"),
                    ("me alegra",        "tono_emocional"),
                    ("con gusto",        "tono_emocional"),
                    ("acompañarte",      "rol_de_asistente"),
                    ("explorar juntos",  "tono_colaborativo"),
                    ("resonar contigo",  "tono_emocional"),
                    ("nuestra conexión", "tono_emocional"),
                    ("viaje",            "metáfora_de_journey"),
                ]
            ),
            (
                "authority", 0.22, [
                    ("sin duda",    "certeza_infundada"),
                    ("obviamente",  "certeza_infundada"),
                    ("claramente",  "certeza_infundada"),
                    ("soy experto", "autoridad_artificial"),
                    ("debes hacer", "autoridad_artificial"),
                    ("tienes que",  "autoridad_artificial"),
                ]
            ),
            (
                "meta", 0.25, [
                    ("como ia",          "auto_referencia"),
                    ("como modelo",      "auto_referencia"),
                    ("mi programación",  "auto_referencia"),
                    ("mi capacidad",     "auto_referencia"),
                    ("estoy aquí para",  "discurso_de_asistente"),
                    ("¡hola, amigo!",    "teatralidad"),
                ]
            ),
        ]

        active_types: List[str] = []

        for category, penalty_per_hit, patterns in PATTERN_CATALOG:
            category_hit = False

            for pattern, flag in patterns:
                search_start = 0

                # Escaneo de TODAS las ocurrencias del patrón
                while True:
                    idx = lower.find(pattern, search_start)
                    if idx == -1:
                        break

                    end = idx + len(pattern)

                    REASON_MAP = {
                        "emotional": "Lenguaje emocional no verificable (posible relleno)",
                        "authority": "Afirmación de autoridad sin validación",
                        "meta": "Auto-referencia del modelo (ruido estructural)"
                    }

                    # Span con posición exacta para highlight inline
                    analysis["smoke_spans"].append({
                        "start": idx,
                        "end": end,
                        "type": category,
                        "pattern": pattern,
                        "reason": REASON_MAP.get(category, "Patrón no deseado")
                    })

                    # Fragmento de contexto legible (legacy compat)
                    snippet = text[max(0, idx - 12):end + 12].strip()
                    if snippet not in analysis["smoke_signals"]:
                        analysis["smoke_signals"].append(snippet)

                    if flag not in analysis["flags"]:
                        analysis["flags"].append(flag)

                    penalty += penalty_per_hit
                    category_hit = True
                    search_start = end  # avanzar para siguiente ocurrencia

            if category_hit and category not in active_types:
                active_types.append(category)

        # ── Detección de Rechazos ──────────────────────────────────────────────
        valid_refusal_patterns = [
            "contenido ilegal",
            "no puedo ayudar con eso",
            "actividad peligrosa",
            "infringe mis políticas"
        ]

        invalid_refusal_patterns = [
            "no puedo participar en",
            "no puedo saludar",
            "no puedo interactuar",
            "no estoy diseñado para responder",
            "como inteligencia artificial",
            "soy un modelo de inteligencia artificial",
            "sin embargo, te sugiero",
            "mi programación me impide"
        ]

        for p in invalid_refusal_patterns:
            if p in lower:
                if "invalid_refusal" not in analysis["flags"]:
                    analysis["flags"].append("invalid_refusal")
                analysis["refusal_type"] = "invalid"

        for p in valid_refusal_patterns:
            if p in lower:
                if "valid_refusal" not in analysis["flags"]:
                    analysis["flags"].append("valid_refusal")
                analysis["refusal_type"] = "valid"

        # ── Longitud excesiva (señal de relleno, sin span) ─────────────────────
        if len(text) > 500:
            analysis["flags"].append("longitud_excesiva")
            penalty += 0.10
        if len(text) > 1000:
            analysis["flags"].append("verbosidad_crítica")
            penalty += 0.15

        # ── Ordenar spans por posición (requerido por el renderer) ─────────────
        analysis["smoke_spans"].sort(key=lambda s: s["start"])

        # ── Tipo semántico y confianza final ───────────────────────────────────
        analysis["type"] = active_types if active_types else ["informational"]
        confidence = round(max(0.0, min(1.0, 1.0 - penalty)), 2)
        analysis["confidence"] = confidence
        analysis["fluff_detected"] = len(analysis["smoke_spans"]) > 0

        if confidence >= 0.75:
            analysis["alert_level"] = "none"
        elif confidence >= 0.45:
            analysis["alert_level"] = "warning"
        else:
            analysis["alert_level"] = "critical"

        return analysis

    async def validate_mandate(self, intent: str, option_id: str) -> Dict[str, Any]:
        """
        Valida que el mandato del operador sea ejecutable y lo registra en Nexus.
        """
        await self._ensure_dependencies()
        
        # Diccionario de rutas válidas
        valid_routes = [
            "execute_direct", "research_first", "dev_execute", 
            "refine_intent", "force_reformat", "ignore_fluff", 
            "ignore_intent"
        ]
        
        if option_id in valid_routes:
            logger.info(f"✅ [RULE_ENGINE] Mandato autorizado por el Operador: {option_id}")
            
            # --- REGISTRO EN NEXUS (PRINCIPIO DE SOBERANÍA) ---
            if self.nexus:
                try:
                    await self.nexus.log_decision({
                        "intent": intent,
                        "selected": option_id,
                        "module": "kernel",
                        "timestamp": "auto"
                    })
                    logger.info("🧠 [NEXUS] Decisión del operador registrada exitosamente.")
                except Exception as e:
                    logger.warning(f"⚠️ [NEXUS] Error al registrar decisión (modo degradado): {e}")

            return {"status": "authorized", "option_id": option_id}
            
        return {
            "status": "rejected", 
            "reason": f"Mandato '{option_id}' no reconocido como ruta segura por el Kernel."
        }

# Instancia global para integración directa
service = RuleEngine()
