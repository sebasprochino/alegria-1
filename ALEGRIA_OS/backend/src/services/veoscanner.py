# backend/src/services/veoscanner.py
import base64
import os
import json
import logging
from .provider_registry import get_registry

logger = logging.getLogger("ALEGRIA_VEOSCANNER")

PROMPT_ANALISIS_VEO = """
Eres el 'Ojo Clínico de ALEGR-IA' (VeoScope). Tu misión es diseccionar la estética de la imagen adjunta para transformarla en directrices de marca precisas.
Analiza la imagen bajo estos 4 pilares estrictos:

1. ADN VISUAL:
   - Composición (refe de tercios, equilibrio, tensión).
   - Iluminación (calidad, dirección, estilo cinematográfico).
   - Paleta de Colores (colores primarios, secundarios y acento en Hex si es posible).
   - Estilo (Ej: Cyberpunk, Minimalista, Brutalista, Organico).

2. CONTEXTO NARRATIVO:
   - ¿Qué historia cuenta esta imagen?
   - Momento emocional y potencial narrativo para una marca.

3. PROMPT TÉCNICO:
   - Traduce esta imagen a un prompt detallado para generadores de IA (tipo Midjourney/Flux) que permita replicar la misma estética exactamente.

4. SUGERENCIA DE MARCA:
   - Recomendaciones de estilo para aplicar este ADN a una identidad corporativa o campaña.

Responde ÚNICAMENTE en JSON plano con esta estructura:
{
  "adn_visual": { "composicion": "", "iluminacion": "", "colores": [], "estilo": "" },
  "contexto_narrativo": { "historia": "", "emocion": "" },
  "prompt_tecnico": "",
  "sugerencias_marca": []
}
"""

class VeoscannerService:
    def __init__(self, nexus=None):
        self.nexus = nexus
        self.registry = get_registry()

    async def analizar_imagen(self, image_path: str, mode: str = "adn"):
        """
        Analiza una imagen física (path local o base64).
        """
        logger.info(f"👁️ [VEOSCANNER] Iniciando análisis clínico: {image_path} (Modo: {mode})")
        
        try:
            # 1. Preparar la imagen (convertir a base64 si es path local)
            image_data = None
            if os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    ext = image_path.split('.')[-1].lower()
                    if ext == 'jpg': ext = 'jpeg'
                    image_data = f"data:image/{ext};base64,{encoded}"
            else:
                image_data = image_path # Asumimos que ya es base64
            
            # 2. Extracón Determinista (VeoScope v2)
            try:
                from src.os.perception.vision.extractor import extract_features
                obj_features = extract_features(image_path)
                features_json = json.dumps(obj_features, indent=2)
                deterministic_context = f"\n\n### MEDICIONES OBJETIVAS EXTRAÍDAS (OPENCV):\n{features_json}\nUsa estos datos deterministas como la base absoluta para tu análisis LLM."
            except ImportError:
                deterministic_context = ""
                logger.warning("⚠️ No se encontró la capa `cv2`. Operando en modo Hallucination-allowed (v1).")
            except Exception as e:
                deterministic_context = ""
                logger.error(f"❌ Error extrayendo métricas con CV2: {e}")

            # 3. Construir lista de fallback inteligente (sin Groq Vision que está roto)
            adapters_to_try = []
            
            openai = self.registry.get_adapter(provider="openai", model="gpt-4o-mini")
            if openai: adapters_to_try.append(openai)
            
            gemini = self.registry.get_adapter(provider="gemini")
            if gemini: adapters_to_try.append(gemini)

            if not adapters_to_try:
                # Bloqueo arquitectónico de proveedores: Forzamos el Fallback Objetivo
                logger.warning("Ningún LLM activo. Volcando features pre-extraidos por OpenCV.")
                return {
                    "status": "partial",
                    "mode": mode,
                    "analysis": {"adn_visual": {}, "mediciones_matematicas": obj_features},
                    "message": "ADVERTENCIA: Red Cognitiva Caída. Solo extracción métrica determinista.",
                    "fallback": "opencv_extractor"
                }

            # 4. Llamada multimodal
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT_ANALISIS_VEO + deterministic_context},
                        {"type": "image_url", "image_url": {"url": image_data}}
                    ]
                }
            ]
            
            res_raw = None
            last_err = None
            used_adapter = None
            
            for adapter in adapters_to_try:
                try:
                    logger.info(f"🚀 [VEOSCANNER] Usando adaptador: {adapter.provider_name} con modelo {adapter.model}")
                    res_raw = await adapter.chat(messages, temperature=0.2)
                    if res_raw:
                        used_adapter = adapter
                        break
                except Exception as e:
                    logger.warning(f"⚠️ [VEOSCANNER] Falló {adapter.provider_name} ({adapter.model}): {e}")
                    last_err = e
                    continue
                    
            if not res_raw:
                return {
                    "status": "partial",
                    "mode": mode,
                    "analysis": {"adn_visual": {}, "mediciones_matematicas": obj_features},
                    "message": f"Falló toda la Cascada LLM (Error: {last_err}). Se devolvió extracción OpenCV pura.",
                    "fallback": "opencv_extractor"
                }

            # 4. Limpieza y parseo
            try:
                cleaned = res_raw.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[-1].split("```")[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[-1].split("```")[0].strip()
                
                analysis = json.loads(cleaned)
                return {
                    "status": "success",
                    "mode": mode,
                    "analysis": analysis,
                    "message": f"Análisis VEO de la imagen completado bajo la modalidad {mode}.",
                    "raw_llm": res_raw
                }
            except Exception as pe:
                logger.error(f"❌ [VEOSCANNER] Error parseando JSON: {pe}")
                return {
                    "status": "partial",
                    "mode": mode,
                    "content": res_raw,
                    "message": "Análisis completado pero el formato no es JSON puro."
                }
                
        except Exception as e:
            logger.error(f"❌ [VEOSCANNER] Error fatal en análisis: {e}")
            return {"status": "error", "message": str(e)}

    async def analizar_marca(self, nombre_marca: str):
        """
        Analiza el ADN Visual y Narrativo de una marca por texto.
        """
        logger.info(f"👁️ [VEOSCANNER] Analizando marca (texto): {nombre_marca}")
        
        # Simulación de análisis clínico para compatibilidad legacy
        reporte = {
            "status": "success",
            "marca": nombre_marca,
            "adn_visual": {
                "paleta": ["#7c3aed", "#3b82f6", "#00f6ff"],
                "mood": "Energético y Confiable",
                "tipografia": "Outfit / Inter"
            },
            "contexto_narrativo": {
                "voz": "Innovadora, accesible, inspiradora",
                "arquetipo": "El Creador / El Mago"
            },
            "sugerencias": [
                "Reforzar el contraste en interfaces de modo oscuro.",
                "Utilizar micro-animaciones para aumentar la percepción de innovación.",
                "Mantener la calma soberana en las respuestas del sistema."
            ]
        }
        
        return reporte

# Singleton instance
service = None

def get_service(nexus=None):
    global service
    if service is None:
        service = VeoscannerService(nexus)
    return service
