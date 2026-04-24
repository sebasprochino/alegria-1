# README — UI de ALEGR-IA

**Guía para Developers (no creativos, no usuarios finales)**

> **Advertencia**  
> Esta UI no es una aplicación común.  
> No representa código, no representa arquitectura interna,  
> y no debe "optimizarse" según criterios clásicos de UX o frontend.

**La UI de ALEGR-IA es una superficie de control cognitivo.**

---

## 1. PRINCIPIO FUNDAMENTAL

La UI **NO** es:
- ❌ una representación del backend
- ❌ un reflejo de carpetas, servicios o endpoints
- ❌ una jerarquía técnica

La UI **SÍ** es:
- ✅ un mapa de acciones posibles del usuario
- ✅ un selector de modos mentales
- ✅ un sistema de bloques desacoplados

> **Si entendés la UI como "pantallas", vas a romper el sistema.**  
> **Si la entendés como "bloques vivos", funciona.**

---

## 2. CONCEPTO DE BLOQUE (CRÍTICO)

Un bloque UI es:
- una capacidad
- una acción
- un modo de interacción

Un bloque:
- puede existir o no
- puede clonarse
- puede desaparecer
- no debe romper el sistema si no está

### Regla de oro

> **Si un bloque no está, el sistema debe abrir igual.**

Nunca:
- hardcodear dependencias
- asumir existencia
- bloquear render por ausencia

---

## 3. AGENTES ≠ SERVICIOS

En la UI, los agentes no son microservicios, son **modos de trabajo**.

| Agente | Qué representa en UI |
|--------|---------------------|
| ANIMA | Modo productivo consciente |
| ANIMA ALEGRÍA | Modo conversacional libre |
| DEVELOPER | Operador técnico del sistema |
| RADAR | Investigación externa asistida |
| VEOSCOPE | Observación visual |
| TALLER | Producción de activos |

Cambiar de agente:
- ❌ no cambia el backend
- ❌ no cambia la sesión
- ✅ cambia el tipo de interacción

---

## 4. MENÚ HAMBURGUESA (NO ES DECORACIÓN)

El menú hamburguesa no es navegación.  
**Es un panel de herramientas externas.**

### Qué puede contener

- LLMs externos (ChatGPT, Gemini, etc.)
- Google / YouTube
- Plataformas de investigación
- Consolas técnicas
- Herramientas visuales

### Comportamiento esperado

- Abre WebView lateral
- Mantiene el chat activo
- Permite doble contexto
- Permite copiar / pegar / comparar

> **El menú hamburguesa es un acelerador cognitivo, no un menú clásico.**

---

## 5. WEBVIEW (PIEZA CLAVE)

El WebView:
- **NO** reemplaza el sistema
- **NO** absorbe lógica
- **NO** guarda estado propio

Sirve para:
- usar herramientas existentes
- investigar
- comparar
- traer info al sistema

> **ALEGR-IA no rehace herramientas que ya existen.**  
> **Las orquesta.**

---

## 6. TALLER / CAMPAÑAS / CONTENIDOS

Estas vistas no son editores.

### Flujo correcto

1. Conversación
2. Propuesta
3. Feedback humano
4. Aprobación explícita
5. Planificación (calendario)
6. Publicación

Nunca:
- auto-publicar
- deducir aprobación
- cerrar el flujo sin confirmación

---

## 7. DEVELOPER (ROL MAL ENTENDIDO)

DEVELOPER en UI:
- no es un generador de código automático
- no es un asistente simpático
- no es creativo

Es:
- auditor
- observador
- operador
- guardián de estabilidad

### Comportamiento

- Chat técnico
- Informes
- Alertas
- Diagnósticos

### Puede:

- abrir herramientas externas
- comparar modelos
- proponer cambios

### No puede:

- ejecutar sin orden
- deducir intención
- "mejorar" por su cuenta

---

## 8. ENDPOINTS Y CONECTORES (UI-FRIENDLY)

La UI no debe conocer endpoints específicos.

### Regla:

- los endpoints se llaman igual
- los conectores se activan o no
- la UI solo pregunta: **¿está activo este bloque?**

### Ejemplo mental:

```
Audio → activo / inactivo
Vision → activo / inactivo
Chat → activo / inactivo
```

Si no está:
- no se muestra
- no falla
- no rompe nada

---

## 9. CLONADO DE BLOQUES (PATRÓN OBLIGATORIO)

**Nunca editar "en caliente".**

### Flujo correcto:

1. Clonar bloque
2. Mostrar bloque nuevo
3. Probar
4. Ajustar
5. Reemplazar

Esto permite:
- experimentar sin romper
- comparar visualmente
- corregir rápido

---

## 10. LO QUE ESTÁ PROHIBIDO PARA DEVELOPERS

- 🚫 Optimizar "porque sí"
- 🚫 Reordenar UI por gusto
- 🚫 Inferir intención del usuario
- 🚫 Hacer dependencias ocultas
- 🚫 Pensar la UI como una app tradicional

---

## 11. FRASE FINAL (PARA EL EQUIPO)

> **ALEGR-IA no es una app que el usuario aprende.**  
> **Es un sistema que aprende a no estorbar al usuario.**

Si como developer sentís que:

> "esto se podría hacer más automático"

👉 frená  
👉 preguntá  
👉 no deduzcas
