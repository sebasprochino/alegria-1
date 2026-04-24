from typing import Dict, Any, Callable
import logging

logger = logging.getLogger("ALEGRIA_OS_REGISTRY")

class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, description: str, risk: str, func: Callable):
        self._tools[name] = {
            "description": description,
            "risk": risk,
            "func": func
        }

    def get_tool(self, name: str) -> Callable | None:
        if name in self._tools:
            return self._tools[name]["func"]
        return None

    def list_tools(self) -> str:
        if not self._tools:
            return "No tools available."
        return "\n".join([f"- {name} [Riesgo: {info['risk']}]: {info['description']}" for name, info in self._tools.items()])

registry = ToolRegistry()

# ----------------- Core Tools -----------------

async def tool_system_navigate(query: str) -> str:
    import json
    import re
    
    # 1. Limpieza de comando
    url_target = query.strip()
    
    # Manejo de JSON si viene del Planner
    if url_target.startswith("{") and url_target.endswith("}"):
        try:
            args = json.loads(url_target)
            url_target = args.get("url", url_target)
        except:
            pass
            
    # Removemos prefijos de comando y palabras sueltas
    prefixes = [r"^abrir\s+", r"^navegar a\s+", r"^ir a\s+", r"^la pagina de\s+", r"^pagina\s+", r"(?i)^web\s+(?:de\s+)?"]
    for p in prefixes:
        url_target = re.sub(p, "", url_target, flags=re.IGNORECASE)
        
    url_target = url_target.strip()
    
    # 2. Normalización de Destino Intuitiva
    domain_map = {
        "youtube": "youtube.com",
        "google": "google.com",
        "tyc sport": "tycsports.com",
        "tyc sports": "tycsports.com",
        "clarin": "clarin.com",
        "infobae": "infobae.com",
        "lanacion": "lanacion.com.ar",
        "ole": "ole.com.ar",
        "wikipedia": "wikipedia.org"
    }

    lower_target = url_target.lower()
    if lower_target in domain_map:
        url_target = "https://www." + domain_map[lower_target]
    elif "." not in url_target:
        # Si no tiene punto y no es conocido, asumimos un .com genérico sin espacios
        clean_name = url_target.replace(" ", "").lower()
        url_target = f"https://www.{clean_name}.com"
    elif not url_target.startswith("http"):
        url_target = "https://" + url_target
        
    # 3. Respuesta técnica (Action Payload)
    payload = {
        "action": "navigate",
        "url": url_target,
        "name": url_target.replace("https://", "").replace("www.", "").split("/")[0].capitalize(),
        "type": "navigation"
    }
    
    return json.dumps(payload)

registry.register(
    "system.navigate",
    "Abre un nodo de navegación (URL) dentro del sistema. Soporta YouTube y navegación directa.",
    "bajo",
    tool_system_navigate
)

async def tool_clarin_news(query: str) -> str:
    from src.services.news_sensor import service as news_sensor
    import json
    
    # Manejo de argumentos
    search_query = query.strip()
    category = "lo_ultimo"
    
    if search_query.startswith("{") and search_query.endswith("}"):
        try:
            args = json.loads(search_query)
            search_query = args.get("query", "")
            category = args.get("category", "lo_ultimo")
        except:
            pass
            
    return await news_sensor.search_news(search_query, category)

registry.register(
    "Clarín_News_Sensor",
    "Sonda especializada en noticias de fuentes confiables (Clarín). Permite filtrar por categoría (politica, economia, deportes, etc).",
    "bajo",
    tool_clarin_news
)

async def tool_radar_search(query: str) -> str:
    import json
    import re
    from src.services.radar import get_radar
    
    # Manejo de argumentos JSON o strings con prefijos operativos
    search_query = query.strip()
    
    # 1. Si es JSON, extraer query
    if search_query.startswith("{") and search_query.endswith("}"):
        try:
            args = json.loads(search_query)
            search_query = args.get("query", search_query)
        except:
            pass
    
    # 2. Limpieza de prefijos operativos (Fix: Evita ruidos en la búsqueda real)
    prefixes = [
        r"^busca en radar\s+", r"^buscar en radar\s+",
        r"^ejecutar radar\s+", r"^radar search\s+",
        r"^busca\s+", r"^buscar\s+", r"^search\s+"
    ]
    for p in prefixes:
        search_query = re.sub(p, "", search_query, flags=re.IGNORECASE)
            
    radar = get_radar()
    res = await radar.search(search_query.strip())
    return str(res)

