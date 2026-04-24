---

## 🌍 Árbol del Proyecto (Estructura de Soberanía)

```text
ALEGRIA_OS/
├── backend/                # Núcleo Operativo (Python/FastAPI)
│   ├── src/
│   │   ├── alegria_sdk/    # KERNEL: Constitución ACSP v1.1 (Soberanía Criptográfica)
│   │   ├── core/           # GOBIERNO: Wrapper del Kernel, RuleEngine, Seguridad
│   │   ├── os/             # ECONOMÍA: Pipeline Creativo, Dynamic Planner, Evolución
│   │   ├── services/       # SERVICIOS: Nexus (Memoria), Radar (Busqueda), Anima (Voz)
│   │   ├── routes/         # API: Despachadores de rutas (FastAPI Routers)
│   │   └── server.py       # Punto de entrada del servidor
│   └── .env                # Configuraciones de llaves y entorno
│
├── frontend/               # Interfaz de Operador (React/Vite)
│   ├── src/
│   │   ├── anima/          # Componentes de la Consola Anima (UI principal)
│   │   ├── components/     # Widgets de sistema (DynamicWorkspace, NexusView)
│   │   ├── core/           # Configuración y Registro de UI
│   │   ├── utils/          # Adapters y API client (Sincronización de protocolos)
│   │   └── App.jsx         # Orquestador visual y máquina de estados UI
│   └── index.html          # Entrada Web y Meta-tags de Marca
└── .skills/                # Conocimiento especializado para el asistente
```

---

## 🧩 Reglas de Transición de Modos

Para eliminar toda ambigüedad operativa, el sistema diferencia entre tres estados de interacción. La transición entre ellos es determinista y supervisada por el Kernel:

### 1. Modo Conversación
- **Criterio**: Interacciones sin un objetivo técnico o creativo explícito (ej. "hola", "¿cómo estás?").
- **Flujo**: `/chat` → Kernel bloquea la activación del pipeline → Respuesta conversacional.
- **Estado**: No genera `intention_id` ejecutable.

### 2. Modo Intención
- **Criterio**: Se activa al detectar un **Objetivo Explícito**, un **Pedido de Acción** o una **Estructura Requerida** (ej. "Crea un plan", "Investiga X").
- **Flujo**: `/chat` → Kernel propone Paths estratégicos → Interfaz muestra opciones de decisión.
- **Estado**: Genera `intention_id` criptográfico y entra en fase de bloqueo de seguridad.

### 3. Modo Ejecución
- **Criterio**: Se activa únicamente tras el **Mandato Humano** (Select).
- **Flujo**: `/execute` → El Kernel autoriza el ID → Se activa la "Economía Creativa" (Pipeline operativo).
- **Estado**: Genera resultado final firmado.

> [!IMPORTANT]
> **La Regla de la Entrada Universal**: Incluso en Modo Conversación, TODA interacción pasa físicamente por los filtros del Kernel. El Kernel nunca se omite; solo decide si la intención califica o no para activar el pipeline de ejecución profunda.

---

## 🔄 Interacción Interfaz-Backend (Ciclo ACSP)

La comunicación entre el operador y el sistema no es un chat libre, es un **Ciclo de Validación Soberana**:

### Paso 1: Detección de Intención (`/chat`)
1. El usuario envía texto desde `App.jsx`.
2. El `sendMessage` (API) despacha a `/anima/chat`.
3. **Backend**: El `SovereignKernel` recibe la intención.
   - `Lexico` filtra el ruido.
   - `Nexus` valida contra constraints.
   - Envía un objeto `decision` con `intention_id` y `paths` (opciones).
4. **Frontend**: El `messageAdapter.ts` transforma la respuesta en un componente de "Decisión".

### Paso 2: Autorización del Operador (`/execute`)
1. El usuario hace clic en una opción en `AnimaUI.tsx`.
2. `App.jsx` dispara `handleExecuteCommand` enviando el `intention_id`.
3. **Backend**: El Kernel valida que el ID sea legítimo.
   - Si es válido, transiciona al estado `ready`.
   - Se activa el `run_pipeline` del OS.
4. **Respuesta**: El sistema devuelve el resultado final firmado con un hash de integridad.

---

## 🏛️ ALEGRIA OS: Arquitectura de Soberanía e Inteligencia Operativa

## 📖 Visión General
**ALEGRIA OS** no es simplemente un asistente de IA; es un **Sistema Operativo SOBERANO** diseñado bajo el protocolo **ACSP 4.0 (ALEGR-IA Cognitive Sovereignty Protocol)**. Su arquitectura está optimizada para la orquestación de marca, la inteligencia de sistemas y el desarrollo de aplicaciones, manteniendo siempre al operador humano como la única fuente legítima de lógica y decisión.

