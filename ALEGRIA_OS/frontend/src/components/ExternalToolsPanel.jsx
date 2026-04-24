import React, { useState } from 'react';
import { X, ExternalLink, RefreshCw, Cpu, Layout, MessageSquare, Clipboard, Search } from 'lucide-react';

const EXTERNAL_TOOLS = [
  { id: 'chatgpt', name: 'ChatGPT', url: 'https://chatgpt.com', icon: '🤖', needsExternal: true },
  { id: 'gemini', name: 'Google Gemini', url: 'https://gemini.google.com', icon: '✨', needsExternal: true },
  { id: 'claude', name: 'Claude AI', url: 'https://claude.ai', icon: '🧠', needsExternal: true },
  { id: 'youtube', name: 'YouTube', url: 'https://www.youtube.com', icon: '📺', needsExternal: true },
  { id: 'google', name: 'Google Search', url: 'https://www.google.com', icon: '🔍', needsExternal: true },
  { id: 'github', name: 'GitHub', url: 'https://github.com', icon: '🐙', needsExternal: false }, // GitHub a veces permite
];

export default function ExternalToolsPanel({ isOpen, onClose }) {
  const [activeTool, setActiveTool] = useState(null);
  const [observation, setObservation] = useState('');

  if (!isOpen) return null;

  const handleLaunch = (tool) => {
    setActiveTool(tool);
    if (tool.needsExternal) {
      window.open(tool.url, '_blank', 'width=1000,height=800,left=200,top=100');
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full md:w-[500px] lg:w-[600px] bg-[#F5F5F4] border-l border-black/5 z-[200] flex flex-col shadow-2xl animate-slide-in-right font-sans tracking-tight">
      
      {/* HEADER — ESTILO SOBERANO */}
      <div className="p-4 flex items-center justify-between border-b border-black/5 bg-white">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-black flex items-center justify-center text-white">
            <Layout size={16} />
          </div>
          <h2 className="text-[11px] font-bold uppercase tracking-[0.2em] text-neutral-400">Acelerador Externo</h2>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-neutral-100 rounded-full transition-colors text-neutral-400">
          <X size={18} />
        </button>
      </div>

      {/* SELECTOR DE HERRAMIENTAS */}
      <div className="p-4 flex gap-2 overflow-x-auto no-scrollbar border-b border-black/5 bg-white/50">
        {EXTERNAL_TOOLS.map(tool => (
          <button
            key={tool.id}
            onClick={() => handleLaunch(tool)}
            className={`flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-full border text-[11px] font-medium transition-all ${
              activeTool?.id === tool.id 
                ? 'bg-black text-white border-black' 
                : 'bg-white border-black/5 text-neutral-500 hover:border-black/10'
            }`}
          >
            <span>{tool.icon}</span>
            <span>{tool.name}</span>
          </button>
        ))}
      </div>

      {/* ÁREA DE TRABAJO (Doble Contexto) */}
      <div className="flex-1 flex flex-col overflow-hidden bg-[#F5F5F4]">
        {!activeTool ? (
          <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
            <Cpu className="text-neutral-200 mb-4" size={48} />
            <h3 className="text-neutral-800 font-light text-lg mb-2">Seleccioná un contexto externo</h3>
            <p className="text-[11px] text-neutral-400 max-w-xs leading-relaxed uppercase tracking-widest">
              Las herramientas externas se abren en ventanas independientes para acelerar tu flujo sin bloquear a Ánima.
            </p>
          </div>
        ) : (
          <div className="flex-1 flex flex-col p-6 space-y-6 overflow-y-auto">
            
            {/* CARD DE ESTADO EXTERNO */}
            <div className="bg-white border border-black/5 rounded-3xl p-6 shadow-sm flex flex-col items-center text-center">
              <div className="text-3xl mb-4">{activeTool.icon}</div>
              <h4 className="text-neutral-800 font-bold mb-1">{activeTool.name} Activo</h4>
              <p className="text-[11px] text-neutral-400 mb-4 uppercase tracking-widest">Ventana Externa Orquestada</p>
              
              <button 
                onClick={() => window.open(activeTool.url, '_blank')}
                className="flex items-center gap-2 px-6 py-2 bg-neutral-100 hover:bg-neutral-200 rounded-full text-[11px] font-bold transition-all"
              >
                <ExternalLink size={14} /> Re-lanzar Herramienta
              </button>
            </div>

            {/* PORTAL DE DATOS (Input para el usuario) */}
            <div className="flex-1 flex flex-col space-y-3">
              <div className="flex items-center gap-2 text-[10px] text-neutral-400 font-bold uppercase tracking-widest px-2">
                <Clipboard size={12} />
                Captura de Hallazgos
              </div>
              <textarea 
                value={observation}
                onChange={(e) => setObservation(e.target.value)}
                placeholder="Pegá resultados, datos o ideas de la herramienta externa para que Ánima los integre..."
                className="flex-1 bg-white border border-black/5 rounded-[32px] p-6 text-sm text-neutral-800 outline-none focus:border-black/10 transition-all resize-none shadow-sm font-light leading-relaxed"
              />
              <button 
                disabled={!observation.trim()}
                className="w-full py-4 bg-black text-white rounded-full text-xs font-bold uppercase tracking-widest hover:opacity-90 disabled:opacity-20 transition-all flex items-center justify-center gap-2"
              >
                <MessageSquare size={14} /> Enviar Hallazgos a Ánima
              </button>
            </div>

          </div>
        )}
      </div>

      {/* FOOTER */}
      <div className="p-4 bg-white border-t border-black/5 text-[9px] text-neutral-300 font-bold uppercase tracking-[0.2em] flex justify-between">
        <span>Contexto: {activeTool?.name || 'Inactivo'}</span>
        <span>Aceleración Cognitiva ALEGR-IA</span>
      </div>

      <style>{`
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
    </div>
  );
}
