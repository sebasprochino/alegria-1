import json
import os
import logging

logger = logging.getLogger("ALEGRIA_CREATIVE_DIRECTOR")

class CreativeDirector:
    """
    Árbitro de Inteligencia Estética (CDM).
    Valida la coherencia de las variantes creativas contra la Biblia de Estilo.
    """
    
    def __init__(self, bible_path=None):
        if bible_path is None:
            # Path relativo al archivo actual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            bible_path = os.path.join(current_dir, "bible.json")
            
        self.bible = self._load_bible(bible_path)
        self.current_preset = "tech_sovereign"

    def _load_bible(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando Biblia Creativa: {e}")
            return {}

    def set_preset(self, preset_name):
        if preset_name in self.bible.get("presets", {}):
            self.current_preset = preset_name
            logger.info(f"Preset creativo actualizado: {preset_name}")
            return True
        return False

    def evaluate_variant(self, variant):
        """
        Wrapper con fail-safe para la evaluación de variantes.
        Asegura resiliencia del pipeline ante errores internos del CDM.
        """
        try:
            return self._evaluate(variant)
        except Exception as e:
            logger.error(f"Error interno en CDM: {e}")
            return {
                "status": "error",
                "fallback": "accept_with_flag",
                "error": str(e)
            }

    def _evaluate(self, variant):
        """
        Lógica interna de evaluación (Coherence & Decisions Manager).
        """
        preset_config = self.bible.get("presets", {}).get(self.current_preset, {})
        variant_meta = variant.get("aesthetic_meta", {})
        
        score = 1.0
        reasoning = []
        status = "approved"

        # 1. Validación de Reglas de Rechazo (REJECT_IF)
        for rule in self.bible.get("validation_rules", {}).get("reject_if", []):
            match = True
            for i, dim in enumerate(rule["dimensions"]):
                val = variant_meta.get(dim)
                if val != rule["pattern"][i]:
                    match = False
                    break
            
            if match:
                logger.warning(f"Variante rechazada por CDM: {rule['reason']}")
                return {
                    "score": 0.0,
                    "reasoning": [rule["reason"]],
                    "status": "rejected"
                }

        # 2. Scoring de Alineación con Preset
        matches = 0
        total_dims = len(preset_config) - 1 # Restamos 'description'
        
        for dim, target_val in preset_config.items():
            if dim == "description": continue
            
            variant_val = variant_meta.get(dim)
            if variant_val == target_val:
                matches += 1
            else:
                reasoning.append(f"Desviación en {dim}: esperado {target_val}, recibido {variant_val}")

        score = matches / total_dims if total_dims > 0 else 1.0
        
        if score < 0.5:
            status = "flagged"
            reasoning.append("Alineación estética baja.")

        return {
            "score": round(score, 2),
            "reasoning": reasoning,
            "status": status
        }

    def get_vision_prompt_snippet(self):
        """
        Retorna un fragmento de prompt basado en el preset actual para inyectar en LLMs.
        """
        preset = self.bible.get("presets", {}).get(self.current_preset, {})
        snippet = f"Sigue estas reglas estéticas de ALEGR-IA: "
        for dim, val in preset.items():
            if dim == "description": continue
            snippet += f"{dim}={val}, "
        return snippet.strip(", ")
