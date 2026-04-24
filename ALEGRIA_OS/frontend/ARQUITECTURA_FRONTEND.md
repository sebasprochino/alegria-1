# ALEGRIA_OS Frontend - Arquitectura Blindada v4.0

> ⚠️ **DOCUMENTO DE REFERENCIA CRÍTICO**  
> Este documento define la arquitectura oficial del frontend. NO modificar sin actualizar este documento.

---

## 📁 Estructura de Archivos

```
frontend/src/
├── App.jsx                    # 🎯 ORQUESTADOR PRINCIPAL
├── main.jsx                   # Entry point
├── index.css                  # Estilos globales + Tailwind
├── anima/                     # 🎤 MÓDULOS DE VOZ
│   ├── AnimaVoice.tsx         # TTS + STT (Text-to-Speech / Speech-to-Text)
│   ├── AnimaUI.tsx            # TTS legacy (solo lectura)
│   └── AlegrIAAnimaV4.tsx     # Prototipo alternativo (NO USAR en producción)
└── components/                # 🖼️ COMPONENTES UI
    ├── AnimaSidebar.jsx       # Navegación lateral
    ├── ChatInterface.jsx      # Vista principal de chat
    ├── NexusView.jsx          # Módulo de memoria
    ├── RadarView.jsx          # Módulo de discovery
    ├── DeveloperView.jsx      # Modo desarrollador
    ├── AppsView.jsx           # Vista de apps
    ├── SettingsPanel.jsx      # Configuración (incluye RejectionManager)
    ├── RejectionManager.tsx   # Gestor de rechazos éticos
    ├── SystemState.jsx        # Indicador de estado del sistema
    └── AnimaPresence.jsx      # Efectos visuales ambientales
```

---

## 🎯 App.jsx - Orquestador Principal

### Estados Críticos (NO ELIMINAR)

```jsx
const [activeView, setActiveView] = useState('chat');     // Navegación
const [sidebarOpen, setSidebarOpen] = useState(false);    // Sidebar mobile
const [messages, setMessages] = useState([]);             // 📌 CHAT PERSISTENTE
const [systemStatus, setSystemStatus] = useState('idle'); // idle/thinking/doubt/rejection
```

### Router de Vistas

| Vista | Componente | Props Requeridas |
|-------|------------|------------------|
| `chat` | `ChatInterface` | `messages`, `setMessages`, `setSystemStatus` |
| `nexus` | `NexusView` | ninguna |
| `radar` | `RadarView` | ninguna |
| `developer` | `DeveloperView` | ninguna |
| `apps` | `AppsView` | ninguna |
| `settings` | `SettingsPanel` | ninguna |

---

## 💬 ChatInterface.jsx - Interfaz de Chat

### Props OBLIGATORIAS

```jsx
export default function ChatInterface({ 
  messages = [],      // ⚠️ SIEMPRE con default []
  setMessages         // Función para actualizar mensajes
}) 
```

### Componentes Internos

1. **Header** - Muestra "Sinapsis Directa" con estado de conexión
2. **Messages Area** - Renderiza mensajes con ReactMarkdown
3. **Input Area** - Textarea + botón enviar

### 🎤 Integración de Voz (AnimaVoice)

```jsx
// Línea ~117 - NO ELIMINAR
<AnimaVoice messages={messages} onVoiceInput={sendMessage} />
```

---

## 🎤 AnimaVoice.tsx - Control de Voz

### Funcionalidades

| Función | Descripción |
|---------|-------------|
| **TTS (Text-to-Speech)** | Lee automáticamente las respuestas de Anima |
| **STT (Speech-to-Text)** | Permite hablar en lugar de escribir |

### Botones que DEBE mostrar

1. **🔊 Voz ON / 🔇 Voz OFF** - Toggle para activar/desactivar lectura
2. **🎤 Hablar / Escuchando...** - Botón para dictar mensajes

### Props OBLIGATORIAS

```tsx
interface Props {
  messages: Message[];           // Array de mensajes del chat
  onVoiceInput: (text: string) => void;  // Callback para enviar mensaje dictado
}
```

---

## 🧭 AnimaSidebar.jsx - Navegación

### Módulos Configurados

```jsx
const MODULE_CONFIG = [
  { id: 'dashboard', label: 'Centro de Mando', view: 'dashboard' },
  { id: 'chat', label: 'Sinapsis (Chat)', view: 'chat' },
  { id: 'developer', label: 'Developer Mode', view: 'developer' },
  { id: 'nexus', label: 'Nexus Memory', view: 'nexus' },
  { id: 'radar', label: 'Radar Discovery', view: 'radar' },
  { id: 'status', label: 'Estado del Sistema', view: 'status' },
  { id: 'settings', label: 'Configuración', view: 'settings' },
];
```

---

## ⚠️ REGLAS DE BLINDAJE

### ❌ NUNCA HACER

1. Eliminar `messages = []` default en ChatInterface
2. Quitar AnimaVoice del ChatInterface
3. Cambiar props de ChatInterface sin actualizar App.jsx
4. Mover estados de App.jsx a componentes hijos
5. Modificar MODULE_CONFIG sin agregar vista correspondiente

### ✅ SIEMPRE HACER

1. Props con defaults para arrays: `{ array = [] }`
2. Pasar `messages` y `setMessages` al chat
3. Actualizar este documento ante cambios de arquitectura
4. Verificar que AnimaVoice tenga sus 2 botones visibles

---

## 🔧 Verificación Rápida

### Chat Funcional

- [ ] AnimaVoice visible con 2 botones
- [ ] Mensajes persisten al cambiar de vista
- [ ] Enter envía mensaje
- [ ] Respuestas se leen automáticamente (si voz ON)

### Navegación Funcional

- [ ] Sidebar muestra todos los módulos
- [ ] Cambio de vista funciona
- [ ] Título de pestaña cambia según vista

---

*Última actualización: 2025-12-24*
