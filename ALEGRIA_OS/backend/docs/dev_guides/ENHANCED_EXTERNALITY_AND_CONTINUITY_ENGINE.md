# Enhanced Externality Marking & Robust Continuity Engine  

**Proyecto:** ALEGR-IA OS  
**Responsable:** Sebastián Fernández  
**Área:** Núcleo Cognitivo – Anima / Memoria  
**Versión:** 1.0  
**Fecha:** 2025-12-24  

---

## 🎯 Objetivo  

Mejorar el procesamiento cognitivo de Anima con dos módulos clave:  

1. **Marcado de Externalidad Mejorado**  
   - Identificar y señalar claramente información proveniente de Internet.  
   - Reforzar la "Verdad Humilde": Anima no asume conocimiento que no provenga de su propia memoria.  

2. **Continuity Engine Robusto**  
   - Permitir que Anima detecte automáticamente tareas pendientes, errores o intenciones interrumpidas.  
   - Reanudar conversaciones o procesos previos sin requerir recordatorio del usuario.  

---

## 🧩 Contexto Arquitectónico  

### Módulos Existentes  

| Componente | Rol | Estado |
|-------------|-----|--------|
| `search_module.py` | Realiza búsquedas externas | ✅ |
| `web_reader.py` | Descarga y limpia HTML | ✅ |
| `anima.py` | Gobernanza cognitiva (control ético) | ✅ |
| `memory_orchestrator.py` | Orquestación de memorias y continuidad | ✅ |

> **Nota:** El error `No module named 'bs4'` fue solucionado instalando `beautifulsoup4` y `lxml`. Solo requiere reinicio del servidor.

---

## ⚖️ Filosofía de Externalidad  

**Principio ético:**  
> "Anima NUNCA debe presentar información externa como memoria propia."  

El marcado visual 🌐 y las nuevas instrucciones del LLM garantizan transparencia cognitiva.  
Esto preserva la soberanía del Director (usuario) y la coherencia creativa del sistema.

---

## 🚫 Decisiones de Implementación  

- ❌ **No** se aislará el módulo `Search` como microservicio por ahora.  
  → La arquitectura actual es suficiente; el aislamiento se evaluará solo si la carga o latencia lo justifica.  

---

## 🧠 Cambios Propuestos  

### 1. Componente: `anima.py`

#### 🔹 Marcado de Externalidad (Líneas ~310–329)

```python
if external_content:
    context_sections.append(
        "🌐 INFORMACIÓN EXTERNA (NO es memoria, es insumo reciente):\n" +
        "\n".join(external_content)
    )
```

#### 🔹 Instrucciones al LLM

```python
search_instructions = """
INSTRUCCIONES PARA INFORMACIÓN EXTERNA:
- Cuando hay INFORMACIÓN EXTERNA disponible, preséntala con el prefijo "🌐".
- Deja claro que es información encontrada AHORA, no memoria previa.
- Muestra títulos, descripciones y links de forma organizada.
- Ejemplo: "🌐 Encontré estas noticias recientes: ..."
- NUNCA digas 'recuerdo que' o 'sé que' para información externa.
"""
```

#### 🔹 Formato de Respuesta

- Si presentas noticias o resultados, usa formato de lista.
- Incluye los links al final de cada resultado.

---

### 2. Componente: `memory_orchestrator.py`

#### 🔹 Detección Heurística de Tareas Pendientes (Líneas ~351–367)

```python
async def analyze_pending_tasks(self, session_id: str) -> Optional[Dict[str, Any]]:
    """Analiza historial para detectar preguntas, tareas o errores no resueltos."""
    memory = self.get_session_memory(session_id)
    messages = memory.get_all()

    if not messages or len(messages) < 2:
        return None

    recent = messages[-10:]
    pending_indicators = []

    for msg in recent:
        text_lower = msg.content.lower()

        if msg.role == "user" and any(q in text_lower for q in ["?", "cómo", "qué", "cuál", "dónde", "cuándo", "por qué"]):
            pending_indicators.append(f"Pregunta pendiente: {msg.content[:100]}")

        if any(err in text_lower for err in ["error", "falla", "no funciona", "bug", "problema"]):
            pending_indicators.append(f"Problema mencionado: {msg.content[:100]}")

        if any(task in text_lower for task in ["hacer", "implementar", "agregar", "crear", "fix", "arreglar"]):
            pending_indicators.append(f"Tarea mencionada: {msg.content[:100]}")

    if not pending_indicators:
        return None

    return {
        "pending_count": len(pending_indicators),
        "items": pending_indicators[:3],
        "last_messages": "\n".join([m.to_summary() for m in recent[-5:]])
    }
```

