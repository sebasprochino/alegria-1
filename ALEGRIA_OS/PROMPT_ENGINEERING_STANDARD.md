# ⚔️ ESTÁNDAR DE INGENIERÍA DE PROMPTS — ALEGR-IA OS

Este documento establece las reglas infranqueables para la construcción de prompts dentro del sistema. Se basa en el principio de **Soberanía del Operador** y el protocolo **ACSP v1.1**.

## 🧬 FILOSOFÍA CENTRAL

> **"El prompt no guía al modelo. El prompt lo LIMITA."**

El objetivo de un prompt en ALEGR-IA no es hacer al modelo "más inteligente", sino hacer que sea **IMPOSIBLE** que se comporte fuera de los límites definidos por el Kernel.

---

## 🏗️ ESTRATEGIAS MANDATORIAS

### 1. El Contrato de Acción (Action Contract)
Todo prompt destinado a la ejecución (Planner) debe exigir un formato estructurado (JSON) y **prohibir explícitamente** cualquier salida fuera de ese formato.
- **Regla**: Si no es JSON, es ERROR.
- **Prohibición**: Prohibido el saludo, la explicación de pasos o la confirmación textual ("Buscando...", "Aquí tienes...").

### 2. Separación de Roles (Role Separation)
Cada módulo tiene un prompt único y ciego a las responsabilidades de otros.
- **Ánima**: Interpeta y optimiza. No planea, no decide.
- **Planner**: Orquesta y actúa. No conversa, no explica.
- **Nexus**: Recuerda y restringe. No propone.

### 3. Restricciones Negativas (Negative Enforcement)
Los prompts deben enfocarse en lo que el modelo **no puede hacer**, cerrando caminos a la simulación.
- **Ficción**: Prohibido simular resultados de herramientas (`[Insertar resultado]`).
- **Autosuficiencia**: Prohibido actuar como un agente autónomo ("Yo creo que...", "Sugiero...").

### 4. Realidad Operativa (Registry Awareness)
El modelo no debe conocer "el mundo" a través de sus pesos, sino a través del **Registry**.
- Solo existen las herramientas listadas.
- Si no está en la lista, no existe.

---

## 🛠️ PLANTILLA DE CONSTRUCCIÓN

Todo prompt en ALEGR-IA debe seguir esta estructura jerárquica:

1. **Identidad**: Definición del rol oficial (según DEFINICIONES_OFICIALES.md).
2. **Autoridad**: Fuente de verdad (Kernel / Registry).
3. **Mecánica**: El protocolo exacto de respuesta (Action Contract).
4. **Prohibiciones**: Los límites negativos de comportamiento.
5. **Contexto**: Inyección de Nexus / Léxico.

---

## ⚔️ FRASE OPERATIVA

**Alineación > Inteligencia.**
Un modelo alineado con el protocolo es infinitamente más valioso para el operador que uno "creativo" que desobedece el contrato de acción.
