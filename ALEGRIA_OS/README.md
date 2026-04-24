# 🌐 ALEGR-IA OS
**Centro de Mando Soberano e Inteligencia Orquestada**

ALEGR-IA OS no es un asistente conversacional estándar. Es un **Sistema Operativo Visual de Inteligencia Soberana**. Su arquitectura (ACSP - Alegr-ia Coherence & Sovereignty Protocol) garantiza que la inteligencia artificial sirva únicamente como un "planificador estratégico" (Radar, Nexus, Ideas), pero sea el **Operador Humano** quien mantenga y despache el control sobre las acciones técnicas subyacentes.

---

## ⚙️ Requisitos Previos

Antes de arrancar, asegurate de tener instalados:
1. **Python 3.10+** (Asegurate de que `python` esté registrado en tus variables de entorno PATH).
2. **Node.js (v18 o superior)** y **npm** (Para cargar el motor visual).

---

## 🚀 Despliegue Rápido (Local)

### Opción A (Método Automático Windows)

Si estás en un ecosistema de Windows, simplemente dá doble click o ejecutá desde tu terminal:
```cmd
START_ALEGRIA.bat
```
*Este script intentará arrancar el Backend y Frontend de forma paralela en dos consolas diferentes.*

---

### Opción B (Método Manual Paso a Paso)

Si el script automático no te sirve, el entorno virtual no fue copiado o estás en Unix/Mac, seguí estos tres pasos:

#### 1. Instalar y Levantar el Motor Lógico (Backend)
Abrí tu terminal en la raíz del proyecto y ejecutá:

```sh
cd backend
# 1. Crear Entorno Virtual
python -m venv venv

# 2. Activar entorno virtual
# En Windows:
.\venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# 3. Instalar dependencias puras del Kernel
pip install -r requirements.txt

# 4. Iniciar el Núcleo (Uvicorn sobre puerto 8000)
python src/main.py
```

#### 2. Instalar y Levantar el Engine Visual (Frontend)
Abrí **otra ventana de terminal** en la raíz del proyecto y ejecutá:

```sh
cd frontend

# 1. Instalar la estructura de módulos de Node
npm install

# 2. Levantar el motor de renderizado (Vite en puerto 5173 / Proxy 8000)
npm run dev
```

#### 3. Acceder al Centro de Mando
Una vez que ambas bases estén corriendo de forma estable, abrí en tu navegador:
👉 **[http://localhost:5173/](http://localhost:5173/)**

---

## 🧠 Arquitectura Cognitiva (Novedades)
* **Kernel & Radar:** La red sensora realiza scraping y lecturas de bases de datos delegadas al SDK orgánico de Python.
* **Separación Estricta:** Un input de texto como "Abrir YouTube" no es tratado como un parseo LLM frágil, ejecuta la delegación de kernel local `system.navigate` sin intermediarios usando un *TOL Bypass*.
* **Web View Integrado:** Los resultados de navegación o herramientas externas pueden manifestarse en consolas o iframes flotantes dentro de la UI, reteniéndote en todo momento dentro del Centro de Mando.

> **¡Tu infraestructura está desplegada, disfrutá del nodo operativo!**