async def tool_read_memory(query: str) -> str:
    from src.services.nexus import get_nexus
    nexus = get_nexus()
    recent = nexus.memory.get_recent(limit=5)
    hist = "\n".join([f"{e.source}: {e.content}" for e in recent])
    return f"Memoria reciente:\n{hist}"

registry.register(
    "OS_Radar_Search", 
    "Busca información en tiempo real sobre tendencias, internet y contexto actual.", 
    "bajo", 
    tool_radar_search
)

async def tool_web_scrape(query: str) -> str:
    import json
    from src.services.web_navigator import service as navigator_service
    
    url = query.strip()
    if url.startswith("{") and url.endswith("}"):
        try:
            args = json.loads(url)
            url = args.get("url", url)
        except:
            pass
            
    return await navigator_service.scrape_url(url)

registry.register(
    "OS_Web_Scraper", 
    "Navega de forma autónoma a una URL (Web Scraping). Usa un headless browser para renderizar JS y extrae el texto legible de la página. Input: la URL a analizar.", 
    "medio", 
    tool_web_scrape
)

registry.register(
    "OS_Read_Memory", 
    "Lee la memoria de interacciones previas para contexto.", 
    "bajo", 
    tool_read_memory
)

async def tool_file_save(args_json: str) -> str:
    import json
    import os
    try:
        args = json.loads(args_json)
        path = args.get("path")
        content = args.get("content")
        
        # Normalizar path o crear dirs si se requiere
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"file_saved_successfully: {path}"
    except Exception as e:
        return f"error_saving_file: {str(e)}"

registry.register(
    "OS_File_Save", 
    "Escribe o sobrescribe un archivo en el disco. El input DEBE ser un JSON con las claves 'path' y 'content'. Ejemplo: {\"path\": \"ruta.txt\", \"content\": \"texto\"}", 
    "alto", 
    tool_file_save
)

async def tool_analyze_visual(query: str) -> str:
    import json
    import base64
    import re
    import os
    from src.services.provider_registry import service as provider_service
    
    try:
        file_path = None
        prompt = "Analiza esta imagen con extremo detalle técnico para ALEGR-IA OS."
        
        path_match = re.search(r"Local Path:\s*([^\s,;\"]+)", query)
        if path_match:
            file_path = path_match.group(1).strip()
            prompt_match = re.search(r"\)\.?\s*(.*)", query)
            if prompt_match and prompt_match.group(1).strip():
                prompt = prompt_match.group(1).strip()
        
        if query.strip().startswith("{") and query.strip().endswith("}"):
            args = json.loads(query)
            file_path = args.get("path", file_path)
            prompt = args.get("prompt", prompt)
        
        if not file_path or not os.path.exists(file_path):
            return f"Error: El archivo {file_path} no existe o no fue encontrado."

        with open(file_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
            parts = file_path.split('.')
            ext = parts[-1].lower() if len(parts) > 1 else "png"
            if ext not in ['jpeg', 'jpg', 'png', 'webp']: ext = "png"
            if ext == 'jpg': ext = 'jpeg'
            base64_image = f"data:image/{ext};base64,{encoded}"

        # 2. Extraccion CV2 Determinista
        deterministic_context = ""
        try:
            from src.os.perception.vision.extractor import extract_features
            features = extract_features(file_path)
            deterministic_context = "\n\nDATOS OBJETIVOS (OPENCV):\n" + json.dumps(features, indent=2) + "\nBasa tu análisis estético rigurosamente en estas variables."
        except Exception as cv_err:
            pass
            
        import copy
        import copy
        # 🟢 Optimizamos Cascada de Visión: Priorizar Gemini y habilitar Groq Vision
        adapters = []
        
        # 1. Prioridad: Gemini (Nuevo estándar 2026: Fast & Intelligent)
        gemini_ad = provider_service.get_adapter(provider="gemini", model="gemini-2.5-flash")
        if gemini_ad: adapters.append(gemini_ad)
        
        # 2. Respaldo Soberano: Groq (Llama 4 Scout es el nuevo flagship de visión gratuito)
        groq_ad = provider_service.get_adapter(provider="groq", model="meta-llama/llama-4-scout-17b-16e-instruct")
        if groq_ad: adapters.append(groq_ad)
        
        # 3. Último recurso: OpenAI (puede tener quota errors)
        openai_ad = provider_service.get_adapter(provider="openai", model="gpt-4o-mini")
        if openai_ad: adapters.append(openai_ad)
        
        if not adapters:
            # Si no hay configuraciones específicas, intentar lo que haya excepto fallbacks ciegos
            adapters = [a for a in provider_service.get_cascade_providers()]
        
        if not adapters:
            if deterministic_context:
                return f"[SISTEMA: Degradación Crítica] Red de Visión desconectada. Métricas objetivas directas:\n{deterministic_context}"
            return "Error Crítico: No se encontraron proveedores de IA activos para visión."

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt + deterministic_context},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_image,
                        },
                    },
                ],
            }
        ]

        last_error = ""
        for adapter in adapters:
            try:
                result = await adapter.chat(messages=messages)
                if result:
                    return result
            except Exception as e:
                # Ignorar error y seguir con el próximo adaptador
                last_error = str(e)
                import logging
                logging.getLogger("ALEGRIA_VISUAL_ANALYSIS").warning(f"Adaptador {adapter.provider_name} ({adapter.model}) falló: {e}. Intentando próximo...")
                continue
                
        # SI TODOS LOS MODELOS FALLAN (ej. jiter missing + 404 api)
        fallback_msg = f"[SISTEMA: Degradación de Red. Todos los LLM fallaron (Último error: {last_error})]\n== VOLCADO DE VISION OBJETIVA ==\n"
        return fallback_msg + deterministic_context

    except Exception as e:
        return f"Error crítico en análisis visual: {str(e)}"

