# 🛠️ ALEGR-IA OS: Especificación Técnica de la Interfaz

## 1. Stack Tecnológico & Base

La interfaz de **ALEGR-IA OS** está construida sobre una base moderna, reactiva y de alto rendimiento, diseñada para la orquestación de sistemas de IA soberanos.

* **Core**: React 18+ (Vite como bundler)
* **Lenguaje**: TypeScript (Estricto) para tipado de protocolos.
* **Estilizado**: TailwindCSS v4 + CSS Vanilla (Custom Tokens).
* **Iconografía**: Lucide React.
* **Arquitectura**: **Master-Detail Reactivo** con navegación basada en estado (no-destructiva).

---

## 2. Arquitectura de Componentes (Nodos de Soberanía)

El sistema se organiza en un **Dynamic Content Area** orquestado por `App.jsx`, que conmuta entre los nodos principales según el ID de servicio seleccionado en el `Sidebar`:

### 🛰️ Nodo A: Radar (`RadarDashboard.tsx`)

* **Propósito**: Investigación profunda y rastreo de datos externos.
* **Layout**: Grid dinámico de herramientas (Cards de Neón).
* **Componentes Clave**:
  * **Terminal de Extracción**: Terminal interactiva para monitorear el progreso del análisis granular.
  * **Generador de Reportes**: Capacidad de exportar hallazgos en formato PDF ejecutivo.
* **Estética**: Modo ultra-oscuro con acentos `neon-cyan` y `glassmorphism`.

### 👨‍💻 Nodo B: Developer (`DeveloperConsole.tsx`)

* **Propósito**: Control de ingeniería y auditoría de bajo nivel.
* **Layout**: Interfaz de pestañas (Tabs) con visualización de datos en tiempo real.
* **Componentes Clave**:
  * **Manager Dependency**: Sub-agente especializado para investigar e instalar dependencias.
  * **Sandbox de Código**: Área para inyectar scripts directamente al Kernel.
  * **System Log Viewer**: Streaming de logs del backend filtrado.

### 🧠 Nodo C: Anima (`AnimaUI.tsx`)

* **Propósito**: Interacción conversacional bajo protocolo ACSP.
* **Innovación Técnica**:
  * **Modo Auditoría (Doble Exposición)**: Permite comparar el `rawAttempt` contra la respuesta depurada.
  * **Doubt Handler**: Renderizado interactivo de opciones cuando hay ambigüedad.

### 📂 Nodo D: Nexus (`DynamicWorkspace.tsx`)

* **Propósito**: Persistencia de estado y visualización de "Huellas de Decisión".
* **Integración**: Conexión con base de datos SQLite para mostrar el historial de mandatos.

### 👁️ Nodo E: Veoscanner (`VeoscannerUI.tsx`)

* **Propósito**: Inteligencia de marca y visión clínica audiovisual.
* **Funcionalidad**: Análisis de ADN Visual y Contexto Narrativo para generación de identidad.

---

## 3. Implementación del Protocolo ACSP (Frontend)

La interfaz no es un simple chat; es un **Executor de Mandatos**. Implementa el *Alegr-ia Coherence & Sovereignty Protocol* mediante el manejo de estados de respuesta:

| Estado | Comportamiento UI | Acción del Operador |
| :--- | :--- | :--- |
| **Authorized** | Renderiza la respuesta limpia inmediatamente. | Ninguna (Auditoría opcional). |
| **Doubt** | Bloquea la respuesta y despliega un panel de opciones lógicas. | Debe seleccionar una ruta de ejecución. |
| **Rejected** | Muestra una alerta de seguridad con el motivo del rechazo. | Reconocer y/o modificar intención. |

---

## 4. Sistema de Diseño (Design System)

### Tokens de Color (CSS Variables)

* `--deep-black`: `#0a0a0b` (Fondo principal)
* `--neon-cyan`: `#00f6ff` (Radar/Acciones seguras)
* `--neon-magenta`: `#ff00de` (Alertas/Dudas)
* `--surface-glow`: `rgba(0, 246, 255, 0.1)` (Efectos de elevación)

### Componentes de UI Propios

* **`.neon-card`**: Contenedores con borde reactivo y desenfoque de fondo.
* **`.wa-background`**: Patrón de fondo estilo WhatsApp invertido.
* **`.sidebar-light-pattern`**: Diseño "Premium Master" con patrón de doodles ligero.

---

## 5. Responsividad y UX Móvil

* **Sidebar Drawer**: En dispositivos móviles, el sidebar se oculta automáticamente al seleccionar un servicio.
* **Back Navigation**: Implementación de callbacks `onBack` para mantener el estado.
* **Touch Optimization**: Áreas de contacto mínimas de 44x44px.

---

## 6. Flujo de Datos (Data Flow)

1. **Input**: El usuario escribe en `AnimaUI` o `DeveloperConsole`.
2. **Dispatcher**: La intención se envía al `/rule-engine` del backend.
3. **Kernel Response**: El backend responde con un objeto de estado (Status: Doubt/Authorized).
4. **UI Update**: El frontend muta dinámicamente.

---

## 7. Mapa de la Arquitectura de Soberanía (File Tree)

```text
ALEGRIA_OS
+-- backend
|   +-- prisma (Base de Datos SQLite)
|   |   \-- schema.prisma
|   +-- src
|   |   +-- core (Kernel de Decisión)
|   |   |   \-- rule_engine.py (ACSP Core)
|   |   +-- services (Servicios del Sistema)
|   |   |   +-- anima.py
|   |   |   +-- nexus.py
|   |   |   +-- radar.py
|   |   |   \-- veoscanner.py
+-- frontend
|   +-- src
|   |   +-- anima (Nodo Conversacional)
|   |   |   \-- AnimaUI.tsx
|   |   +-- veoscanner (Visión Clínica)
|   |   |   \-- VeoscannerUI.tsx
|   |   +-- radar (Módulo Radar)
|   |   |   \-- RadarDashboard.tsx
|   |   +-- App.jsx (Orquestador Principal)
|   |   +-- index.css (Design System Tokens)
\-- START_ALEGRIA.bat
```

**Soberanía garantizada mediante arquitectura auditable.**
**ALEGR-IA OS — V1.0.0**
