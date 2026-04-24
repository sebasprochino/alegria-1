# src/services/query_classifier.py

class QueryClassifier:
    """
    Clasificador de intención.
    Vive sobre el léxico compartido.
    """
    def __init__(self, lexicon):
        self.lexicon = lexicon
        print("[CLASSIFIER] Query Classifier inicializado")

    def classify(self, text: str) -> str:
        """
        Clasifica la intención en niveles de riesgo/complejidad.
        LOW: trivial / human
        MID: informational
        HIGH: search / memory / complex
        """
        if not text:
            return "empty"
            
        lower = text.lower().strip()
        
        # 1. TRIVIAL (LOW RISK) - Saludos, cortesía, frases muy cortas
        trivial_patterns = [
            "hola", "buenos días", "buenas tardes", "buenas noches",
            "qué tal", "cómo estás", "gracias", "chau", "adiós"
        ]
        if any(lower == p or lower.startswith(p + " ") for p in trivial_patterns):
            return "trivial"
            
        if len(lower.split()) <= 2 and not any(kw in lower for kw in ["ejecuta", "borra", "run"]):
            return "trivial"

        # 2. INFORMATIONAL (MID RISK) - Preguntas directas, aclaraciones
        info_patterns = [
            "qué es", "quien es", "explica", "cómo funciona", "ayuda con",
            "dame info", "decime", "cuéntame", "información sobre"
        ]
        if any(p in lower for p in info_patterns):
            return "informational"

        # 3. HIGH RISK / ACTIONS
        if "buscar" in lower or "radar" in lower:
            return "search"
        if "guardar" in lower or "recordá" in lower or "memoria" in lower:
            return "memory"
            
        return "complex"