---

## 🏗️ Los Cinco Pilares del Sistema

### 1. La Constitución (ALEGR-IA SDK v1.1)
El núcleo legal del sistema. Define las reglas inamovibles de cómo el sistema debe interactuar con el operador.
- **Protocolo ACSP v1.1**: Proceso determinista de `Process` → `Select` → `Execute`.
- **Lexico**: Filtro de ambigüedad que impide ejecuciones basadas en órdenes vagas.
- **Nexus (Guard)**: Valida que la salida de la IA respete estrictamente las restricciones impuestas.

### 2. El Gobierno (Sovereign Kernel)
La capa de mediación que aplica la Constitución sobre el sistema operativo.
- **Validación de Intención**: El Kernel utiliza el SDK para proponer caminos de ejecución (Paths).
- **Autorización Criptográfica**: Genera y valida `intention_id` y hashes de integridad para cada mandato.
- **Control de Estado**: Bloquea físicamente el motor de ejecución (`Executor`) hasta que se reciba el mandato del operador.

### 3. La Economía (OS Creative Pipeline)
Donde ocurre la magia y el procesamiento pesado. Una vez que el Gobierno autoriza, el OS ejecuta con máxima potencia.
- **Dynamic Planner**: Un orquestador nivel "Planner" que fragmenta tareas complejas.
- **Creative System**: Pipeline de generación de contenido, estrategia y código.
- **Multiverse Logic**: Capacidad de generar y comparar múltiples iteraciones creativas.

### 4. Dirección Estética (CDM)
El "Chief Design Member" integrado.
- **Filtro de Salida**: Analiza el contenido generado no solo por veracidad, sino por calidad estética y tono de marca.
- **Aesthetic Scoring**: Evalúa si el resultado es digno de ser presentado al operador.

### 5. Historia Verificable (Telemetry & Audit)
La memoria inalterable de cada decisión.
- **Chain of Intent**: Traza de hashes que une la intención humana con el resultado final.
- **Decision Log**: Registro transparente de por qué el sistema eligió un camino u otro (Auditoría Step-by-Step).

---

## 🛠️ Stack Tecnológico

### Backend (Python / FastAPI)
- **FastAPI**: Servidor de alta performance para orquestación en tiempo real.
- **ALEGR-IA SDK**: El motor de soberanía (Kernels Python).
- **Uvicorn**: Servidor ASGI con soporte de auto-recarga.
- **Integraciones**: Groq (Gobernanza veloz), Ollama (Soberanía Local), OpenAI/Anthropic (Músculo creativo).

### Frontend (React / Vite)
- **Architecture Master-Detail**: Interfaz premium con navegación enfocada en módulos operativos.
- **AnimaUI**: Consola de operador de alta fidelidad con inspección de trazas en tiempo real.
- **Lazy Loading**: Fragmentación de código por módulos para carga instantánea (LCP optimizado).
- **Lucide Icons & Tailwind Modern**: Estética oscura, premium y profesional.

---

## 🔄 Flujo del Protocolo (ACSP 4.0)

1.  **Intención**: El operador ingresa un objetivo (e.g., "Crea una campaña de marca para X").
2.  **Procesamiento (Kernel)**:
    - `Lexico` limpia el "humo" emocional.
    - `Anima (SDK)` genera 2-4 caminos estratégicos.
    - El sistema se bloquea en estado `Doubt`.
3.  **Mandato (Humano)**: El operador selecciona el `Path` deseado.
4.  **Ejecución (OS Pipeline)**:
    - Se activa el `run_pipeline`.
    - El sistema "piensa" (Thinking) y ejecuta los pasos técnicos.
5.  **Filtrado (CDM)**: Se evalúa la calidad y coherencia.
6.  **Entrega**: El resultado se presenta firmado con un hash de integridad.

---

## 🛰️ Módulos Operativos

- **Radar**: Sonda de investigación externa (Web Search + Scraping).
- **Anima**: Orquestador de comunicación y gestión de intención.
- **Nexus**: Memoria estructural y base de conocimientos soberana.
- **Developer**: Entorno de generación de código y despliegue iterativo.
- **Genesis / VEOscope**: Herramientas de diagnóstico de marca y estrategia.

---

## 📜 Declaración de Soberanía
En ALEGRIA OS, la inteligencia artificial es el **músculo**, pero la inteligencia humana es la **voluntad**. El sistema está programado para ser incapaz de autorizarse a sí mismo.

**"Sovereignty by Design, Intelligence by Intent."**