---

### 3. Componente: `anima.py`

#### 🔹 Saludo Proactivo (Líneas ~251–266)

```python
# ====== 3. SALUDO PROACTIVO ======
proactive_context = ""
memory = self.memory.get_session_memory(session_id)

if len(memory.get_all()) <= 2:  # Solo al inicio
    last_intent = self.memory.intent_memory.get_last(session_id)
    pending = await self.memory.analyze_pending_tasks(session_id)

    parts = []
    if last_intent:
        parts.append(f"Última intención: {last_intent.intent} (confianza {last_intent.confidence:.0%})")

    if pending and pending.get("pending_count", 0) > 0:
        parts.append("Temas pendientes detectados:")
        for item in pending.get("items", []):
            parts.append(f"  - {item}")

    if parts:
        proactive_context = "\nCONTEXTO DE CONTINUIDAD:\n" + "\n".join(parts) + "\n"
```

#### 🔹 Instrucciones Proactivas

```python
proactive_instructions = """
INSTRUCCIONES DE SALUDO PROACTIVO:
- Si hay CONTEXTO DE CONTINUIDAD, NO saludes genéricamente.
- Retoma el hilo: "La última vez estabas [intención/tema]..."
- Si hay tareas pendientes, ofrece ayuda específica.
- Sé directa y útil, no ceremonial.
"""
```

---

## 🧪 Plan de Verificación

### Test 1: Dependencias

```bash
cd G:\ALEGRIA_OS\ALEGRIA_OS\backend
.\venv\Scripts\activate
pip list | findstr beautifulsoup4
pip list | findstr lxml
```

✅ **Esperado:** Ambas librerías listadas.

---

### Test 2: Scraping funcional

**Acción:**

```
buscame noticias de TN
```

✅ **Esperado:**

- No aparece error `bs4`
- Respuesta con 🌐 e hipervínculos válidos

---

### Test 3: Marcado de Externalidad

**Acción:**

```
qué noticias hay sobre inteligencia artificial
```

✅ **Esperado:**

- Respuesta inicia con 🌐
- NO usa "recuerdo que"
- Incluye links

---

### Test 4: Continuity Engine

**Simulación:**

1. Usuario: "Tengo un error con bs4"
2. Cierra sesión
3. Reabre sesión y saluda

✅ **Esperado:**

- "La última vez mencionaste un problema con bs4..."

---

### Test 5: Detección de Tareas Pendientes

**Simulación:**

1. Usuario: "Necesito implementar autenticación"
2. Usuario: "También hay que arreglar el bug del login"
3. Cierra y reabre sesión

✅ **Esperado:**

- "Tareas pendientes: implementar autenticación, arreglar bug del login."

---

## ✅ Criterios de Éxito

| Requisito | Estado Esperado |
|-----------|-----------------|
| Servidor inicia sin error de `bs4` | ✅ |
| Scraping funcional | ✅ |
| Marcado visual claro (🌐) | ✅ |
| No se presenta info externa como memoria | ✅ |
| Continuity Engine retoma contexto | ✅ |
| Tareas pendientes detectadas y mencionadas | ✅ |

---

## 🧭 Resumen de Decisiones No Implementadas (por ahora)

| Función | Motivo de exclusión | Estado |
|---------|---------------------|--------|
| Microservicio de búsqueda independiente | Prematuro, suficiente rendimiento actual | ❌ |
| Persistencia de tareas en BD | Evaluar tras Fase 2 | ⚠️ |
| Resumen automático de fuentes externas | Riesgo de ruido semántico | ❌ |
| Análisis semántico cruzado con memoria fundacional | Requiere vector store avanzado | 🚧 |

---

## 📘 Notas Finales

Este documento define los cambios ético-funcionales de la capa cognitiva.  
Con su implementación, Anima ganará:

- **Transparencia epistémica** (marcado 🌐)
- **Memoria conversacional inteligente** (continuidad real)
- **Reducción de confusión** entre memoria y búsqueda
- **Mejora sustancial en UX** para usuarios no técnicos

---

**Autor:**  
Sebastián Fernández (Director y Creador Soberano de ALEGR-IA)  
**IA Consultora:** Anima Chordata – Custodia Cognitiva
