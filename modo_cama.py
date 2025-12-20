import os
import socket
import subprocess
from pathlib import Path

# ==========================================
# 1. INTERFAZ MÓVIL (APP.JSX)
# ==========================================
# Cambios clave: 
# - API_URL dinámica (usa la IP de la red, no localhost)
# - Diseño responsivo para dedos (touch-friendly)
MOBILE_APP_CODE = """import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Zap, Activity, Radio } from 'lucide-react';

// TRUCO: Detecta automáticamente la IP de tu PC
const API_URL = `http://${window.location.hostname}:8000`;

function App() {
  const [status, setStatus] = useState({});
  const [messages, setMessages] = useState([
    { role: 'system', content: '🛌 MODO CAMA ACTIVADO. ¿Qué construimos hoy?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  // Monitor de Estado (Simplificado para Celular)
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
      // Si el usuario pide "crear", usamos al Developer
      if (input.toLowerCase().startsWith("/crear") || input.toLowerCase().includes("crea un")) {
         const res = await axios.post(`${API_URL}/developer/create`, {
            module_name: "mobile_request", // Nombre temporal
            description: input,
            tech_tags: "python"
         });
         setMessages(prev => [...prev, { role: 'ai', content: `✅ CÓDIGO GENERADO:\\n${res.data.message || "Listo."}\\n(Revisa tu PC)` }]);
      } else {
         // Conexión con ANIMA (Cerebro)
         // Aquí pronto conectaremos el endpoint real de charla
         setMessages(prev => [...prev, { role: 'ai', content: `🦋 Anima: Recibido. (Modo Programación Remota)` }]);
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'error', content: '❌ Error: No llego a la PC.' }]);
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-[100dvh] bg-slate-950 text-slate-200 font-sans">
      
      {/* HEADER MÓVIL */}
      <header className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex justify-between items-center shadow-md z-10">
        <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${status.anima === 'active' ? 'bg-green-400 animate-pulse' : 'bg-red-500'}`}></div>
            <h1 className="font-bold text-lg tracking-wider text-indigo-400">ALEGRIA<span className="text-xs text-slate-500 ml-1">MOBILE</span></h1>
        </div>
        <div className="flex gap-1">
            {/* Solo mostramos indicadores clave en el celular */}
            <Activity size={16} className={status.nexus === 'active' ? 'text-green-500' : 'text-slate-600'} />
            <Radio size={16} className={status.radar === 'active' ? 'text-green-500' : 'text-slate-600'} />
            <Zap size={16} className={status.developer === 'active' ? 'text-yellow-400' : 'text-slate-600'} />
        </div>
      </header>

      {/* CHAT AREA */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-950/50">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none' 
                : msg.role === 'error'
                  ? 'bg-red-900/40 text-red-200 border border-red-800'
                  : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-none'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && <div className="text-xs text-slate-500 ml-4 animate-pulse">Pensando...</div>}
        <div ref={endRef} />
      </main>

      {/* INPUT AREA (Optimizado para pulgares) */}
      <footer className="p-3 bg-slate-900 border-t border-slate-800 pb-safe">
        <div className="flex gap-2 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ordena desde la cama..."
            className="flex-1 bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3 focus:outline-none focus:border-indigo-500 text-base max-h-32 min-h-[50px] resize-none"
            rows={1}
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim()}
            className="bg-indigo-600 h-[50px] w-[50px] rounded-full flex items-center justify-center shadow-lg active:scale-95 transition-transform"
          >
            <Send size={20} color="white" />
          </button>
        </div>
      </footer>
    </div>
  )
}

export default App
"""

def configurar_modo_cama():
    print("🛌 PREPARANDO ENTORNO PARA PROGRAMACIÓN REMOTA...")

    # 1. Obtener IP Local
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # 2. Actualizar App.jsx para móviles
    frontend_path = Path("frontend/src/App.jsx")
    if frontend_path.exists():
        with open(frontend_path, "w", encoding="utf-8") as f:
            f.write(MOBILE_APP_CODE)
        print("✅ Interfaz adaptada para celular.")
    else:
        print("❌ Error: No encuentro frontend/src/App.jsx")

    # 3. Configurar Vite para aceptar conexiones externas
    # (Esto ya lo hacemos con el comando --host al arrancar, pero aseguramos package.json)
    package_json_path = Path("frontend/package.json")
    if package_json_path.exists():
        with open(package_json_path, "r", encoding="utf-8") as f:
            content = f.read()
        if '"dev": "vite"' in content and '"dev": "vite --host"' not in content:
            content = content.replace('"dev": "vite"', '"dev": "vite --host"')
            with open(package_json_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ Vite configurado para red Wifi.")

    print("\n📱 INSTRUCCIONES PARA TU CELULAR:")
    print("---------------------------------------")
    print(f"1. Asegúrate que tu celular esté en el mismo WIFI que esta PC.")
    print(f"2. Abre Chrome/Safari en tu celular.")
    print(f"3. Escribe esta dirección exacta:")
    print(f"\n   👉 http://{local_ip}:5173\n")
    print("---------------------------------------")
    
    # 4. Lanzar todo
    print("🚀 Reiniciando sistemas...")
    
    # Matar procesos viejos
    subprocess.run("taskkill /F /IM python.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Iniciar Backend
    backend_cmd = r".\backend\venv\Scripts\python.exe anima_guardian.py"
    subprocess.Popen(f'start "CEREBRO" {backend_cmd}', shell=True)
    
    # Iniciar Frontend (con host expuesto)
    frontend_cmd = "cd frontend && npm run dev"
    subprocess.Popen(f'start "VISTA - MODO WIFI" cmd /k "{frontend_cmd}"', shell=True)

if __name__ == "__main__":
    configurar_modo_cama()