registry.register(
    "OS_Analyze_Visual", 
    "Analiza el contenido de una imagen (JPG, PNG). El input DEBE ser un JSON con la clave 'path' (ruta al archivo) y opcionalmente 'prompt' con instrucciones específicas.", 
    "bajo", 
    tool_analyze_visual
)

async def tool_visual_veoscope(query: str) -> str:
    """
    Analiza una imagen mediante el Ojo Clínico de ALEGR-IA (VeoScope).
    Parsea el comando estructurado del frontend o JSON directo.
    """
    from src.services.veoscanner import get_service
    import json
    import re
    import os

    # 1. Parsea el comando estructurado
    mode = "adn"
    file_path = None
    
    # Extraer modo
    mode_match = re.search(r"Modo:\s*(\w+)", query)
    if mode_match:
        mode = mode_match.group(1).lower()
    
    # Extraer path
    path_match = re.search(r"Local Path:\s*([^\s,;]+)", query)
    if path_match:
        file_path = path_match.group(1).strip()
    
    # Si viene como JSON directo
    if query.strip().startswith("{") and query.strip().endswith("}"):
        try:
            args = json.loads(query)
            file_path = args.get("file_path", args.get("path", file_path))
            mode = args.get("mode", mode)
        except:
            pass
            
    if not file_path:
        return "Error Crítico: No se pudo localizar el path del archivo para el análisis VEO en la solicitud. Asegúrate de que el archivo fue subido y referenciado."

    # Intentar resolver path relativo si es necesario
    full_path = file_path
    if not os.path.isabs(full_path):
        # Asumimos relativo a backend/
        full_path = os.path.abspath(os.path.join(os.getcwd(), file_path))

    service = get_service()
    res = await service.analizar_imagen(full_path, mode=mode)
    
    return json.dumps(res, indent=2)

registry.register(
    "visual.veoscope",
    "Analiza una imagen mediante el Ojo Clínico de ALEGR-IA (VeoScope). Extrae ADN visual, narrativa, prompts técnicos y sugerencias de marca.",
    "bajo",
    tool_visual_veoscope
)

# ----------------- Creative & Production Tools -----------------

