import os
import subprocess
from pathlib import Path

# ==========================================
# CÓDIGO DE LA INTERFAZ (CORREGIDO)
# ==========================================

PACKAGE_JSON = """{
  "name": "alegria-ui",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "lucide-react": "^0.290.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.15",
    "@types/react-dom": "^18.2.7",
    "@vitejs/plugin-react": "^4.0.3",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.27",
    "tailwindcss": "^3.3.3",
    "vite": "^4.4.5"
  }
}"""

VITE_CONFIG = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173
  }
})"""

TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}"""

POSTCSS_CONFIG = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}"""

INDEX_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ALEGRIA OS</title>
    <style>body { background-color: #0f172a; color: white; }</style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>"""

MAIN_JSX = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)"""

INDEX_CSS = """@tailwind base;
@tailwind components;
@tailwind utilities;

::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #1e293b;
}
::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
"""

APP_JSX = """import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Terminal, Cpu, Activity, Database, Eye, Globe } from 'lucide-react';

const API_URL = 'http://localhost:8000';

function App() {
  const [status, setStatus] = useState({});
  const [messages, setMessages] = useState([
    { role: 'system', content: 'ALEGRIA OS v1.0 [ONLINE]. Esperando input...' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await axios.get(`${API_URL}/system/status`);
        setStatus(res.data);
      } catch (e) {
        console.error("Offline");
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      if (input.startsWith("/crear")) {
         const res = await axios.post(`${API_URL}/developer/create`, {
            module_name: "demo_module",
            description: input.replace("/crear", ""),
            tech_tags: "python"
         });
         setMessages(prev => [...prev, { role: 'ai', content: `🔧 Developer: ${res.data.message || res.data.error}` }]);
      } else {
         setMessages(prev => [...prev, { role: 'ai', content: `🦋 Anima: Recibí tu mensaje: "${input}". (Endpoint de chat en construcción)` }]);
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'error', content: '❌ Error de conexión con el Núcleo.' }]);
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const StatusIcon = ({ name, active }) => {
    const color = active === 'active' ? 'text-green-400' : 'text-red-500';
    const icons = {
      developer: <Terminal size={16} />,
      nexus: <Database size={16} />,
      radar: <Globe size={16} />,
      anima: <Eye size={16} />,
      gateway: <Activity size={16} />,
      default: <Cpu size={16} />
    };
    return (
      <div className={`flex items-center gap-2 ${color} bg-slate-800 px-3 py-1 rounded-full text-xs font-mono uppercase border border-slate-700`}>
        {icons[name] || icons.default}
        <span>{name}</span>
        <div className={`w-2 h-2 rounded-full ${active === 'active' ? 'bg-green-400 animate-pulse' : 'bg-red-500'}`}></div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-200 font-sans selection:bg-indigo-500 selection:text-white">
      <header className="p-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur flex flex-wrap gap-3 items-center shadow-lg">
        <h1 className="text-lg font-bold tracking-wider mr-4 text-indigo-400">ALEGRIA<span className="text-slate-500">_OS</span></h1>
        {Object.entries(status).map(([key, val]) => (
          <StatusIcon key={key} name={key} active={val} />
        ))}
      </header>

      <main className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-2xl shadow-md leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none' 
                : msg.role === 'error'
                  ? 'bg-red-900/50 text-red-200 border border-red-800'
                  : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none'
            }`}>
              {msg.role === 'system' && <div className="text-xs text-indigo-300 font-mono mb-1">SYSTEM NOTIFICATION</div>}
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
             <div className="bg-slate-800 p-4 rounded-2xl rounded-tl-none border border-slate-700 flex gap-2">
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-200"></div>
             </div>
          </div>
        )}
        <div ref={endRef} />
      </main>

      <footer className="p-4 bg-slate-900 border-t border-slate-800">
        <div className="max-w-4xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe a Anima..."
            className="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder-slate-600"
            autoFocus
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed p-3 rounded-xl transition-colors shadow-lg shadow-indigo-900/20"
          >
            <Send size={20} />
          </button>
        </div>
        <div className="text-center mt-2 text-[10px] text-slate-600 font-mono">
           ALEGRIA OS v1.0 &bull; Running on Localhost
        </div>
      </footer>
    </div>
  )
}

export default App
"""

def install_frontend():
    print("\n🎨 REPARANDO INTERFAZ VISUAL...\n")
    
    # CAMBIO IMPORTANTE: Apuntamos directamente a "frontend" sin prefijos raros
    base_dir = Path("frontend")
    src_dir = base_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "package.json": PACKAGE_JSON,
        "vite.config.js": VITE_CONFIG,
        "tailwind.config.js": TAILWIND_CONFIG,
        "postcss.config.js": POSTCSS_CONFIG,
        "index.html": INDEX_HTML,
        "src/main.jsx": MAIN_JSX,
        "src/index.css": INDEX_CSS,
        "src/App.jsx": APP_JSX
    }

    for filename, content in files.items():
        path = base_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 Escrito: {path}")

    print("\n✅ Archivos colocados en el lugar correcto.")
    print("---------------------------------------")
    print("Ahora ejecuta estos comandos en orden:")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm run dev")
    print("---------------------------------------")

if __name__ == "__main__":
    install_frontend()