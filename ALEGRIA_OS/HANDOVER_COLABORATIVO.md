# 🌐 ALEGR-IA OS: HANDOVER TÉCNICO Y ESTADO ACTUAL

Este documento está diseñado específicamente para proveer **contexto técnico, arquitectónico y operativo** a un AI Agent colaborador. ALEGR-IA OS no es una aplicación convencional. Contiene reglas de arquitectura no-negociables que debes entender antes de escribir una sola línea de código.

---

## 🏗️ 1. CONCEPTO Y ARQUITECTURA CORE: PROTOCOLO ACSP

ALEGR-IA OS es un **Centro de Mando Soberano e Inteligencia Orquestada**. Aplica el protocolo arquitectónico **ACSP 4.0** (Alegr-ia Coherence & Sovereignty Protocol), bajo el cual la IA es **estrictamente una planificadora/orquestadora** y **el humano es el único originador de mandatos ejecutivos**.

### Tecnologías:
- **Backend**: Python 3.10+ con FastAPI, Uvicorn (ASGI). Entorno en `.venv`.
- **Frontend**: React (18+) + Vite. Manejo de estado/routing, `TailwindCSS` / CSS Vanilla moderno.
- **Modelos integrados**: OpenAI, Groq para inferencia veloz / toma de decisiones algorítmica, y modelos locales gestionados.

### Directrices de Frontend (Reglas de Oro):
- **Desacoplamiento Absoluto UI/Backend (UI-FRIENDLY)**: La interfaz es un "Sistema de Bloques Vivos", NO "pantallas". Si un servicio back falla o no se conecta, la UI *no debe crashear*, simplemente asume que el "bloque" o "agente" está temporalmente inactivo.
- **Transiciones de "Modos" (Agentes)**: La barra lateral o selector invoca modos de trabajo: *Anima* (orquestador/consciente), *Developer* (técnico), *Radar* (búsqueda web), *Veoscope* (visión). Cambiar de agente *cambia el pipeline de interacción*, NO la topología del backend.
- **WebView & Herramientas Aisladas**: Las integraciones pesadas se muestran en WebViews o consolas laterales sin sobreescribir la memoria conversacional central.

---

## 🚨 2. FALLAS CRÍTICAS RECIENTES (Historial de Bug-Fixing)

Hemos atravesado ciclos intensos intentando estabilizar la comunicación y el pipeline operacional. A continuación las fallas que veníamos enfrentando (y que pueden resurgir):

1. **Bug Crítico - 500 Internal Server Error en `ContentMachineUI.tsx` (`/api/brand/all`)**:
   - Estuvimos recibiendo errores 500 al intentar acceder al endpoint `/api/brand/all`.
   - **Causa/Proceso**: Problemas profundos en el `BrandService` y el ruteador de `brand.py` en el backend relacionados a la serialización de JSON, fallas de parseo en lectura local de datos, o falta de manejo adecuado de rutas vacías. Esto rompía el renderizado de lista de la `ContentMachineUI`.
2. **Conectividad Backend y dependencias rotas (`ECONNREFUSED`)**:
   - El Vite Proxy fallaba al intentar dirigir tráfico al puerto 8000 porque Uvicorn no iniciaba.
   - **Causa/Proceso**: Problemas de dependencias en el `.venv` de Python con `pydantic_core` y `python-multipart`. Sumado a bloqueos en la inicialización de rutas del sistema (ej. endpoints como `/storage`).
3. **Flujo de Seguridad - Integración de API Keys**:
   - Inconvenientes con la inyección segura y dinámica de las keys (OpenAI, Groq) en el backend, sin acoplarlas al estado persistente o vulnerarlas en el transporte. 
4. **Layout Frontend - Bug de "Body Overflow Layout"**:
   - La disposición del UI en modos "Master-Detail" presentaba overflow excesivo fuera del viewport en `App.jsx`, ocultando el input chat cuando la consola mostraba mucho texto.
5. **Cajas Negras en el Pipeline de Ejecución**:
   - En el backend, las transiciones de estados (interpretación rápida de la *intention*, el chequeo en *Lexico*, *Nexus*, etc.) eran invisibles. Al fallar un step, no había rastro. 

---

## 🛠️ 3. TAREAS PENDIENTES Y REQUERIMIENTOS A COMPLETAR

Tu enfoque principal debe continuar sobre esta hoja de ruta, respetando las arquitecturas de soberanía:

### [A] Completar el Soberano Vision Pipeline (`ModalityRouter` / `Veoscanner`)
- **Meta**: Diferenciar orgánicamente las entradas visuales de las entradas textuales antes de enviarlas al LLM cascade.
- **Ejecución**: El "ModalityRouter" del back debe identificar si hay un attachment de imagen. Si es así, debe enrutar al `Veoscanner` service para extracción semántica **antes** de enviarlo a interpretación de intención, permitiendo al sistema reaccionar de manera diferente ante inputs bimodales. 

### [B] System Audit & Pipeline Tracing en la UI (`AnimaUI`)
- **Meta**: Eliminar definitivamente el estado de "Caja Negra" del OS.
- **Ejecución**: El Backend Executor ahora fue modificado para generar una traza secuencial de las operaciones (Lexicon matched, Nexus State Check, Radar query, LLM gen). Esto **tiene que conectarse a la interfaz Frontend `AnimaUI.tsx`** para que el Operador vea en *tiempo real* un Audit-Log de pasos (Step-by-step tree visual) antes de la resolución final.

### [C] Robustez en el `ContentMachineUI` y `BrandStudioUI`
- **Meta**: Garantizar que el manejo del módulo de marcas ("Brands") sea resiliente.
- **Ejecución**: Auditar los endpoints de `brand.py` (y sus consumos en el componente React `ContentMachineUI.tsx`). Si la API no retorna datos o JSON malformado, la UI **debe manejar los estados vacíos con gracia**, de manera premium y sin romper el layout, informando el estado "Doubt" (esperando comando) en el OS.

### [D] Routing Basado en Riesgo (`alert_level` integration)
- **Meta**: Orquestar señales tempranas en la UI.
- **Ejecución**: Conectar correctamente la señal backend `alert_level` evaluada por el `RuleEngine` con el `messageAdapter` del Frontend. Los resultados de alta incertidumbre/riesgo deben marcarse visualmente como `Rejected` (requiriendo acceso explícito vía `/execute`), mientras que operaciones informativas deben mostrar *confidence warnings* pasivos en diseño Modern UI / Tailwind.

---

## 📜 DIRECTRICES PARA EL AI AGENT COLABORADOR

1. **NO deduzcas intenciones ni "mejores" UX a tu propio juicio**. Si el requerimiento pide conectar una consola de desarrollo, **no la hagas auto-ejecutarse**. En `ALEGRIA_OS`, la IA propone, el usuario dicta la orden (click manual).
2. **Si modificas componentes (UI)**, respeta la estética oscura premium y animaciones (Glassmorphism, Lucide Icons, diseño High-End). El requerimiento no admite aplicaciones crudas.
3. **Clonado de Bloques UI**: Cuando modifiques la UI, utiliza el patrón de clonado (como estipula `README_UI.md`). Si vas a rehacer un panel, crea una versión provisoria e integra de forma atómica para no paralizar el flujo de trabajo existente.
4. Antes de tocar rutas en Python, verifica el estado del `venv` y no modifiques librerías globales de FastAPI a menos que sea estrictamente sobre `python-multipart` o `pydantic`.

> **Firma el Operador Principal.**  
> *Sovereignty by Design, Intelligence by Intent.*