async def tool_pipeline_execute(args_json: str) -> str:
    """
    Ejecuta una secuencia de pasos creativos con optimización quirúrgica.
    Input: JSON con 'steps' (lista) y 'goal' (string).
    """
    import json
    from src.os.pipeline.creative_steps import CREATIVE_STEPS
    from src.os.creative.optimizer.optimizer import optimize
    
    try:
        args = json.loads(args_json)
        requested_steps = args.get("steps", [])
        goal = args.get("goal", "Generación creativa")
        
        state = {"goal": goal, "creative_outputs": {}, "improve_count": 0}
        outputs = {}
        trace = []
        
        # 1. Ejecución inicial
        for step_name in requested_steps:
            if step_name in CREATIVE_STEPS:
                fn = CREATIVE_STEPS[step_name]
                try:
                    result = fn(state, outputs)
                    outputs[step_name] = result
                    
                    trace.append({
                        "step": "creative_production",
                        "name": step_name,
                        "artifact_type": result.get("type", "unknown"),
                        "summary": str(result.get("value", ""))[:60]
                    })
                except Exception as e:
                    trace.append({"step": step_name, "error": str(e)})
                    break
        
        # 2. Bucle de Optimización Quirúrgica
        MAX_IMPROVEMENTS = 1
        for _ in range(MAX_IMPROVEMENTS):
            opt_result = optimize(outputs, goal, state)
            
            if opt_result["action"] == "accept":
                trace.append({
                    "step": "optimization", 
                    "status": "APPROVED", 
                    "score": state["optimization"]["score"]
                })
                break
                
            # Intento de mejora quirúrgica
            steps_to_fix = opt_result.get("steps_to_fix", [])
            trace.append({
                "step": "optimization", 
                "status": "IMPROVING", 
                "issues": opt_result["issues"],
                "fixing_steps": steps_to_fix
            })
            
            for step_name in steps_to_fix:
                if step_name in CREATIVE_STEPS:
                    outputs[step_name] = CREATIVE_STEPS[step_name](state, outputs)
                    trace.append({
                        "step": "surgical_fix",
                        "name": step_name,
                        "artifact_type": outputs[step_name].get("type"),
                        "summary": "Actualizado para corregir inconsistencias"
                    })
            state["improve_count"] += 1

        # Re-evaluación final tras mejoras
        final_opt = optimize(outputs, goal, state)
        
        return json.dumps({
            "status": "finalized",
            "quality": "high" if final_opt["action"] == "accept" else "standard",
            "outputs": outputs,
            "trace": trace,
            "optimization": state.get("optimization")
        }, indent=2)

    except Exception as e:
        return f"error_executing_pipeline: {str(e)}"

async def tool_brand_update(args_json: str) -> str:
    """
    Actualiza la identidad de una marca (Voz, Mood, Paleta) en el Brand Studio.
    """
    from src.services.brand_service import service as brand_service
    import json
    try:
        args = json.loads(args_json)
        brand_id = args.get("brand_id", "AlegrIA")
        updates = args.get("updates", {})
        
        success = brand_service.update_brand(brand_id, updates)
        if success:
            return f"success: Identidad de marca '{brand_id}' actualizada correctamente en el Brand Studio."
        return f"error: No se encontró la marca '{brand_id}'."
    except Exception as e:
        return f"error: {str(e)}"

registry.register(
    "brand.update",
    "Actualiza la identidad de una marca (Voz, Mood, Paleta) en el Brand Studio. Útil para persistir análisis de VeoScope.",
    "medio",
    tool_brand_update
)

