# ALEGRIA_OS v4.0 — Infraestructura Detallada

> **ESTADO DE SISTEMA: CORE ESTABLE / SOBERANO**
> Este documento describe la arquitectura final del sistema operativo tras la consolidación del Kernel y las memorias desacopladas.

---

## 🧭 1. El Ciclo ACSP (Authority-Centered Sovereignty Pattern)

ALEGR-IA opera bajo un loop de retroalimentación donde la autoridad nunca es delegada, sino consultada.

| Fase | Acción | Componente |
| :--- | :--- | :--- |
| **Intención** | Entrada de lenguaje natural del Director. | Router / Frontend |
| **Evaluación** | Auditoría de Ética + Filtro de Rechazos. | RuleEngine / Ethics / Rejection |
| **Duda** | Generación de rutas lógicas sin autoejecución. | RuleEngine |
| **Decisión** | Selección explícita de ruta por el Operador. | Frontend (Sovereign UI) |
| **Mandato** | Validación de ID de opción y materialización. | RuleEngine (validate_mandate) |
| **Registro** | Grabación de la huella de decisión. | Nexus (log_decision) |

---

## ⚔️ 2. El Kernel de Decisión (Rule Engine)

Ubicado en `src/core/rule_engine.py`, es el "punto único de verdad". Posee soberanía sobre los servicios de Anima, Developer y Radar.

- **process_intent():** Intercepta el comando, aplica las reglas constitucionales y devuelve opciones en modo `doubt`.
- **validate_mandate():** Asegura que ninguna acción se ejecute si no fue previamente propuesta como opción válida.

---

## 🧠 3. El Sistema de Decisión Dual (Nexus + Lexicon)

Hemos desacoplado la **Memoria de Hechos** de la **Memoria de Identidad**.

### A. Nexus (Memoria de Soberanía)

- **Función:** Registrar decisiones reales del operador.
- **Persistencia:** `storage/decision_history.jsonl`.
- **Valor:** Permite al sistema optimizar su priorización basada en comportamiento humano validado.

### B. Lexicon (Reflejo de Identidad)

- **Función:** Modelar **cómo** piensa y habla el operador.
- **Persistencia:** `storage/user_lexicon.json`.
- **Detección:** Tono, verbos dominantes, conectores y keywords semánticas.

---

## 🛡️ 4. Blindaje de Interfaz (Sovereign UI)

El frontend ya no es conversacional por defecto; es **gobernable**.

- **SystemStatus:** Reacciona a los estados `doubt` y `rejected`.
- **Decision Panel:** Renderiza botones físicos para confirmar rutas lógicas del backend.
- **LastIntent Tracking:** Garantiza que el mandato ejecutado sea idéntico a la intención evaluada.

---

## 🛑 Conclusión del Hito

ALEGRIA_OS v4.0 es estable porque sus componentes están desacoplados:

1. El **Kernel** ya no depende de que el LLM "se porte bien".
2. La **Identidad** ya no se pierde al cerrar la sesión.
3. La **Soberanía** ya no es un concepto; es un endpoint (`/execute`).

---

*Fin de la documentación de infraestructura.*
