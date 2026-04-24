# 🧠 FUENTE DE VERDAD DE DECISIONES — ALEGR-IA OS

> **Documento Constitucional**
> Ningún agente, módulo o servicio puede violar estas reglas.

---

## 📜 REGLA MAESTRA DE DECISIÓN

```
Antes de CUALQUIER acción, clasificar el query.
La clasificación determina qué recursos están PERMITIDOS.
```

---

## 🎯 CLASIFICACIÓN DE QUERIES

| Tipo | Descripción | SEARCH | MEMORY | CASCADE |
|------|-------------|--------|--------|---------|
| **INTERNAL** | Referencias al sistema, memoria, historial | ❌ PROHIBIDO | ✅ OBLIGATORIO | ⚙️ Opcional |
| **EXTERNAL** | Requiere info del mundo exterior | ✅ Si confianza ≥ 0.7 | ✅ Primero | ⚙️ Opcional |
| **CREATIVE** | Exploración, ideas, estrategia | ⚙️ Solo si explícito | ✅ Contexto | ✅ Principal |
| **GENERAL** | Fallback | ⚙️ Con restricciones | ✅ Contexto | ✅ Principal |

---

## 🔴 REGLA DE ORO — PRIORIDAD ABSOLUTA DE MEMORIA

```python
if query_type == "INTERNAL":
    # ⛔ PROHIBIDO: SEARCH, GOOGLE, LLM externo
    # ✅ OBLIGATORIO: Responder desde MEMORY
    # ✅ Si no hay memoria: ADMITIR honestamente
    
    return respond_from_memory_only()
```

### Ejemplos que activan INTERNAL

- "Buscá mi historial"
- "¿Guardaste lo que dije?"
- "Qué hablamos antes"
- "Recordás lo que decidimos?"
- "Qué sabés de mi proyecto"

### Respuesta correcta si NO hay memoria

```
No tengo registros sobre eso en mi memoria.
(No busqué en internet porque es una consulta interna)
```

---

## 🔍 REGLA SEARCH — MUY RESTRINGIDA

```python
if query_type == "EXTERNAL":
    if classification.confidence < 0.7:
        return ask_for_clarification()
    
    # Solo ahora SEARCH está permitido
    return search_and_respond()
```

### Condiciones para SEARCH

1. Query clasificado como EXTERNAL
2. Confianza de clasificación ≥ 0.7
3. NO hay bloqueadores internos (ej: "mi historial")

---

## 🎨 MODO CREATIVO

```python
if query_type == "CREATIVE":
    context = memory.recall_relevant()
    return cascade.generate(
        input=user_input,
        context=context,
        role="Anima Chordata"
    )
```

### Características

- LLM activo
- Imaginación permitida
- SEARCH solo si el usuario lo pide explícitamente

---

## 🚨 GUARDIAN — OBSERVA EL SISTEMA, NO EL MUNDO

```python
def guardian_watch(task):
    # GUARDIAN no observa:
    if task.origin in ["SEARCH", "GROQ", "HTTP_EXTERNAL"]:
        return  # NO vigilar recursos externos
    
    # GUARDIAN sí observa:
    if task.runtime > MAX_INTERNAL_TIME:
        raise GuardianAlert("Timeout en operación interna")
```

---

## 📋 TABLA DE VERDAD (ABSOLUTA)

| Consulta del usuario | Query Type | Acción |
|----------------------|------------|--------|
| "Buscá mi historial" | INTERNAL | Solo MEMORY |
| "¿Guardaste lo que dije?" | INTERNAL | Solo MEMORY |
| "Qué hablamos antes" | INTERNAL | Solo MEMORY |
| "Buscá en Google…" | EXTERNAL | SEARCH permitido |
| "Qué es FastAPI" | EXTERNAL | SEARCH permitido |
| "No me sirve si no recordás" | INTERNAL | MEMORY + explicación |
| "Explorá esta idea" | CREATIVE | CASCADE |
| "Dame las noticias" | EXTERNAL | SEARCH permitido |

---

## ⚙️ IMPLEMENTACIÓN TÉCNICA

### Archivos clave

- `backend/src/services/query_classifier.py` — Clasificador
- `backend/src/services/memory/session_source.py` — FVS
- `backend/src/services/anima.py` — Lógica de decisión

### Flujo en `anima.respond()`

```python
# 1. Cargar Fuente de Verdad de Sesión
source = session_source.load(session_id)

# 2. CLASIFICAR (antes de todo)
classification = classifier.classify(user_input)

# 3. Aplicar regla según tipo
if classification.query_type == QueryType.INTERNAL:
    return await self._respond_internal(...)  # SEARCH bloqueado

# 4. Para otros tipos, continuar flujo normal
```

---

## ✅ RESULTADOS ESPERADOS

- ❌ Se terminan búsquedas absurdas
- ❌ Se terminan timeouts falsos
- ✅ El sistema confía en sí mismo
- ✅ El usuario siente continuidad real
- ✅ Anima Chordata deja de parecer distraída

---

## 📝 MANTENIMIENTO

### Para agregar nuevos patrones INTERNAL

Editar `query_classifier.py`:

```python
INTERNAL_KEYWORDS = [
    # Agregar aquí nuevos patrones
]
```

### Para modificar umbrales

```python
# En _build_governed_context_data()
if classification.confidence >= 0.7:  # Umbral para SEARCH
```

---

> **Este documento es LEY OPERATIVA.**
> Cualquier cambio requiere actualizar tests en `test_decision_rules.py`.