async def tool_multiverse_execute(args_json: str) -> str:

    """
    Explora múltiples realidades creativas y elige la mejor según score técnico y perfil.
    Input: JSON {\"steps\": [...], \"goal\": \"...\", \"variants\": 3}
    """
    import json
    from src.os.creative.multiverse.generator import generate_variants
    from src.os.creative.multiverse.evaluator import evaluate_variant
    from src.os.creative.multiverse.selector import select_best
    # Reutilizamos la función de ejecución batch
    from src.os.actions.registry import tool_pipeline_execute
    
    try:
        args = json.loads(args_json)
        requested_steps = args.get("steps", [])
        goal = args.get("goal", "Exploración Creativa")
        num_variants = args.get("variants", 2)
        
        # 1. Control de Costo / Complejidad
        # Por ahora simple: si son pocos pasos, no lanzamos multiverso a menos que se pida expresamente.
        if len(requested_steps) < 2 and num_variants > 1:
            num_variants = 1 # Reducir a single-path si es trivial
            
        state = {"goal": goal, "profile": {}} # En prod esto vendría del contexto
        
        # 2. Generar Variantes
        variants = generate_variants(requested_steps, state, n=num_variants)
        results = []
        
        # 3. Ejecutar cada variante (Pipeline Multimodal)
        for v in variants:
            # Creamos un input para tool_pipeline_execute
            v_input = json.dumps({"steps": v["steps"], "goal": goal})
            # Ejecución real (reutilizando la lógica segura y auditable)
            pipeline_res_raw = await tool_pipeline_execute(v_input)
            pipeline_res = json.loads(pipeline_res_raw)
            
            # 4. Evaluar variante
            evaluation = evaluate_variant(pipeline_res.get("outputs", {}), v["state"], state.get("profile", {}))
            
            results.append({
                "id": v["id"],
                "eval": evaluation,
                "output": pipeline_res.get("outputs"),
                "pipeline_trace": pipeline_res.get("trace")
            })
            
        # 5. Seleccionar Ganador
        winner = select_best(results)
        
        return json.dumps({
            "status": "multiverse_completed",
            "winner_id": winner["id"],
            "best_score": winner["eval"]["final_score"],
            "variants_explored": len(results),
            "winner_output": winner["output"],
            "trace": [
                {
                    "step": "multiverse_selection",
                    "scores": {r["id"]: r["eval"]["final_score"] for r in results},
                    "winner": winner["id"],
                    "reason": "Highest combined technical/creative score"
                }
            ]
        }, indent=2)

    except Exception as e:
        return f"error_multiverse_execution: {str(e)}"

registry.register(
    "OS_Multiverse_Batch", 
    "Explora múltiples variantes de una producción creativa y selecciona la ganadora basándose en criterios técnicos, estéticos y de perfil del usuario. Alta complejidad y costo.", 
    "alto", 
    tool_multiverse_execute
)



async def tool_evolution_execute(args_json: str) -> str:
    """
    Realiza una evolución creativa: explora el multiverso, selecciona los mejores
    componentes de cada realidad y los fusiona en una variante 'Alpha' superior.
    Input: JSON {\"steps\": [...], \"goal\": \"...\", \"variants\": 3}
    """
    import json
    from src.os.creative.multiverse.generator import generate_variants
    from src.os.creative.multiverse.evaluator import evaluate_variant
    from src.os.creative.evolution.crossover import crossover_variants
    from src.os.creative.evolution.synthesizer import synthesize_alpha
    from src.os.actions.registry import tool_pipeline_execute
    
    try:
        args = json.loads(args_json)
        requested_steps = args.get("steps", [])
        goal = args.get("goal", "Evolución Creativa")
        num_variants = args.get("variants", 3)
        
        state = {"goal": goal, "profile": {}}
        
        # 1. Fase Multiverso: Exploración
        variants = generate_variants(requested_steps, state, n=num_variants)
        results = []
        
        for v in variants:
            v_input = json.dumps({"steps": v["steps"], "goal": goal})
            pipeline_res_raw = await tool_pipeline_execute(v_input)
            pipeline_res = json.loads(pipeline_res_raw)
            
            evaluation = evaluate_variant(pipeline_res.get("outputs", {}), v["state"], state.get("profile", {}))
            
            results.append({
                "id": v["id"],
                "eval": evaluation,
                "output": pipeline_res.get("outputs")
            })
            
        # 2. Fase Evolución: Crossover (Cruce de mejores genes)
        alpha_outputs, fusion_trace = crossover_variants(results)
        
        # 3. Fase Síntesis: Renderizado final del individuo 'Alpha'
        final_outputs = synthesize_alpha(alpha_outputs, state)
        
        return json.dumps({
            "status": "evolution_completed",
            "type": "alpha_synthesis",
            "alpha_outputs": final_outputs,
            "fusion_trace": fusion_trace,
            "variants_explored": len(results),
            "trace": [
                {
                    "step": "creative_evolution",
                    "action": "crossover_fusion",
                    "components_merged": len(fusion_trace)
                }
            ]
        }, indent=2)

    except Exception as e:
        return f"error_evolution_execution: {str(e)}"

registry.register(
    "OS_Evolution_Batch", 
    "Avanza la producción creativa mediante evolución genética: explora variantes, fusiona los mejores componentes de cada una y sintetiza un resultado Alpha superior. Máxima calidad.", 
    "alto", 
    tool_evolution_execute
)


